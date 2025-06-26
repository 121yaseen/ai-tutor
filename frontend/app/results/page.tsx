import { createClient } from '@/lib/supabase/server'
import { redirect } from 'next/navigation'
import StatsCards from '@/components/StatsCards'
import PerformanceChart from '@/components/PerformanceChart'
import LatestSessionFeedback from '@/components/LatestSessionFeedback'

export default async function ResultsPage() {
  const supabase = createClient()

  const {
    data: { user },
  } = await supabase.auth.getUser()

  if (!user) {
    redirect('/login')
  }

  // Get user profile for target score
  const { data: profile } = await supabase
    .from('profiles')
    .select('target_band_score')
    .single()

  const targetScore = profile?.target_band_score || 7.5

  return (
    <div className="min-h-screen bg-gray-900 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">Your Progress Report</h1>
          <p className="text-gray-400">
            Track your journey to your target band score of {targetScore}.
          </p>
        </div>

        {/* Stats Cards */}
        <StatsCards userEmail={user.email!} />

        {/* Performance Chart */}
        <div className="mt-8">
          <PerformanceChart userEmail={user.email!} targetScore={targetScore} />
        </div>

        {/* Latest Session Feedback */}
        <div className="mt-8">
          <LatestSessionFeedback userEmail={user.email!} />
        </div>
      </div>
    </div>
  )
} 