// Tests for the model allowlist + mock behavior (no chain / no funds).
// Run:  node --test
import { test } from "node:test";
import assert from "node:assert/strict";
import { ZerogClient } from "../src/zerogClient.js";

test("mock mode lists mock models", async () => {
  const c = new ZerogClient({ mock: true });
  const models = await c.listChatModels();
  assert.ok(Array.isArray(models) && models.length > 0);
});

test("allowlist filters to served models, preserving order", async () => {
  const c = new ZerogClient({ mock: true });
  const all = await c.listChatModels();
  const pick = [all[all.length - 1], all[0]]; // reversed subset
  const filtered = new ZerogClient({ mock: true, allowModels: pick });
  const got = await filtered.listChatModels();
  assert.deepEqual(got, pick);
});

test("allowlist ignores ids 0G does not serve", async () => {
  const c = new ZerogClient({ mock: true, allowModels: ["totally-fake-model"] });
  const got = await c.listChatModels();
  // none of the allowlist is served → fall back to the full list (never empty picker)
  assert.ok(got.length > 0);
});

test("empty allowlist means no filtering", async () => {
  const a = await new ZerogClient({ mock: true }).listChatModels();
  const b = await new ZerogClient({ mock: true, allowModels: [] }).listChatModels();
  assert.deepEqual(a, b);
});

test("mock chatCompletion returns a verification block", async () => {
  const c = new ZerogClient({ mock: true });
  const { openai, verification } = await c.chatCompletion({
    messages: [{ role: "user", content: "hi" }],
  });
  assert.ok(openai.choices[0].message.content);
  assert.equal(verification.verified, true);
});
