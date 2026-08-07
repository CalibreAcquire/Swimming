import twilio from "twilio";
import { env, mockMode } from "./env";

let client: ReturnType<typeof twilio> | null = null;
function getClient(): ReturnType<typeof twilio> | null {
  if (!env.twilioAccountSid || !env.twilioAuthToken) return null;
  if (!client) client = twilio(env.twilioAccountSid, env.twilioAuthToken);
  return client;
}

export type SmsChannel = "SMS" | "WHATSAPP";

export interface SendResult {
  ok: boolean;
  externalId?: string;
  error?: string;
}

export async function sendText(channel: SmsChannel, to: string, body: string): Promise<SendResult> {
  const tw = mockMode ? null : getClient();
  if (!tw) {
    console.log(`[mock ${channel.toLowerCase()}] to=${to}\n${body}\n`);
    return { ok: true, externalId: `mock-${channel.toLowerCase()}-${Date.now()}` };
  }
  const from = channel === "WHATSAPP" ? `whatsapp:${env.twilioWhatsappNumber}` : env.twilioSmsNumber;
  const toAddr = channel === "WHATSAPP" ? `whatsapp:${to}` : to;
  try {
    const msg = await tw.messages.create({ from, to: toAddr, body });
    return { ok: true, externalId: msg.sid };
  } catch (e) {
    return { ok: false, error: e instanceof Error ? e.message : String(e) };
  }
}

export interface InboundText {
  from: string;
  channel: SmsChannel;
  body: string;
  messageSid: string;
}

/** Twilio posts inbound SMS/WhatsApp as application/x-www-form-urlencoded. */
export function parseTwilioInbound(form: URLSearchParams): InboundText {
  const rawFrom = form.get("From") ?? "";
  const channel: SmsChannel = rawFrom.startsWith("whatsapp:") ? "WHATSAPP" : "SMS";
  return {
    from: rawFrom.replace("whatsapp:", ""),
    channel,
    body: form.get("Body") ?? "",
    messageSid: form.get("MessageSid") ?? "",
  };
}

export function verifyTwilioSignature(fullUrl: string, params: Record<string, string>, signature: string | null): boolean {
  if (mockMode || !env.twilioAuthToken) return true;
  if (!signature) return false;
  return twilio.validateRequest(env.twilioAuthToken, signature, fullUrl, params);
}
