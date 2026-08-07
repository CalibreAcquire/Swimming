import { env } from "./env";

/**
 * Vercel Cron sends `Authorization: Bearer <CRON_SECRET>` automatically when
 * CRON_SECRET is set as an env var — see
 * https://vercel.com/docs/cron-jobs/manage-cron-jobs#securing-cron-jobs.
 * In mock/dev mode with no secret configured, allow the request through.
 */
export function isAuthorizedCronRequest(request: Request): boolean {
  if (!env.cronSecret) return true;
  const header = request.headers.get("authorization");
  return header === `Bearer ${env.cronSecret}`;
}
