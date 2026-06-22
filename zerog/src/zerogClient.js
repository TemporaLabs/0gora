import { ethers } from "ethers";

// 0G compute broker SDK — pinned to ^0.7.5 for a known-good broker API.
async function loadBroker() {
  const candidates = ["@0glabs/0g-serving-broker", "@0gfoundation/0g-compute-ts-sdk"];
  for (const pkg of candidates) {
    try {
      return await import(pkg);
    } catch {
      /* try next */
    }
  }
  throw new Error("0G broker SDK not installed. `npm i @0glabs/0g-serving-broker@^0.7.5`.");
}

// processResponse's TEE signature isn't available immediately — retry w/ backoff.
async function withRetry(fn, { tries = 6, baseMs = 1000 } = {}) {
  let lastErr;
  for (let i = 0; i < tries; i++) {
    try {
      return await fn();
    } catch (e) {
      lastErr = e;
      await new Promise((r) => setTimeout(r, baseMs * 2 ** i));
    }
  }
  throw lastErr;
}

// Shown in mock mode so the model picker is populated without funds.
const MOCK_MODELS = ["zai-org/GLM-5-FP8", "glm-5.1", "deepseek-v4-pro", "qwen3.7-max"];

/**
 * Multi-model 0G direct-broker client. Resolves each requested model to its 0G
 * compute provider, runs the wallet-signed + TEE-verified flow, and returns an
 * OpenAI-shaped body + verification. Powers Onyx's model picker over 0G models.
 */
export class ZerogClient {
  constructor({ rpcUrl, privateKey, defaultModel, mock }) {
    this.rpcUrl = rpcUrl;
    this.privateKey = privateKey;
    this.defaultModel = defaultModel;
    this.mock = Boolean(mock);
    this.broker = null;
    this._chain = Promise.resolve(); // serialize broker calls (nonce not concurrency-safe)
    this._services = null;
    this._servicesAt = 0;
    this._ack = new Set(); // providers we've acknowledged on-chain
  }

  isConfigured() {
    return this.mock || Boolean(this.privateKey);
  }

  _serialize(task) {
    const run = this._chain.then(task, task);
    this._chain = run.then(
      () => {},
      () => {}
    );
    return run;
  }

  async _broker() {
    if (this.broker) return this.broker;
    const { createZGComputeNetworkBroker } = await loadBroker();
    const wallet = new ethers.Wallet(this.privateKey, new ethers.JsonRpcProvider(this.rpcUrl));
    this.broker = await createZGComputeNetworkBroker(wallet);
    return this.broker;
  }

  // Cached list of 0G chatbot services {model, provider} (5-min TTL).
  async _chatServices() {
    if (this._services && Date.now() - this._servicesAt < 300000) return this._services;
    const broker = await this._broker();
    const all = await broker.inference.listService();
    this._services = all
      .filter((s) => s.serviceType === "chatbot")
      .map((s) => ({ model: s.model, provider: s.provider }));
    this._servicesAt = Date.now();
    return this._services;
  }

  async listChatModels() {
    if (this.mock) return MOCK_MODELS;
    return (await this._chatServices()).map((s) => s.model);
  }

  async _resolve(model) {
    const svcs = await this._chatServices();
    return (
      svcs.find((s) => s.model === model) ||
      svcs.find((s) => s.model === this.defaultModel) ||
      svcs[0]
    );
  }

  _mockCompletion(req) {
    const userMsg =
      [...(req?.messages || [])].reverse().find((m) => m.role === "user")?.content || "";
    const model = req?.model || this.defaultModel || "zai-org/GLM-5-FP8";
    return {
      openai: {
        id: "chatcmpl-mock-0g",
        object: "chat.completion",
        model,
        choices: [
          {
            index: 0,
            finish_reason: "stop",
            message: {
              role: "assistant",
              content:
                `[MOCK 0G · ${model}] Placeholder answer in mock mode` +
                (userMsg ? ` (re: "${String(userMsg).slice(0, 80)}")` : "") +
                `. Fund the wallet to get real verified inference.`,
            },
          },
        ],
        usage: { prompt_tokens: 0, completion_tokens: 0, total_tokens: 0 },
      },
      verification: {
        verified: true,
        mock: true,
        model,
        chatID: "mock-chatid-0000",
        provider: "0xMOCKPROVIDER000000000000000000000000000",
        rpc: this.rpcUrl,
      },
    };
  }

  async chatCompletion(req) {
    if (this.mock) return this._mockCompletion(req);
    return this._serialize(() => this._real(req));
  }

  async _real(req) {
    const broker = await this._broker();
    const svc = await this._resolve(req.model || this.defaultModel);
    if (!svc) throw new Error("no 0G chatbot service available");
    const provider = svc.provider;
    if (!this._ack.has(provider)) {
      try {
        await broker.inference.acknowledgeProviderSigner(provider);
      } catch (e) {
        console.warn("[sidecar] ack:", e?.message);
      }
      this._ack.add(provider);
    }
    const { endpoint } = await broker.inference.getServiceMetadata(provider);
    const messages = req.messages || [];
    const content =
      [...messages].reverse().find((m) => m.role === "user")?.content ||
      JSON.stringify(messages);
    const headers = await broker.inference.getRequestHeaders(provider, content);
    const resp = await fetch(`${endpoint}/chat/completions`, {
      method: "POST",
      headers: { "Content-Type": "application/json", ...headers },
      body: JSON.stringify({
        ...req,
        model: svc.model,
        chat_template_kwargs: { enable_thinking: false, ...(req.chat_template_kwargs || {}) },
      }),
    });
    const data = await resp.json();
    // GLM reasoning models sometimes leave `content` empty and put the answer in
    // `reasoning`/`reasoning_content`. Fall back so the user never gets a blank answer.
    const choice = data?.choices?.[0];
    if (choice?.message && !String(choice.message.content || "").trim()) {
      const fb = choice.message.reasoning || choice.message.reasoning_content;
      if (fb) choice.message.content = String(fb);
    }
    const chatID = resp.headers.get("ZG-Res-Key") || data?.id;
    let verified = false;
    try {
      verified = await withRetry(() => broker.inference.processResponse(provider, chatID));
    } catch (e) {
      console.warn("[sidecar] processResponse failed:", e?.message);
    }
    return {
      openai: data,
      verification: { verified: Boolean(verified), chatID, provider, model: svc.model, rpc: this.rpcUrl },
    };
  }
}
