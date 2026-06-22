import { ZerogClient } from "./zerogClient.js";

// Lists the 0G chatbot models reachable by the direct broker (confirms GLM availability
// + exact wire ids before going live). Requires ZEROG_PRIVATE_KEY (wallet-signed query).
if (!process.env.ZEROG_PRIVATE_KEY) {
  console.error("ZEROG_PRIVATE_KEY required for the probe.");
  process.exit(1);
}
const client = new ZerogClient({
  rpcUrl: process.env.ZEROG_RPC_URL || "https://evmrpc.0g.ai",
  privateKey: process.env.ZEROG_PRIVATE_KEY,
  defaultModel: process.env.ZEROG_MODEL || "zai-org/GLM-5-FP8",
});
const models = await client.listChatModels();
console.log("0G chatbot models available via the broker:");
for (const m of models) console.log("  -", m);
