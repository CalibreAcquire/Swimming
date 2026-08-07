import { NextRequest, NextResponse } from "next/server";
import { isAuthorizedCronRequest } from "@/lib/cronAuth";
import { runArrearsCheck } from "@/lib/workflows/arrears";
import { runComplianceCheck } from "@/lib/workflows/compliance";
import { runStaleLeadFollowup } from "@/lib/workflows/leads";

// Scheduled once daily (see vercel.json) — ages arrears cases forward,
// checks compliance deadlines, and nudges stale leads.
export async function GET(request: NextRequest) {
  if (!isAuthorizedCronRequest(request)) {
    return NextResponse.json({ error: "unauthorized" }, { status: 401 });
  }

  const results = await Promise.allSettled([runArrearsCheck(), runComplianceCheck(), runStaleLeadFollowup()]);

  const summary = {
    arrears: results[0].status,
    compliance: results[1].status,
    leadFollowup: results[2].status,
    errors: results.filter((r) => r.status === "rejected").map((r) => (r as PromiseRejectedResult).reason?.message ?? "unknown error"),
  };

  return NextResponse.json(summary);
}
