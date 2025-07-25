
import ProfileForm from '@/components/ProfileForm'
import { getProfile } from '@/lib/actions'
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

  const profile = await getProfile()

  // The logic for 'onboarding_presented' will be handled differently,
  // likely within the ProfileForm or a separate action.
  // For now, we fetch the profile and pass it down.

  return (
    <div className="container mx-auto p-4 sm:p-8 bg-gray-900 min-h-screen">
      <ProfileForm isOnboarding={true} profile={profile} />
    </div>
  )
}
