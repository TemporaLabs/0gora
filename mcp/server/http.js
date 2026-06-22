// 0Gora MCP server (Streamable HTTP transport) — remote, reachable by URL so any
// agent can connect without running anything locally. Deployed alongside the web
// app on the same host. Stateless: a fresh server+transport per request.
import express from "express";
import { StreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/streamableHttp.js";
import { createServer, API } from "./tools.js";

const PORT = process.env.PORT || 8091;
const app = express();
app.use(express.json({ limit: "1mb" }));

app.get("/mcp/health", (_req, res) => res.json({ status: "ok", service: "0gora-mcp", api: API }));

// MCP endpoint at /mcp (matches the external nginx path, so no URI rewriting).
// Stateless request/response (no server-initiated streams needed for these
// tools), so each POST gets its own transport that is torn down after.
app.post("/mcp", async (req, res) => {
  const server = createServer();
  const transport = new StreamableHTTPServerTransport({ sessionIdGenerator: undefined });
  res.on("close", () => {
    transport.close();
    server.close();
  });
  try {
    await server.connect(transport);
    await transport.handleRequest(req, res, req.body);
  } catch (e) {
    console.error("[0gora-mcp http] error:", e?.message);
    if (!res.headersSent) {
      res.status(500).json({ jsonrpc: "2.0", error: { code: -32603, message: "Internal server error" }, id: null });
    }
  }
});

// Stateless mode has no long-lived SSE stream; GET/DELETE are not supported.
app.get("/mcp", (_req, res) =>
  res.status(405).json({ jsonrpc: "2.0", error: { code: -32000, message: "Method not allowed (use POST)" }, id: null })
);

app.listen(PORT, () => console.error(`[0gora-mcp] streamable-http on :${PORT} (API=${API})`));
