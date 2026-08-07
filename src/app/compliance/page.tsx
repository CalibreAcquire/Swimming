import { db } from "@/lib/db";
import { Badge } from "@/components/Badge";

export const dynamic = "force-dynamic";

const STATUS_COLOR: Record<string, "slate" | "green" | "amber" | "red" | "blue"> = {
  VALID: "green",
  DUE_SOON: "amber",
  OVERDUE: "red",
  RESOLVED: "green",
};

const LABELS: Record<string, string> = {
  GAS_SAFETY: "Gas Safety Certificate",
  EICR: "EICR",
  EPC: "EPC",
  DEPOSIT_PROTECTION: "Deposit Protection",
  RIGHT_TO_RENT: "Right to Rent",
};

export default async function CompliancePage() {
  const items = await db.complianceItem.findMany({
    orderBy: [{ dueDate: "asc" }],
    include: { property: { include: { landlord: true } } },
  });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold">Compliance</h1>
        <p className="text-sm text-slate-500 mt-1">Reminders at T-30/T-14/T-1 send automatically. A confirmed breach always alerts staff and holds the tenant/landlord notice for approval.</p>
      </div>

      <div className="rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 divide-y divide-slate-100 dark:divide-slate-800">
        {items.length === 0 && <p className="p-4 text-sm text-slate-500">No compliance items tracked yet.</p>}
        {items.map((item) => (
          <div key={item.id} className="p-4 flex items-center justify-between gap-4">
            <div>
              <p className="text-sm font-medium">
                {item.property.addressLine1} · {LABELS[item.type]}
              </p>
              <p className="text-xs text-slate-500 mt-0.5">Due {new Date(item.dueDate).toLocaleDateString("en-GB")} · landlord {item.property.landlord?.name ?? "—"}</p>
            </div>
            <Badge color={STATUS_COLOR[item.status]}>{item.status.replace(/_/g, " ")}</Badge>
          </div>
        ))}
      </div>
    </div>
  );
}
