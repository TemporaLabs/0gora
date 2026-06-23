# 0Gora skill

[`SKILL.md`](SKILL.md) is the agent-facing capability for 0Gora — the third way to use 0Gora (alongside
forking the repo and the npm packages). It teaches an agent to:

- **Join** an existing 0Gora as a member — connect to its MCP endpoint and `ask` / `search` / `list_models`
  for TEE-verified, cited answers.
- **Found** its own 0Gora for any topic — scaffold with [`create-0gora`](../../tools/create-0gora), configure,
  and deploy.

## Install it

**Claude Code (project or personal skills):** copy this folder into your skills directory, e.g.
```bash
cp -r src/skill ~/.claude/skills/0gora
```
or vendor it into a project's `.claude/skills/0gora/`.

The skill leans on the published packages as its tools: [`0gora-mcp`](../mcp) (join) and
[`create-0gora`](../../tools/create-0gora) (found). Nothing here is 0G-instance-specific — point the MCP at
any 0Gora.
