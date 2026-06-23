# Using 0Gora

0Gora has **two front doors to the same verifiable 0G brain**: a web app for people, and an MCP server for AI
agents. Both return answers that are **generated and cryptographically verified on 0G** (TEE-attested), with
citations.

---

## Path 1 — Humans (the web app)

Go to **[0gora.temporalabs.com](https://0gora.temporalabs.com)**.

1. **Ask a question.** The knowledge base is seeded with 0G's documentation and blog, so try things like
   *"What is 0G Storage?"*, *"How does 0G data availability work?"*, or *"Which models does 0Gora offer?"*
2. **Pick a model** (optional) from the dropdown — four TEE-verified 0G models, with **0GM** (0G Foundation's
   own model) as the default. See [`MODELS.md`](MODELS.md).
3. **Read the answer.** Every answer comes with:
   - **inline citations** `[n]` linking to the source pages, and
   - a **"Verified on 0G"** badge — proof the answer was produced inside a hardware TEE and attested on 0G.
4. If a question isn't covered by the corpus, 0Gora says so rather than guessing.

> The public app is **read-only** today (ask, don't write). Open community contribution — the *agora* — is on
> the roadmap.

---

## Path 2 — AI agents (the MCP server)

A live **MCP server** lets agents (e.g. Claude Code) consume the same verifiable knowledge.

**Endpoint (hosted, Streamable HTTP):**
```
https://0gora.temporalabs.com/mcp
```

### Connect
**Claude Code — hosted (nothing to install):**
```bash
claude mcp add --transport http 0gora https://0gora.temporalabs.com/mcp
```
**Claude Code — local stdio server** (runs the server on your machine, still calls the hosted brain):
```bash
claude mcp add 0gora -- node /path/to/0gora/mcp/server/stdio.js
```
or add the hosted endpoint to a project `.mcp.json` (see [`../mcp/.mcp.json.example`](../mcp/.mcp.json.example)).

**From your own code:** see [`../mcp/client/example.mjs`](../mcp/client/example.mjs) and
[`../mcp/README.md`](../mcp/README.md).

### Tools
| Tool | Arguments | Returns |
|------|-----------|---------|
| `ask_0gora` | `question` (string), `model?` (string) | Grounded answer + citations + the **verification block** (`verified`, `model`, `chatID`). |
| `search_0g_knowledge` | `query` (string), `k?` (number, default 8) | Raw matching passages with source URLs (no LLM). |
| `list_models` | — | The TEE-verified 0G models available. |

### What an agent gets back
`ask_0gora` returns the answer text followed by a line like:
```
Verified on 0G: ✓ yes  (model: 0GM-1.0-35B-A3B, chatID: 4d75e263-…)
Sources:
  [1] https://docs.0g.ai/concepts/storage
  …
```
So an agent doesn't just get text — it gets knowledge it can **verify came from a TEE-attested model on 0G**.

### Server details
- **Transports:** local **stdio** (`mcp/server/stdio.js`) and remote **Streamable HTTP** (`mcp/server/http.js`,
  served at `/mcp`). Tool definitions are shared (`mcp/server/tools.js`).
- **Stateless HTTP:** each request is independent — simple to scale and to call.
- **Self-host:** point `OGORA_API` at your own 0Gora backend to run the whole thing yourself.

---

See also: [`ARCHITECTURE.md`](ARCHITECTURE.md) · [`MODELS.md`](MODELS.md) · [`../mcp/README.md`](../mcp/README.md)
