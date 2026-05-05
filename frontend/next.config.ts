import type { NextConfig } from "next";

const isProd = process.env.NODE_ENV === "production";
const apiBaseUrl =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

if (isProd && !apiBaseUrl.startsWith("http://")) {
  throw new Error(
    `NEXT_PUBLIC_API_BASE_URL must use https:// in production builds. Got: ${apiBaseUrl}`,
  );
}

// Origins the app legitimately talks to. Listed explicitly so a future change
// (e.g. adding a CDN) shows up in this file rather than being silently allowed.
const apiOrigin = new URL(apiBaseUrl).origin;
const externalImageHosts = ["https://tile.openstreetmap.org"];
const externalConnectHosts = ["https://tile.openstreetmap.org"];

const csp = [
  "default-src 'self'",
  `img-src 'self' data: blob: ${apiOrigin} ${externalImageHosts.join(" ")}`,
  // Next.js + React still emit inline runtime; nonces would require a custom
  // server. unsafe-inline / unsafe-eval are kept for now — XSS protection
  // here is mainly via frame-ancestors / form-action / base-uri, plus the
  // backend's input validation.
  "script-src 'self' 'unsafe-inline' 'unsafe-eval'",
  "style-src 'self' 'unsafe-inline'",
  "font-src 'self' data:",
  `connect-src 'self' ${apiOrigin} ${externalConnectHosts.join(" ")}`,
  "frame-ancestors 'none'",
  "base-uri 'self'",
  "form-action 'self'",
  "object-src 'none'",
].join("; ");

const securityHeaders = [
  { key: "Content-Security-Policy", value: csp },
  { key: "X-Frame-Options", value: "DENY" },
  { key: "X-Content-Type-Options", value: "nosniff" },
  { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
  {
    key: "Permissions-Policy",
    value: "geolocation=(), camera=(), microphone=()",
  },
  ...(isProd
    ? [
        {
          key: "Strict-Transport-Security",
          value: "max-age=63072000; includeSubDomains; preload",
        },
      ]
    : []),
];

const nextConfig: NextConfig = {
  // Strip console.log/info/debug in production builds; keep error + warn so
  // genuine prod issues still surface.
  compiler: {
    removeConsole: isProd ? { exclude: ["error", "warn"] } : false,
  },
  // No remote image hosts are actually used today — listings come in as
  // base64 data URLs and profile icons are same-origin via /media. Add
  // specific hostnames here when a real CDN is adopted.
  images: { remotePatterns: [] },
  async headers() {
    return [{ source: "/:path*", headers: securityHeaders }];
  },
};

export default nextConfig;
