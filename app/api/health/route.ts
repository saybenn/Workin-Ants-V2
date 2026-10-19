export const runtime = "nodejs";

export function GET() {
  return Response.json(
    { status: "ok", service: "workin-ants", check: "process" },
    { headers: { "Cache-Control": "no-store" } },
  );
}
