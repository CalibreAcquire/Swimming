// The Action queue: every AI-decided outbound message (email/SMS/WhatsApp/
// internal alert) flows through here. `ruleFor(type).autoSend` decides
// whether it goes out immediately or waits for a human in the Approvals
// screen. Monday.com item creation/updates are *not* routed through this
// queue — they're internal record-keeping side effects performed directly by
// the workflow handlers (lib/workflows/*), since they're reversible and not
// tenant/landlord/contractor-facing.

import { Channel, Workflow } from "@prisma/client";
import { db } from "./db";
import { ActionType, ruleFor } from "./rules";
import { sendEmail } from "./email";
import { sendText } from "./sms";
import { alertStaff } from "./alerts";

export interface CreateActionInput {
  type: ActionType;
  channel: Channel;
  contactId?: string;
  contactEmail?: string; // used when contactId isn't yet persisted (rare)
  contactPhone?: string;
  relatedType?: string;
  relatedId?: string;
  subject?: string;
  body: string;
  reasoning?: string;
}

/**
 * Creates an Action per the rulebook. Auto-send actions are dispatched
 * immediately (still recorded first, so there's always an audit trail even
 * if the send fails). Approval-required actions just land in the queue.
 */
export async function createAction(input: CreateActionInput) {
  const rule = ruleFor(input.type);

  const action = await db.action.create({
    data: {
      type: input.type,
      workflow: rule.workflow,
      autoSend: rule.autoSend,
      status: rule.autoSend ? "APPROVED" : "PENDING",
      channel: input.channel,
      contactId: input.contactId,
      relatedType: input.relatedType,
      relatedId: input.relatedId,
      subject: input.subject,
      body: input.body,
      reasoning: input.reasoning,
      decidedBy: rule.autoSend ? "auto" : null,
      decidedAt: rule.autoSend ? new Date() : null,
    },
  });

  if (rule.autoSend) {
    await dispatchAction(action.id);
  }

  return action;
}

export async function approveAction(id: string, decidedBy: string) {
  const action = await db.action.update({
    where: { id },
    data: { status: "APPROVED", decidedBy, decidedAt: new Date() },
  });
  await dispatchAction(action.id);
  return action;
}

export async function rejectAction(id: string, decidedBy: string) {
  return db.action.update({
    where: { id },
    data: { status: "REJECTED", decidedBy, decidedAt: new Date() },
  });
}

/** Sends an APPROVED action through the right channel adapter and records the outcome. */
export async function dispatchAction(id: string) {
  const action = await db.action.findUniqueOrThrow({ where: { id }, include: { contact: true } });
  if (action.status !== "APPROVED") return action;

  try {
    let externalId: string | undefined;

    if (action.channel === "INTERNAL") {
      await alertStaff(action.body);
    } else if (action.channel === "EMAIL") {
      const to = action.contact?.email;
      if (!to) throw new Error("No email address on file for this contact");
      const res = await sendEmail({ to, subject: action.subject ?? "Message from Calibre Lettings", body: action.body });
      if (!res.ok) throw new Error(res.error ?? "Email send failed");
      externalId = res.externalId;
    } else if (action.channel === "SMS" || action.channel === "WHATSAPP") {
      const to = action.contact?.phone;
      if (!to) throw new Error("No phone number on file for this contact");
      const res = await sendText(action.channel, to, action.body);
      if (!res.ok) throw new Error(res.error ?? "Text send failed");
      externalId = res.externalId;
    }

    // Log the outbound message in the conversation history.
    if (action.contactId && action.channel !== "INTERNAL") {
      await db.message.create({
        data: {
          contactId: action.contactId,
          channel: action.channel,
          direction: "OUTBOUND",
          workflow: action.workflow,
          subject: action.subject ?? undefined,
          body: action.body,
          externalId,
          relatedType: action.relatedType ?? undefined,
          relatedId: action.relatedId ?? undefined,
        },
      });
    }

    return db.action.update({ where: { id }, data: { status: "SENT", sentAt: new Date(), error: null } });
  } catch (e) {
    const error = e instanceof Error ? e.message : String(e);
    return db.action.update({ where: { id }, data: { status: "FAILED", error } });
  }
}

/** Resets a FAILED action back to APPROVED and retries the send (e.g. after fixing a missing phone number). */
export async function retryAction(id: string) {
  await db.action.update({ where: { id }, data: { status: "APPROVED", error: null } });
  return dispatchAction(id);
}

/** Cron safety net: retry anything stuck APPROVED (send failed transiently, or process crashed mid-send). */
export async function processApprovedActions() {
  const pending = await db.action.findMany({ where: { status: "APPROVED" }, select: { id: true } });
  const results = [];
  for (const { id } of pending) {
    results.push(await dispatchAction(id));
  }
  return results;
}

export type { Workflow };
