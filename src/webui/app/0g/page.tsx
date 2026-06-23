"use client";

import { useEffect, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

// Contribution is closed until the contributor system ships. Build with
// NEXT_PUBLIC_CONTRIBUTE=on to expose the Contribute UI again.
const CONTRIBUTE_ENABLED = process.env.NEXT_PUBLIC_CONTRIBUTE === "on";

// Instance branding is config-driven: the backend serves it at /api/config from the
// deployment's 0gora.config.json. These defaults mirror the 0G example, so the first
// paint (and any fetch failure) renders exactly as before — no flash, no regression.
type InstanceConfig = {
  name: string;
  logo: string;
  instanceLabel: string;
  hero: { title: string; lead: string; sub: string };
  examples: string[];
  placeholder: string;
};

const DEFAULT_CONFIG: InstanceConfig = {
  name: "0Gora",
  logo: "ØGora",
  instanceLabel: "the 0G agora · an example built on 0Gora",
  hero: {
    title: "ØGora",
    lead: "Ask. Verify. Trust.",
    sub: "A marketplace of knowledge on 0G. Every answer is generated and cryptographically verified inside a 0G TEE — so you can trust where it came from.",
  },
  examples: [
    "What is 0G?",
    "What is Auto model?",
    "What is 0G Storage?",
    "How does TEE verification work?",
  ],
  placeholder: "Ask 0Gora…",
};

type Citation = { n: number; url?: string; bin?: string };
type Verification = { verified?: boolean; mock?: boolean; model?: string; chatID?: string };
// Set when the picker is on "Auto": which model the backend routed to, and why.
type Routing = { chosen?: string; reason?: string; via?: string };
type Msg = {
  role: "user" | "assistant";
  content: string;
  citations?: Citation[];
  verification?: Verification | null;
  routing?: Routing | null;
};

// Turn inline [n] citation markers into clickable links to their source — the
// ChatGPT/Perplexity pattern. The [n] keeps its text; the <a> component below
// renders bracketed-number links as a small superscript pill (.cite-ref).
function linkifyCitations(content: string, citations?: Citation[]): string {
  if (!citations?.length) return content;
  const urlByN = new Map(citations.filter((c) => c.url).map((c) => [c.n, c.url as string]));
  return content.replace(/\[(\d+)\]/g, (full, n) => {
    const url = urlByN.get(Number(n));
    return url ? `[\\[${n}\\]](${url})` : full;
  });
}

export default function Home() {
  const [cfg, setCfg] = useState<InstanceConfig>(DEFAULT_CONFIG);
  const [models, setModels] = useState<string[]>([]);
  // Default to Auto: the backend picks the best model per query (manual pin still available).
  const [model, setModel] = useState<string>("auto");
  const [messages, setMessages] = useState<Msg[]>([]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const [showContribute, setShowContribute] = useState(false);
  const [contributeUrl, setContributeUrl] = useState("");
  const [contributeMsg, setContributeMsg] = useState("");
  const [listening, setListening] = useState(false);
  const [voiceOK, setVoiceOK] = useState(false);
  const [voiceErr, setVoiceErr] = useState("");
  const endRef = useRef<HTMLDivElement>(null);
  const recogRef = useRef<any>(null);

  useEffect(() => {
    fetch("/api/models")
      .then((r) => r.json())
      .then((d) => {
        const ms: string[] = d.models || [];
        setModels(ms);
        // Keep the default on "Auto"; the live list just populates the manual-pin options.
      })
      .catch(() => {});
    // Pull this instance's branding/examples from the backend (config-driven).
    fetch("/api/config")
      .then((r) => r.json())
      .then((d) => setCfg((c) => ({ ...c, ...d, hero: { ...c.hero, ...(d.hero || {}) } })))
      .catch(() => {});
  }, []);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, busy]);

  // Voice input via the Web Speech API (Chrome/Edge). The mic only shows when supported.
  useEffect(() => {
    const SR = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (!SR) return;
    const r = new SR();
    r.lang = "en-US";
    r.interimResults = true;
    r.continuous = false;
    r.onresult = (e: any) => {
      setVoiceErr("");
      const t = Array.from(e.results)
        .map((res: any) => res[0]?.transcript || "")
        .join("");
      setInput(t);
    };
    r.onend = () => setListening(false);
    r.onerror = (e: any) => {
      setListening(false);
      const err = e?.error;
      if (err === "not-allowed" || err === "service-not-allowed")
        setVoiceErr("Microphone blocked — allow mic access for this site (check the address-bar icon), then tap the mic again.");
      else if (err === "no-speech") setVoiceErr("Didn't catch that — tap the mic and speak.");
      else if (err === "audio-capture") setVoiceErr("No microphone found.");
      else if (err && err !== "aborted") setVoiceErr("Voice input error — try again.");
    };
    recogRef.current = r;
    setVoiceOK(true);
    return () => {
      try {
        r.abort();
      } catch {
        /* noop */
      }
    };
  }, []);

  function toggleVoice() {
    const r = recogRef.current;
    if (!r) return;
    if (listening) {
      try {
        r.stop();
      } catch {
        /* noop */
      }
      setListening(false);
    } else {
      setVoiceErr("");
      setInput("");
      try {
        r.start();
        setListening(true);
      } catch {
        // start() throws if a prior session is still winding down — reset and let the user retry.
        try {
          r.abort();
        } catch {
          /* noop */
        }
        setListening(false);
      }
    }
  }

  async function send(question?: string) {
    const q = (question ?? input).trim();
    if (!q || busy) return;
    setInput("");
    setMessages((m) => [...m, { role: "user", content: q }]);
    setBusy(true);
    try {
      const r = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: q, model: model || "auto" }),
      });
      // Parse defensively: an error response may be plain text, not JSON.
      const raw = await r.text();
      let d: any = {};
      try {
        d = raw ? JSON.parse(raw) : {};
      } catch {
        d = { answer: r.ok ? raw : `⚠️ The service returned an error (${r.status}). Please try again.` };
      }
      setMessages((m) => [
        ...m,
        {
          role: "assistant",
          content: d.answer || d.detail || "⚠️ No answer returned. Please try again.",
          citations: d.citations,
          verification: d.x_0g_verification,
          routing: d.routing,
        },
      ]);
    } catch {
      setMessages((m) => [
        ...m,
        { role: "assistant", content: "⚠️ Couldn't reach 0Gora. Check your connection and try again." },
      ]);
    } finally {
      setBusy(false);
    }
  }

  async function contribute() {
    const url = contributeUrl.trim();
    if (!url) return;
    setContributeMsg("Ingesting…");
    try {
      const r = await fetch("/api/contribute", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url }),
      });
      const d = await r.json();
      setContributeMsg(`Added ${d.chunks ?? 0} chunks from ${url}`);
      setContributeUrl("");
    } catch {
      setContributeMsg("Failed to ingest that URL.");
    }
  }

  return (
    <div className="wrap">
      <div className="header">
        <a className="logo" href="/" title="Back to 0Gora">{cfg.logo}</a>
        <span className="tag">{cfg.instanceLabel}</span>
        <span className="spacer" />
        <label className="model-pick" title="0G model — Auto picks the best one per query">
          <span className="model-label">Model</span>
          <select value={model} onChange={(e) => setModel(e.target.value)}>
            <option value="auto">Auto</option>
            {models.map((m) => (
              <option key={m} value={m}>
                {m}
              </option>
            ))}
          </select>
        </label>
        {CONTRIBUTE_ENABLED && (
          <button className="ghost" onClick={() => setShowContribute(true)}>
            + Contribute
          </button>
        )}
      </div>

      {messages.length === 0 ? (
        <div className="hero">
          <div className="hero-bg" />
          <div className="hero-wash" />
          <div className="hero-scrim" />
          <div className="hero-inner">
            <h1>{cfg.hero.title}</h1>
            <p className="lead">{cfg.hero.lead}</p>
            <p className="sub">{cfg.hero.sub}</p>
            <div className="chips">
              {cfg.examples.map((ex) => (
                <button key={ex} className="chip" onClick={() => send(ex)}>
                  {ex}
                </button>
              ))}
            </div>
          </div>
        </div>
      ) : (
        <div className="messages">
          {messages.map((m, i) => (
            <div key={i} className={`msg ${m.role}`}>
              {m.role === "assistant" ? (
                <>
                  <div className="answer">
                    <ReactMarkdown
                      remarkPlugins={[remarkGfm]}
                      components={{
                        a({ node, children, ...props }) {
                          const txt = Array.isArray(children) ? children.join("") : String(children ?? "");
                          const isRef = /^\[\d+\]$/.test(txt);
                          return (
                            <a {...props} target="_blank" rel="noreferrer" className={isRef ? "cite-ref" : undefined}>
                              {children}
                            </a>
                          );
                        },
                      }}
                    >
                      {linkifyCitations(m.content, m.citations)}
                    </ReactMarkdown>
                  </div>
                  {m.verification && (
                    <div className={`seal ${m.verification.mock ? "mock" : ""}`}>
                      <span className="mark">{m.verification.verified ? "✓" : "!"}</span>
                      <span>
                        <span className="seal-main">
                          {m.verification.verified ? "Verified on 0G" : "0G — unverified"}
                          {m.verification.mock ? " · mock" : ""}
                        </span>
                        <br />
                        <span className="seal-sub">
                          TEE-attested · <b>{m.verification.model || "0G"}</b>
                          {m.verification.chatID ? ` · ${m.verification.chatID.slice(0, 10)}…` : ""}
                        </span>
                      </span>
                    </div>
                  )}
                  {m.routing?.chosen && (
                    <div className="route" title="Auto routing chose this model for your query">
                      ⤷ Auto routed to <b>{m.routing.chosen}</b>
                      {m.routing.reason ? ` · ${m.routing.reason}` : ""}
                    </div>
                  )}
                  {(() => {
                    // Only show sources the answer actually cites inline ([n]). Hybrid
                    // retrieval always returns top-k passages, so a non-answer ("I don't
                    // have that information") would otherwise show unrelated citations.
                    const used = new Set(
                      (m.content.match(/\[(\d+)\]/g) || []).map((x) => x.replace(/\D/g, ""))
                    );
                    const shown = (m.citations || []).filter((c) => used.has(String(c.n)));
                    return shown.length > 0 ? (
                      <div className="cites">
                        {shown.map((c) => (
                          <a key={c.n} className="cite" href={c.url} target="_blank" rel="noreferrer">
                            <span className="n">[{c.n}]</span>
                            <span className="host">{c.url ? new URL(c.url).hostname : c.bin}</span>
                          </a>
                        ))}
                      </div>
                    ) : null;
                  })()}
                </>
              ) : (
                m.content
              )}
            </div>
          ))}
          {busy && (
            <div className="thinking">
              <span className="dot" /> Thinking on 0G…
            </div>
          )}
          <div ref={endRef} />
        </div>
      )}

      {voiceErr && <div className="voice-note">{voiceErr}</div>}

      <div className="composer">
        <textarea
          value={input}
          placeholder={listening ? "Listening… speak now (tap the mic to stop)" : cfg.placeholder}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              send();
            }
          }}
        />
        {voiceOK && (
          <button
            className={`mic${listening ? " rec" : ""}`}
            onClick={toggleVoice}
            disabled={busy}
            title={listening ? "Stop voice input" : "Voice input"}
            aria-label="Voice input"
          >
            🎤
          </button>
        )}
        <button className="primary" onClick={() => send()} disabled={busy}>
          Send
        </button>
      </div>

      <div className="foot">
        Built for agents too — connect over <a href="https://github.com/TemporaLabs/0gora/tree/main/src/mcp" target="_blank" rel="noreferrer">MCP</a>.
      </div>

      {showContribute && (
        <div className="modal-bg" onClick={() => setShowContribute(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h3 style={{ marginTop: 0 }}>Contribute knowledge</h3>
            <p className="muted">Paste a URL to add it to the community commons (the agora).</p>
            <div className="row">
              <input
                style={{ flex: 1 }}
                value={contributeUrl}
                placeholder="https://…"
                onChange={(e) => setContributeUrl(e.target.value)}
              />
              <button className="primary" onClick={contribute}>
                Add
              </button>
            </div>
            {contributeMsg && <p className="muted" style={{ marginBottom: 0 }}>{contributeMsg}</p>}
          </div>
        </div>
      )}
    </div>
  );
}
