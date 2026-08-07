import { NextRequest, NextResponse } from "next/server";
import { rejectAction } from "@/lib/actions";
import { getCurrentSession } from "@/lib/session";

export async function POST(_request: NextRequest, { params }: { params: Promise<{ id: string }> }) {
  const session = await getCurrentSession();
  if (!session) return NextResponse.json({ error: "unauthorized" }, { status: 401 });

  const { id } = await params;
  const action = await rejectAction(id, session.name);
  return NextResponse.json({ action });
}
