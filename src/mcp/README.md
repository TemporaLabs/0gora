# 0Gora MCP

Expose **0Gora's verifiable 0G knowledge** to AI agents over the [Model Context
Protocol](https://modelcontextprotocol.io). Every answer is generated **and cryptographically verified on
0G's decentralized TEE compute** — so an agent gets knowledge it can *trust*, not just text.

This is the **agent-facing side of the agora**: humans use [`0gora.temporalabs.com`](https://0gora.temporalabs.com);
agents use this MCP server. Same verifiable 0G brain.

Published to npm as [`0gora-mcp`](https://www.npmjs.com/package/0gora-mcp) — run it with `npx`, no clone needed.

```
src/mcp/
  server/   the MCP server — tools.js (shared) + stdio.js (local) + http.js (remote)
  client/   an example MCP client (call 0Gora from your own code)
  test/     smoke tests for both transports
```

## Tools
| Tool | What it does |
|------|--------------|
| `ask_0gora(question, model?, instance?)` | Grounded, cited answer + the **0G verification block** (verified, model, chatID). |
| `search_0g_knowledge(query, k?, instance?)` | Raw matching passages + source URLs (hybrid retrieval, no LLM). |
| `list_models()` | The TEE-verified 0G models 0Gora offers. |
| `list_agoras()` | The knowledge agoras this deployment hosts. Pass an `id` as `instance` to `ask`/`search` a specific one (most deployments host one — omit `instance`). |

## Use it with Claude Code

**Easiest — the hosted remote endpoint** (nothing to install):
```bash
claude mcp add --transport http 0gora https://0gora.temporalabs.com/mcp
```

**Or run the stdio server locally via the published package** (no clone):
```bash
claude mcp add 0gora -- npx -y 0gora-mcp
```
or add to your project's `.mcp.json` (see [`.mcp.json.example`](.mcp.json.example)):
```json
{
  "mcpServers": {
    "0gora": {
      "command": "npx",
      "args": ["-y", "0gora-mcp"],
      "env": { "OGORA_API": "https://0gora.temporalabs.com/api" }
    }
  }
}
```
(From a clone instead of npm: `node src/mcp/server/stdio.js`.)
Then ask Claude Code things like *"use 0gora to find out what 0G Storage is"* — it calls `ask_0gora` and
gets a TEE-verified, cited answer.

## Call it from your own code
Agents like Claude Code bring their own MCP client — you don't need one. But to query 0Gora programmatically,
[`client/example.mjs`](client/example.mjs) shows the pattern:
```bash
cd src/mcp && npm install
npm run client:example -- "What is 0G Storage?"     # connects to the hosted endpoint
```

## Config
- `OGORA_API` — base API URL the server calls (default `https://0gora.temporalabs.com/api`). Point it at a
  local stack (`http://localhost:8000`) to run fully self-hosted.
- `MCP_URL` — used by the example client / tests to pick the MCP endpoint.

## Develop
```bash
cd src/mcp && npm install
npm start            # stdio server   (server/stdio.js)
npm run start:http   # remote server  (server/http.js, listens on :8091)
npm test             # smoke-test all three tools over stdio
```

Licensed under Apache-2.0 (see ../LICENSE).
