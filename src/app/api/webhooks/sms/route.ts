import { NextRequest, NextResponse } from "next/server";
import { parseTwilioInbound, verifyTwilioSignature } from "@/lib/sms";
import { handleInboundMessage } from "@/lib/inbound";
import { env } from "@/lib/env";

// Configure this URL as the "A message comes in" webhook for both your
// Twilio SMS number and your Twilio WhatsApp Sender.
export async function POST(request: NextRequest) {
  const rawBody = await request.text();
  const form = new URLSearchParams(rawBody);

  const signature = request.headers.get("x-twilio-signature");
  const fullUrl = `${env.appBaseUrl}/api/webhooks/sms`;
  const params = Object.fromEntries(form.entries());
  if (!verifyTwilioSignature(fullUrl, params, signature)) {
    return NextResponse.json({ error: "unauthorized" }, { status: 401 });
  }

  const inbound = parseTwilioInbound(form);
  if (!inbound.from || !inbound.body) {
    return NextResponse.json({ error: "missing from/body" }, { status: 400 });
  }

  await handleInboundMessage({
    channel: inbound.channel,
    fromPhone: inbound.from,
    body: inbound.body,
    externalId: inbound.messageSid,
  });

  // Twilio just needs a 200; empty TwiML means "don't send an auto-reply" (we handle replies via the Action queue).
  return new NextResponse('<?xml version="1.0" encoding="UTF-8"?><Response></Response>', {
    status: 200,
    headers: { "Content-Type": "text/xml" },
  });
}
