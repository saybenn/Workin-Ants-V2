"""Bounded Linux pipe handling for one reviewed psql transaction at a time."""

import os
import re
import secrets
import selectors
import time


CHANNEL_LIMIT = 65536
INPUT_LIMIT = 256 * 1024
CALL_SECONDS = 15
CLOSE_SECONDS = 10
APP_ROLES = ("postgres", "wa_context_issuer", "wa_app_runtime")


class SessionStop(RuntimeError):
    def __init__(self, code):
        super().__init__(code)
        self.code = code


def need(value, code):
    if not value:
        raise SessionStop(code)


class BoundedSession:
    """Keep psql payload and response bytes in memory until the protocol checks them."""

    def __init__(self, role, coordinator):
        need(role in APP_ROLES, "APP_LOGIN_SCOPE")
        self.role, self.coordinator = role, coordinator
        self.backend, self.process, self.failure = None, None, None
        self.active = self.closed = False
        self.readers = {}
        try:
            self.process = coordinator.spawn(role)
            for stream in (self.process.stdin, self.process.stdout, self.process.stderr):
                os.set_blocking(stream.fileno(), False)
            self.readers = {self.process.stdout.fileno(): "stdout", self.process.stderr.fileno(): "stderr"}
        except BaseException:
            self.fail("APP_SESSION_START_UNCONFIRMED")

    def fail(self, code):
        self.failure = self.failure or code
        try:
            self.coordinator.uncertain(self.failure)
        except BaseException:
            pass
        finally:
            if self.process is not None:
                try:
                    for action, timeout in ((self.process.terminate, 1), (self.process.kill, 2)):
                        try:
                            if self.process.poll() is not None:
                                break
                        except BaseException:
                            pass
                        try:
                            action()
                        except BaseException:
                            pass
                        try:
                            self.process.wait(timeout=timeout)
                            break
                        except BaseException:
                            continue
                finally:
                    self.close_pipes()
        raise SessionStop(self.failure) from None

    def close_pipes(self):
        closed = True
        for stream in (self.process.stdin, self.process.stdout, self.process.stderr):
            try:
                stream.close()
                closed = closed and stream.closed
            except BaseException:
                closed = False
        return closed

    def exchange(self, payload, *, ack=None, closing=False):
        response = {"stdout": bytearray(), "stderr": bytearray()}
        sent = 0
        deadline = time.monotonic() + (CLOSE_SECONDS if closing else CALL_SECONDS)
        terminal = None
        with selectors.DefaultSelector() as selector:
            for fd, channel in self.readers.items():
                selector.register(fd, selectors.EVENT_READ, channel)
            if payload:
                stdin = self.process.stdin.fileno()
                selector.register(stdin, selectors.EVENT_WRITE, "stdin")
            while True:
                stdout = response["stdout"]
                acknowledged = ack is not None and ack in stdout.split(b"\n")[:-1]
                terminal = self.process.poll()
                if terminal is not None and not self.readers:
                    need(type(terminal) is int and 0 <= terminal <= 3 and sent == len(payload) and not acknowledged,
                         "APP_SESSION_EXIT_UNCONFIRMED")
                    break
                remaining = deadline - time.monotonic()
                need(remaining > 0, "APP_SESSION_DEADLINE")
                ready = selector.select(0 if acknowledged else min(0.1, remaining))
                if acknowledged and not ready:
                    need(terminal is None and len(self.readers) == 2 and sent == len(payload) and stdout.endswith(b"\n")
                         and stdout.split(b"\n")[-2] == ack, "APP_SESSION_ACK_BOUNDARY")
                    break
                for key, _ in ready:
                    try:
                        if key.data == "stdin":
                            sent += os.write(key.fd, payload[sent:sent + 16384])
                            if sent == len(payload):
                                selector.unregister(key.fd)
                                if closing:
                                    self.process.stdin.close()
                        else:
                            chunk = os.read(key.fd, 16384)
                            if not chunk:
                                selector.unregister(key.fd)
                                del self.readers[key.fd]
                            else:
                                output = response[key.data]
                                need(len(output) + len(chunk) <= CHANNEL_LIMIT, "APP_SESSION_OUTPUT_LIMIT")
                                output.extend(chunk)
                    except BlockingIOError:
                        continue
        stdout = bytes(response["stdout"])
        need(not stdout or stdout.endswith(b"\n"), "APP_SESSION_TRUNCATED_OUTPUT")
        rows = [line for line in stdout.split(b"\n") if line]
        need(not acknowledged or rows.pop() == ack and ack not in rows, "APP_SESSION_ACK_BOUNDARY")
        need(len(rows) <= 16, "APP_SESSION_RECORD_LIMIT")
        return [line.decode("utf-8") for line in rows], acknowledged, bytes(response["stderr"]).decode("utf-8")

    def call(self, text):
        need(not self.closed and type(text) is str, "APP_SESSION_CALL_SCOPE")
        if self.failure is not None:
            raise SessionStop(self.failure)
        ack = ("WA_CLOUD_APP_ACK|" + secrets.token_hex(16)).encode()
        try:
            self.coordinator.socket_checked()
            need(self.process.poll() is None, "APP_SESSION_EXIT_UNCONFIRMED")
            payload = text.encode("utf-8") + b"\nSELECT '" + ack + b"';\n"
            need(len(payload) <= INPUT_LIMIT and b"\x00" not in payload, "APP_SESSION_INPUT_LIMIT")
            rows, acknowledged, errors = self.exchange(payload, ack=ack)
            self.coordinator.socket_checked()
            if acknowledged and re.search(r"\b(?:COMMIT|ROLLBACK);\s*$", text):
                self.active = False
            return rows, acknowledged, errors
        except BaseException as error:
            self.fail(error.code if isinstance(error, SessionStop) else "APP_SESSION_IO_UNCONFIRMED")

    def close(self):
        if self.closed:
            return self.process.returncode
        if self.failure is not None:
            raise SessionStop(self.failure)
        try:
            if self.process.poll() is None:
                payload = b"ROLLBACK;\n\\q\n" if self.active else b"\\q\n"
            else:
                payload = b""
            rows, _, errors = self.exchange(payload, closing=True)
            pipes_closed = self.close_pipes()
            need(pipes_closed and not rows and not errors and self.backend is not None, "APP_SESSION_CLOSURE_UNCONFIRMED")
            self.coordinator.socket_checked()
            self.coordinator.require_backend_absent(self.role, self.backend)
            self.closed = True
            return self.process.returncode
        except BaseException as error:
            self.fail(error.code if isinstance(error, SessionStop) else "APP_SESSION_CLOSURE_UNCONFIRMED")
