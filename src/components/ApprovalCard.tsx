"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Badge } from "./Badge";

export interface ApprovalActionView {
  id: string;
  type: string;
  workflow: string;
  channel: string;
  contactName: string | null;
  subject: string | null;
  body: string;
  reasoning: string | null;
  createdAt: string;
}

export function ApprovalCard({ action }: { action: ApprovalActionView }) {
  const router = useRouter();
  const [body, setBody] = useState(action.body);
  const [busy, setBusy] = useState<"approve" | "reject" | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function decide(kind: "approve" | "reject") {
    setBusy(kind);
    setError(null);
    const res = await fetch(`/api/actions/${action.id}/${kind}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: kind === "approve" ? JSON.stringify({ body }) : undefined,
    });
    setBusy(null);
    if (!res.ok) {
      const data = await res.json().catch(() => ({}));
      setError(data.error ?? "Something went wrong");
      return;
    }
    router.refresh();
  }

  return (
    <div className="rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-4 space-y-3">
      <div className="flex items-start justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 flex-wrap">
            <Badge color="amber">{action.workflow}</Badge>
            <Badge color="slate">{action.channel}</Badge>
            <span className="text-sm font-medium">{action.contactName ?? "Internal"}</span>
          </div>
          {action.subject && <p className="text-sm text-slate-500 mt-1">{action.subject}</p>}
        </div>
        <span className="text-xs text-slate-400 whitespace-nowrap">{new Date(action.createdAt).toLocaleString("en-GB")}</span>
      </div>

      {action.reasoning && <p className="text-xs text-slate-500 italic">Why: {action.reasoning}</p>}

      <textarea
        value={body}
        onChange={(e) => setBody(e.target.value)}
        rows={5}
        className="w-full rounded-lg border border-slate-300 dark:border-slate-700 bg-transparent px-3 py-2 text-sm font-mono focus:outline-none focus:ring-2 focus:ring-emerald-500"
      />

      {error && <p className="text-sm text-red-600">{error}</p>}

      <div className="flex items-center gap-2">
        <button
          onClick={() => decide("approve")}
          disabled={busy !== null}
          className="rounded-lg bg-emerald-600 hover:bg-emerald-700 disabled:opacity-60 text-white text-sm font-medium px-4 py-2 transition"
        >
          {busy === "approve" ? "Sending…" : "Approve & send"}
        </button>
        <button
          onClick={() => decide("reject")}
          disabled={busy !== null}
          className="rounded-lg border border-slate-300 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-800 disabled:opacity-60 text-sm font-medium px-4 py-2 transition"
        >
          {busy === "reject" ? "…" : "Reject"}
        </button>
      </div>
    </div>
  );
}
