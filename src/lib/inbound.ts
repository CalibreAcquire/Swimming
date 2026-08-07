// Single entry point for every inbound message, regardless of channel.
// Webhook handlers (app/api/webhooks/*) normalize their provider's payload
// into an InboundPayload and hand it here: find-or-create the contact, log
// the message, triage it with AI, and route to the matching workflow.

import { Channel, Prisma } from "@prisma/client";
import { db } from "./db";
import { triageInboundMessage } from "./ai";
import { createAction } from "./actions";
import { handleInboundLeadMessage } from "./workflows/leads";
import { handleInboundMaintenanceMessage } from "./workflows/maintenance";
import { handleInboundArrearsMessage } from "./workflows/arrears";
import { handleInboundComplianceMessage } from "./workflows/compliance";

export interface InboundPayload {
  channel: Channel;
  fromEmail?: string;
  fromPhone?: string;
  fromName?: string;
  subject?: string;
  body: string;
  externalId?: string;
}

export async function handleInboundMessage(payload: InboundPayload) {
  const contact = await findOrCreateContact(payload);

  const message = await db.message.create({
    data: {
      contactId: contact.id,
      channel: payload.channel,
      direction: "INBOUND",
      subject: payload.subject,
      body: payload.body,
      externalId: payload.externalId,
      threadId: contact.id,
    },
  });

  const triage = await triageInboundMessage(payload.body);
  await db.message.update({ where: { id: message.id }, data: { workflow: triage.workflow } });

  switch (triage.workflow) {
    case "LEAD":
      await handleInboundLeadMessage(contact, payload.body, triage, payload.channel);
      break;
    case "MAINTENANCE":
      await handleInboundMaintenanceMessage(contact, payload.body, triage, payload.channel);
      break;
    case "ARREARS":
      await handleInboundArrearsMessage(contact, payload.body, triage, payload.channel);
      break;
    case "COMPLIANCE":
      await handleInboundComplianceMessage(contact, payload.body, triage, payload.channel);
      break;
    default:
      await createAction({
        type: "general.staff_flag",
        channel: "INTERNAL",
        contactId: contact.id,
        body: `Unclassified message from ${contact.name} (via ${payload.channel}): "${payload.body}"`,
        reasoning: triage.summary,
      });
  }

  return { contact, message, triage };
}

async function findOrCreateContact(payload: InboundPayload) {
  const or: Prisma.ContactWhereInput[] = [];
  if (payload.fromEmail) or.push({ email: payload.fromEmail });
  if (payload.fromPhone) or.push({ phone: payload.fromPhone });

  const existing = or.length ? await db.contact.findFirst({ where: { OR: or } }) : null;
  if (existing) return existing;

  return db.contact.create({
    data: {
      kind: "LEAD", // unknown senders default to LEAD; tenants/landlords/contractors are matched by email/phone once on file
      name: payload.fromName || payload.fromEmail || payload.fromPhone || "Unknown",
      email: payload.fromEmail,
      phone: payload.fromPhone,
    },
  });
}
