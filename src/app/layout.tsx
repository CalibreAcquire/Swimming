import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { getCurrentSession } from "@/lib/session";
import { Nav } from "@/components/Nav";
import { db } from "@/lib/db";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Lettings AI System",
  description: "Bespoke automation for lead handling, maintenance, arrears, and compliance.",
};

export default async function RootLayout({ children }: LayoutProps<"/">) {
  const session = await getCurrentSession();
  const pendingCount = session ? await db.action.count({ where: { status: "PENDING" } }).catch(() => 0) : 0;

  return (
    <html lang="en" className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}>
      <body className="min-h-full flex flex-col bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100">
        {session && <Nav staffName={session.name} pendingCount={pendingCount} />}
        <main className="flex-1 w-full max-w-6xl mx-auto px-4 sm:px-6 py-8">{children}</main>
      </body>
    </html>
  );
}
