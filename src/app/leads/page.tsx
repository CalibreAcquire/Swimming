import { db } from "@/lib/db";
import { Badge } from "@/components/Badge";

export const dynamic = "force-dynamic";

export default async function LeadsPage() {
  const leads = await db.contact.findMany({
    where: { kind: "LEAD" },
    orderBy: { updatedAt: "desc" },
    include: {
      messages: { orderBy: { createdAt: "desc" }, take: 1 },
      viewingSlotBookings: { include: { property: true } },
    },
  });

  const openSlots = await db.viewingSlot.findMany({ where: { status: "OPEN" }, include: { property: true }, orderBy: { startsAt: "asc" } });

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-xl font-semibold">Leads & viewings</h1>
        <p className="text-sm text-slate-500 mt-1">Prospective tenants and landlords currently in the pipeline.</p>
      </div>

      <div className="rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 divide-y divide-slate-100 dark:divide-slate-800">
        {leads.length === 0 && <p className="p-4 text-sm text-slate-500">No leads yet — inbound enquiries will appear here automatically.</p>}
        {leads.map((lead) => (
          <div key={lead.id} className="p-4 flex items-start justify-between gap-4">
            <div className="min-w-0">
              <p className="text-sm font-medium">{lead.name}</p>
              <p className="text-xs text-slate-500 mt-0.5">{lead.email || lead.phone}</p>
              {lead.messages[0] && <p className="text-sm text-slate-600 dark:text-slate-400 mt-2 line-clamp-2">&ldquo;{lead.messages[0].body}&rdquo;</p>}
            </div>
            <div className="flex flex-col items-end gap-1 shrink-0">
              {lead.viewingSlotBookings.length > 0 && <Badge color="green">Viewing booked</Badge>}
              {lead.mondayItemId && <span className="text-[11px] text-slate-400">synced to Monday</span>}
            </div>
          </div>
        ))}
      </div>

      <div>
        <h2 className="text-sm font-semibold text-slate-700 dark:text-slate-300 mb-3">Open viewing slots</h2>
        <div className="rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 divide-y divide-slate-100 dark:divide-slate-800">
          {openSlots.length === 0 && <p className="p-4 text-sm text-slate-500">No open slots — add some via the database or a future scheduling screen.</p>}
          {openSlots.map((slot) => (
            <div key={slot.id} className="p-4 flex items-center justify-between">
              <span className="text-sm">{slot.property.addressLine1}</span>
              <span className="text-sm text-slate-500">{new Date(slot.startsAt).toLocaleString("en-GB", { weekday: "short", day: "numeric", month: "short", hour: "2-digit", minute: "2-digit" })}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
