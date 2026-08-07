import Link from "next/link";
import { db } from "@/lib/db";
import { mockMode } from "@/lib/env";
import { StatCard } from "@/components/StatCard";
import { Badge } from "@/components/Badge";

export const dynamic = "force-dynamic";

const STATUS_COLOR: Record<string, "slate" | "green" | "amber" | "red" | "blue"> = {
  PENDING: "amber",
  APPROVED: "blue",
  SENT: "green",
  REJECTED: "slate",
  FAILED: "red",
};

export default async function DashboardPage() {
  const [leadCount, openMaintenance, emergencyMaintenance, openArrears, complianceDueOrOverdue, pendingApprovals, recentActions] = await Promise.all([
    db.contact.count({ where: { kind: "LEAD" } }),
    db.maintenanceTicket.count({ where: { status: { not: "RESOLVED" } } }),
    db.maintenanceTicket.count({ where: { status: { not: "RESOLVED" }, urgency: "EMERGENCY" } }),
    db.arrearsCase.count({ where: { stage: { not: "RESOLVED" } } }),
    db.complianceItem.count({ where: { status: { in: ["DUE_SOON", "OVERDUE"] } } }),
    db.action.count({ where: { status: "PENDING" } }),
    db.action.findMany({ orderBy: { createdAt: "desc" }, take: 10, include: { contact: true } }),
  ]);

  return (
    <div className="space-y-8">
      {mockMode && (
        <div className="rounded-lg border border-amber-300 bg-amber-50 dark:bg-amber-950 dark:border-amber-800 px-4 py-3 text-sm text-amber-800 dark:text-amber-300">
          <strong>Mock mode is on.</strong> No real emails/texts are sent and Monday.com isn&apos;t written to — everything is logged to the server console instead. Set{" "}
          <code className="font-mono">MOCK_INTEGRATIONS=false</code> plus real API keys when you&apos;re ready to go live (see README).
        </div>
      )}

      <div>
        <h1 className="text-xl font-semibold">Overview</h1>
        <p className="text-sm text-slate-500 mt-1">What the system is watching right now.</p>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
        <StatCard label="Leads" value={leadCount} />
        <StatCard label="Open maintenance" value={openMaintenance} tone={emergencyMaintenance > 0 ? "danger" : "default"} />
        <StatCard label="Emergencies" value={emergencyMaintenance} tone={emergencyMaintenance > 0 ? "danger" : "default"} />
        <StatCard label="Open arrears cases" value={openArrears} tone={openArrears > 0 ? "warn" : "default"} />
        <StatCard label="Compliance due/overdue" value={complianceDueOrOverdue} tone={complianceDueOrOverdue > 0 ? "warn" : "default"} />
        <StatCard label="Pending approvals" value={pendingApprovals} tone={pendingApprovals > 0 ? "warn" : "default"} />
      </div>

      {pendingApprovals > 0 && (
        <Link
          href="/approvals"
          className="block rounded-lg border border-amber-300 dark:border-amber-800 bg-amber-50 dark:bg-amber-950 px-4 py-3 text-sm text-amber-800 dark:text-amber-300 hover:bg-amber-100 dark:hover:bg-amber-900 transition"
        >
          {pendingApprovals} action{pendingApprovals === 1 ? "" : "s"} waiting for your review →
        </Link>
      )}

      <div>
        <h2 className="text-sm font-semibold text-slate-700 dark:text-slate-300 mb-3">Recent activity</h2>
        <div className="rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 divide-y divide-slate-100 dark:divide-slate-800">
          {recentActions.length === 0 && <p className="p-4 text-sm text-slate-500">Nothing yet — inbound messages and scheduled checks will show up here.</p>}
          {recentActions.map((a) => (
            <div key={a.id} className="p-4 flex items-start justify-between gap-4">
              <div className="min-w-0">
                <p className="text-sm font-medium truncate">{a.subject || a.body.slice(0, 80)}</p>
                <p className="text-xs text-slate-500 mt-0.5">
                  {a.contact?.name ?? "—"} · {a.workflow.toLowerCase()} · {new Date(a.createdAt).toLocaleString("en-GB")}
                </p>
              </div>
              <Badge color={STATUS_COLOR[a.status] ?? "slate"}>{a.status}</Badge>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
