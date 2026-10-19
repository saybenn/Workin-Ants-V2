import { isProduction, publicEnv } from "@/lib/env";

export function EnvironmentBanner() {
  if (isProduction) {
    return null;
  }

  return (
    <div className="border-b border-amber-300 bg-amber-50 px-4 py-2 text-center text-sm font-medium text-amber-950">
      Environment: {publicEnv.appEnv}
    </div>
  );
}
