"use client";

import { useEffect, useRef, useState } from "react";

// Contribution is closed until the contributor system ships. Build with
// NEXT_PUBLIC_CONTRIBUTE=on to expose the Contribute UI again.
const CONTRIBUTE_ENABLED = process.env.NEXT_PUBLIC_CONTRIBUTE === "on";

type Citation = { n: number; url?: string; bin?: string };
type Verification = { verified?: boolean; mock?: boolean; model?: string; chatID?: string };
type Msg = {
  role: "user" | "assistant";
  content: string;
  citations?: Citation[];
  verification?: Verification | null;
};

export default function Home() {
  const [models, setModels] = useState<string[]>([]);
  const [model, setModel] = useState<string>("");
  const [messages, setMessages] = useState<Msg[]>([]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const [showContribute, setShowContribute] = useState(false);
  const [contributeUrl, setContributeUrl] = useState("");
  const [contributeMsg, setContributeMsg] = useState("");
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    fetch("/api/models")
      .then((r) => r.json())
      .then((d) => {
        const ms: string[] = d.models || [];
        setModels(ms);
        if (ms.length) setModel(ms[0]);
      })
      .catch(() => {});
  }, []);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, busy]);

  async function send() {
    const q = input.trim();
    if (!q || busy) return;
    setInput("");
    setMessages((m) => [...m, { role: "user", content: q }]);
    setBusy(true);
    try {
      const r = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: q, model: model || undefined }),
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
        <span className="logo">ØGora</span>
        <span className="tag">verifiable knowledge on 0G</span>
        <span className="spacer" />
        {models.length > 0 && (
          <select value={model} onChange={(e) => setModel(e.target.value)} title="0G model">
            {models.map((m) => (
              <option key={m} value={m}>
                {m}
              </option>
            ))}
          </select>
        )}
        {CONTRIBUTE_ENABLED && (
          <button className="ghost" onClick={() => setShowContribute(true)}>
            + Contribute
          </button>
        )}
      </div>

      <div className="messages">
        {messages.length === 0 && (
          <div className="muted">
            Ask anything about the contributed knowledge. Try: <em>“What is 0G?”</em> — answers are
            generated and verified on 0G Compute.
          </div>
        )}
        {messages.map((m, i) => (
          <div key={i} className={`msg ${m.role}`}>
            {m.role === "assistant" ? (
              <>
                <div className="answer">{m.content}</div>
                {m.verification && (
                  <span className="badge" title={`model: ${m.verification.model || ""}\nchatID: ${m.verification.chatID || ""}`}>
                    ◇ {m.verification.verified ? "Verified on 0G" : "0G (unverified)"}
                    {m.verification.mock ? " · mock" : ""}
                  </span>
                )}
                {m.citations && m.citations.length > 0 && (
                  <div className="cites">
                    {m.citations.map((c) => (
                      <a key={c.n} className="cite" href={c.url} target="_blank" rel="noreferrer">
                        [{c.n}] {c.url ? new URL(c.url).hostname : c.bin}
                      </a>
                    ))}
                  </div>
                )}
              </>
            ) : (
              m.content
            )}
          </div>
        ))}
        {busy && <div className="muted">Thinking on 0G…</div>}
        <div ref={endRef} />
      </div>

      <div className="composer">
        <textarea
          value={input}
          placeholder="Ask 0Gora…"
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              send();
            }
          }}
        />
        <button className="primary" onClick={send} disabled={busy}>
          Send
        </button>
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
