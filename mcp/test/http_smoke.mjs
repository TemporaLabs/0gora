// Smoke test for the Streamable HTTP transport. Point MCP_URL at the endpoint
// (default local). Run:  MCP_URL=http://localhost:8091/mcp node test/http_smoke.mjs
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StreamableHTTPClientTransport } from "@modelcontextprotocol/sdk/client/streamableHttp.js";

const url = new URL(process.env.MCP_URL || "http://localhost:8091/mcp");
const transport = new StreamableHTTPClientTransport(url);
const client = new Client({ name: "0gora-http-smoke", version: "0.0.0" });
await client.connect(transport);

let fail = 0;
const tools = (await client.listTools()).tools.map((t) => t.name).sort();
console.log("tools:", tools.join(", "));
if (!tools.includes("ask_0gora") || !tools.includes("list_models") || !tools.includes("search_0g_knowledge")) {
  console.log("FAIL: missing tools"); fail++;
}

const m = await client.callTool({ name: "list_models", arguments: {} });
console.log("list_models ->", m.content[0].text.replace(/\n/g, ", "));
if (!m.content[0].text.includes("0GM")) { console.log("FAIL: list_models missing 0GM"); fail++; }

const a = await client.callTool({ name: "ask_0gora", arguments: { question: "What is 0G in one sentence?" } });
console.log("ask_0gora ->", a.content[0].text.slice(0, 140).replace(/\n/g, " "), "...");
if (!a.content[0].text.includes("Verified on 0G")) { console.log("FAIL: ask missing verification"); fail++; }

await client.close();
console.log(fail === 0 ? "\nHTTP MCP SMOKE PASSED" : `\n${fail} FAILURE(S)`);
process.exit(fail === 0 ? 0 : 1);
