import { Channel, Contact, Property } from "@prisma/client";
import { db } from "../db";
import { createAction } from "../actions";
import { draftReply, TriageResult } from "../ai";
import { createMondayItem, updateMondayItem } from "../monday";
import { env } from "../env";

function matchProperty<P extends Pick<Property, "id" | "addressLine1">>(text: string, properties: P[]): P | null {
  const t = text.toLowerCase();
  return properties.find((p) => t.includes(p.addressLine1.toLowerCase().split(" ").slice(-2).join(" ").toLowerCase())) ?? null;
}

export async function handleInboundLeadMessage(contact: Contact, messageText: string, triage: TriageResult, channel: Channel) {
  const properties = await db.property.findMany({ where: { status: "AVAILABLE" } });
  const matched = matchProperty(messageText, properties);

  // Sync to the Leads & Viewings board.
  const itemName = `${contact.name} — ${matched ? matched.addressLine1 : "General enquiry"}`;
  let mondayItemId = contact.mondayItemId;
  if (!mondayItemId) {
    mondayItemId = await createMondayItem(env.mondayBoards.leads, itemName, { status: { label: "New enquiry" } });
    await db.contact.update({ where: { id: contact.id }, data: { mondayItemId } });
  } else {
    await updateMondayItem(env.mondayBoards.leads, mondayItemId, { status: { label: "Follow-up" } });
  }

  const wantsViewing = /\bview(ing)?\b|see the (flat|property|house|place)/i.test(messageText);

  if (wantsViewing) {
    const slots = matched
      ? await db.viewingSlot.findMany({ where: { propertyId: matched.id, status: "OPEN" }, orderBy: { startsAt: "asc" }, take: 3 })
      : [];
    const slotLines = slots
      .map((s) => `- ${s.startsAt.toLocaleString("en-GB", { weekday: "short", day: "numeric", month: "short", hour: "2-digit", minute: "2-digit" })}`)
      .join("\n");

    const context = matched
      ? `Property: ${matched.addressLine1}, ${matched.city} ${matched.postcode}. Rent: £${((matched.rentPcm ?? 0) / 100).toFixed(0)} pcm.\n${
          slots.length ? `Open viewing slots:\n${slotLines}` : "No open viewing slots on file yet — say we'll follow up shortly to arrange one."
        }`
      : "We couldn't identify the specific property from the message — ask which property they mean.";

    const body = await draftReply(`Reply to a lead asking to view a property. Original message: "${messageText}"`, context);

    await createAction({
      type: "lead.viewing_slot_proposal",
      channel,
      contactId: contact.id,
      relatedType: matched ? "Property" : undefined,
      relatedId: matched?.id,
      subject: matched ? `Viewing — ${matched.addressLine1}` : "Re: your enquiry",
      body,
      reasoning: `${triage.summary} — proposed ${slots.length} open slot(s).`,
    });
    return;
  }

  const context = matched
    ? `Property: ${matched.addressLine1}, ${matched.city} ${matched.postcode}. ${matched.bedrooms ?? "?"} bed. Rent: £${(
        (matched.rentPcm ?? 0) / 100
      ).toFixed(0)} pcm. Deposit is 5 weeks' rent. Status: ${matched.status}.`
    : "No specific property was identified from the message — answer generally and ask which property they're interested in.";

  const body = await draftReply(`Reply to a prospective tenant/landlord enquiry: "${messageText}"`, context);

  await createAction({
    type: "lead.faq_reply",
    channel,
    contactId: contact.id,
    relatedType: matched ? "Property" : undefined,
    relatedId: matched?.id,
    subject: matched ? `Re: ${matched.addressLine1}` : "Re: your enquiry",
    body,
    reasoning: triage.summary,
  });
}

/** Confirms a lead's chosen viewing slot — called from the slot-booking endpoint, not from inbound triage. */
export async function confirmViewingSlot(slotId: string, contactId: string) {
  const slot = await db.viewingSlot.update({
    where: { id: slotId },
    data: { status: "BOOKED", bookedById: contactId },
    include: { property: true },
  });
  const contact = await db.contact.findUniqueOrThrow({ where: { id: contactId } });

  await createAction({
    type: "lead.viewing_confirmed",
    channel: contact.email ? "EMAIL" : "SMS",
    contactId,
    relatedType: "ViewingSlot",
    relatedId: slot.id,
    subject: `Viewing confirmed — ${slot.property.addressLine1}`,
    body: `Hi ${contact.name},\n\nYour viewing at ${slot.property.addressLine1} is confirmed for ${slot.startsAt.toLocaleString("en-GB", {
      weekday: "long",
      day: "numeric",
      month: "long",
      hour: "2-digit",
      minute: "2-digit",
    })}. See you then!\n\nCalibre Lettings`,
    reasoning: "Slot booking confirmed directly by the lead.",
  });

  return slot;
}

/** Daily nudge for leads who went quiet after their first enquiry. */
export async function runStaleLeadFollowup() {
  const leads = await db.contact.findMany({ where: { kind: "LEAD" } });
  const cutoff = new Date(Date.now() - 3 * 86400000);

  for (const lead of leads) {
    const lastMessage = await db.message.findFirst({ where: { contactId: lead.id }, orderBy: { createdAt: "desc" } });
    if (!lastMessage || lastMessage.direction !== "INBOUND" || lastMessage.createdAt > cutoff) continue;

    const alreadyFollowedUp = await db.action.findFirst({
      where: { type: "lead.stale_followup", contactId: lead.id, createdAt: { gt: lastMessage.createdAt } },
    });
    if (alreadyFollowedUp) continue;

    const body = await draftReply(
      "Send a brief, friendly check-in to a lead who went quiet after enquiring — no pressure, just checking if they still need help.",
      `Lead name: ${lead.name}. Their last message: "${lastMessage.body}"`
    );

    await createAction({
      type: "lead.stale_followup",
      channel: lastMessage.channel,
      contactId: lead.id,
      body,
      reasoning: `No reply since ${lastMessage.createdAt.toDateString()}.`,
    });
  }
}
