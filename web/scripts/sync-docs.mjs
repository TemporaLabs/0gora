// Mirror the repo's docs/*.md into the web app so the /docs page can render them
// at build time. The repo docs/ stay the single source of truth; this copy is a
// build artifact (committed so the Docker build — which only sees web/ — has it,
// and refreshed automatically on every local `npm run build` via prebuild).
import fs from "node:fs";
import path from "node:path";

const SRC = path.resolve(process.cwd(), "../docs");
const DEST = path.resolve(process.cwd(), "app/docs/_content");
const FILES = ["README.md", "GUIDE.md", "ARCHITECTURE.md", "MODELS.md"];

if (!fs.existsSync(SRC)) {
  // In the Docker build context ../docs doesn't exist — keep the committed copy.
  console.log("[sync-docs] ../docs not found; using committed copy");
  process.exit(0);
}
fs.mkdirSync(DEST, { recursive: true });
for (const f of FILES) {
  const from = path.join(SRC, f);
  if (fs.existsSync(from)) {
    fs.copyFileSync(from, path.join(DEST, f));
    console.log(`[sync-docs] ${f}`);
  }
}
