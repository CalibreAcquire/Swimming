import { Channel, ComplianceType, Contact } from "@prisma/client";
import { db } from "../db";
import { createAction } from "../actions";
import { draftReply, TriageResult } from "../ai";
import { alertStaff } from "../alerts";
import { createMondayItem, updateMondayItem } from "../monday";
import { env } from "../env";

const REMINDER_WINDOWS_DAYS = [30, 14, 1];

const LABELS: Record<ComplianceType, string> = {
  GAS_SAFETY: "Gas Safety Certificate",
  EICR: "Electrical Installation Condition Report (EICR)",
  EPC: "Energy Performance Certificate (EPC)",
  DEPOSIT_PROTECTION: "Deposit Protection",
  RIGHT_TO_RENT: "Right to Rent check",
};

/** Daily check across all tracked compliance deadlines — reminders while due, alert + hold-for-approval once breached. */
export async function runComplianceCheck() {
  const items = await db.complianceItem.findMany({
    where: { status: { not: "RESOLVED" } },
    include: { property: { include: { landlord: true } } },
  });
  const now = new Date();

  for (const item of items) {
    const daysUntilDue = Math.ceil((item.dueDate.getTime() - now.getTime()) / 86400000);
    const label = LABELS[item.type];

    if (daysUntilDue < 0) {
      if (item.status !== "OVERDUE") {
        await db.complianceItem.update({ where: { id: item.id }, data: { status: "OVERDUE" } });
        await alertStaff(`COMPLIANCE BREACH: ${label} at ${item.property.addressLine1} expired ${Math.abs(daysUntilDue)} day(s) ago.`);

        if (item.property.landlordId) {
          await createAction({
            type: "compliance.breach_tenant_notice",
            channel: "EMAIL",
            contactId: item.property.landlordId,
            relatedType: "ComplianceItem",
            relatedId: item.id,
            subject: `Urgent: ${label} has expired — ${item.property.addressLine1}`,
            body: `Hi ${item.property.landlord?.name ?? "there"},\n\nThe ${label} for ${item.property.addressLine1} expired ${Math.abs(
              daysUntilDue
            )} day(s) ago. This needs urgent attention to keep the property compliant. Please let us know how you'd like to proceed with booking a renewal.\n\nCalibre Lettings`,
            reasoning: "Confirmed compliance breach carries legal weight — held for approval before it reaches the landlord.",
          });
        }
      }
      await syncComplianceToMonday(item.id);
      continue;
    }

    if (REMINDER_WINDOWS_DAYS.includes(daysUntilDue)) {
      if (item.status !== "DUE_SOON") await db.complianceItem.update({ where: { id: item.id }, data: { status: "DUE_SOON" } });

      if (item.property.landlordId) {
        await createAction({
          type: "compliance.reminder",
          channel: "EMAIL",
          contactId: item.property.landlordId,
          relatedType: "ComplianceItem",
          relatedId: item.id,
          subject: `${label} due in ${daysUntilDue} day(s) — ${item.property.addressLine1}`,
          body: `Hi ${item.property.landlord?.name ?? "there"},\n\nThe ${label} for ${item.property.addressLine1} is due in ${daysUntilDue} day(s). Let us know if you'd like us to arrange the renewal.\n\nCalibre Lettings`,
          reasoning: `T-${daysUntilDue} reminder window.`,
        });
      }
    }

    await syncComplianceToMonday(item.id);
  }
}

async function syncComplianceToMonday(itemId: string) {
  const item = await db.complianceItem.findUniqueOrThrow({ where: { id: itemId }, include: { property: true } });
  const label = LABELS[item.type];
  const columnValues = { status: { label: item.status.replace(/_/g, " ") }, due_date: item.dueDate.toISOString().slice(0, 10) };

  let mondayItemId = item.mondayItemId;
  if (!mondayItemId) {
    mondayItemId = await createMondayItem(env.mondayBoards.compliance, `${item.property.addressLine1} — ${label}`, columnValues);
    await db.complianceItem.update({ where: { id: item.id }, data: { mondayItemId } });
  } else {
    await updateMondayItem(env.mondayBoards.compliance, mondayItemId, columnValues);
  }
}

/** Inbound messages classified as COMPLIANCE (e.g. a tenant asking about referencing/document status). */
export async function handleInboundComplianceMessage(contact: Contact, messageText: string, triage: TriageResult, channel: Channel) {
  const body = await draftReply(
    `Reply to a message about referencing/compliance documents: "${messageText}"`,
    `Contact type: ${contact.kind}. Keep it short and tell them we'll confirm what's outstanding shortly if unsure.`
  );

  await createAction({
    type: "referencing.document_chase",
    channel,
    contactId: contact.id,
    body,
    reasoning: triage.summary,
  });
}
