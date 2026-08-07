import { PrismaClient } from "@prisma/client";
import { Pool, neonConfig } from "@neondatabase/serverless";
import { PrismaNeon } from "@prisma/adapter-neon";

// Neon's HTTP driver, not a raw TCP connection — this is Neon's own
// recommended setup for serverless hosts (Vercel functions included), since
// it avoids the connection-pool-exhaustion problems raw TCP has under
// serverless concurrency, and works through networks that only allow
// standard HTTPS egress.
neonConfig.poolQueryViaFetch = true;

const globalForPrisma = globalThis as unknown as { prisma?: PrismaClient };

function createClient() {
  const pool = new Pool({ connectionString: process.env.DATABASE_URL });
  const adapter = new PrismaNeon(pool);
  return new PrismaClient({
    adapter,
    log: process.env.NODE_ENV === "development" ? ["error", "warn"] : ["error"],
  });
}

export const db = globalForPrisma.prisma ?? createClient();

if (process.env.NODE_ENV !== "production") globalForPrisma.prisma = db;
