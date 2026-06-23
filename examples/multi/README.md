# Co-hosted 0Gora — 0G + ERC-8226 on one deployment

This is the **production layout** for `0gora.temporalabs.com`: a single stack that serves **two agoras
side by side** — the [0G agora](../0g/README.md) and the [ERC-8226 agora](../erc-8226/README.md) — behind
one in-app switcher at **`/app`**. Both are powered by the **same funded 0G wallet**; the switcher (left of
the model picker) flips the chat between them.

## How it works

- **One stack, two corpora.** One web UI, one backend, one Qdrant, one 0G inference sidecar. Each agora
  keeps its **own Qdrant collection** (`0gora` vs `erc8226`, from each config's `collection` field), so
  their knowledge never mixes. The backend routes each request to the right collection by `instance` id.
- **One wallet, shared.** Both agoras answer on the single 0G sidecar — one funded key. Because it's one
  process with serialized broker calls, there are **no cross-instance nonce races** (running two separate
  sidecars on one key would race; co-hosting on one is exactly how we avoid that).
- **Declarative.** This folder adds **no config of its own** — it just mounts the two sibling
  `0gora.config.json` files and lists them in `OGORA_INSTANCES`. The first (`0g`) is the default instance
  (served at `/app` before the user touches the switcher, and to API/MCP callers that omit `instance`).

```
                       0gora.temporalabs.com/app   ← in-app switcher: [ 0G | ERC-8226 ]
                                  │ nginx
                    ┌─────────────┴─────────────┐
                  web                          backend ──► instance=0g ──► Qdrant: 0gora
                                                     └──► instance=erc-8226 ──► Qdrant: erc8226
                                                     └──► 0G sidecar (one funded wallet) ──► TEE-verified
```

## Run it

```bash
cp examples/multi/.env.example examples/multi/.env   # set ZEROG_PRIVATE_KEY (funded) — ZEROG_MOCK=false

docker compose -f src/deploy/docker-compose.yml \
               -f src/deploy/docker-compose.prod.yml \
               -f examples/multi/compose.override.yml \
               --env-file examples/multi/.env up -d --build
```

For local development without funds, drop the `prod.yml` line and set `ZEROG_MOCK=true` in `.env`.

## Seed both corpora

Once the stack is up, seed each agora (each `seed.sh` reads its config and tags its own `instance`, so
sources land in the right collection):

```bash
CONTRIBUTE_KEY=... API=http://localhost:8000 ./examples/0g/seed.sh
CONTRIBUTE_KEY=... API=http://localhost:8000 ./examples/erc-8226/seed.sh
```

## Add a third agora

1. `cp -r examples/0g examples/<your-topic>` and edit its `0gora.config.json` (`id`, `collection`,
   `switcherLabel`, branding, `corpus.seeds`).
2. Mount it and append its path to `OGORA_INSTANCES` in `compose.override.yml`.
3. Redeploy and run its `seed.sh`. The switcher picks it up automatically.
