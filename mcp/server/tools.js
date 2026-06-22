// Shared 0Gora MCP tool definitions, used by both the stdio (server.js) and
// HTTP (http.js) transports. Calls the 0Gora API (OGORA_API, default the hosted
// public API; set to http://backend:8000 when running inside the compose net).
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";

export const API = (process.env.OGORA_API || "https://0gora.temporalabs.com/api").replace(/\/+$/, "");

async function api(path, init) {
  const r = await fetch(`${API}${path}`, init);
  const text = await r.text();
  let data;
  try {
    data = text ? JSON.parse(text) : {};
  } catch {
    throw new Error(`0Gora API ${path} returned non-JSON (${r.status}): ${text.slice(0, 200)}`);
  }
  if (!r.ok) throw new Error(`0Gora API ${path} -> ${r.status}: ${JSON.stringify(data).slice(0, 200)}`);
  return data;
}

export function createServer() {
  const server = new McpServer({ name: "0gora", version: "0.1.4" });

  server.tool(
    "ask_0gora",
    "Ask 0Gora a question about its knowledge base. Returns a grounded answer with inline citations, " +
      "generated AND cryptographically verified on 0G's decentralized TEE compute (TeeML attestation). " +
      "Use this when you want a synthesized, source-cited answer you can trust came from a verified model.",
    {
      question: z.string().describe("The question to ask 0Gora"),
      model: z.string().optional().describe("Optional 0G model id (default: 0GM-1.0-35B-A3B)"),
    },
    async ({ question, model }) => {
      const d = await api("/chat", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ message: question, ...(model ? { model } : {}) }),
      });
      const v = d.x_0g_verification || {};
      const cites = (d.citations || []).map((c) => `  [${c.n}] ${c.url || c.bin || ""}`).join("\n");
      const text = [
        d.answer || "(no answer)",
        "",
        `Verified on 0G: ${v.verified ? "✓ yes" : "✗ no"}  (model: ${v.model || "?"}, chatID: ${v.chatID || "?"})`,
        cites ? `Sources:\n${cites}` : "",
      ]
        .filter(Boolean)
        .join("\n");
      return { content: [{ type: "text", text }] };
    }
  );

  server.tool(
    "search_0g_knowledge",
    "Search 0Gora's knowledge base and return the raw matching passages with their source URLs " +
      "(hybrid vector + keyword retrieval, no LLM synthesis). Use this when you want the source text " +
      "yourself rather than a synthesized answer.",
    {
      query: z.string().describe("Search query"),
      k: z.number().int().min(1).max(20).optional().describe("Number of passages to return (default 8)"),
    },
    async ({ query, k }) => {
      const d = await api("/search", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ query, k: k || 8 }),
      });
      const text =
        (d.results || [])
          .map((r, i) => `[${i + 1}] ${r.url || r.bin || ""}\n${(r.text || "").slice(0, 500)}`)
          .join("\n\n") || "(no results)";
      return { content: [{ type: "text", text }] };
    }
  );

  server.tool(
    "list_models",
    "List the 0G models available in 0Gora. All are TEE-verified (TeeML) on the 0G compute broker.",
    {},
    async () => {
      const d = await api("/models", {});
      return { content: [{ type: "text", text: (d.models || []).join("\n") || "(none)" }] };
    }
  );

  return server;
}
