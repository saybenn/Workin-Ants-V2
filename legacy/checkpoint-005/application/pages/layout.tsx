import type { Metadata } from "next";
import { EnvironmentBanner } from "@/components/EnvironmentBanner";
import "./globals.css";

export const metadata: Metadata = {
  title: "WorkinAnts",
  description: "Professional marketplace foundation",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="h-full antialiased">
      <body className="min-h-full flex flex-col">
        <EnvironmentBanner />
        {children}
      </body>
    </html>
  );
}
