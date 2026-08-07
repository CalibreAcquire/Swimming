# Lettings AI System

A bespoke automation system for Calibre Lettings, covering four workflows:

- **Leads & viewings** — triages inbound enquiries, answers FAQs, proposes and confirms viewing slots.
- **Maintenance** — triages tenant reports, always alerts staff immediately on emergencies, drafts contractor instructions for approval.
- **Arrears** — ages open cases forward and fires reminders automatically; formal notices and landlord escalations wait for a human.
- **Compliance** — reminds ahead of certificate/deadline expiry; a confirmed breach always alerts staff and holds the tenant/landlord notice for approval.

It watches email and SMS/WhatsApp, uses Claude to triage and draft, and keeps Monday.com as the operational system of record. Every AI-decided outbound message runs through an **Action queue** — routine stuff auto-sends, anything touching money, legal standing, or a compliance breach waits in **Approvals** for a person. See `src/lib/rules.ts` for the exact rulebook, also viewable in the app under **Settings**.

## How it's built

- **Next.js 14 (App Router, TypeScript)** — one deployable app: dashboard UI + API routes (webhooks, cron) together.
- **Postgres via Prisma** — see `prisma/schema.prisma` for the full data model.
- **Anthropic Claude** — triages inbound messages and drafts informational replies. Arrears/compliance notices are built from fixed templates (`src/lib/workflows/*`), not freely generated — the AI decides *when* to fire a template, not the legal wording itself.
- **Postmark** — inbound/outbound email.
- **Twilio** — inbound/outbound SMS and WhatsApp.
- **Monday.com** — boards for Leads & Viewings, Maintenance, Arrears, Compliance.

Everything runs in **mock mode** by default (`MOCK_INTEGRATIONS=true`) — no third-party accounts required to explore the app. Messages "sent" in mock mode are logged to the server console instead of actually going anywhere.

## Quick start (mock mode, no accounts needed)

```bash
npm install
cp .env.example .env          # defaults are fine for local mock-mode use
# You'll still need a real Postgres DATABASE_URL even in mock mode —
# the fastest free option is https://neon.tech (a few clicks, no card needed).
npm run db:migrate            # creates the schema
npm run db:seed               # loads demo data (leads, an emergency ticket, arrears case, etc.)
npm run dev
```

Open http://localhost:3000, sign in with the name you like and the password from `.env` (`DASHBOARD_PASSWORD`, defaults to `changeme`), and click around:

- **Dashboard** — live counts and recent activity.
- **Approvals** — the seeded contractor instruction and formal arrears notice are sitting there waiting for you.
- **Leads / Maintenance / Arrears / Compliance** — the underlying records.
- **Settings** — the full approval rulebook and integration status.

## Going live: accounts to create

None of these are needed to explore the app in mock mode — only when you're ready for it to send real messages.

1. **Postgres** — [Neon](https://neon.tech) (recommended) or any Postgres host. Set `DATABASE_URL`.
2. **Anthropic** — [console.anthropic.com](https://console.anthropic.com) → create an API key. Set `ANTHROPIC_API_KEY`.
3. **Postmark** — [postmarkapp.com](https://postmarkapp.com) → create a server, verify a sending domain, grab the Server API Token. Set `POSTMARK_SERVER_TOKEN` and `POSTMARK_FROM_EMAIL`. Pick a random string for `POSTMARK_INBOUND_WEBHOOK_SECRET`.
4. **Twilio** — [twilio.com](https://www.twilio.com) → buy an SMS-capable number and set up a WhatsApp Sender (Twilio's WhatsApp onboarding takes a few days for approval — start this early). Set `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_SMS_NUMBER`, `TWILIO_WHATSAPP_NUMBER`.
5. **Monday.com** — you already have an account. Go to your avatar → **Admin** → **API** to generate a personal API token. Set `MONDAY_API_TOKEN`, then run:
   ```bash
   npm run setup:monday
   ```
   This creates the four boards (safe to re-run) and prints the `MONDAY_BOARD_*` values to add to `.env`.
6. **Vercel** (recommended host) — [vercel.com](https://vercel.com), import this repo, add every `.env` var as a Project Environment Variable. Vercel Cron picks up `vercel.json` automatically. The build command (`prisma migrate deploy && next build`) applies any pending database migrations automatically on every deploy — no manual migration step needed once `DATABASE_URL` is set as an env var.

Once real keys are in place, set `MOCK_INTEGRATIONS=false` and redeploy.

### Wire up the webhooks

- **Postmark inbound**: set the inbound stream's webhook URL to `https://<your-domain>/api/webhooks/email?token=<POSTMARK_INBOUND_WEBHOOK_SECRET>`.
- **Twilio**: set the "A message comes in" webhook (both the SMS number and the WhatsApp Sender) to `https://<your-domain>/api/webhooks/sms`.

### Cron

`vercel.json` schedules:
- `/api/cron/daily` once a day — ages arrears cases, checks compliance deadlines, nudges stale leads.
- `/api/cron/process-actions` once daily — safety-net retry for anything stuck mid-send. (Vercel's Hobby plan caps cron jobs at once/day; bump this to hourly in `vercel.json` if you're on Pro.)

Set `CRON_SECRET` to any random string; Vercel sends it automatically as a bearer token once the env var exists.

## What's intentionally out of scope for this first version

- **Goodlord integration** — you mentioned this is for when managed properties grow. The data model (`Tenancy`, `ArrearsCase`, etc.) is shaped so a payment webhook can create/resolve `ArrearsCase` rows directly, rather than the manual entry this MVP uses.
- **Multi-user accounts** — one shared dashboard password today, with a display name captured per session purely for approval attribution (`decidedBy`). Swap in NextAuth (or similar) once more than one or two people need access.
- **Address/property matching** — inbound lead messages are matched to a property by a naive substring check on the address. Fine for a handful of live listings; worth revisiting if the portfolio grows.

## Everyday commands

| Command | What it does |
|---|---|
| `npm run dev` | Local dev server |
| `npm run build` | Production build |
| `npm run db:migrate` | Apply schema changes (dev) |
| `npm run db:deploy` | Apply schema changes (prod, non-interactive) |
| `npm run db:seed` | Load demo data (wipes existing data first — don't run against a live DB with real data) |
| `npm run setup:monday` | Create/verify the four Monday.com boards |

## Tuning the approval rules

Edit `src/lib/rules.ts` — each action type has `autoSend: true/false` and a `rationale` string (shown in Settings). Nothing else needs to change; the Action queue and dashboard read from this file.
