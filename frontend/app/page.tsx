import { VoiceAssistant } from '@/components/VoiceAssistant'
import { createClient } from '@/lib/supabase/server'
import { redirect } from 'next/navigation'

export default async function Page() {
  const supabase = createClient()

  const { data: { user } } = await supabase.auth.getUser()

  if (!user) {
    return redirect('/login')
  }

  // Removed onboarding check and redirect

  return (
    <main className="h-full bg-gradient-to-b from-gray-900 via-gray-900 to-gray-950">
      <div
        data-lk-theme="default"
        className="h-full grid content-center bg-[var(--lk-bg)]"
      >
        <VoiceAssistant />
      </div>
    </main>
  )
}
