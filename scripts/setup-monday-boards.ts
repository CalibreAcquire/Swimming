// Idempotently provisions the four Monday.com boards this app writes to:
// Leads & Viewings, Maintenance, Arrears, Compliance. Safe to re-run — it
// looks up existing boards/columns by name before creating anything.
//
// Usage: set MONDAY_API_TOKEN in .env, then `npm run setup:monday`.
// It prints the MONDAY_BOARD_* env vars to add to your .env afterwards.

import "dotenv/config";
import { ProxyAgent, setGlobalDispatcher } from "undici";

// Node's built-in fetch doesn't honor HTTPS_PROXY/https_proxy on its own —
// unlike curl, npm, etc. Respect it explicitly so this script also works
// from behind a corporate/sandboxed proxy, not just on an open network.
const proxyUrl = process.env.HTTPS_PROXY || process.env.https_proxy;
if (proxyUrl) {
  setGlobalDispatcher(new ProxyAgent(proxyUrl));
}

const MONDAY_API_URL = "https://api.monday.com/v2";
const TOKEN = process.env.MONDAY_API_TOKEN;

if (!TOKEN) {
  console.error("MONDAY_API_TOKEN is not set. Add it to .env first (see README).");
  process.exit(1);
}

async function mondayRequest<T = unknown>(query: string, variables?: Record<string, unknown>): Promise<T> {
  const res = await fetch(MONDAY_API_URL, {
    method: "POST",
    headers: { "Content-Type": "application/json", Authorization: TOKEN as string, "API-Version": "2024-10" },
    body: JSON.stringify({ query, variables }),
  });
  const json = await res.json();
  if (json.errors) throw new Error(`Monday API error: ${JSON.stringify(json.errors)}`);
  return json.data as T;
}

interface ColumnDef {
  title: string;
  type: "status" | "text" | "date" | "numbers" | "email" | "phone";
  labels?: string[]; // for status columns
}

interface BoardDef {
  envVar: string;
  name: string;
  columns: ColumnDef[];
}

const BOARDS: BoardDef[] = [
  {
    envVar: "MONDAY_BOARD_LEADS",
    name: "Leads & Viewings",
    columns: [
      { title: "Status", type: "status", labels: ["New enquiry", "Follow-up", "Viewing booked", "Let", "Lost"] },
      { title: "Email", type: "email" },
      { title: "Phone", type: "phone" },
    ],
  },
  {
    envVar: "MONDAY_BOARD_MAINTENANCE",
    name: "Maintenance",
    columns: [
      { title: "Status", type: "status", labels: ["Emergency", "New", "Acknowledged", "Contractor Assigned", "In Progress", "Resolved"] },
      { title: "Category", type: "text" },
    ],
  },
  {
    envVar: "MONDAY_BOARD_ARREARS",
    name: "Arrears",
    columns: [
      { title: "Status", type: "status", labels: ["Reminder 1", "Reminder 2", "Formal Notice", "Escalated", "Resolved"] },
      { title: "Days overdue", type: "numbers" },
    ],
  },
  {
    envVar: "MONDAY_BOARD_COMPLIANCE",
    name: "Compliance",
    columns: [
      { title: "Status", type: "status", labels: ["Valid", "Due Soon", "Overdue", "Resolved"] },
      { title: "Due date", type: "date" },
    ],
  },
];

async function findBoardIdByName(name: string): Promise<string | null> {
  const data = await mondayRequest<{ boards: { id: string; name: string }[] }>(
    `query { boards (limit: 200) { id name } }`
  );
  return data.boards.find((b) => b.name === name)?.id ?? null;
}

async function createBoard(name: string): Promise<string> {
  const data = await mondayRequest<{ create_board: { id: string } }>(
    `mutation ($name: String!) { create_board (board_name: $name, board_kind: public) { id } }`,
    { name }
  );
  return data.create_board.id;
}

async function existingColumnTitles(boardId: string): Promise<Set<string>> {
  const data = await mondayRequest<{ boards: { columns: { title: string }[] }[] }>(
    `query ($boardId: [ID!]) { boards (ids: $boardId) { columns { title } } }`,
    { boardId: [boardId] }
  );
  return new Set(data.boards[0]?.columns.map((c) => c.title) ?? []);
}

async function createColumn(boardId: string, col: ColumnDef) {
  const defaults = col.type === "status" && col.labels ? JSON.stringify({ labels: col.labels }) : undefined;
  await mondayRequest(
    `mutation ($boardId: ID!, $title: String!, $type: ColumnType!, $defaults: JSON) {
      create_column (board_id: $boardId, title: $title, column_type: $type, defaults: $defaults) { id }
    }`,
    { boardId, title: col.title, type: col.type, defaults }
  );
}

async function main() {
  const results: Record<string, string> = {};

  for (const board of BOARDS) {
    let boardId = await findBoardIdByName(board.name);
    if (boardId) {
      console.log(`✓ Board "${board.name}" already exists (${boardId})`);
    } else {
      boardId = await createBoard(board.name);
      console.log(`+ Created board "${board.name}" (${boardId})`);
    }

    const existing = await existingColumnTitles(boardId);
    for (const col of board.columns) {
      if (existing.has(col.title)) continue;
      await createColumn(boardId, col);
      console.log(`  + Added column "${col.title}" (${col.type})`);
    }

    results[board.envVar] = boardId;
  }

  console.log("\nAdd these to your .env:\n");
  for (const [key, value] of Object.entries(results)) {
    console.log(`${key}=${value}`);
  }
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
