import { NextRequest, NextResponse } from "next/server";
import { createSessionToken } from "@/lib/session";
import { env } from "@/lib/env";

export async function POST(request: NextRequest) {
  const { name, password } = await request.json();

  if (!env.dashboardPassword) {
    return NextResponse.json({ error: "DASHBOARD_PASSWORD is not configured on the server — see README." }, { status: 500 });
  }
  if (typeof password !== "string" || password !== env.dashboardPassword) {
    return NextResponse.json({ error: "Incorrect password" }, { status: 401 });
  }
  if (typeof name !== "string" || !name.trim()) {
    return NextResponse.json({ error: "Enter your name" }, { status: 400 });
  }

  const token = await createSessionToken(name.trim());
  const res = NextResponse.json({ ok: true });
  res.cookies.set("session", token, {
    httpOnly: true,
    secure: process.env.NODE_ENV === "production",
    sameSite: "lax",
    maxAge: 60 * 60 * 24 * 30,
    path: "/",
  });
  return res;
}
