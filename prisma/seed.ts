// Seeds enough data to click through every screen and workflow in mock mode.
// Run with: npm run db:seed
import { PrismaClient } from "@prisma/client";

const db = new PrismaClient();

async function main() {
  await db.action.deleteMany();
  await db.message.deleteMany();
  await db.complianceItem.deleteMany();
  await db.arrearsCase.deleteMany();
  await db.maintenanceTicket.deleteMany();
  await db.viewingSlot.deleteMany();
  await db.tenancy.deleteMany();
  await db.property.deleteMany();
  await db.contact.deleteMany();
  await db.staffUser.deleteMany();

  await db.staffUser.create({
    data: { name: "Jake", email: "jake@calibreacquire.co.uk" },
  });

  const landlord = await db.contact.create({
    data: { kind: "LANDLORD", name: "Priya Shah", email: "priya.shah@example.com", phone: "+447700900001" },
  });

  const propertyA = await db.property.create({
    data: {
      addressLine1: "12 Elm Court",
      city: "Bristol",
      postcode: "BS1 4ST",
      bedrooms: 2,
      rentPcm: 125000,
      status: "AVAILABLE",
      landlordId: landlord.id,
    },
  });

  const propertyB = await db.property.create({
    data: {
      addressLine1: "4 Oak Terrace",
      city: "Bristol",
      postcode: "BS6 7QF",
      bedrooms: 3,
      rentPcm: 165000,
      status: "LET",
      landlordId: landlord.id,
    },
  });

  const lead = await db.contact.create({
    data: { kind: "LEAD", name: "Tom Fielding", email: "tom.fielding@example.com", phone: "+447700900002" },
  });

  const tenant = await db.contact.create({
    data: { kind: "TENANT", name: "Amara Okafor", email: "amara.okafor@example.com", phone: "+447700900003" },
  });

  const contractor = await db.contact.create({
    data: { kind: "CONTRACTOR", name: "FastFix Plumbing", email: "jobs@fastfixplumbing.example.com", phone: "+447700900004" },
  });

  const tenancy = await db.tenancy.create({
    data: {
      propertyId: propertyB.id,
      tenantId: tenant.id,
      startDate: new Date("2025-03-01"),
      rentDueDay: 1,
      rentPcm: 165000,
      depositProtected: true,
    },
  });

  await db.viewingSlot.createMany({
    data: [
      { propertyId: propertyA.id, startsAt: new Date(Date.now() + 86400000), endsAt: new Date(Date.now() + 86400000 + 1800000), status: "OPEN" },
      { propertyId: propertyA.id, startsAt: new Date(Date.now() + 172800000), endsAt: new Date(Date.now() + 172800000 + 1800000), status: "OPEN" },
    ],
  });

  const inboundLeadMsg = await db.message.create({
    data: {
      contactId: lead.id,
      channel: "EMAIL",
      direction: "INBOUND",
      workflow: "LEAD",
      subject: "Enquiry about 12 Elm Court",
      body: "Hi, is 12 Elm Court still available? What's the deposit and can I view this week?",
      threadId: `lead-${lead.id}`,
    },
  });

  await db.action.create({
    data: {
      type: "lead.faq_reply",
      workflow: "LEAD",
      autoSend: true,
      status: "SENT",
      channel: "EMAIL",
      contactId: lead.id,
      relatedType: "Message",
      relatedId: inboundLeadMsg.id,
      subject: "Re: Enquiry about 12 Elm Court",
      body:
        "Hi Tom,\n\nThanks for your interest — 12 Elm Court is still available. It's £1,250 pcm with a deposit of £1,442 (5 weeks). I've got two viewing slots open this week — I'll follow up shortly with times that work.\n\nBest,\nCalibre Lettings",
      reasoning: "Answered availability/deposit FAQ directly from the property record.",
      sentAt: new Date(),
      decidedBy: "auto",
    },
  });

  await db.message.create({
    data: {
      contactId: tenant.id,
      channel: "WHATSAPP",
      direction: "INBOUND",
      workflow: "MAINTENANCE",
      body: "Hi, there's water coming through the kitchen ceiling, it's getting worse.",
      threadId: `maint-${tenant.id}-1`,
    },
  });

  const emergencyTicket = await db.maintenanceTicket.create({
    data: {
      propertyId: propertyB.id,
      tenantId: tenant.id,
      category: "plumbing",
      urgency: "EMERGENCY",
      description: "Water coming through kitchen ceiling, worsening.",
      status: "ACKNOWLEDGED",
    },
  });

  await db.action.createMany({
    data: [
      {
        type: "maintenance.acknowledgement",
        workflow: "MAINTENANCE",
        autoSend: true,
        status: "SENT",
        channel: "WHATSAPP",
        contactId: tenant.id,
        relatedType: "MaintenanceTicket",
        relatedId: emergencyTicket.id,
        body: "Got this — that sounds urgent, we're on it right away. Please turn off the water at the stopcock if it's safe to do so. We're calling an emergency plumber now.",
        reasoning: "Classified as EMERGENCY (active water ingress) — immediate acknowledgement required.",
        sentAt: new Date(),
        decidedBy: "auto",
      },
      {
        type: "maintenance.emergency_internal_alert",
        workflow: "MAINTENANCE",
        autoSend: true,
        status: "SENT",
        channel: "INTERNAL",
        relatedType: "MaintenanceTicket",
        relatedId: emergencyTicket.id,
        body: "EMERGENCY: Water ingress at 4 Oak Terrace (tenant: Amara Okafor). Reported via WhatsApp.",
        reasoning: "Emergency alerts always fire regardless of approval tier.",
        sentAt: new Date(),
        decidedBy: "auto",
      },
      {
        type: "maintenance.contractor_instruction",
        workflow: "MAINTENANCE",
        autoSend: false,
        status: "PENDING",
        channel: "EMAIL",
        contactId: contractor.id,
        relatedType: "MaintenanceTicket",
        relatedId: emergencyTicket.id,
        subject: "Emergency callout — 4 Oak Terrace",
        body: "Hi FastFix, we need an emergency callout at 4 Oak Terrace — active water ingress through the kitchen ceiling, likely a leak from the bathroom above. Tenant Amara Okafor is on site. Please confirm ETA.",
        reasoning: "Commits an emergency callout cost — held for approval per rules.",
        decidedBy: null,
      },
    ],
  });

  const arrearsCase = await db.arrearsCase.create({
    data: {
      tenancyId: tenancy.id,
      amountOwedPence: 165000,
      daysOverdue: 12,
      stage: "REMINDER_2",
    },
  });

  await db.action.create({
    data: {
      type: "arrears.formal_notice",
      workflow: "ARREARS",
      autoSend: false,
      status: "PENDING",
      channel: "EMAIL",
      contactId: tenant.id,
      relatedType: "ArrearsCase",
      relatedId: arrearsCase.id,
      subject: "Formal notice: rent arrears on 4 Oak Terrace",
      body:
        "Dear Amara,\n\nOur records show £1,650.00 rent remains unpaid, now 12 days overdue, despite two earlier reminders. Under the terms of your tenancy agreement, continued non-payment may result in further formal action. Please contact us immediately to arrange payment or discuss a plan.\n\nCalibre Lettings",
      reasoning: "12 days overdue with two prior reminders unanswered — escalated to formal notice, references tenancy terms so it needs sign-off.",
      decidedBy: null,
    },
  });

  const gasSafety = await db.complianceItem.create({
    data: {
      propertyId: propertyB.id,
      type: "GAS_SAFETY",
      dueDate: new Date(Date.now() + 12 * 86400000),
      status: "DUE_SOON",
    },
  });

  await db.action.create({
    data: {
      type: "compliance.reminder",
      workflow: "COMPLIANCE",
      autoSend: true,
      status: "SENT",
      channel: "EMAIL",
      contactId: landlord.id,
      relatedType: "ComplianceItem",
      relatedId: gasSafety.id,
      subject: "Gas safety certificate due soon — 4 Oak Terrace",
      body: "Hi Priya, the gas safety certificate for 4 Oak Terrace is due in 12 days. Let us know if you'd like us to book the engineer.",
      reasoning: "T-14 reminder window.",
      sentAt: new Date(),
      decidedBy: "auto",
    },
  });

  console.log("Seed complete.");
}

main()
  .catch((e) => {
    console.error(e);
    process.exit(1);
  })
  .finally(async () => {
    await db.$disconnect();
  });
