import { db } from "@/lib/db";
import { Badge } from "@/components/Badge";

export const dynamic = "force-dynamic";

const STAGE_COLOR: Record<string, "slate" | "green" | "amber" | "red" | "blue"> = {
  REMINDER_1: "slate",
  REMINDER_2: "amber",
  FORMAL_NOTICE: "red",
  ESCALATED: "red",
  RESOLVED: "green",
};

function gbp(pence: number) {
  return `£${(pence / 100).toFixed(2)}`;
}

export default async function ArrearsPage() {
  const cases = await db.arrearsCase.findMany({
    orderBy: [{ daysOverdue: "desc" }],
    include: { tenancy: { include: { tenant: true, property: true } } },
  });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold">Rent arrears</h1>
        <p className="text-sm text-slate-500 mt-1">
          Reminders 1–2 send automatically; formal notices and landlord escalations wait for approval. No live payment feed yet — cases are opened manually until Goodlord is
          connected (see README).
        </p>
      </div>

      <div className="rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 divide-y divide-slate-100 dark:divide-slate-800">
        {cases.length === 0 && <p className="p-4 text-sm text-slate-500">No open arrears cases.</p>}
        {cases.map((c) => (
          <div key={c.id} className="p-4 flex items-center justify-between gap-4">
            <div>
              <p className="text-sm font-medium">
                {c.tenancy.property.addressLine1} · {c.tenancy.tenant.name}
              </p>
              <p className="text-xs text-slate-500 mt-0.5">
                {gbp(c.amountOwedPence)} owed · {c.daysOverdue} days overdue
              </p>
            </div>
            <Badge color={STAGE_COLOR[c.stage]}>{c.stage.replace(/_/g, " ")}</Badge>
          </div>
        ))}
      </div>
    </div>
  );
}
