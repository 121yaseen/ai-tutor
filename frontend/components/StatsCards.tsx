'use client'

import { useEffect, useState } from 'react'
import { createClient } from '@/lib/supabase/client'

interface TestResult {
  band_score: number
  test_date: string
}

interface StatsData {
  latestScore: number
  bestScore: number
  averageScore: number
  totalTests: number
}

export default function StatsCards({ userEmail }: { userEmail: string }) {
  const [stats, setStats] = useState<StatsData>({
    latestScore: 0,
    bestScore: 0,
    averageScore: 0,
    totalTests: 0,
  })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function fetchStats() {
      try {
        const supabase = createClient()
        const { data, error } = await supabase
          .from('students')
          .select('history')
          .eq('email', userEmail)
          .single()

        if (error || !data?.history) {
          setLoading(false)
          return
        }

        const history: TestResult[] = data.history
        
        if (history.length === 0) {
          setLoading(false)
          return
        }

        const scores = history.map(test => test.band_score).filter(score => score > 0)
        
        const latestScore = scores[scores.length - 1] || 0
        const bestScore = Math.max(...scores)
        const averageScore = scores.reduce((sum, score) => sum + score, 0) / scores.length
        const totalTests = history.length

        setStats({
          latestScore,
          bestScore,
          averageScore: Math.round(averageScore * 10) / 10,
          totalTests,
        })
      } catch (error) {
        console.error('Error fetching stats:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchStats()
  }, [userEmail])

  const statCards = [
    {
      title: 'Latest Score',
      value: stats.latestScore.toString(),
      icon: '📚',
      bgColor: 'bg-blue-900/50',
      borderColor: 'border-blue-700',
    },
    {
      title: 'Best Score',
      value: stats.bestScore.toString(),
      icon: '🏆',
      bgColor: 'bg-green-900/50',
      borderColor: 'border-green-700',
    },
    {
      title: 'Average Score',
      value: stats.averageScore.toString(),
      icon: '📊',
      bgColor: 'bg-purple-900/50',
      borderColor: 'border-purple-700',
    },
    {
      title: 'Total Tests',
      value: stats.totalTests.toString(),
      icon: '📝',
      bgColor: 'bg-orange-900/50',
      borderColor: 'border-orange-700',
    },
  ]

  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {[...Array(4)].map((_, index) => (
          <div key={index} className="bg-gray-800 rounded-lg p-6 border border-gray-700 animate-pulse">
            <div className="h-4 bg-gray-600 rounded w-3/4 mb-4"></div>
            <div className="h-8 bg-gray-600 rounded w-1/2"></div>
          </div>
        ))}
      </div>
    )
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {statCards.map((card, index) => (
        <div
          key={index}
          className={`${card.bgColor} rounded-lg p-6 border ${card.borderColor} backdrop-blur-sm`}
        >
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-gray-300 text-sm font-medium">{card.title}</h3>
            <span className="text-2xl">{card.icon}</span>
          </div>
          <div className="text-3xl font-bold text-white">{card.value}</div>
        </div>
      ))}
    </div>
  )
} 