import { ServerClient } from "postmark";
import { env, mockMode } from "./env";

let client: ServerClient | null = null;
function getClient(): ServerClient | null {
  if (!env.postmarkToken) return null;
  if (!client) client = new ServerClient(env.postmarkToken);
  return client;
}

export interface SendEmailInput {
  to: string;
  subject: string;
  body: string;
}

export interface SendResult {
  ok: boolean;
  externalId?: string;
  error?: string;
}

export async function sendEmail(input: SendEmailInput): Promise<SendResult> {
  const postmark = mockMode ? null : getClient();
  if (!postmark) {
    console.log(`[mock email] to=${input.to} subject="${input.subject}"\n${input.body}\n`);
    return { ok: true, externalId: `mock-email-${Date.now()}` };
  }
  try {
    const res = await postmark.sendEmail({
      From: env.postmarkFromEmail,
      To: input.to,
      Subject: input.subject,
      TextBody: input.body,
      MessageStream: "outbound",
    });
    return { ok: true, externalId: res.MessageID };
  } catch (e) {
    return { ok: false, error: e instanceof Error ? e.message : String(e) };
  }
}

export interface InboundEmail {
  fromEmail: string;
  fromName?: string;
  subject: string;
  textBody: string;
  messageId: string;
}

/** Shape reference: https://postmarkapp.com/developer/webhooks/inbound-webhook */
export function parsePostmarkInbound(payload: Record<string, unknown>): InboundEmail {
  const fromFull = payload.FromFull as { Email?: string; Name?: string } | undefined;
  return {
    fromEmail: fromFull?.Email ?? String(payload.From ?? ""),
    fromName: fromFull?.Name,
    subject: String(payload.Subject ?? ""),
    textBody: String(payload.TextBody ?? payload.StrippedTextReply ?? ""),
    messageId: String(payload.MessageID ?? ""),
  };
}

/**
 * Postmark inbound webhooks can carry a shared secret as a query string param
 * (?token=...) since Postmark itself doesn't sign payloads. Configure the same
 * value as POSTMARK_INBOUND_WEBHOOK_SECRET and as the webhook URL's token.
 */
export function verifyInboundToken(providedToken: string | null): boolean {
  if (mockMode || !env.postmarkInboundSecret) return true;
  return providedToken === env.postmarkInboundSecret;
}
