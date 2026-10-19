import { publicEnv } from "@/lib/env";
import { logger } from "@/server/logger";
import { getRequestId } from "@/server/request-id";

export const runtime = "nodejs";

export function GET(request: Request) {
  const requestId = getRequestId(request.headers);

  logger.info("Health check hit", {
    route: "/api/health",
    requestId,
  });

  return Response.json({
    ok: true,
    service: "workin-ants",
    environment: publicEnv.appEnv,
    timestamp: new Date().toISOString(),
    requestId,
  });
}
