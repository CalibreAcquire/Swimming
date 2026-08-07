// Internal staff alerts — used for maintenance emergencies and compliance
// breaches, which always notify a human immediately regardless of the
// action's approval tier. Sends by whichever of email/SMS is configured.
import { sendEmail } from "./email";
import { sendText } from "./sms";
import { env } from "./env";

export async function alertStaff(message: string): Promise<void> {
  const jobs: Promise<unknown>[] = [];
  if (env.internalAlertEmail) {
    jobs.push(sendEmail({ to: env.internalAlertEmail, subject: "⚠ Lettings AI alert", body: message }));
  }
  if (env.internalAlertPhone) {
    jobs.push(sendText("SMS", env.internalAlertPhone, `Lettings AI alert: ${message}`));
  }
  if (jobs.length === 0) {
    console.log(`[internal alert — no INTERNAL_ALERT_EMAIL/PHONE configured] ${message}`);
    return;
  }
  await Promise.allSettled(jobs);
}
