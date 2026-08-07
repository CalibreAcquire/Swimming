import { db } from "@/lib/db";
import { Badge } from "@/components/Badge";

export const dynamic = "force-dynamic";

const URGENCY_COLOR: Record<string, "slate" | "green" | "amber" | "red" | "blue"> = {
  EMERGENCY: "red",
  URGENT: "amber",
  ROUTINE: "slate",
};

const STATUS_COLOR: Record<string, "slate" | "green" | "amber" | "red" | "blue"> = {
  NEW: "amber",
  ACKNOWLEDGED: "blue",
  CONTRACTOR_ASSIGNED: "blue",
  IN_PROGRESS: "blue",
  RESOLVED: "green",
};

export default async function MaintenancePage() {
  const tickets = await db.maintenanceTicket.findMany({
    orderBy: [{ urgency: "asc" }, { createdAt: "desc" }],
    include: { property: true, tenant: true, contractor: true },
  });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold">Maintenance</h1>
        <p className="text-sm text-slate-500 mt-1">Emergencies always alert staff immediately; contractor instructions wait for approval.</p>
      </div>

      <div className="rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 divide-y divide-slate-100 dark:divide-slate-800">
        {tickets.length === 0 && <p className="p-4 text-sm text-slate-500">No maintenance tickets yet.</p>}
        {tickets.map((t) => (
          <div key={t.id} className="p-4 space-y-2">
            <div className="flex items-start justify-between gap-4">
              <div>
                <p className="text-sm font-medium">
                  {t.property.addressLine1} · {t.category}
                </p>
                <p className="text-xs text-slate-500 mt-0.5">
                  {t.tenant.name} · reported {new Date(t.createdAt).toLocaleString("en-GB")}
                  {t.contractor && ` · assigned to ${t.contractor.name}`}
                </p>
              </div>
              <div className="flex items-center gap-2 shrink-0">
                <Badge color={URGENCY_COLOR[t.urgency]}>{t.urgency}</Badge>
                <Badge color={STATUS_COLOR[t.status]}>{t.status.replace(/_/g, " ")}</Badge>
              </div>
            </div>
            <p className="text-sm text-slate-600 dark:text-slate-400">{t.description}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
