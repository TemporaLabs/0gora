#!/usr/bin/env node
// 0Gora MCP server (stdio transport) — for local use with Claude Code and any
// MCP client. Exposes 0Gora's verifiable 0G knowledge. Tools live in tools.js
// (shared with the HTTP transport in http.js).
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { createServer, API } from "./tools.js";

const server = createServer();
const transport = new StdioServerTransport();
await server.connect(transport);
console.error(`[0gora-mcp] stdio connected (API=${API})`);
