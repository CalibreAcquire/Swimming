// Minimal signed-cookie session — a single shared dashboard password plus a
// display name (used purely for "decidedBy" attribution on approvals). No
// per-user accounts yet; see README for the recommended next step
// (NextAuth or similar) once the team grows beyond one or two people.
import { env } from "./env";

const encoder = new TextEncoder();

async function getKey() {
  return crypto.subtle.importKey("raw", encoder.encode(env.sessionSecret), { name: "HMAC", hash: "SHA-256" }, false, ["sign", "verify"]);
}

function toBase64Url(bytes: ArrayBuffer | Uint8Array): string {
  const arr = bytes instanceof Uint8Array ? bytes : new Uint8Array(bytes);
  let str = "";
  for (const b of arr) str += String.fromCharCode(b);
  return btoa(str).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}

function fromBase64Url(str: string): Uint8Array<ArrayBuffer> {
  const b64 = str.replace(/-/g, "+").replace(/_/g, "/") + "===".slice((str.length + 3) % 4);
  const bin = atob(b64);
  const bytes = new Uint8Array(new ArrayBuffer(bin.length));
  for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
  return bytes;
}

export interface SessionPayload {
  name: string;
  exp: number;
}

export async function createSessionToken(name: string, ttlSeconds = 60 * 60 * 24 * 30): Promise<string> {
  const payload: SessionPayload = { name, exp: Date.now() + ttlSeconds * 1000 };
  const payloadB64 = toBase64Url(encoder.encode(JSON.stringify(payload)));
  const sig = await crypto.subtle.sign("HMAC", await getKey(), encoder.encode(payloadB64));
  return `${payloadB64}.${toBase64Url(sig)}`;
}

export async function verifySessionToken(token: string | undefined | null): Promise<SessionPayload | null> {
  if (!token) return null;
  const [payloadB64, sigB64] = token.split(".");
  if (!payloadB64 || !sigB64) return null;

  try {
    const valid = await crypto.subtle.verify("HMAC", await getKey(), fromBase64Url(sigB64), encoder.encode(payloadB64));
    if (!valid) return null;
    const payload: SessionPayload = JSON.parse(new TextDecoder().decode(fromBase64Url(payloadB64)));
    if (payload.exp < Date.now()) return null;
    return payload;
  } catch {
    return null;
  }
}

/** Server Component / Route Handler helper — reads the session from the request cookie jar. */
export async function getCurrentSession(): Promise<SessionPayload | null> {
  const { cookies } = await import("next/headers");
  const store = await cookies();
  return verifySessionToken(store.get("session")?.value);
}
