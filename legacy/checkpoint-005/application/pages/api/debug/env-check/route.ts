import { isProduction, publicEnv } from "@/lib/env";

export const runtime = "nodejs";

export function GET() {
  if (isProduction) {
    return Response.json({ ok: false }, { status: 404 });
  }

  return Response.json({
    ok: true,
    environment: publicEnv.appEnv,
    hasAppUrl: Boolean(publicEnv.appUrl),
    timestamp: new Date().toISOString(),
  });
}
