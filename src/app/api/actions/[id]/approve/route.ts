import { NextRequest, NextResponse } from "next/server";
import { approveAction } from "@/lib/actions";
import { getCurrentSession } from "@/lib/session";

export async function POST(request: NextRequest, { params }: { params: Promise<{ id: string }> }) {
  const session = await getCurrentSession();
  if (!session) return NextResponse.json({ error: "unauthorized" }, { status: 401 });

  const { id } = await params;
  const body = await request.json().catch(() => ({}));
  const editedBody: string | undefined = typeof body.body === "string" ? body.body : undefined;

  // Allow editing the draft at the moment of approval (the whole point of a review step).
  if (editedBody !== undefined) {
    const { db } = await import("@/lib/db");
    await db.action.update({ where: { id }, data: { body: editedBody } });
  }

  const action = await approveAction(id, session.name);
  return NextResponse.json({ action });
}
