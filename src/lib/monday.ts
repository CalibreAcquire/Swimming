import { env, mockMode } from "./env";

const MONDAY_API_URL = "https://api.monday.com/v2";

export async function mondayRequest<T = unknown>(query: string, variables?: Record<string, unknown>): Promise<T> {
  if (!env.mondayApiToken) throw new Error("MONDAY_API_TOKEN is not set");
  const res = await fetch(MONDAY_API_URL, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: env.mondayApiToken,
      "API-Version": "2024-10",
    },
    body: JSON.stringify({ query, variables }),
  });
  const json = await res.json();
  if (json.errors) throw new Error(`Monday API error: ${JSON.stringify(json.errors)}`);
  return json.data as T;
}

export async function createMondayItem(
  boardId: string,
  itemName: string,
  columnValues: Record<string, unknown> = {}
): Promise<string> {
  if (mockMode || !env.mondayApiToken || !boardId) {
    const id = `mock-item-${Date.now()}`;
    console.log(`[mock monday] create item on board ${boardId || "(unset)"}: "${itemName}"`, columnValues);
    return id;
  }
  const data = await mondayRequest<{ create_item: { id: string } }>(
    `mutation ($boardId: ID!, $itemName: String!, $columnValues: JSON) {
      create_item(board_id: $boardId, item_name: $itemName, column_values: $columnValues) { id }
    }`,
    { boardId, itemName, columnValues: JSON.stringify(columnValues) }
  );
  return data.create_item.id;
}

export async function updateMondayItem(
  boardId: string,
  itemId: string,
  columnValues: Record<string, unknown>
): Promise<void> {
  if (mockMode || !env.mondayApiToken || !boardId) {
    console.log(`[mock monday] update item ${itemId} on board ${boardId || "(unset)"}`, columnValues);
    return;
  }
  await mondayRequest(
    `mutation ($boardId: ID!, $itemId: ID!, $columnValues: JSON!) {
      change_multiple_column_values(board_id: $boardId, item_id: $itemId, column_values: $columnValues) { id }
    }`,
    { boardId, itemId, columnValues: JSON.stringify(columnValues) }
  );
}
