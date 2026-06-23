import express from "express";
import { ZerogClient } from "./zerogClient.js";

// 0Gora 0G compute service — OpenAI-compatible front for 0G Compute. Runs GLM on
// 0G via the direct broker (TEE-verified), returns the answer + verification block.
// 0Gora's FastAPI backend calls this; this is the load-bearing 0G integration.

const PORT = process.env.PORT || 8090;
const app = express();
app.use(express.json({ limit: "25mb" }));

const client = new ZerogClient({
  rpcUrl: process.env.ZEROG_RPC_URL || "https://evmrpc.0g.ai",
  privateKey: process.env.ZEROG_PRIVATE_KEY,
  defaultModel: process.env.ZEROG_MODEL || "zai-org/GLM-5-FP8",
  mock: process.env.ZEROG_MOCK === "true",
  // ZEROG_MODELS=comma,separated → only advertise funded/working models in the picker.
  allowModels: (process.env.ZEROG_MODELS || "")
    .split(",")
    .map((s) => s.trim())
    .filter(Boolean),
});

app.get("/health", (_req, res) =>
  res.json({ status: "ok", configured: client.isConfigured() })
);

// Available 0G chatbot models (for the model picker).
app.get("/v1/models", async (_req, res) => {
  try {
    const ids = await client.listChatModels();
    res.json({ object: "list", data: ids.map((id) => ({ id, object: "model", owned_by: "0g" })) });
  } catch (e) {
    res.status(502).json({ error: { message: e?.message || "failed to list models" } });
  }
});

// OpenAI-compatible chat completion executed + verified on 0G.
app.post("/v1/chat/completions", async (req, res) => {
  if (!client.isConfigured()) {
    return res
      .status(503)
      .json({ error: { message: "0G compute not configured (set ZEROG_PRIVATE_KEY)" } });
  }
  try {
    // `verify` is a 0Gora control flag, not an upstream param — strip it before the
    // body reaches the 0G provider. verify=false skips the TEE attestation round-trip
    // (used by the backend's routing classifier, which isn't a user-facing answer).
    const { verify, ...body } = req.body || {};
    const { openai, verification } = await client.chatCompletion(body, { verify: verify !== false });
    res.setHeader("x-0g-verified", String(verification?.verified ?? false));
    res.json({ ...openai, x_0g_verification: verification });
  } catch (err) {
    console.error("[zerog] error:", err?.message);
    res.status(502).json({ error: { message: err?.message || "0G inference failed" } });
  }
});

app.listen(PORT, () => {
  console.log(`[0gora-zerog] listening on :${PORT} (configured=${client.isConfigured()})`);
  if (process.env.ZEROG_MOCK === "true") {
    console.warn(
      "\n  ⚠️  ZEROG_MOCK=true — answers are CANNED and NOT verified on 0G.\n" +
        "      This is local-dev mode only. Never run production with mock enabled.\n"
    );
  }
});
