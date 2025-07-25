'use client'

import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import type { Profile } from '@prisma/client'
import { JsonValue } from '@prisma/client/runtime/library'

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

interface StatsData {
  latestScore: number
  bestScore: number
  averageScore: number
  totalTests: number
  improvement: number
  weakestArea: string
}

export default function PremiumStatsCards({ 
  profile,
  history
}: { 
  profile: Profile | null,
  history: JsonValue[] | null
}) {
  const [stats, setStats] = useState<StatsData>({
    latestScore: 0,
    bestScore: 0,
    averageScore: 0,
    totalTests: 0,
    improvement: 0,
    weakestArea: 'grammar'
  })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    function calculateStats() {
      if (!history || history.length === 0) {
        setLoading(false)
        return
      }

      const testResults = history as unknown as TestResult[]
      const scores = testResults.map(test => test.band_score).filter(score => score > 0)
      
      const latestScore = scores[scores.length - 1] || 0
      const bestScore = Math.max(...scores)
      const averageScore = scores.reduce((sum, score) => sum + score, 0) / scores.length
      const totalTests = testResults.length

      // Calculate improvement
      const improvement = scores.length > 1 
        ? ((latestScore - scores[0]) / scores[0]) * 100 
        : 0

      // Find weakest area from latest test
      const latestTest = testResults[testResults.length - 1]
      let weakestArea = 'grammar'
      if (latestTest.detailed_scores) {
        const areas = latestTest.detailed_scores
        const minScore = Math.min(areas.fluency, areas.vocabulary, areas.grammar, areas.pronunciation)
        if (areas.fluency === minScore) weakestArea = 'fluency'
        else if (areas.vocabulary === minScore) weakestArea = 'vocabulary'
        else if (areas.pronunciation === minScore) weakestArea = 'pronunciation'
      }

      setStats({
        latestScore,
        bestScore,
        averageScore: Math.round(averageScore * 10) / 10,
        totalTests,
        improvement: Math.round(improvement * 10) / 10,
        weakestArea
      })
      setLoading(false)
    }

    calculateStats()
  }, [history])

  const targetScore = profile?.target_band_score || 7.5

  const statCards = [
    {
      title: 'Current Score',
      value: stats.latestScore.toString(),
      subtitle: `Target: ${targetScore}`,
      icon: '🎯',
      gradient: 'from-blue-500 to-purple-600',
      bgGradient: 'from-blue-500/20 to-purple-600/20',
      borderGradient: 'from-blue-400/50 to-purple-500/50',
      progress: (stats.latestScore / targetScore) * 100,
    },
    {
      title: 'Personal Best',
      value: stats.bestScore.toString(),
      subtitle: stats.improvement >= 0 ? `+${stats.improvement}% growth` : `${stats.improvement}% change`,
      icon: '🏆',
      gradient: 'from-amber-500 to-orange-500',
      bgGradient: 'from-amber-500/20 to-orange-500/20',
      borderGradient: 'from-amber-400/50 to-orange-400/50',
      progress: (stats.bestScore / 9) * 100,
    },
    {
      title: 'Average Score',
      value: stats.averageScore.toString(),
      subtitle: 'Consistency meter',
      icon: '📊',
      gradient: 'from-green-500 to-emerald-500',
      bgGradient: 'from-green-500/20 to-emerald-500/20',
      borderGradient: 'from-green-400/50 to-emerald-400/50',
      progress: (stats.averageScore / 9) * 100,
    },
    {
      title: 'Practice Sessions',
      value: stats.totalTests.toString(),
      subtitle: `Focus area: ${stats.weakestArea}`,
      icon: '📚',
      gradient: 'from-purple-500 to-pink-500',
      bgGradient: 'from-purple-500/20 to-pink-500/20',
      borderGradient: 'from-purple-400/50 to-pink-400/50',
      progress: Math.min((stats.totalTests / 10) * 100, 100),
    },
  ]

  if (loading) {
    return (
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
        {[...Array(4)].map((_, index) => (
          <motion.div 
            key={index} 
            className="bg-white/5 backdrop-blur-xl rounded-xl sm:rounded-2xl p-4 sm:p-6 border border-white/10 animate-pulse"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
          >
            <div className="h-4 sm:h-6 bg-gray-600 rounded w-3/4 mb-3 sm:mb-4"></div>
            <div className="h-8 sm:h-10 bg-gray-600 rounded w-1/2 mb-2"></div>
            <div className="h-3 sm:h-4 bg-gray-600 rounded w-2/3"></div>
          </motion.div>
        ))}
      </div>
    )
  }

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
      {statCards.map((card, index) => (
        <motion.div
          key={index}
          className={`relative group bg-gradient-to-br ${card.bgGradient} backdrop-blur-xl rounded-xl sm:rounded-2xl p-4 sm:p-6 border border-gradient-to-r ${card.borderGradient} shadow-xl sm:shadow-2xl hover:shadow-xl transition-all duration-500 touch-manipulation`}
          initial={{ opacity: 0, y: 30, scale: 0.9 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          transition={{ 
            delay: index * 0.1, 
            duration: 0.6,
            ease: [0.215, 0.61, 0.355, 1]
          }}
          whileHover={{ 
            scale: 1.02, 
            transition: { duration: 0.3 }
          }}
          whileTap={{ scale: 0.98 }}
        >
          {/* Glow Effect */}
          <div className={`absolute inset-0 bg-gradient-to-r ${card.gradient} opacity-0 group-hover:opacity-20 rounded-xl sm:rounded-2xl blur-xl transition-opacity duration-500`}></div>
          
          {/* Content */}
          <div className="relative z-10">
            {/* Header */}
            <div className="flex items-center justify-between mb-3 sm:mb-4">
              <div className="flex-1 min-w-0">
                <h3 className="text-gray-300 text-xs sm:text-sm font-medium uppercase tracking-wider truncate">{card.title}</h3>
                <p className="text-xs text-gray-500 mt-1 truncate">{card.subtitle}</p>
              </div>
              <div className={`w-10 h-10 sm:w-12 sm:h-12 bg-gradient-to-r ${card.gradient} rounded-xl sm:rounded-2xl flex items-center justify-center shadow-lg flex-shrink-0 ml-2`}>
                <span className="text-lg sm:text-2xl">{card.icon}</span>
              </div>
            </div>

            {/* Main Value */}
            <div className="mb-3 sm:mb-4">
              <motion.div 
                className="text-2xl sm:text-3xl lg:text-4xl font-bold text-white mb-2"
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ delay: (index * 0.1) + 0.3, duration: 0.5, type: "spring" }}
              >
                {card.value}
              </motion.div>
              
              {/* Progress Bar */}
              <div className="w-full bg-gray-700/50 rounded-full h-1.5 overflow-hidden">
                <motion.div
                  className={`h-full bg-gradient-to-r ${card.gradient} rounded-full`}
                  initial={{ width: 0 }}
                  animate={{ width: `${Math.min(card.progress, 100)}%` }}
                  transition={{ delay: (index * 0.1) + 0.5, duration: 0.8, ease: "easeOut" }}
                />
              </div>
            </div>

            {/* Micro-interaction indicator */}
            <div className="absolute top-2 right-2 w-2 h-2 bg-gradient-to-r from-green-400 to-blue-500 rounded-full opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
          </div>
        </motion.div>
      ))}
    </div>
  )
} 