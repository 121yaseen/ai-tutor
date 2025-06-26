
import OnboardingForm from '@/components/OnboardingForm'
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

  return (
    <div className="container mx-auto p-4 sm:p-8 bg-gray-900 min-h-screen">
      <OnboardingForm user={user} />
    </div>
  )
}
