import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Allow localtunnel (loca.lt) and ngrok origins during development.
  // Without this, Next.js 15+ blocks /__nextjs_original-stack-frames with 403,
  // making error overlays non-functional when accessed via a tunnel URL.
  allowedDevOrigins: ["*.loca.lt", "*.ngrok-free.app", "*.ngrok.io"],
};

export default nextConfig;
