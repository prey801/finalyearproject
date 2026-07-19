import { createServerClient } from '@supabase/ssr'
import { cookies } from 'next/headers'

const SUPABASE_URL = process.env.NEXT_PUBLIC_SUPABASE_URL ?? ''
const SUPABASE_KEY = process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY ?? ''

/**
 * Server-side Supabase client.
 * Falls back to a placeholder during static prerender so builds don't crash
 * when NEXT_PUBLIC_SUPABASE_* env vars aren't present.
 */
export async function createClient() {
  const cookieStore = await cookies()

  const url = SUPABASE_URL || 'https://placeholder.supabase.co'
  const key = SUPABASE_KEY || 'placeholder-key'

  return createServerClient(url, key, {
    cookies: {
      getAll() {
        return cookieStore.getAll()
      },
      setAll(cookiesToSet) {
        try {
          cookiesToSet.forEach(({ name, value, options }) =>
            cookieStore.set(name, value, options)
          )
        } catch {
          // Called from a Server Component — safe to ignore.
        }
      },
    },
  })
}
