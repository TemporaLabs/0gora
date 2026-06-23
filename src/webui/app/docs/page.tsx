import fs from "node:fs";
import path from "node:path";
import Link from "next/link";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

export const metadata = {
  title: "Docs — 0Gora",
  description: "0Gora documentation: what it is, how to use it (web + MCP), architecture, and the verifiable 0G model catalog.",
};

const GITHUB_URL = "https://github.com/TemporaLabs/0gora";

const DOCS = [
  { slug: "overview", file: "README.md", title: "What is 0Gora?" },
  { slug: "why-0g", file: "WHY-0G.md", title: "Why 0G?" },
  { slug: "inside", file: "INSIDE.md", title: "Inside 0Gora" },
];

function load(file: string): string {
  try {
    return fs.readFileSync(path.join(process.cwd(), "app/docs/_content", file), "utf8");
  } catch {
    return "_Documentation is being updated._";
  }
}

export default function Docs() {
  const sections = DOCS.map((d) => ({ ...d, body: load(d.file) }));
  return (
    <div className="lp">
      <header className="lp-head">
        <Link className="logo" href="/">ØGora</Link>
        <nav className="lp-nav">
          <Link href="/0g">Try the app</Link>
          <a href={GITHUB_URL} target="_blank" rel="noreferrer">GitHub</a>
        </nav>
      </header>

      <div className="docs-wrap">
        <aside className="docs-side">
          <div className="docs-side-title">Documentation</div>
          <nav>
            {DOCS.map((d) => (
              <a key={d.slug} href={`#${d.slug}`}>{d.title}</a>
            ))}
          </nav>
          <div className="docs-side-foot">
            <a href={`${GITHUB_URL}/tree/main/docs`} target="_blank" rel="noreferrer">Edit on GitHub →</a>
          </div>
        </aside>

        <main className="docs-main">
          {sections.map((s) => (
            <section key={s.slug} id={s.slug} className="docs-section">
              <div className="answer">
                <ReactMarkdown remarkPlugins={[remarkGfm]}>{s.body}</ReactMarkdown>
              </div>
            </section>
          ))}
          <p className="docs-end muted">
            Kept short on purpose — writing style inspired by the{" "}
            <a href="https://github.com/juliusbrussee/caveman" target="_blank" rel="noreferrer">caveman</a>{" "}
            principle (less is more), not fully emulated. · Built originally for the 0G Zero Cup ·{" "}
            <Link href="/">← back to 0Gora</Link>
          </p>
        </main>
      </div>
    </div>
  );
}
