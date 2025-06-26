import { VoiceAssistant } from '@/components/VoiceAssistant'
import { createClient } from '@/lib/supabase/server'
import { redirect } from 'next/navigation'

export default async function Page() {
  const supabase = createClient()

  const { data: { user } } = await supabase.auth.getUser()

  if (!user) {
    return redirect('/login')
  }

  const { data: profile } = await supabase
    .from('profiles')
    .select('onboarding_completed')
    .single()

  if (profile && !profile.onboarding_completed) {
    return redirect('/onboarding')
  }

  return (
    <main className="h-full bg-gray-900">
      <div
        data-lk-theme="default"
        className="h-full grid content-center bg-[var(--lk-bg)]"
      >
        <VoiceAssistant />
      </div>
    </main>
  )
}
