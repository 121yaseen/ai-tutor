'use client'

import { useEffect, useState } from 'react'
import { createClient } from '@/lib/supabase/client'
import { motion } from 'framer-motion'

interface TestResult {
  band_score: number
  test_date: string
  detailed_scores?: {
    fluency: number
    vocabulary: number
    grammar: number
    pronunciation: number
  }
}

interface InsightData {
  currentLevel: string
  nextLevel: string
  pointsToTarget: number
  strongestSkill: string
  weakestSkill: string
  recommendation: string
  consistencyScore: number
  improvementRate: number
}

export default function ScoreInsights({ 
  userEmail, 
  targetScore 
}: { 
  userEmail: string
  targetScore: number 
}) {
  const [insights, setInsights] = useState<InsightData | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function generateInsights() {
      try {
        const supabase = createClient()
        const { data, error } = await supabase
          .from('students')
          .select('history')
          .eq('email', userEmail)
          .single()

        if (error || !data?.history || data.history.length === 0) {
          setLoading(false)
          return
        }

        const history: TestResult[] = data.history
        const latestTest = history[history.length - 1]
        const scores = history.map(test => test.band_score).filter(score => score > 0)

        // Calculate insights
        const currentScore = latestTest.band_score
        const currentLevel = getBandLevel(currentScore)
        const nextLevel = getBandLevel(Math.min(currentScore + 0.5, 9))
        const pointsToTarget = Math.max(0, targetScore - currentScore)

        // Find strongest and weakest skills
        let strongestSkill = 'vocabulary'
        let weakestSkill = 'grammar'
        if (latestTest.detailed_scores) {
          const skills = latestTest.detailed_scores
          const maxScore = Math.max(skills.fluency, skills.vocabulary, skills.grammar, skills.pronunciation)
          const minScore = Math.min(skills.fluency, skills.vocabulary, skills.grammar, skills.pronunciation)
          
          if (skills.fluency === maxScore) strongestSkill = 'fluency'
          else if (skills.vocabulary === maxScore) strongestSkill = 'vocabulary'
          else if (skills.grammar === maxScore) strongestSkill = 'grammar'
          else if (skills.pronunciation === maxScore) strongestSkill = 'pronunciation'

          if (skills.fluency === minScore) weakestSkill = 'fluency'
          else if (skills.vocabulary === minScore) weakestSkill = 'vocabulary'
          else if (skills.grammar === minScore) weakestSkill = 'grammar'
          else if (skills.pronunciation === minScore) weakestSkill = 'pronunciation'
        }

        // Calculate consistency (lower variation = higher consistency)
        const consistency = scores.length > 1 
          ? Math.max(0, 100 - (Math.max(...scores) - Math.min(...scores)) * 20)
          : 100

        // Calculate improvement rate
        const improvementRate = scores.length > 1
          ? ((scores[scores.length - 1] - scores[0]) / scores.length) * 100
          : 0

        // Generate recommendation
        const recommendation = generateRecommendation(pointsToTarget, weakestSkill, consistency)

        setInsights({
          currentLevel,
          nextLevel,
          pointsToTarget,
          strongestSkill,
          weakestSkill,
          recommendation,
          consistencyScore: Math.round(consistency),
          improvementRate: Math.round(improvementRate * 10) / 10
        })
      } catch (error) {
        console.error('Error generating insights:', error)
      } finally {
        setLoading(false)
      }
    }

    generateInsights()
  }, [userEmail, targetScore])

  const getBandLevel = (score: number): string => {
    if (score >= 8.5) return 'Expert'
    if (score >= 7.5) return 'Very Good'
    if (score >= 6.5) return 'Competent'
    if (score >= 5.5) return 'Modest'
    if (score >= 4.5) return 'Limited'
    return 'Extremely Limited'
  }

  const generateRecommendation = (pointsToTarget: number, weakestSkill: string, consistency: number): string => {
    if (pointsToTarget <= 0) return "Congratulations! You've reached your target. Consider aiming higher!"
    if (pointsToTarget >= 2) return `Focus intensively on ${weakestSkill} - it needs significant improvement to reach your target.`
    if (consistency < 70) return `Work on consistency across all skills. Practice regularly to stabilize your performance.`
    return `You're close to your target! Fine-tune your ${weakestSkill} with targeted practice sessions.`
  }

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="h-8 bg-gray-600 rounded w-1/2 animate-pulse"></div>
        <div className="grid grid-cols-2 gap-4">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="h-20 bg-gray-600 rounded animate-pulse"></div>
          ))}
        </div>
      </div>
    )
  }

  if (!insights) {
    return (
      <div className="text-center py-12">
        <div className="w-16 h-16 bg-gradient-to-br from-purple-500 to-blue-500 rounded-full flex items-center justify-center mx-auto mb-4">
          <span className="text-2xl">🔍</span>
        </div>
        <h3 className="text-xl font-light text-white mb-2">Insights Pending</h3>
        <p className="text-gray-400">Complete more practice sessions for detailed insights.</p>
      </div>
    )
  }

  const insightCards = [
    {
      title: 'Current Level',
      value: insights.currentLevel,
      subtitle: 'Your proficiency',
      icon: '📊',
      color: 'from-blue-500 to-purple-600',
    },
    {
      title: 'Next Milestone',
      value: insights.nextLevel,
      subtitle: 'Achievement ahead',
      icon: '🎯',
      color: 'from-purple-500 to-pink-600',
    },
    {
      title: 'To Target',
      value: `${insights.pointsToTarget} pts`,
      subtitle: 'Points needed',
      icon: '🚀',
      color: 'from-amber-500 to-orange-600',
    },
    {
      title: 'Consistency',
      value: `${insights.consistencyScore}%`,
      subtitle: 'Performance stability',
      icon: '⚡',
      color: 'from-green-500 to-emerald-600',
    },
  ]

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h3 className="text-2xl font-light text-white mb-2 flex items-center">
          <span className="w-8 h-8 bg-gradient-to-r from-purple-400 to-blue-500 rounded-full flex items-center justify-center mr-3">
            🧠
          </span>
          AI Insights
        </h3>
        <p className="text-gray-400">Personalized analysis of your learning journey</p>
      </div>

      {/* Insight Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {insightCards.map((card, index) => (
          <motion.div
            key={index}
            className={`bg-gradient-to-br ${card.color} bg-opacity-20 backdrop-blur-sm rounded-xl p-4 border border-white/10`}
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: index * 0.1, duration: 0.5 }}
            whileHover={{ scale: 1.05 }}
          >
            <div className="flex items-center justify-between mb-3">
              <span className="text-2xl">{card.icon}</span>
              <div className={`w-2 h-2 bg-gradient-to-r ${card.color} rounded-full`}></div>
            </div>
            <div className="text-xl font-bold text-white mb-1">{card.value}</div>
            <div className="text-sm text-gray-400">{card.title}</div>
            <div className="text-xs text-gray-500 mt-1">{card.subtitle}</div>
          </motion.div>
        ))}
      </div>

      {/* Skills Analysis */}
      <motion.div
        className="bg-gradient-to-r from-gray-800/50 to-gray-900/50 rounded-xl p-6 border border-white/10"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
      >
        <h4 className="text-lg font-medium text-white mb-4 flex items-center">
          <span className="w-6 h-6 bg-gradient-to-r from-green-400 to-blue-500 rounded-full flex items-center justify-center mr-3">
            ⚖️
          </span>
          Skills Balance
        </h4>
        <div className="grid md:grid-cols-2 gap-6">
          <div className="flex items-center justify-between p-4 bg-green-500/10 rounded-lg border border-green-500/20">
            <div>
              <div className="text-green-400 font-medium capitalize">Strongest: {insights.strongestSkill}</div>
              <div className="text-sm text-gray-400">Keep leveraging this strength</div>
            </div>
            <span className="text-2xl">💪</span>
          </div>
          <div className="flex items-center justify-between p-4 bg-orange-500/10 rounded-lg border border-orange-500/20">
            <div>
              <div className="text-orange-400 font-medium capitalize">Focus Area: {insights.weakestSkill}</div>
              <div className="text-sm text-gray-400">Greatest improvement potential</div>
            </div>
            <span className="text-2xl">🎯</span>
          </div>
        </div>
      </motion.div>

      {/* AI Recommendation */}
      <motion.div
        className="bg-gradient-to-br from-amber-500/10 via-orange-500/10 to-red-500/10 backdrop-blur-sm rounded-xl p-6 border border-amber-500/20"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.7 }}
      >
        <h4 className="text-lg font-medium text-amber-400 mb-3 flex items-center">
          <span className="w-6 h-6 bg-gradient-to-r from-amber-400 to-orange-500 rounded-full flex items-center justify-center mr-3">
            🤖
          </span>
          AI Recommendation
        </h4>
        <p className="text-gray-300 leading-relaxed">{insights.recommendation}</p>
        
        {/* Progress Indicator */}
        <div className="mt-4">
          <div className="flex justify-between text-sm text-gray-400 mb-2">
            <span>Progress to Target</span>
            <span>{Math.max(0, 100 - (insights.pointsToTarget / targetScore) * 100).toFixed(0)}%</span>
          </div>
          <div className="w-full bg-gray-700/50 rounded-full h-2">
            <motion.div
              className="h-full bg-gradient-to-r from-amber-400 to-orange-500 rounded-full"
              initial={{ width: 0 }}
              animate={{ width: `${Math.max(0, 100 - (insights.pointsToTarget / targetScore) * 100)}%` }}
              transition={{ delay: 1, duration: 1 }}
            />
          </div>
        </div>
      </motion.div>

      {/* Improvement Trend */}
      {insights.improvementRate !== 0 && (
        <motion.div
          className={`${insights.improvementRate > 0 ? 'bg-green-500/10 border-green-500/20' : 'bg-red-500/10 border-red-500/20'} backdrop-blur-sm rounded-xl p-6 border`}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.9 }}
        >
          <h4 className={`text-lg font-medium ${insights.improvementRate > 0 ? 'text-green-400' : 'text-red-400'} mb-3 flex items-center`}>
            <span className={`w-6 h-6 ${insights.improvementRate > 0 ? 'bg-green-500' : 'bg-red-500'} rounded-full flex items-center justify-center mr-3`}>
              {insights.improvementRate > 0 ? '📈' : '📉'}
            </span>
            Improvement Trend
          </h4>
          <p className="text-gray-300">
            {insights.improvementRate > 0 
              ? `You're improving at a rate of ${insights.improvementRate}% per test. Keep up the excellent work!`
              : `Your scores show some fluctuation. Focus on consistent practice to stabilize your performance.`
            }
          </p>
        </motion.div>
      )}
    </div>
  )
} 