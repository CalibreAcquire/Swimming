import { NextRequest, NextResponse } from "next/server";
import { isAuthorizedCronRequest } from "@/lib/cronAuth";
import { processApprovedActions } from "@/lib/actions";

// Safety-net cron (see vercel.json) — auto-send and just-approved actions are
// dispatched inline already; this retries anything stuck in APPROVED
// (e.g. the process crashed mid-send, or a transient provider error).
export async function GET(request: NextRequest) {
  if (!isAuthorizedCronRequest(request)) {
    return NextResponse.json({ error: "unauthorized" }, { status: 401 });
  }

  const results = await processApprovedActions();
  return NextResponse.json({ processed: results.length });
}
