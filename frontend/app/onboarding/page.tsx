
import ProfileForm from '@/components/ProfileForm'
import { createClient } from '@/lib/supabase/server'
import { redirect } from 'next/navigation'

export default async function OnboardingPage() {
  const supabase = createClient()

  const {
    data: { user },
  } = await supabase.auth.getUser()

  if (!user) {
    redirect('/login')
  }

  // Check and set onboarding_presented
  const { data: profile } = await supabase
    .from('profiles')
    .select('onboarding_presented')
    .eq('id', user.id)
    .single()

  if (profile && !profile.onboarding_presented) {
    await supabase
      .from('profiles')
      .update({ onboarding_presented: true })
      .eq('id', user.id)
  }

  return (
    <div className="container mx-auto p-4 sm:p-8 bg-gray-900 min-h-screen">
      <ProfileForm user={user} isOnboarding={true} />
    </div>
  )
}
