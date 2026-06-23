import Link from "next/link";

// External links. DOCS_URL points to the repo docs today; swap to the GitBook
// URL (GitHub-synced from the same docs/) once the space exists — one line.
const GITHUB_URL = "https://github.com/TemporaLabs/0gora";
const DOCS_URL = "/docs";
const APP_URL = "/0g";

export default function Landing() {
  return (
    <div className="lp">
      <header className="lp-head">
        <span className="logo">ØGora</span>
        <nav className="lp-nav">
          <a href={GITHUB_URL} target="_blank" rel="noreferrer">GitHub</a>
          <Link href={DOCS_URL}>Docs</Link>
        </nav>
      </header>

      {/* ---------- hero ---------- */}
      <section className="lp-hero">
        <div className="lp-hero-bg" />
        <div className="lp-hero-wash" />
        <div className="lp-hero-scrim" />
        <div className="lp-hero-inner">
          <h1 className="lp-word">ØGora</h1>
          <p className="lp-headline">
            Create any town square — for anything, for anyone.
            <br />
            <span className="lp-accent">Human or agent.</span>
          </p>
          <p className="lp-def">
            <b>0G + <a href="https://www.britannica.com/topic/agora" target="_blank" rel="noreferrer">agora</a></b> —
            a public square of knowledge. Built by the community. <b>Answers you can trust.</b>
          </p>
          <div className="lp-cta">
            <a className="btn btn-primary" href={GITHUB_URL} target="_blank" rel="noreferrer">
              Build your 0Gora <span className="arr">→</span>
            </a>
            <Link className="btn btn-ghost" href={DOCS_URL}>
              Read the docs
            </Link>
          </div>
        </div>
      </section>

      {/* ---------- what is 0Gora ---------- */}
      <section className="lp-section">
        <h2 className="lp-h2">What is 0Gora?</h2>
        <p className="lp-lead">
          A shared knowledge base for any community — that <em>people</em> and <em>AI</em> can ask,
          with answers you can trust.
        </p>
        <div className="lp-cards">
          <div className="lp-card">
            <div className="lp-card-ic">⌘</div>
            <h3>Crowdsourced</h3>
            <p>Anyone can add to it — open, not locked away.</p>
          </div>
          <div className="lp-card">
            <div className="lp-card-ic">◇</div>
            <h3>Verified on 0G</h3>
            <p>Every answer is checked on 0G — no black box.</p>
          </div>
          <div className="lp-card">
            <div className="lp-card-ic">⚇</div>
            <h3>People <span className="lp-accent">and</span> AI</h3>
            <p>Ask it yourself, or let your AI agent ask.</p>
          </div>
        </div>
      </section>

      {/* ---------- try the 0G 0Gora ---------- */}
      <section className="lp-try">
        <div className="lp-try-inner">
          <span className="lp-eyebrow">Live example</span>
          <h2 className="lp-h2">Try the 0G 0Gora</h2>
          <p className="lp-lead">
            See one in action — a knowledge base about <b>0G itself</b>. Ask it anything.
          </p>
          <Link className="btn btn-primary btn-lg" href={APP_URL}>
            Open the app <span className="arr">→</span>
          </Link>
        </div>
      </section>

      <footer className="lp-foot">
        <span className="logo logo-sm">ØGora</span>
        <nav>
          <a href={GITHUB_URL} target="_blank" rel="noreferrer">GitHub</a>
          <Link href={DOCS_URL}>Docs</Link>
          <a href={`${GITHUB_URL}/tree/main/src/mcp`} target="_blank" rel="noreferrer">MCP (for agents)</a>
          <Link href={APP_URL}>The 0G app</Link>
        </nav>
        <span className="lp-foot-note">Built for the 0G Zero Cup</span>
      </footer>
    </div>
  );
}
