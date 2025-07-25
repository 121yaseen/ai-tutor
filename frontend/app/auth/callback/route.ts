import { createClient } from '@/lib/supabase/server'
import { NextRequest, NextResponse } from 'next/server'
import { getProfile, updateProfile } from '@/lib/actions'

export async function GET(request: NextRequest) {
  const requestUrl = new URL(request.url)
  const code = requestUrl.searchParams.get('code')
  const origin = requestUrl.origin

  if (code) {
    const supabase = createClient()
    
    // Exchange the code for a session
    const { data, error } = await supabase.auth.exchangeCodeForSession(code)
    
    if (!error && data?.user) {
      // Check if user has a profile using our server action
      const profile = await getProfile()
      
      // If no profile exists, create one and redirect to onboarding
      if (!profile) {
        await updateProfile({
          full_name: data.user.user_metadata?.full_name || 
                     data.user.user_metadata?.name || 
                     data.user.email?.split('@')[0] || 
                     'User',
          onboarding_completed: false,
          onboarding_presented: true, // Set to true since user is being shown onboarding
        })
        return NextResponse.redirect(`${origin}/onboarding`)
      }

      // For existing profiles, check if onboarding has been presented
      if (!profile.onboarding_presented) {
        // Set onboarding_presented to true when user reaches onboarding page
        await updateProfile({
          onboarding_presented: true,
        })
        return NextResponse.redirect(`${origin}/onboarding`)
      }
      
      // If presented, redirect to results
      return NextResponse.redirect(`${origin}/results`)
    }
  }

  // If there's an error or no code, redirect to login with error
  return NextResponse.redirect(`${origin}/login?error=auth_failed`)
} 