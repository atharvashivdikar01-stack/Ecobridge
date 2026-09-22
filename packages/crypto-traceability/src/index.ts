import { createHash } from "node:crypto";

export type CustodyPayload = Record<string, unknown>;

export function hashCustodyEvent(
  payload: CustodyPayload,
  previousHash = "0".repeat(64),
): string {
  return createHash("sha256")
    .update(`${previousHash}:${JSON.stringify(payload)}`)
    .digest("hex");
}
