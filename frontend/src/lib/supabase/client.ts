import { createBrowserClient } from '@supabase/ssr'

const SUPABASE_URL = process.env.NEXT_PUBLIC_SUPABASE_URL ?? ''
const SUPABASE_KEY = process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY ?? ''

export function createClient() {
  if (!SUPABASE_URL || !SUPABASE_KEY) {
    // During build/prerender the env vars may not be present.
    // Return a no-op placeholder so SSR doesn't crash.
    return createBrowserClient('https://placeholder.supabase.co', 'placeholder-key')
  }
  return createBrowserClient(SUPABASE_URL, SUPABASE_KEY)
}
