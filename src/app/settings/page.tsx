import { ACTION_RULES } from "@/lib/rules";
import { env, mockMode } from "@/lib/env";
import { Badge } from "@/components/Badge";

export const dynamic = "force-dynamic";

function IntegrationRow({ name, configured }: { name: string; configured: boolean }) {
  return (
    <div className="flex items-center justify-between px-4 py-3">
      <span className="text-sm">{name}</span>
      <Badge color={configured ? "green" : "slate"}>{configured ? "Configured" : "Not configured"}</Badge>
    </div>
  );
}

export default function SettingsPage() {
  const grouped = Object.entries(ACTION_RULES).reduce<Record<string, typeof ACTION_RULES>>((acc, [type, rule]) => {
    (acc[rule.workflow] ??= {} as typeof ACTION_RULES)[type as keyof typeof ACTION_RULES] = rule;
    return acc;
  }, {});

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-xl font-semibold">Settings</h1>
        <p className="text-sm text-slate-500 mt-1">
          {mockMode ? "Running in mock mode — no real messages send, nothing writes to Monday.com." : "Live mode — real integrations are active."}
        </p>
      </div>

      <div>
        <h2 className="text-sm font-semibold text-slate-700 dark:text-slate-300 mb-3">Integrations</h2>
        <div className="rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 divide-y divide-slate-100 dark:divide-slate-800">
          <IntegrationRow name="Anthropic (AI triage & drafting)" configured={!!env.anthropicApiKey} />
          <IntegrationRow name="Postmark (email)" configured={!!env.postmarkToken} />
          <IntegrationRow name="Twilio (SMS & WhatsApp)" configured={!!env.twilioAccountSid && !!env.twilioAuthToken} />
          <IntegrationRow name="Monday.com" configured={!!env.mondayApiToken} />
        </div>
      </div>

      <div>
        <h2 className="text-sm font-semibold text-slate-700 dark:text-slate-300 mb-1">Approval rules</h2>
        <p className="text-xs text-slate-500 mb-3">
          This is the full rulebook (see <code className="font-mono">src/lib/rules.ts</code>) — auto-send vs. hold-for-approval, per action type. Edit that file and redeploy to
          change a rule.
        </p>
        <div className="space-y-6">
          {Object.entries(grouped).map(([workflow, rules]) => (
            <div key={workflow}>
              <h3 className="text-xs font-semibold uppercase tracking-wide text-slate-400 mb-2">{workflow}</h3>
              <div className="rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 divide-y divide-slate-100 dark:divide-slate-800">
                {Object.entries(rules).map(([type, rule]) => (
                  <div key={type} className="p-4 flex items-start justify-between gap-4">
                    <div>
                      <p className="text-sm font-medium">{rule.label}</p>
                      <p className="text-xs text-slate-500 mt-0.5">{rule.rationale}</p>
                    </div>
                    <Badge color={rule.autoSend ? "green" : "amber"}>{rule.autoSend ? "Auto-send" : "Needs approval"}</Badge>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
