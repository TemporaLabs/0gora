#!/usr/bin/env node
// create-0gora — scaffold your own verifiable knowledge agora on 0G.
//
//   npm create 0gora@latest my-agora
//   npm create 0gora@latest my-agora -- --name "CoffeeGora" --topic "specialty coffee"
//
// What it does: shallow-clones the 0Gora framework, then generates a configured
// instance under examples/<slug>/ (config + .env + compose overlay) so you can
// `docker compose … up` immediately. The framework in src/ is never edited — you
// only own your example folder. Dependency-free (Node built-ins only).
import { execFileSync } from "node:child_process";
import { existsSync, readdirSync, readFileSync, writeFileSync, cpSync, rmSync } from "node:fs";
import { join, resolve } from "node:path";
import { createInterface } from "node:readline/promises";
import { stdin, stdout, argv, exit } from "node:process";

// Override to scaffold from a fork or a local path (also used in tests).
const REPO = process.env.OGORA_REPO || "https://github.com/TemporaLabs/0gora.git";

function parseArgs(args) {
  const out = { _: [], yes: false, ref: "main" };
  for (let i = 0; i < args.length; i++) {
    const a = args[i];
    if (a === "--yes" || a === "-y") out.yes = true;
    else if (a === "--name") out.name = args[++i];
    else if (a === "--topic") out.topic = args[++i];
    else if (a === "--slug") out.slug = args[++i];
    else if (a === "--ref") out.ref = args[++i];
    else if (a.startsWith("--")) { /* ignore unknown flag */ }
    else out._.push(a);
  }
  return out;
}

const slugify = (s) =>
  s.toLowerCase().trim().replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "") || "my-agora";

function die(msg) {
  console.error(`\n✗ ${msg}`);
  exit(1);
}

async function main() {
  const opts = parseArgs(argv.slice(2));
  const interactive = !opts.yes && stdin.isTTY;
  const rl = interactive ? createInterface({ input: stdin, output: stdout }) : null;
  const ask = async (q, def) => {
    if (!rl) return def;
    const a = (await rl.question(`${q}${def ? ` (${def})` : ""}: `)).trim();
    return a || def;
  };

  // Verify git is available — we clone the framework.
  try {
    execFileSync("git", ["--version"], { stdio: "ignore" });
  } catch {
    die("git is required (it clones the 0Gora framework). Install git and retry.");
  }

  const dir = opts._[0] || (await ask("Project directory", "my-agora"));
  const target = resolve(process.cwd(), dir);
  if (existsSync(target) && readdirSync(target).length > 0) {
    die(`${dir} already exists and is not empty.`);
  }

  const name = opts.name || (await ask("Agora name", "My 0Gora"));
  const topic = opts.topic || (await ask("Topic / ecosystem (what is it about?)", "your topic"));
  const slug = slugify(opts.slug || name);
  rl?.close();

  console.log(`\n→ Cloning the 0Gora framework into ${dir} …`);
  execFileSync("git", ["clone", "--depth", "1", "--branch", opts.ref, REPO, target], {
    stdio: "inherit",
  });
  // Start fresh history — this is the founder's own project, not a fork of ours.
  rmSync(join(target, ".git"), { recursive: true, force: true });

  // Generate the instance from the shipped 0G example as a template.
  const tmpl = join(target, "examples", "0g");
  const inst = join(target, "examples", slug);
  if (!existsSync(tmpl)) die("framework template examples/0g not found (unexpected clone state).");
  if (slug !== "0g") cpSync(tmpl, inst, { recursive: true });

  // Rewrite the config with the founder's answers (keep everything else as a sane default).
  const cfgPath = join(inst, "0gora.config.json");
  const cfg = JSON.parse(readFileSync(cfgPath, "utf8"));
  cfg.$comment =
    `The ${name} agora — your instance config. Single declarative source of truth (no secrets). ` +
    `Edit branding/examples/corpus here; secrets live in .env. The framework in ../../src reads this at runtime.`;
  cfg.name = name;
  cfg.logo = name;
  cfg.instanceLabel = `a verifiable knowledge agora · built on 0Gora`;
  cfg.ecosystem = topic;
  cfg.hero = {
    title: name,
    lead: "Ask. Verify. Trust.",
    sub: `A verifiable knowledge base about ${topic}. Every answer is generated and cryptographically verified inside a 0G TEE — so you can trust where it came from.`,
  };
  cfg.examples = [`What is ${topic}?`, "How does this work?", "Which models can I use?"];
  cfg.placeholder = `Ask about ${topic}…`;
  cfg.corpus = {
    $comment: "Seed sources for your knowledge base, ingested via seed.sh. Add your own URLs.",
    seeds: [],
  };
  cfg.prompts = { grounded: null, chat: null };
  writeFileSync(cfgPath, JSON.stringify(cfg, null, 2) + "\n");

  // Point the compose overlay at the new folder + create a mock .env to start.
  const ovPath = join(inst, "compose.override.yml");
  if (existsSync(ovPath)) {
    const ov = readFileSync(ovPath, "utf8").replaceAll("examples/0g/", `examples/${slug}/`);
    writeFileSync(ovPath, ov);
  }
  const envExample = join(inst, ".env.example");
  if (existsSync(envExample)) {
    writeFileSync(join(inst, ".env"), readFileSync(envExample, "utf8"));
  }

  console.log(`\n✓ Created ${dir} — your "${name}" agora (examples/${slug}/).\n`);
  console.log("Next:");
  console.log(`  cd ${dir}`);
  console.log(`  # edit examples/${slug}/.env — set ZEROG_PRIVATE_KEY (or keep ZEROG_MOCK=true to try it free)`);
  console.log(`  # add your sources to examples/${slug}/0gora.config.json → corpus.seeds`);
  console.log(`  docker compose -f src/deploy/docker-compose.yml \\`);
  console.log(`                 -f examples/${slug}/compose.override.yml \\`);
  console.log(`                 --env-file examples/${slug}/.env up -d --build`);
  console.log(`  CONTRIBUTE_KEY=... API=http://localhost:8000 ./examples/${slug}/seed.sh   # seed the corpus`);
  console.log(`\nThat's your own verifiable agora — same framework, your knowledge. 🏛️`);
}

main().catch((e) => die(e?.message || String(e)));
