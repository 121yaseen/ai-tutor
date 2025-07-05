import { createClient } from '@/lib/supabase/server'
import { redirect } from 'next/navigation'
import PremiumStatsCards from '@/components/PremiumStatsCards'
import LuxuryPerformanceChart from '@/components/LuxuryPerformanceChart'
import AdvancedSessionFeedback from '@/components/AdvancedSessionFeedback'
import ScoreInsights from '@/components/ScoreInsights'
import Link from 'next/link'

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
    .select('target_band_score, first_name, exam_date')
    .single()

  const targetScore = profile?.target_band_score || 7.5
  const firstName = profile?.first_name || 'Student'
  const examDate = profile?.exam_date

  // Calculate days until exam
  const daysUntilExam = examDate 
    ? Math.ceil((new Date(examDate).getTime() - new Date().getTime()) / (1000 * 60 * 60 * 24))
    : null

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 pt-20 sm:pt-24 lg:pt-28">
      {/* Hero Section */}
      <div className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-amber-500/10 via-transparent to-purple-500/10"></div>
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-12 lg:py-16">
          <div className="text-center mb-8 sm:mb-12">
            <h1 className="text-3xl sm:text-4xl md:text-5xl lg:text-6xl font-light text-white mb-4 sm:mb-6 tracking-tight">
              Your <span className="font-medium bg-gradient-to-r from-amber-400 via-orange-500 to-purple-500 bg-clip-text text-transparent">Progress</span> Journey
            </h1>
            <p className="text-base sm:text-lg lg:text-xl text-gray-300 max-w-3xl mx-auto font-light leading-relaxed px-4">
              Welcome back, <span className="text-amber-400 font-medium">{firstName}</span>. 
              Track your evolution toward your target score of <span className="text-purple-400 font-semibold">{targetScore}</span>
              {daysUntilExam && daysUntilExam > 0 && (
                <span className="block mt-2 text-sm sm:text-base lg:text-lg">
                  <span className="text-orange-400 font-medium">{daysUntilExam} days</span> until your exam
                </span>
              )}
            </p>
          </div>

          {/* Premium Stats Grid */}
          <PremiumStatsCards userEmail={user.email!} targetScore={targetScore} />
        </div>
      </div>

      {/* Analytics Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-12 lg:py-16 space-y-8 sm:space-y-12 lg:space-y-16">
        {/* Performance Visualization */}
        <div className="bg-white/5 backdrop-blur-xl rounded-2xl sm:rounded-3xl border border-white/10 p-4 sm:p-6 lg:p-8 shadow-2xl">
          <LuxuryPerformanceChart userEmail={user.email!} targetScore={targetScore} />
        </div>

        {/* Two Column Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 sm:gap-8">
          {/* Score Insights */}
          <div className="bg-gradient-to-br from-purple-500/10 to-blue-500/10 backdrop-blur-xl rounded-2xl sm:rounded-3xl border border-white/10 p-4 sm:p-6 lg:p-8 shadow-2xl">
            <ScoreInsights userEmail={user.email!} targetScore={targetScore} />
          </div>

          {/* Latest Session Feedback */}
          <div className="bg-gradient-to-br from-amber-500/10 to-orange-500/10 backdrop-blur-xl rounded-2xl sm:rounded-3xl border border-white/10 p-4 sm:p-6 lg:p-8 shadow-2xl">
            <AdvancedSessionFeedback userEmail={user.email!} />
          </div>
        </div>

        {/* Achievement Timeline */}
        <div className="bg-white/5 backdrop-blur-xl rounded-2xl sm:rounded-3xl border border-white/10 p-4 sm:p-6 lg:p-8 shadow-2xl">
          <h3 className="text-xl sm:text-2xl font-light text-white mb-6 sm:mb-8 flex items-center">
            <span className="w-6 h-6 sm:w-8 sm:h-8 bg-gradient-to-r from-green-400 to-blue-500 rounded-full flex items-center justify-center mr-3 sm:mr-4 text-sm sm:text-base">
              🏆
            </span>
            Achievement Timeline
          </h3>
          <div className="text-gray-400 text-center py-8 sm:py-12">
            <p className="text-base sm:text-lg px-4">Your achievements and milestones will appear here as you progress</p>
          </div>
        </div>
      </div>

      {/* Floating Action Button */}
      <div className="fixed bottom-4 right-4 sm:bottom-6 sm:right-6 lg:bottom-8 lg:right-8 z-40">
        <Link 
          href="/" 
          className="group bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-400 hover:to-orange-400 text-white px-4 py-3 sm:px-6 sm:py-4 lg:px-8 lg:py-4 rounded-xl sm:rounded-2xl shadow-2xl hover:shadow-amber-500/25 transition-all duration-300 transform hover:scale-105 inline-flex touch-manipulation"
        >
          <span className="flex items-center space-x-2 sm:space-x-3">
            <span className="text-base sm:text-lg">🎯</span>
            <span className="font-medium text-sm sm:text-base">Start Practice</span>
            <svg className="w-4 h-4 sm:w-5 sm:h-5 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
            </svg>
          </span>
        </Link>
      </div>
    </div>
  )
} 