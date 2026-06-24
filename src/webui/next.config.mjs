const backend = process.env.BACKEND_URL || "http://backend:8000";

/** @type {import('next').NextConfig} */
export default {
  output: "standalone",
  async rewrites() {
    return [
      // Proxy /api/* to the FastAPI backend (avoids CORS).
      { source: "/api/:path*", destination: `${backend}/:path*` },
      // The chat lives in app/chat/ (route /chat) but is served at the public /app URL.
      // We avoid a literal app/app/ route folder: a route segment named "app" nested in
      // the App-Router app/ dir breaks the standalone build's root / route (it renders the
      // chat at / instead of the landing).
      { source: "/app", destination: "/chat" },
    ];
  },
};
