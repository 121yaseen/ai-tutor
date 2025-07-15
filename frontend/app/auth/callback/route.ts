import { createClient } from '@/lib/supabase/server'
import { NextRequest, NextResponse } from 'next/server'


export async function GET(request: NextRequest) {
  const requestUrl = new URL(request.url)
  const code = requestUrl.searchParams.get('code')
  const origin = requestUrl.origin

  if (code) {
    const supabase = createClient()
    
    // Exchange the code for a session
    const { data, error } = await supabase.auth.exchangeCodeForSession(code)
    
    if (!error && data?.user) {
      // Check if user has a profile
      const { data: profile } = await supabase
        .from('profiles')
        .select('*')
        .eq('id', data.user.id)
        .single()
      
      // If no profile exists, create one with flags and redirect to onboarding
      if (!profile) {
        await supabase.from('profiles').insert([
          {
            id: data.user.id,
            full_name: data.user.user_metadata?.full_name || 
                      data.user.user_metadata?.name || 
                      data.user.email?.split('@')[0] || 
                      'User',
            updated_at: new Date().toISOString(),
            onboarding_completed: false,
            onboarding_presented: false,
          }
        ])
        return NextResponse.redirect(`${origin}/onboarding`)
      }

      // For existing profiles, check if onboarding has been presented
      if (!profile.onboarding_presented) {
        return NextResponse.redirect(`${origin}/onboarding`)
      }
      
      // If presented, redirect to results
      return NextResponse.redirect(`${origin}/results`)
    }
  }

  // If there's an error or no code, redirect to login with error
  return NextResponse.redirect(`${origin}/login?error=auth_failed`)
} 