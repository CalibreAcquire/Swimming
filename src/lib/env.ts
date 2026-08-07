// Central place that reads integration config. Every adapter checks `mockMode`
// and returns deterministic fake data instead of calling out — this lets the
// whole app run and be demoed with zero third-party accounts. Flip
// MOCK_INTEGRATIONS=false (and supply real keys) when you're ready to go live.

export const mockMode = process.env.MOCK_INTEGRATIONS !== "false";

export const env = {
  mockMode,
  anthropicApiKey: process.env.ANTHROPIC_API_KEY ?? "",
  aiModel: process.env.ANTHROPIC_MODEL ?? "claude-sonnet-5",

  postmarkToken: process.env.POSTMARK_SERVER_TOKEN ?? "",
  postmarkFromEmail: process.env.POSTMARK_FROM_EMAIL ?? "letting@example.com",
  postmarkInboundSecret: process.env.POSTMARK_INBOUND_WEBHOOK_SECRET ?? "",

  twilioAccountSid: process.env.TWILIO_ACCOUNT_SID ?? "",
  twilioAuthToken: process.env.TWILIO_AUTH_TOKEN ?? "",
  twilioSmsNumber: process.env.TWILIO_SMS_NUMBER ?? "",
  twilioWhatsappNumber: process.env.TWILIO_WHATSAPP_NUMBER ?? "",

  mondayApiToken: process.env.MONDAY_API_TOKEN ?? "",
  mondayBoards: {
    leads: process.env.MONDAY_BOARD_LEADS ?? "",
    maintenance: process.env.MONDAY_BOARD_MAINTENANCE ?? "",
    arrears: process.env.MONDAY_BOARD_ARREARS ?? "",
    compliance: process.env.MONDAY_BOARD_COMPLIANCE ?? "",
  },

  internalAlertEmail: process.env.INTERNAL_ALERT_EMAIL ?? "",
  internalAlertPhone: process.env.INTERNAL_ALERT_PHONE ?? "",

  dashboardPassword: process.env.DASHBOARD_PASSWORD ?? "",
  sessionSecret: process.env.SESSION_SECRET ?? "dev-only-insecure-secret-change-me",

  cronSecret: process.env.CRON_SECRET ?? "",
  appBaseUrl: process.env.APP_BASE_URL ?? "http://localhost:3000",
};
