import { db } from "@/lib/db";
import { ApprovalCard } from "@/components/ApprovalCard";
import { Badge } from "@/components/Badge";

export const dynamic = "force-dynamic";

const STATUS_COLOR: Record<string, "slate" | "green" | "amber" | "red" | "blue"> = {
  SENT: "green",
  REJECTED: "slate",
  FAILED: "red",
};

export default async function ApprovalsPage() {
  const [pending, recentDecided] = await Promise.all([
    db.action.findMany({ where: { status: "PENDING" }, orderBy: { createdAt: "asc" }, include: { contact: true } }),
    db.action.findMany({
      where: { status: { in: ["SENT", "REJECTED", "FAILED"] }, autoSend: false },
      orderBy: { decidedAt: "desc" },
      take: 10,
      include: { contact: true },
    }),
  ]);

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-xl font-semibold">Approvals</h1>
        <p className="text-sm text-slate-500 mt-1">
          Anything with money, legal weight, or a third-party commitment waits here. Everything else sends automatically per the rules in Settings.
        </p>
      </div>

      {pending.length === 0 ? (
        <p className="text-sm text-slate-500">Nothing waiting on you right now.</p>
      ) : (
        <div className="space-y-4">
          {pending.map((a) => (
            <ApprovalCard
              key={a.id}
              action={{
                id: a.id,
                type: a.type,
                workflow: a.workflow,
                channel: a.channel,
                contactName: a.contact?.name ?? null,
                subject: a.subject,
                body: a.body,
                reasoning: a.reasoning,
                createdAt: a.createdAt.toISOString(),
              }}
            />
          ))}
        </div>
      )}

      {recentDecided.length > 0 && (
        <div>
          <h2 className="text-sm font-semibold text-slate-700 dark:text-slate-300 mb-3">Recently decided</h2>
          <div className="rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 divide-y divide-slate-100 dark:divide-slate-800">
            {recentDecided.map((a) => (
              <div key={a.id} className="p-4 flex items-center justify-between gap-4">
                <div className="min-w-0">
                  <p className="text-sm font-medium truncate">{a.subject || a.body.slice(0, 80)}</p>
                  <p className="text-xs text-slate-500 mt-0.5">
                    {a.contact?.name ?? "—"} · by {a.decidedBy ?? "—"} · {a.decidedAt ? new Date(a.decidedAt).toLocaleString("en-GB") : ""}
                  </p>
                </div>
                <Badge color={STATUS_COLOR[a.status] ?? "slate"}>{a.status}</Badge>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
