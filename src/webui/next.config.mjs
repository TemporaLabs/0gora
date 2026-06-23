const backend = process.env.BACKEND_URL || "http://backend:8000";

/** @type {import('next').NextConfig} */
export default {
  output: "standalone",
  async rewrites() {
    // Proxy /api/* to the FastAPI backend (avoids CORS).
    return [{ source: "/api/:path*", destination: `${backend}/:path*` }];
  },
};
