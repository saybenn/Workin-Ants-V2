"use client";

export default function Error({
  error,
  unstable_retry,
}: {
  error: Error & { digest?: string };
  unstable_retry: () => void;
}) {
  console.error(error);

  return (
    <main className="mx-auto flex w-full max-w-3xl flex-1 flex-col justify-center gap-4 px-6 py-16">
      <h1 className="text-3xl font-semibold tracking-tight">
        Something went wrong
      </h1>
      <p className="text-zinc-600">
        The app hit an unexpected rendering error. Try again, and check the
        server logs if this continues.
      </p>
      <button
        className="w-fit border border-zinc-900 px-4 py-2 text-sm font-medium"
        onClick={() => unstable_retry()}
        type="button"
      >
        Try again
      </button>
    </main>
  );
}
