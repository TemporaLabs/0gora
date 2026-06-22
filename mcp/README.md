# 0Gora MCP server

Expose **0Gora's verifiable 0G knowledge** to AI agents over the [Model Context
Protocol](https://modelcontextprotocol.io). Every answer is generated **and cryptographically verified on
0G's decentralized TEE compute** — so an agent gets knowledge it can *trust*, not just text.

This is the **agent-facing side of the agora**: humans use [`0gora.temporalabs.com`](https://0gora.temporalabs.com);
agents use this MCP server. Same verifiable 0G brain.

## Tools
| Tool | What it does |
|------|--------------|
| `ask_0gora(question, model?)` | Grounded, cited answer + the **0G verification block** (verified, model, chatID). |
| `search_0g_knowledge(query, k?)` | Raw matching passages + source URLs (hybrid retrieval, no LLM). |
| `list_models()` | The TEE-verified 0G models 0Gora offers. |

## Use it with Claude Code
```bash
# from anywhere, pointing at the hosted 0Gora:
claude mcp add 0gora -- node /path/to/0gora/mcp/src/server.js
```
or add to your project's `.mcp.json` (see [`.mcp.json.example`](.mcp.json.example)):
```json
{
  "mcpServers": {
    "0gora": {
      "command": "node",
      "args": ["./mcp/src/server.js"],
      "env": { "OGORA_API": "https://0gora.temporalabs.com/api" }
    }
  }
}
```
Then ask Claude Code things like *"use 0gora to find out what 0G Storage is"* — it calls `ask_0gora` and
gets a TEE-verified, cited answer.

## Config
- `OGORA_API` — base API URL (default `https://0gora.temporalabs.com/api`). Point it at a local stack
  (`http://localhost:8000`) to run fully self-hosted.

## Develop
```bash
cd mcp && npm install
npm start          # run the stdio server
npm test           # smoke test all three tools against the live API
```

Licensed under Apache-2.0 (see ../LICENSE).
