import "./globals.css";
import { ReactNode } from "react";

import { Sidebar } from "@/components/layout/sidebar";
import { AuthGate } from "@/components/auth/auth-gate";

export const metadata = {
  title: "NEXUS AI",
  description: "A personal AI engineering workspace.",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body><AuthGate><main className="mesh mx-auto flex min-h-screen max-w-[1440px] flex-col gap-6 px-4 py-4 md:px-6 md:py-6 lg:flex-row"><Sidebar /><div className="flex-1">{children}</div></main></AuthGate></body>
    </html>
  );
}
