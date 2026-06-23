# The ERC-8226 0Gora — example instance

A verifiable public forum for **[ERC-8226 — the Regulated Agent Mandate](https://github.com/ethereum/ERCs/blob/master/ERCS/erc-8226.md)**,
built on the [0Gora](../../README.md) framework. Its corpus is the **ERC text** plus the
**[Ethereum Magicians discussion](https://ethereum-magicians.org/t/erc-8226-regulated-agent-mandate)** —
ask a question, get a grounded answer with citations, **generated and cryptographically verified inside a 0G TEE**.

It is the same framework as the [0G agora](../0g/README.md) — **config, not code**. The only thing that
makes it about ERC-8226 is [`0gora.config.json`](0gora.config.json) (branding + corpus). In production it
is **co-hosted with the 0G agora** on one deployment, behind an in-app switcher, both answering on the
**same funded 0G wallet** — see [`../multi/`](../multi/README.md).

## What's here

| File | What | Committed? |
|------|------|------------|
| `0gora.config.json` | Branding, example questions, the ERC-8226 seed corpus, prompts. `id`/`collection` keep it separate from the 0G agora. **No secrets.** | ✅ yes |
| `.env.example` | Template for the wallet key + runtime toggles (standalone runs only). | ✅ yes |
| `.env` | Your real secrets. | ❌ **gitignored** |
| `compose.override.yml` | **Standalone** overlay — runs ERC-8226 on its own. | ✅ yes |
| `seed.sh` | Ingests the corpus seeds into the `erc8226` collection (sends `instance: erc-8226`). | ✅ yes |

## Run it standalone

```bash
cp examples/erc-8226/.env.example examples/erc-8226/.env   # set ZEROG_PRIVATE_KEY (or keep ZEROG_MOCK=true)

docker compose -f src/deploy/docker-compose.yml \
               -f examples/erc-8226/compose.override.yml \
               --env-file examples/erc-8226/.env up -d --build
# web :3000 · backend :8000 · qdrant :6333 · mcp :8091
```

Seed the corpus once the stack is up (needs `CONTRIBUTE_KEY` set in `.env`):

```bash
CONTRIBUTE_KEY=... API=http://localhost:8000 ./examples/erc-8226/seed.sh
```

> **Corpus note.** The Ethereum Magicians thread is a Discourse page whose replies paginate. If `seed.sh`
> reports too few chunks for that source, switch its seed in `0gora.config.json` to the raw markdown URL
> or to `mode: "site"` with a small `max_pages`, and re-seed.

## Run it co-hosted with the 0G agora (production)

This is the live layout — one deployment, two agoras, one wallet, an in-app switcher at `/app`.
See **[`../multi/README.md`](../multi/README.md)**.
