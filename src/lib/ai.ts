// AI layer. Deliberate design choice: the model is used for *triage and
// free-text drafting on informational surfaces* (what is this message about,
// how urgent, answer a lead's FAQ). Anything with legal or financial weight
// (arrears notices, compliance breach notices) is built from the fixed
// templates in lib/workflows/* — the AI decides *when* to trigger a template
// and fills in the variables, but never freehand-writes the legal wording.
// That split is what makes "auto-send the routine stuff" safe to do at all.

import Anthropic from "@anthropic-ai/sdk";
import { env, mockMode } from "./env";

let client: Anthropic | null = null;
function getClient(): Anthropic | null {
  if (!env.anthropicApiKey) return null;
  if (!client) client = new Anthropic({ apiKey: env.anthropicApiKey });
  return client;
}

export type TriageWorkflow = "LEAD" | "MAINTENANCE" | "ARREARS" | "COMPLIANCE" | "GENERAL";
export type TriageUrgency = "EMERGENCY" | "URGENT" | "ROUTINE" | "NONE";

export interface TriageResult {
  workflow: TriageWorkflow;
  urgency: TriageUrgency;
  category: string;
  summary: string;
}

const TRIAGE_SYSTEM_PROMPT = `You are the inbound-message triage assistant for a UK residential lettings company.
Classify each message into exactly one workflow:
- LEAD: a prospective tenant or landlord enquiring about a property, availability, price, or a viewing.
- MAINTENANCE: an existing tenant reporting a repair/issue in their property.
- ARREARS: anything about rent payment, being unable to pay, or a payment plan.
- COMPLIANCE: documents, certificates, right-to-rent, referencing paperwork.
- GENERAL: anything else.

For MAINTENANCE, set urgency:
- EMERGENCY: immediate danger or severe property damage risk (gas smell, fire, flooding/water ingress, total loss of heating in freezing weather, no power, lock/security failure, carbon monoxide alarm).
- URGENT: significant inconvenience but not dangerous (no hot water, broken appliance, leaking tap).
- ROUTINE: cosmetic or minor issues.
For all other workflows use urgency "NONE" unless something reads as time-critical, then "URGENT".

Reply with ONLY a JSON object: {"workflow": "...", "urgency": "...", "category": "short label", "summary": "one sentence"}. No prose, no markdown fences.`;

export async function triageInboundMessage(text: string): Promise<TriageResult> {
  const anthropic = mockMode ? null : getClient();
  if (!anthropic) return heuristicTriage(text);

  try {
    const msg = await anthropic.messages.create({
      model: env.aiModel,
      max_tokens: 300,
      system: TRIAGE_SYSTEM_PROMPT,
      messages: [{ role: "user", content: text }],
    });
    const block = msg.content.find((b) => b.type === "text");
    const raw = block && block.type === "text" ? block.text : "";
    const parsed = JSON.parse(extractJson(raw));
    return {
      workflow: parsed.workflow ?? "GENERAL",
      urgency: parsed.urgency ?? "NONE",
      category: parsed.category ?? "general",
      summary: parsed.summary ?? text.slice(0, 140),
    };
  } catch {
    // AI call failed or returned unparsable output — fall back rather than block the pipeline.
    return heuristicTriage(text);
  }
}

/** Keyword-based fallback used in mock mode and whenever the AI call fails. */
export function heuristicTriage(text: string): TriageResult {
  const t = text.toLowerCase();

  const emergencyWords = ["gas smell", "smell of gas", "flood", "flooding", "water coming through", "no heating", "no heat", "fire", "smoke", "carbon monoxide", "can't get in", "locked out", "break-in", "burst pipe"];
  const urgentMaintWords = ["no hot water", "leak", "leaking", "broken boiler", "not working", "appliance", "tap"];
  const maintWords = ["repair", "broken", "fix", "plumb", "electric", "heating", "boiler", "leak", "mould", "damp", "pest", "mice", "ceiling", "roof"];
  const arrearsWords = ["rent", "arrears", "can't pay", "cannot pay", "payment plan", "overdue", "behind on"];
  const complianceWords = ["gas certificate", "epc", "right to rent", "reference", "id document", "proof of income", "deposit protection", "eicr"];
  const leadWords = ["available", "viewing", "view the property", "enquir", "interested in", "deposit", "move in", "let"];

  if (emergencyWords.some((w) => t.includes(w))) {
    return { workflow: "MAINTENANCE", urgency: "EMERGENCY", category: "emergency", summary: text.slice(0, 140) };
  }
  if (arrearsWords.some((w) => t.includes(w))) {
    return { workflow: "ARREARS", urgency: "NONE", category: "rent", summary: text.slice(0, 140) };
  }
  if (complianceWords.some((w) => t.includes(w))) {
    return { workflow: "COMPLIANCE", urgency: "NONE", category: "documents", summary: text.slice(0, 140) };
  }
  if (maintWords.some((w) => t.includes(w))) {
    const urgency = urgentMaintWords.some((w) => t.includes(w)) ? "URGENT" : "ROUTINE";
    return { workflow: "MAINTENANCE", urgency, category: "repair", summary: text.slice(0, 140) };
  }
  if (leadWords.some((w) => t.includes(w))) {
    return { workflow: "LEAD", urgency: "NONE", category: "enquiry", summary: text.slice(0, 140) };
  }
  return { workflow: "GENERAL", urgency: "NONE", category: "general", summary: text.slice(0, 140) };
}

const DRAFT_SYSTEM_PROMPT = `You write short, warm, plain-English replies on behalf of a UK residential lettings company.
Keep it factual — only use information given in the context, never invent prices, dates, or policies.
No legal or financial threats, no commitments the context doesn't support. Sign off as "Calibre Lettings".
Reply with the message body only, no subject line, no markdown, no preamble.`;

/**
 * Free-text drafting for informational replies (lead FAQs, status updates).
 * Not used for arrears/compliance notices — those are templated in lib/workflows/*.
 */
export async function draftReply(purpose: string, context: string): Promise<string> {
  const anthropic = mockMode ? null : getClient();
  if (!anthropic) return heuristicDraft(purpose, context);

  try {
    const msg = await anthropic.messages.create({
      model: env.aiModel,
      max_tokens: 400,
      system: DRAFT_SYSTEM_PROMPT,
      messages: [{ role: "user", content: `Purpose: ${purpose}\n\nContext:\n${context}` }],
    });
    const block = msg.content.find((b) => b.type === "text");
    return block && block.type === "text" ? block.text.trim() : heuristicDraft(purpose, context);
  } catch {
    return heuristicDraft(purpose, context);
  }
}

function heuristicDraft(purpose: string, context: string): string {
  return `Hi,\n\n${purpose}\n\n${context}\n\nBest,\nCalibre Lettings`;
}

/** Strips markdown code fences etc. in case the model wraps its JSON despite instructions. */
function extractJson(raw: string): string {
  const match = raw.match(/\{[\s\S]*\}/);
  return match ? match[0] : raw;
}
