import { notFound } from "next/navigation";

export default function DevelopmentStatusPage() {
  if (process.env.NODE_ENV !== "development") {
    notFound();
  }

  return (
    <main className="foundation-frame">
      <h1>Development diagnostics</h1>
      <p>Application process only. Database and provider health are unverified.</p>
    </main>
  );
}
