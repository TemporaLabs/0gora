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
            <b>0Gora</b> — 0G + <a href="https://www.britannica.com/topic/agora" target="_blank" rel="noreferrer">agora</a>,
            the public square where knowledge was exchanged. A community-crowdsourced commons of
            <b> verifiable knowledge</b>, built on 0G — every answer generated <em>and</em> cryptographically
            sealed in a 0G TEE.
          </p>
          <div className="lp-cta">
            <a className="btn btn-primary" href={GITHUB_URL} target="_blank" rel="noreferrer">
              Build your 0Gora today <span className="arr">→</span>
              <span className="btn-sub">on GitHub</span>
            </a>
            <Link className="btn btn-ghost" href={DOCS_URL}>
              Read the Docs <span className="arr">→</span>
              <span className="btn-sub">guides &amp; architecture</span>
            </Link>
          </div>
        </div>
      </section>

      {/* ---------- what is 0Gora ---------- */}
      <section className="lp-section">
        <h2 className="lp-h2">What is 0Gora?</h2>
        <p className="lp-lead">
          A townhall of exchange. Spin up a living, crowdsourced knowledge base for any community or
          domain — then let people <em>and</em> AI agents ask it, and trust the answers, because every
          response is verified on 0G's decentralized compute.
        </p>
        <div className="lp-cards">
          <div className="lp-card">
            <div className="lp-card-ic">⌘</div>
            <h3>Crowdsourced knowledge</h3>
            <p>A shared commons anyone can contribute to — a marketplace of knowledge, not a walled garden.</p>
          </div>
          <div className="lp-card">
            <div className="lp-card-ic">◇</div>
            <h3>Verifiable on 0G</h3>
            <p>Answers are generated and TEE-attested on 0G compute, so you can trust where each one came from.</p>
          </div>
          <div className="lp-card">
            <div className="lp-card-ic">⚇</div>
            <h3>Humans <span className="lp-accent">and</span> agents</h3>
            <p>A clean web square for people, and an MCP surface so AI agents can read and reason over it too.</p>
          </div>
        </div>
      </section>

      {/* ---------- try the 0G 0Gora ---------- */}
      <section className="lp-try">
        <div className="lp-try-inner">
          <span className="lp-eyebrow">Live example</span>
          <h2 className="lp-h2">Try the 0G 0Gora</h2>
          <p className="lp-lead">
            One agora we built: a living knowledge base about <b>0G itself</b> — its docs, blog, and
            models. Ask it anything; every answer is sealed in a 0G TEE.
          </p>
          <Link className="btn btn-primary btn-lg" href={APP_URL}>
            Open the 0G 0Gora app <span className="arr">→</span>
          </Link>
        </div>
      </section>

      <footer className="lp-foot">
        <span className="logo logo-sm">ØGora</span>
        <nav>
          <a href={GITHUB_URL} target="_blank" rel="noreferrer">GitHub</a>
          <Link href={DOCS_URL}>Docs</Link>
          <a href={`${GITHUB_URL}/tree/main/mcp`} target="_blank" rel="noreferrer">MCP (for agents)</a>
          <Link href={APP_URL}>The 0G app</Link>
        </nav>
        <span className="lp-foot-note">Built for the 0G Zero Cup</span>
      </footer>
    </div>
  );
}
