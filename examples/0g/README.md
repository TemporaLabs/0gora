# The 0G 0Gora — example instance

This folder is the **example that ships with the [0Gora](../../README.md) framework**: a
verifiable knowledge agora about **0G itself**, live at
[0gora.temporalabs.com/0g](https://0gora.temporalabs.com/0g).

It is **config, not code**. The framework lives in [`../../src`](../../src); this folder only
declares what makes *this* instance about 0G. That's the whole point of 0Gora — to found your
own agora, you copy this folder and edit the config; you never touch the framework.

## What's here

| File | What | Committed? |
|------|------|------------|
| `0gora.config.json` | Branding, example questions, seed corpus, prompt overrides. **No secrets.** | ✅ yes |
| `.env.example` | Template for the wallet key + runtime toggles. | ✅ yes |
| `.env` | Your real secrets (wallet key, `ZEROG_MOCK`, model allowlist). | ❌ **gitignored** |
| `compose.override.yml` | Layers this instance's config onto the framework base compose. | ✅ yes |
| `seed.sh` | Ingests the corpus seeds from `0gora.config.json` into a running instance. | ✅ yes |

The split is deliberate: **declarative config is committed and secret-free; secrets live only in
`.env`**, which the repo's `.gitignore` excludes. The framework reads `0gora.config.json` at
runtime — nothing is baked into the image.

## Run it

```bash
# from the repo root — copy the secret template and edit it
cp examples/0g/.env.example examples/0g/.env   # then set ZEROG_PRIVATE_KEY (or keep ZEROG_MOCK=true)

docker compose -f src/deploy/docker-compose.yml \
               -f examples/0g/compose.override.yml \
               --env-file examples/0g/.env up -d --build
# web :3000 · backend :8000 · qdrant :6333 · mcp :8091
```

Add `-f src/deploy/docker-compose.prod.yml` (before `--env-file`) for TLS (nginx + Let's Encrypt).

Seed the corpus once the stack is up (needs `CONTRIBUTE_KEY` set in `.env`):

```bash
CONTRIBUTE_KEY=... API=http://localhost:8000 ./examples/0g/seed.sh
```

## Found your own

1. `cp -r examples/0g examples/<your-topic>`
2. Edit `0gora.config.json` — name, branding, example questions, your seed URLs.
3. Set `.env` — your funded 0G wallet key and chosen models.
4. Bring it up with your folder's `compose.override.yml`, then run `seed.sh`.

That's it — same framework, a brand-new verifiable agora.
