# What is 0Gora?

**0Gora** — 0G + [agora](https://www.britannica.com/topic/agora), the public square where knowledge was
exchanged. A community-crowdsourced knowledge base, built on 0G. Ask it anything; every answer is grounded,
cited, and **verified on 0G**.

**For people and AI agents alike** — humans use the web, agents connect over MCP. Same verified brain.

## What it's for
- A shared, open knowledge base for any community or domain — not a walled garden.
- Answers you can trust: each is generated and TEE-verified on 0G, with citations. No black box.
- One source of truth your team **and** your agents can query.

## Where it fits
- Project/protocol docs that answer questions (our live demo: a 0Gora about 0G itself).
- A community or DAO knowledge commons.
- An internal knowledge base with verifiable answers.
- A knowledge tool your AI agents can call — and trust.

## Using 0Gora

Two front doors, one verified brain.

### Humans — the web
Open **[0gora.temporalabs.com/0g](https://0gora.temporalabs.com/0g)**. Ask — by default 0Gora **auto-picks**
the best 0G model for each query (a short *Auto routed to…* line shows which model answered and why); pin a
specific model from the picker if you prefer. Each answer shows inline citations `[n]` and a **Verified on 0G**
seal. If a question isn't in the corpus, 0Gora answers from general knowledge instead of guessing.

### Agents — MCP
Connect over MCP (hosted, Streamable HTTP): `https://0gora.temporalabs.com/mcp`

```bash
claude mcp add --transport http 0gora https://0gora.temporalabs.com/mcp
```

| Tool | Args | Returns |
|------|------|---------|
| `ask_0gora` | `question`, `model?` | answer + citations + verification (`verified`, `model`, `chatID`) + `routing` (`chosen`, `reason`) when the model is auto-picked |
| `search_0g_knowledge` | `query`, `k?` | raw passages + source URLs (no LLM) |
| `list_models` | — | the verified 0G models |

`model?` accepts a specific id or `"auto"` (the default) to let 0Gora route. An agent gets knowledge it can
**verify came from a TEE-attested model on 0G** — not just text. See [`../src/mcp/README.md`](../src/mcp/README.md).

---
Next: [Why 0G?](WHY-0G.md) · [Inside 0Gora](INSIDE.md)
