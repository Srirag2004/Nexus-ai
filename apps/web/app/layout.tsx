import "./globals.css";
import { ReactNode } from "react";

import { Sidebar } from "@/components/layout/sidebar";

export const metadata = {
  title: "NEXUS AI",
  description: "A personal AI engineering workspace.",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>
        <main className="mx-auto flex min-h-screen max-w-7xl flex-col gap-6 px-4 py-6 lg:flex-row">
          <Sidebar />
          <div className="flex-1">{children}</div>
        </main>
      </body>
    </html>
  );
}

