export const runtime = "nodejs";

function respond(request: Request) {
  if (process.env.NODE_ENV !== "development") {
    return Response.json(
      { status: "not-found" },
      { status: 404, headers: { "Cache-Control": "no-store" } },
    );
  }

  if (request.method !== "GET" && request.method !== "HEAD") {
    return Response.json(
      { status: "method-not-allowed" },
      { status: 405, headers: { Allow: "GET, HEAD", "Cache-Control": "no-store" } },
    );
  }

  if (request.method === "HEAD") {
    return new Response(null, { headers: { "Cache-Control": "no-store" } });
  }

  return Response.json(
    { status: "ok", mode: "development", check: "process" },
    { headers: { "Cache-Control": "no-store" } },
  );
}

export const GET = respond;
export const HEAD = respond;
export const POST = respond;
export const PUT = respond;
export const PATCH = respond;
export const DELETE = respond;
export const OPTIONS = respond;
