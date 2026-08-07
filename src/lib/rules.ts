// The risk-tier rulebook. Every Action the AI decides to take is tagged with
// a `type` from this table, which decides whether it auto-sends or waits in
// the Approvals queue for a human. Tune this file as trust in the system
// grows — nothing else needs to change to loosen or tighten a rule.
//
// Default posture (per Jake): auto-send routine stuff, hold anything that
// touches money, legal standing, or a confirmed compliance breach.

import { Workflow } from "@prisma/client";

export type ActionType =
  // Leads & viewings
  | "lead.faq_reply"
  | "lead.viewing_slot_proposal"
  | "lead.viewing_confirmed"
  | "lead.stale_followup"
  // Maintenance
  | "maintenance.acknowledgement"
  | "maintenance.emergency_internal_alert"
  | "maintenance.contractor_instruction"
  | "maintenance.tenant_status_update"
  // Arrears
  | "arrears.reminder_1"
  | "arrears.reminder_2"
  | "arrears.formal_notice"
  | "arrears.landlord_escalation"
  | "arrears.tenant_reply"
  | "arrears.internal_flag"
  // Compliance
  | "compliance.reminder"
  | "compliance.breach_internal_alert"
  | "compliance.breach_tenant_notice"
  | "referencing.document_chase"
  // Fallback
  | "general.staff_flag";

export interface ActionRule {
  workflow: Workflow;
  autoSend: boolean;
  label: string;
  /** Why this tier was chosen — shown in Settings so the reasoning is never hidden. */
  rationale: string;
}

export const ACTION_RULES: Record<ActionType, ActionRule> = {
  "lead.faq_reply": {
    workflow: "LEAD",
    autoSend: true,
    label: "Answer lead FAQ",
    rationale: "Informational only (rent, availability, deposit terms) — low risk.",
  },
  "lead.viewing_slot_proposal": {
    workflow: "LEAD",
    autoSend: true,
    label: "Propose viewing slots",
    rationale: "No commitment made until the lead confirms a slot.",
  },
  "lead.viewing_confirmed": {
    workflow: "LEAD",
    autoSend: true,
    label: "Confirm booked viewing",
    rationale: "Simple scheduling confirmation, reversible.",
  },
  "lead.stale_followup": {
    workflow: "LEAD",
    autoSend: true,
    label: "Follow up a quiet lead",
    rationale: "Low-stakes nudge.",
  },
  "maintenance.acknowledgement": {
    workflow: "MAINTENANCE",
    autoSend: true,
    label: "Acknowledge maintenance report",
    rationale: "Tenants should always get an immediate, non-committal acknowledgement.",
  },
  "maintenance.emergency_internal_alert": {
    workflow: "MAINTENANCE",
    autoSend: true,
    label: "Alert staff of an emergency",
    rationale: "Always fires immediately regardless of tier — a human must know about emergencies fast.",
  },
  "maintenance.contractor_instruction": {
    workflow: "MAINTENANCE",
    autoSend: false,
    label: "Instruct a contractor",
    rationale: "Commits cost and a third party on your behalf — needs a human okay.",
  },
  "maintenance.tenant_status_update": {
    workflow: "MAINTENANCE",
    autoSend: true,
    label: "Update tenant on ticket status",
    rationale: "Informational status update, no commitment.",
  },
  "arrears.reminder_1": {
    workflow: "ARREARS",
    autoSend: true,
    label: "Friendly rent reminder",
    rationale: "Routine, non-threatening nudge.",
  },
  "arrears.reminder_2": {
    workflow: "ARREARS",
    autoSend: true,
    label: "Firmer rent reminder",
    rationale: "Still informational, no legal language yet.",
  },
  "arrears.formal_notice": {
    workflow: "ARREARS",
    autoSend: false,
    label: "Formal arrears notice",
    rationale: "References lease terms / possible legal next steps — must be reviewed before it goes out.",
  },
  "arrears.landlord_escalation": {
    workflow: "ARREARS",
    autoSend: false,
    label: "Escalate arrears to landlord",
    rationale: "Recommends formal process to the landlord — a judgement call, not an autonomous one.",
  },
  "arrears.tenant_reply": {
    workflow: "ARREARS",
    autoSend: true,
    label: "Reply to a tenant's payment message",
    rationale: "Acknowledging/reassuring reply, no legal or financial commitment made.",
  },
  "arrears.internal_flag": {
    workflow: "ARREARS",
    autoSend: true,
    label: "Flag a payment difficulty to staff",
    rationale: "Tenant hardship signals should reach a human quickly, even though the reply itself is routine.",
  },
  "compliance.reminder": {
    workflow: "COMPLIANCE",
    autoSend: true,
    label: "Compliance deadline reminder",
    rationale: "Informational reminder ahead of a deadline (T-30/T-14/T-1).",
  },
  "compliance.breach_internal_alert": {
    workflow: "COMPLIANCE",
    autoSend: true,
    label: "Alert staff of a compliance breach",
    rationale: "Always fires immediately — a lapsed gas safety cert etc. is a legal risk that needs eyes now.",
  },
  "compliance.breach_tenant_notice": {
    workflow: "COMPLIANCE",
    autoSend: false,
    label: "Tell tenant/landlord about a breach",
    rationale: "Carries legal weight (e.g. a lapsed safety certificate) — must be reviewed before sending.",
  },
  "referencing.document_chase": {
    workflow: "COMPLIANCE",
    autoSend: true,
    label: "Chase a missing document",
    rationale: "Routine reminder to supply ID/references/right-to-rent evidence.",
  },
  "general.staff_flag": {
    workflow: "GENERAL",
    autoSend: true,
    label: "Route an unclassified message to staff",
    rationale: "Doesn't fit a known workflow — a human should read it rather than the AI guessing.",
  },
};

export function ruleFor(type: ActionType): ActionRule {
  return ACTION_RULES[type];
}
