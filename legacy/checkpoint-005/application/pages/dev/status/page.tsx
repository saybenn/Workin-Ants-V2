import { isProduction, publicEnv } from "@/lib/env";

export default function DevStatusPage() {
  if (isProduction) {
    return (
      <main className="mx-auto flex w-full max-w-3xl flex-1 flex-col justify-center px-6 py-16">
        <h1 className="text-3xl font-semibold tracking-tight">
          Not available in production
        </h1>
      </main>
    );
  }

  return (
    <main className="mx-auto flex w-full max-w-3xl flex-1 flex-col gap-8 px-6 py-16">
      <div>
        <p className="text-sm font-medium uppercase tracking-wide text-zinc-500">
          Developer Status
        </p>
        <h1 className="mt-3 text-4xl font-semibold tracking-tight">
          WorkinAnts infrastructure
        </h1>
      </div>

      <dl className="grid gap-4 sm:grid-cols-2">
        <div className="border border-zinc-200 p-4">
          <dt className="text-sm font-medium text-zinc-500">Environment</dt>
          <dd className="mt-1 text-lg font-semibold">{publicEnv.appEnv}</dd>
        </div>
        <div className="border border-zinc-200 p-4">
          <dt className="text-sm font-medium text-zinc-500">App URL</dt>
          <dd className="mt-1 break-words text-lg font-semibold">
            {publicEnv.appUrl}
          </dd>
        </div>
        <div className="border border-zinc-200 p-4">
          <dt className="text-sm font-medium text-zinc-500">Health</dt>
          <dd className="mt-1 text-lg font-semibold">/api/health</dd>
        </div>
        <div className="border border-zinc-200 p-4">
          <dt className="text-sm font-medium text-zinc-500">Debug env check</dt>
          <dd className="mt-1 text-lg font-semibold">
            /api/debug/env-check
          </dd>
        </div>
      </dl>

      <p className="text-sm leading-6 text-zinc-600">
        This page is for non-production diagnostics only. It must never display
        service keys, role claims, payment state, ownership claims, or protected
        data.
      </p>
    </main>
  );
}
