import { Channel, Contact, MaintenanceUrgency } from "@prisma/client";
import { db } from "../db";
import { createAction } from "../actions";
import { TriageResult } from "../ai";
import { createMondayItem } from "../monday";
import { env } from "../env";

const CATEGORY_KEYWORDS: [string, string][] = [
  ["boiler", "heating"],
  ["heating", "heating"],
  ["radiator", "heating"],
  ["leak", "plumbing"],
  ["tap", "plumbing"],
  ["pipe", "plumbing"],
  ["toilet", "plumbing"],
  ["water", "plumbing"],
  ["electric", "electrical"],
  ["socket", "electrical"],
  ["fuse", "electrical"],
  ["mice", "pest"],
  ["mouse", "pest"],
  ["rat", "pest"],
  ["pest", "pest"],
  ["wasp", "pest"],
  ["mould", "damp"],
  ["damp", "damp"],
  ["lock", "security"],
  ["door", "structural"],
  ["window", "structural"],
  ["roof", "structural"],
  ["fridge", "appliance"],
  ["oven", "appliance"],
  ["washing machine", "appliance"],
  ["dishwasher", "appliance"],
];

function categorize(text: string): string {
  const t = text.toLowerCase();
  for (const [kw, cat] of CATEGORY_KEYWORDS) if (t.includes(kw)) return cat;
  return "general";
}

export async function handleInboundMaintenanceMessage(contact: Contact, messageText: string, triage: TriageResult, channel: Channel) {
  const tenancy = await db.tenancy.findFirst({ where: { tenantId: contact.id, active: true }, include: { property: true } });

  if (!tenancy) {
    await createAction({
      type: "maintenance.acknowledgement",
      channel,
      contactId: contact.id,
      body: "Thanks for letting us know — we're looking into this and will be in touch shortly.",
      reasoning: "No active tenancy on file for this contact; flagged for manual linking.",
    });
    return;
  }

  const urgency: MaintenanceUrgency =
    triage.urgency === "EMERGENCY" ? "EMERGENCY" : triage.urgency === "URGENT" ? "URGENT" : "ROUTINE";
  const category = categorize(messageText);

  const ticket = await db.maintenanceTicket.create({
    data: {
      propertyId: tenancy.propertyId,
      tenantId: contact.id,
      category,
      urgency,
      description: messageText,
      status: "ACKNOWLEDGED",
    },
  });

  const mondayItemId = await createMondayItem(
    env.mondayBoards.maintenance,
    `${tenancy.property.addressLine1} — ${category} (${urgency})`,
    { status: { label: urgency === "EMERGENCY" ? "Emergency" : "New" } }
  );
  await db.maintenanceTicket.update({ where: { id: ticket.id }, data: { mondayItemId } });

  const ackBody =
    urgency === "EMERGENCY"
      ? "Got this — that sounds urgent and we're on it right away. If it's safe to do so, take any immediate precautions (e.g. shut off water/gas at the mains). We're contacting an emergency contractor now and will update you shortly."
      : urgency === "URGENT"
      ? "Thanks for reporting this — we've logged it and are arranging a contractor. We'll be in touch with next steps shortly."
      : "Thanks for letting us know — we've logged this and will arrange for someone to take a look. We'll keep you posted.";

  await createAction({
    type: "maintenance.acknowledgement",
    channel,
    contactId: contact.id,
    relatedType: "MaintenanceTicket",
    relatedId: ticket.id,
    body: ackBody,
    reasoning: `Classified as ${urgency} (${triage.summary}).`,
  });

  if (urgency === "EMERGENCY") {
    await createAction({
      type: "maintenance.emergency_internal_alert",
      channel: "INTERNAL",
      relatedType: "MaintenanceTicket",
      relatedId: ticket.id,
      body: `EMERGENCY maintenance report at ${tenancy.property.addressLine1} (tenant: ${contact.name}, via ${channel}): "${messageText}"`,
      reasoning: "Emergency alerts always fire immediately regardless of tier.",
    });
  }

  // If we have a contractor on file, draft an instruction — held for approval since it commits cost.
  const contractor = await db.contact.findFirst({ where: { kind: "CONTRACTOR" } });
  if (contractor) {
    await createAction({
      type: "maintenance.contractor_instruction",
      channel: "EMAIL",
      contactId: contractor.id,
      relatedType: "MaintenanceTicket",
      relatedId: ticket.id,
      subject: `${urgency === "EMERGENCY" ? "Emergency callout" : "Job"} — ${tenancy.property.addressLine1}`,
      body: `Hi ${contractor.name},\n\nWe have a ${category} issue at ${tenancy.property.addressLine1} reported as ${urgency.toLowerCase()}:\n"${messageText}"\n\nTenant ${contact.name} can be reached on ${
        contact.phone ?? contact.email ?? "the number on file"
      }. Please confirm availability.\n\nCalibre Lettings`,
      reasoning: "Instructing a contractor commits cost on your behalf — held for approval.",
    });
  }

  return ticket;
}
