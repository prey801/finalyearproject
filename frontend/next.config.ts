import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Allow localtunnel and ngrok tunnel origins during development/Colab.
  // Without this, Next.js 15+ blocks /__nextjs_original-stack-frames with 403.
  allowedDevOrigins: ["*.loca.lt", "*.ngrok-free.app", "*.ngrok.io", "*.ngrok.app"],

  // Suppress the Node.js version deprecation noise from @supabase/supabase-js
  // (warning is informational only — no functional impact on Node 20)
  serverExternalPackages: [],

  // Disable strict type-checking on env vars at build time so the build
  // succeeds even when NEXT_PUBLIC_SUPABASE_* are provided at runtime (Colab).
  env: {
    NEXT_PUBLIC_SUPABASE_URL:            process.env.NEXT_PUBLIC_SUPABASE_URL            ?? '',
    NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY: process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY ?? '',
    NEXT_PUBLIC_SUPABASE_ANON_KEY:        process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY        ?? '',
    NEXT_PUBLIC_API_URL:                 process.env.NEXT_PUBLIC_API_URL                 ?? '',
  },
  experimental: {
    turbo: {
      root: process.cwd(),
    },
  },
};

export default nextConfig;
