// Rent arrears aging. Note: this MVP has no live payment feed (Goodlord
// integration is a documented fast-follow — see README) so ArrearsCase rows
// are created manually via the dashboard when a payment is missed, and this
// daily check ages them forward and fires the right reminder/notice at each
// stage threshold. Once Goodlord is wired in, its payment webhook should
// create/resolve ArrearsCase rows instead of a person doing it by hand.

import { ArrearsStage, Channel, Contact } from "@prisma/client";
import { db } from "../db";
import { createAction } from "../actions";
import { draftReply, TriageResult } from "../ai";
import { createMondayItem, updateMondayItem } from "../monday";
import { env } from "../env";
import { ActionType } from "../rules";

const STAGE_THRESHOLDS: { days: number; stage: ArrearsStage; actionType: ActionType }[] = [
  { days: 3, stage: "REMINDER_1", actionType: "arrears.reminder_1" },
  { days: 7, stage: "REMINDER_2", actionType: "arrears.reminder_2" },
  { days: 14, stage: "FORMAL_NOTICE", actionType: "arrears.formal_notice" },
  { days: 21, stage: "ESCALATED", actionType: "arrears.landlord_escalation" },
];

function gbp(pence: number) {
  return `£${(pence / 100).toFixed(2)}`;
}

export async function runArrearsCheck() {
  const cases = await db.arrearsCase.findMany({
    where: { stage: { not: "RESOLVED" } },
    include: { tenancy: { include: { tenant: true, property: { include: { landlord: true } } } } },
  });

  for (const c of cases) {
    const daysOverdue = c.daysOverdue + 1; // one cron tick == one day
    const crossed = [...STAGE_THRESHOLDS].reverse().find((t) => daysOverdue >= t.days);

    if (crossed && crossed.stage !== c.stage) {
      const tenant = c.tenancy.tenant;
      const property = c.tenancy.property;
      const owed = gbp(c.amountOwedPence);

      let subject: string;
      let body: string;
      let recipientContactId: string | undefined;
      const channel: Channel = "EMAIL";

      switch (crossed.actionType) {
        case "arrears.reminder_1":
          subject = "Friendly reminder: rent payment";
          body = `Hi ${tenant.name},\n\nJust a quick note that we haven't yet received this month's rent of ${owed} for ${property.addressLine1}. If you've already paid, please disregard this — otherwise let us know if there's anything we can help with.\n\nCalibre Lettings`;
          recipientContactId = tenant.id;
          break;
        case "arrears.reminder_2":
          subject = "Second reminder: rent payment overdue";
          body = `Hi ${tenant.name},\n\nWe still haven't received ${owed} rent for ${property.addressLine1}, now ${daysOverdue} days overdue. Please arrange payment as soon as possible, or get in touch if you're having difficulty so we can help.\n\nCalibre Lettings`;
          recipientContactId = tenant.id;
          break;
        case "arrears.formal_notice":
          subject = `Formal notice: rent arrears on ${property.addressLine1}`;
          body = `Dear ${tenant.name},\n\nOur records show ${owed} rent remains unpaid, now ${daysOverdue} days overdue, despite previous reminders. Under the terms of your tenancy agreement, continued non-payment may result in further formal action. Please contact us immediately to arrange payment or discuss a plan.\n\nCalibre Lettings`;
          recipientContactId = tenant.id;
          break;
        case "arrears.landlord_escalation":
        default:
          subject = `Arrears escalation — ${property.addressLine1}`;
          body = `Hi ${property.landlord?.name ?? "there"},\n\n${tenant.name} at ${property.addressLine1} is now ${daysOverdue} days in arrears (${owed}) and hasn't responded to the formal notice. We recommend proceeding to the next formal step — let us know how you'd like to proceed.\n\nCalibre Lettings`;
          recipientContactId = property.landlordId ?? undefined;
          break;
      }

      await createAction({
        type: crossed.actionType,
        channel,
        contactId: recipientContactId,
        relatedType: "ArrearsCase",
        relatedId: c.id,
        subject,
        body,
        reasoning: `${daysOverdue} days overdue, entering stage ${crossed.stage}.`,
      });
    }

    const effectiveStage = crossed?.stage ?? c.stage;
    let mondayItemId = c.mondayItemId;
    const columnValues = { status: { label: effectiveStage.replace(/_/g, " ") }, days_overdue: daysOverdue };
    if (!mondayItemId) {
      mondayItemId = await createMondayItem(env.mondayBoards.arrears, `${c.tenancy.property.addressLine1} — ${c.tenancy.tenant.name}`, columnValues);
    } else {
      await updateMondayItem(env.mondayBoards.arrears, mondayItemId, columnValues);
    }

    await db.arrearsCase.update({
      where: { id: c.id },
      data: { daysOverdue, stage: effectiveStage, mondayItemId, ...(crossed && crossed.stage !== c.stage ? { lastActionAt: new Date() } : {}) },
    });
  }
}

/**
 * A tenant proactively messaging about rent (e.g. "I can't pay this month") —
 * reply supportively (auto, no legal language) and always flag it to staff,
 * since a hardship signal deserves a human's eyes regardless of the reply tier.
 */
export async function handleInboundArrearsMessage(contact: Contact, messageText: string, triage: TriageResult, channel: Channel) {
  const body = await draftReply(
    `Reply to a tenant's message about rent/payment: "${messageText}"`,
    "Be supportive and non-judgmental. Say a member of the team will follow up shortly to discuss options. Do not mention arrears stages, notices, or legal consequences."
  );

  await createAction({
    type: "arrears.tenant_reply",
    channel,
    contactId: contact.id,
    body,
    reasoning: triage.summary,
  });

  await createAction({
    type: "arrears.internal_flag",
    channel: "INTERNAL",
    contactId: contact.id,
    body: `${contact.name} messaged about rent/payment (via ${channel}): "${messageText}"`,
    reasoning: "Payment difficulty signals are flagged to staff regardless of tier.",
  });
}
