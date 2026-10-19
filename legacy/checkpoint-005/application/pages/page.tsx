import Link from "next/link";
import { isProduction, publicEnv } from "@/lib/env";

export default function Home() {
  return (
    <main className="mx-auto flex w-full max-w-4xl flex-1 flex-col justify-center gap-8 px-6 py-16">
      <div className="max-w-2xl">
        <p className="text-sm font-medium uppercase tracking-wide text-zinc-500">
          WorkinAnts
        </p>
        <h1 className="mt-3 text-4xl font-semibold tracking-tight sm:text-5xl">
          Discovery-first marketplace foundation
        </h1>
        <p className="mt-5 text-lg leading-8 text-zinc-600">
          Phase 1 infrastructure is in place for a production-oriented
          professional marketplace. Product workflows are intentionally deferred.
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        <div className="border border-zinc-200 p-4">
          <p className="text-sm font-medium text-zinc-500">Environment</p>
          <p className="mt-1 text-lg font-semibold">{publicEnv.appEnv}</p>
        </div>
        <div className="border border-zinc-200 p-4">
          <p className="text-sm font-medium text-zinc-500">Source of truth</p>
          <p className="mt-1 text-lg font-semibold">Postgres later</p>
        </div>
      </div>

      {!isProduction ? (
        <Link
          className="w-fit border border-zinc-900 px-4 py-2 text-sm font-medium transition-colors hover:bg-zinc-900 hover:text-white"
          href="/dev/status"
        >
          Developer status
        </Link>
      ) : null}
    </main>
  );
}
