# create-0gora

Scaffold **your own verifiable knowledge agora** on [0G](https://0g.ai) in one command.

```bash
npm create 0gora@latest my-agora
# or non-interactive:
npm create 0gora@latest my-agora -- --name "CoffeeGora" --topic "specialty coffee" --yes
```

It shallow-clones the [0Gora](https://github.com/TemporaLabs/0gora) framework, then generates a configured
instance under `examples/<slug>/` — `0gora.config.json` (branding, example questions, corpus — **no
secrets**), a `.env` (mock mode by default), and a compose overlay — so you can bring it straight up:

```bash
cd my-agora
# edit examples/<slug>/.env → set ZEROG_PRIVATE_KEY (or keep ZEROG_MOCK=true to try it free)
docker compose -f src/deploy/docker-compose.yml \
               -f examples/<slug>/compose.override.yml \
               --env-file examples/<slug>/.env up -d --build
```

You only ever edit your example folder — the framework in `src/` is shared and untouched. Add your sources to
`corpus.seeds` and run `examples/<slug>/seed.sh` to fill the knowledge base.

## Options
| Flag | Meaning |
|------|---------|
| `--name` | Display name of your agora |
| `--topic` | What it's about (sets ecosystem, examples, prompts) |
| `--slug` | Folder name under `examples/` (defaults from `--name`) |
| `--ref` | Framework branch/tag to clone (default `main`) |
| `--yes` / `-y` | Non-interactive; use defaults/flags |

Requires Node ≥18 and `git`. Apache-2.0.
