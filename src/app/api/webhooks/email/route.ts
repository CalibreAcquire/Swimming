import { NextRequest, NextResponse } from "next/server";
import { parsePostmarkInbound, verifyInboundToken } from "@/lib/email";
import { handleInboundMessage } from "@/lib/inbound";

// Configure this URL (with ?token=<POSTMARK_INBOUND_WEBHOOK_SECRET>) as your
// Postmark inbound stream's webhook: https://postmarkapp.com/developer/webhooks/inbound-webhook
export async function POST(request: NextRequest) {
  const token = request.nextUrl.searchParams.get("token");
  if (!verifyInboundToken(token)) {
    return NextResponse.json({ error: "unauthorized" }, { status: 401 });
  }

  const payload = await request.json();
  const inbound = parsePostmarkInbound(payload);

  if (!inbound.fromEmail || !inbound.textBody) {
    return NextResponse.json({ error: "missing from/body" }, { status: 400 });
  }

  const result = await handleInboundMessage({
    channel: "EMAIL",
    fromEmail: inbound.fromEmail,
    fromName: inbound.fromName,
    subject: inbound.subject,
    body: inbound.textBody,
    externalId: inbound.messageId,
  });

  return NextResponse.json({ ok: true, workflow: result.triage.workflow });
}
