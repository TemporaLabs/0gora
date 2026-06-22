// Example MCP *client* — how to call 0Gora's verifiable knowledge from your own
// code (not via Claude Code, which brings its own client). Connects to the
// hosted remote MCP server over Streamable HTTP, lists the tools, and asks a
// question — printing the answer plus its on-chain verification status.
//
//   node client/example.mjs                       # uses the hosted endpoint
//   MCP_URL=http://localhost:8091/mcp node client/example.mjs   # a local server
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StreamableHTTPClientTransport } from "@modelcontextprotocol/sdk/client/streamableHttp.js";

const url = new URL(process.env.MCP_URL || "https://0gora.temporalabs.com/mcp");
const question = process.argv.slice(2).join(" ") || "What is 0G in one sentence?";

const client = new Client({ name: "0gora-example-client", version: "1.0.0" });
await client.connect(new StreamableHTTPClientTransport(url));

const tools = await client.listTools();
console.log("0Gora tools:", tools.tools.map((t) => t.name).join(", "));

const res = await client.callTool({ name: "ask_0gora", arguments: { question } });
console.log(`\nQ: ${question}\n`);
console.log(res.content.map((c) => c.text).join("\n"));

await client.close();
