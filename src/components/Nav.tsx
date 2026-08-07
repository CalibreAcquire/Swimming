"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { LogoutButton } from "./LogoutButton";

const LINKS = [
  { href: "/", label: "Dashboard" },
  { href: "/approvals", label: "Approvals" },
  { href: "/leads", label: "Leads" },
  { href: "/maintenance", label: "Maintenance" },
  { href: "/arrears", label: "Arrears" },
  { href: "/compliance", label: "Compliance" },
  { href: "/settings", label: "Settings" },
];

export function Nav({ staffName, pendingCount }: { staffName: string; pendingCount: number }) {
  const pathname = usePathname();

  return (
    <header className="border-b border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900">
      <div className="max-w-6xl mx-auto px-4 sm:px-6">
        <div className="flex items-center justify-between h-14">
          <div className="flex items-center gap-6">
            <span className="font-semibold text-slate-900 dark:text-slate-100 text-sm">Lettings AI</span>
            <nav className="flex items-center gap-1">
              {LINKS.map((link) => {
                const active = pathname === link.href;
                return (
                  <Link
                    key={link.href}
                    href={link.href}
                    className={`relative px-3 py-1.5 rounded-md text-sm transition ${
                      active
                        ? "bg-emerald-50 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-400"
                        : "text-slate-600 hover:text-slate-900 dark:text-slate-400 dark:hover:text-slate-100"
                    }`}
                  >
                    {link.label}
                    {link.href === "/approvals" && pendingCount > 0 && (
                      <span className="ml-1.5 inline-flex items-center justify-center rounded-full bg-amber-500 text-white text-[10px] font-semibold h-4 min-w-4 px-1">
                        {pendingCount}
                      </span>
                    )}
                  </Link>
                );
              })}
            </nav>
          </div>
          <div className="flex items-center gap-4">
            <span className="text-sm text-slate-500 hidden sm:inline">{staffName}</span>
            <LogoutButton />
          </div>
        </div>
      </div>
    </header>
  );
}
