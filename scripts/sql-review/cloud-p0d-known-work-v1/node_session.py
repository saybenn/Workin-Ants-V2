"""Use the accepted binary pipe pump for the fixed known-work Node protocol."""

from pathlib import Path
import re
import subprocess
import time
from types import ModuleType

APP_PIPE = "scripts/sql-review/cloud-app-source8-v1/host_session.py"
APP_PIPE_SHA = "0149b82add667b485a2d6e044ee252f5f30add8db8ea87df9147cf9181fe3757"
REMOTE = "/run/wa-f0-known-work"
ENTRY = "known-work-child.mjs"
LOGIN = "known_work_node"
NODE = "/run/wa-f0-tools/node/bin/node"
DRIVER = "/run/wa-f0-tools/node_modules/postgres/src/index.js"
BRIDGE = "P0D_KNOWN_WORK_BRIDGE_UNCONFIRMED"
SOCKET = "P0D_KNOWN_WORK_SOCKET_UNCONFIRMED"
ABORT = "P0D_KNOWN_WORK_CHILD_ABORTED"
DEADLINE = "P0D_KNOWN_WORK_SESSION_DEADLINE"
SESSION_SECONDS = 90
CODES = {BRIDGE, SOCKET, ABORT, DEADLINE, "APP_LOGIN_SCOPE", "APP_SESSION_START_UNCONFIRMED", "APP_SESSION_EXIT_UNCONFIRMED",
         "APP_SESSION_DEADLINE", "APP_SESSION_ACK_BOUNDARY", "APP_SESSION_OUTPUT_LIMIT", "APP_SESSION_TRUNCATED_OUTPUT",
         "APP_SESSION_RECORD_LIMIT"}


def session_type(raw, root, S, validation):
    # The reviewed App pump ignores blank psql output rows. The Node framing consumes every LF-delimited row.
    replacements = {
        b'rows = [line for line in stdout.split(b"\\n") if line]': b'rows = stdout.split(b"\\n")[:-1] if stdout else []',
        b'deadline = time.monotonic() + (CLOSE_SECONDS if closing else CALL_SECONDS)\n        terminal = None':
        b'deadline = min(self.deadline, time.monotonic() + (CLOSE_SECONDS if closing else CALL_SECONDS))\n        terminal = None',
        b'0 <= terminal <= 3 and sent == len(payload) and not acknowledged,':
        b'0 <= terminal <= 3 and (sent == len(payload) or self.index == 0 and sent == 0) and not acknowledged,',
        b'                    except BlockingIOError:\n                        continue\n        stdout = bytes(response["stdout"])':
        b'                    except BrokenPipeError:\n'
        b'                        need(key.data == "stdin" and self.index == 0 and sent == 0, BRIDGE_ERROR)\n'
        b'                        selector.unregister(key.fd)\n'
        b'                    except BlockingIOError:\n                        continue\n        stdout = bytes(response["stdout"])',
        b'        return [line.decode("utf-8") for line in rows], acknowledged, bytes(response["stderr"]).decode("utf-8")':
        b'        return [line.decode("utf-8") for line in rows], acknowledged, bytes(response["stderr"]).decode("utf-8"), sent',
    }
    S.require(S.sha(raw) == APP_PIPE_SHA and all(raw.count(old) == 1 for old in replacements), BRIDGE)
    for old, new in replacements.items():
        raw = raw.replace(old, new)
    base = ModuleType("_workinants_known_work_pipe")
    base.__file__ = str(Path(root) / APP_PIPE)
    exec(compile(raw, base.__file__, "exec", dont_inherit=True), base.__dict__)
    base.APP_ROLES = (LOGIN,)
    base.CHANNEL_LIMIT = 2048 + max(len(phase) for phase in validation.PHASES) + 32
    base.BRIDGE_ERROR = BRIDGE

    class Session(base.BoundedSession):
        def __init__(self, owner):
            self.owner = owner
            self.index = 0
            self.deadline = time.monotonic() + SESSION_SECONDS
            super().__init__(LOGIN, self)

        def socket_checked(self):
            self.owner.check_socket(SOCKET)

        def limit(self, seconds):
            remaining = self.deadline - time.monotonic()
            if remaining <= seconds:
                self.fail(DEADLINE)
            return remaining

        def uncertain(self, code):
            self.owner.sticky()
            self.owner.program._required_safety_first_exception(S.Held(code), self.owner.report["stage"])

        def spawn(self, role):
            self.limit(0)
            self.socket_checked()
            cid = self.owner.resources.cid
            base.need(role == LOGIN and type(cid) is str and re.fullmatch(r"[0-9a-f]{64}", cid), BRIDGE)
            args = self.owner.docker.argv("exec", "-i", "--user", "65534:65534", cid, "/usr/bin/env", "-i", NODE,
                                          f"{REMOTE}/{ENTRY}", DRIVER)
            return self.owner.transport.io.Popen(args, cwd=str(root), shell=False, stdin=subprocess.PIPE,
                                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=0)

        def advance(self, phase, payload, server_ms=None):
            try:
                self.limit(0)
                self.socket_checked()
                base.need(not self.closed and self.index < len(validation.PHASES)
                          and phase == validation.PHASES[self.index] and (phase == "INIT" or self.process.poll() is None),
                          BRIDGE)
                base.need(type(payload) is bytes and 2 <= len(payload) <= 256
                          and payload.isascii() and payload.count(b"\n") == 1 and payload.endswith(b"\n"), BRIDGE)
                closing = phase == "FINISH"
                ack = None if closing else ("WA_P0D_WORK_ACK|" + phase).encode()
                rows, acknowledged, errors, sent = self.exchange(payload, ack=ack, closing=closing)
                self.socket_checked()
                terminal = self.process.poll()
                base.need(not errors and len(rows) == 1 and all(" " <= character <= "~" for character in rows[0]), BRIDGE)
                raw = rows[0].encode()
                base.need(not any(secret.encode() in raw for secret in self.owner.program.all_secrets), BRIDGE)
                record = validation.receipt(raw, phase, acknowledged=acknowledged, process_exit=terminal, server_ms=server_ms)
                base.need(sent == len(payload) or record["phase"] == "ENTRY" and sent == 0, BRIDGE)
                if terminal is not None:
                    base.need(not self.readers and self.close_pipes(), BRIDGE)
                    self.closed = True
                self.limit(0)
                self.index += 1
                return record
            except BaseException as error:
                if self.failure is not None:
                    raise
                observed = getattr(error, "code", None)
                code = observed if type(observed) is str and observed in CODES else BRIDGE
                self.fail(DEADLINE if time.monotonic() >= self.deadline else code)

        def terminate_unconfirmed(self):
            if not self.closed and self.failure is None:
                self.fail(ABORT)

    return Session
