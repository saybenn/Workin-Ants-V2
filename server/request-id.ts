export function getRequestId(headers: Headers): string {
  return (
    headers.get("x-request-id") ??
    headers.get("x-vercel-id") ??
    crypto.randomUUID()
  );
}
