// Smoke test: spawn the MCP server over stdio, list tools, and call each one
// against the live 0Gora API. Run:  npm test   (from mcp/)
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";

const transport = new StdioClientTransport({
  command: "node",
  args: ["server/stdio.js"],
  env: { ...process.env },
});
const client = new Client({ name: "0gora-mcp-smoke", version: "0.0.0" });
await client.connect(transport);

let fail = 0;
const tools = (await client.listTools()).tools.map((t) => t.name).sort();
const expect = ["ask_0gora", "list_agoras", "list_models", "search_0g_knowledge"];
console.log("tools:", tools.join(", "));
if (JSON.stringify(tools) !== JSON.stringify(expect)) { console.log("FAIL: tool list mismatch"); fail++; }

const models = await client.callTool({ name: "list_models", arguments: {} });
const mtext = models.content[0].text;
console.log("list_models ->", mtext.replace(/\n/g, ", "));
if (!mtext.includes("0GM")) { console.log("FAIL: list_models missing 0GM"); fail++; }

const search = await client.callTool({ name: "search_0g_knowledge", arguments: { query: "0G storage", k: 3 } });
console.log("search_0g_knowledge ->", search.content[0].text.slice(0, 120).replace(/\n/g, " "), "...");
if (!search.content[0].text.trim() || search.content[0].text.includes("(no results)")) { console.log("FAIL: search empty"); fail++; }

const ans = await client.callTool({ name: "ask_0gora", arguments: { question: "What is 0G in one sentence?" } });
const atext = ans.content[0].text;
console.log("ask_0gora ->", atext.slice(0, 160).replace(/\n/g, " "), "...");
if (!atext.includes("Verified on 0G")) { console.log("FAIL: ask_0gora missing verification line"); fail++; }

await client.close();
console.log(fail === 0 ? "\nALL MCP SMOKE TESTS PASSED" : `\n${fail} FAILURE(S)`);
process.exit(fail === 0 ? 0 : 1);
