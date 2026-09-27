import type { NextConfig } from "next";

const BACKEND_URL = process.env.BACKEND_URL ?? "http://127.0.0.1:5000";

const nextConfig: NextConfig = {
  // Proxy API calls to the Flask backend so the browser only talks to one origin (no CORS).
  async rewrites() {
    return [{ source: "/api/:path*", destination: `${BACKEND_URL}/api/:path*` }];
  },
  experimental: {
    // Pricing scrapes two supermarkets per ingredient; allow it more than the 30s default.
    proxyTimeout: 120_000,
  },
};

export default nextConfig;
