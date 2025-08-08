import { createClient } from '@/lib/supabase/server'
import { NextRequest, NextResponse } from 'next/server'
import { getProfile, updateProfile } from '@/lib/actions'

export async function GET(request: NextRequest) {
  const requestUrl = new URL(request.url)
  const code = requestUrl.searchParams.get('code')
  const origin = requestUrl.origin

  console.log('🔍 Auth Callback - Starting with code:', !!code)

  if (code) {
    const supabase = createClient()
    
    // Exchange the code for a session
    console.log('🔍 Auth Callback - Exchanging code for session...')
    const { data, error } = await supabase.auth.exchangeCodeForSession(code)
    
    console.log('🔍 Auth Callback - Exchange result:', {
      hasData: !!data,
      hasUser: !!data?.user,
      hasSession: !!data?.session,
      error: error ? {
        message: error.message,
        status: error.status
      } : null,
      user: data?.user ? {
        id: data.user.id,
        email: data.user.email,
        user_metadata: data.user.user_metadata,
        identities: data.user.identities
      } : null
    })
    
    if (!error && data?.user) {
      console.log('✅ Auth Callback - Session exchange successful, checking profile...')
      
      // Check if user has a profile using our server action
      const profile = await getProfile()
      
      console.log('🔍 Auth Callback - Profile check result:', {
        hasProfile: !!profile,
        profileId: profile?.id,
        profileEmail: profile?.email
      })
      
      // If no profile exists, create one and redirect to onboarding
      if (!profile) {
        console.log('🆕 Auth Callback - Creating new profile...')
        const profileData = {
          full_name: data.user.user_metadata?.full_name || 
                     data.user.user_metadata?.name || 
                     data.user.email?.split('@')[0] || 
                     'User',
          onboarding_completed: false,
          onboarding_presented: true, // Set to true since user is being shown onboarding
        }
        console.log('🔍 Auth Callback - Profile data to create:', profileData)
        
        await updateProfile(profileData)
        console.log('✅ Auth Callback - Profile created, redirecting to onboarding')
        return NextResponse.redirect(`${origin}/onboarding`)
      }

      // For existing profiles, check if onboarding has been presented
      if (!profile.onboarding_presented) {
        console.log('🔍 Auth Callback - Existing profile needs onboarding presentation')
        // Set onboarding_presented to true when user reaches onboarding page
        await updateProfile({
          onboarding_presented: true,
        })
        console.log('✅ Auth Callback - Updated onboarding_presented, redirecting to onboarding')
        return NextResponse.redirect(`${origin}/onboarding`)
      }
      
      console.log('✅ Auth Callback - Profile exists and onboarding presented, redirecting to results')
      // If presented, redirect to results
      return NextResponse.redirect(`${origin}/results`)
    }
  }

  console.log('❌ Auth Callback - No code or error occurred, redirecting to login')
  // If there's an error or no code, redirect to login with error
  return NextResponse.redirect(`${origin}/login?error=auth_failed`)
} 