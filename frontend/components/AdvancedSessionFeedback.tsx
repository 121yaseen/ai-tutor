'use client'

import { useEffect, useState } from 'react'
import { createClient } from '@/lib/supabase/client'
import { motion } from 'framer-motion'

interface TestResult {
  test_date: string
  test_number: number
  band_score: number
  feedback?: {
    fluency?: string
    vocabulary?: string
    grammar?: string
    pronunciation?: string
  }
  strengths?: string[]
  improvements?: string[]
  detailed_scores?: {
    fluency: number
    vocabulary: number
    grammar: number
    pronunciation: number
  }
}

export default function AdvancedSessionFeedback({ userEmail }: { userEmail: string }) {
  const [latestSession, setLatestSession] = useState<TestResult | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function fetchLatestSession() {
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
        const latest = history[history.length - 1]
        setLatestSession(latest)
      } catch (error) {
        console.error('Error fetching latest session:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchLatestSession()
  }, [userEmail])

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="h-8 bg-gray-600 rounded w-1/2 animate-pulse"></div>
        <div className="space-y-3">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="h-4 bg-gray-600 rounded animate-pulse"></div>
          ))}
        </div>
      </div>
    )
  }

  if (!latestSession) {
    return (
      <div className="text-center py-12">
        <div className="w-16 h-16 bg-gradient-to-br from-amber-500 to-orange-500 rounded-full flex items-center justify-center mx-auto mb-4">
          <span className="text-2xl">💭</span>
        </div>
        <h3 className="text-xl font-light text-white mb-2">No Feedback Yet</h3>
        <p className="text-gray-400">Complete a practice session to see detailed feedback here.</p>
      </div>
    )
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    })
  }

  const skillAreas = [
    {
      name: 'Fluency',
      key: 'fluency',
      icon: '🗣️',
      color: 'from-blue-500 to-indigo-600',
    },
    {
      name: 'Vocabulary',
      key: 'vocabulary',
      icon: '📚',
      color: 'from-purple-500 to-pink-600',
    },
    {
      name: 'Grammar',
      key: 'grammar',
      icon: '📝',
      color: 'from-green-500 to-emerald-600',
    },
    {
      name: 'Pronunciation',
      key: 'pronunciation',
      icon: '🎵',
      color: 'from-orange-500 to-red-600',
    },
  ]

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-2xl font-light text-white mb-2 flex items-center">
            <span className="w-8 h-8 bg-gradient-to-r from-amber-400 to-orange-500 rounded-full flex items-center justify-center mr-3">
              💡
            </span>
            Latest Session Insights
          </h3>
          <p className="text-gray-400">
            Test #{latestSession.test_number} • {formatDate(latestSession.test_date)}
          </p>
        </div>
        <div className="text-right">
          <div className="text-3xl font-bold text-white">{latestSession.band_score}</div>
          <div className="text-sm text-gray-400">Overall Score</div>
        </div>
      </div>

      {/* Skill Breakdown */}
      {latestSession.detailed_scores && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {skillAreas.map((skill, index) => {
            const score = latestSession.detailed_scores![skill.key as keyof typeof latestSession.detailed_scores]
            return (
              <motion.div
                key={skill.key}
                className={`bg-gradient-to-br ${skill.color} bg-opacity-20 backdrop-blur-sm rounded-xl p-4 border border-white/10`}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                whileHover={{ scale: 1.02 }}
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="text-2xl">{skill.icon}</span>
                  <span className="text-2xl font-bold text-white">{score}</span>
                </div>
                <h4 className="text-white font-medium">{skill.name}</h4>
                <div className="w-full bg-gray-700/50 rounded-full h-1.5 mt-2">
                  <motion.div
                    className={`h-full bg-gradient-to-r ${skill.color} rounded-full`}
                    initial={{ width: 0 }}
                    animate={{ width: `${(score / 9) * 100}%` }}
                    transition={{ delay: (index * 0.1) + 0.3, duration: 0.8 }}
                  />
                </div>
              </motion.div>
            )
          })}
        </div>
      )}

      {/* Strengths Section */}
      {latestSession.strengths && latestSession.strengths.length > 0 && (
        <motion.div
          className="space-y-4"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
        >
          <h4 className="text-lg font-medium text-green-400 flex items-center">
            <span className="w-6 h-6 bg-green-500 rounded-full flex items-center justify-center mr-3">
              ✨
            </span>
            Strengths
          </h4>
          <div className="space-y-2">
            {latestSession.strengths.map((strength, index) => (
              <motion.div
                key={index}
                className="flex items-start space-x-3 p-3 bg-green-500/10 rounded-xl border border-green-500/20"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.6 + index * 0.1 }}
              >
                <span className="w-2 h-2 bg-green-400 rounded-full mt-2 flex-shrink-0"></span>
                <p className="text-gray-300 text-sm leading-relaxed">{strength}</p>
              </motion.div>
            ))}
          </div>
        </motion.div>
      )}

      {/* Improvements Section */}
      {latestSession.improvements && latestSession.improvements.length > 0 && (
        <motion.div
          className="space-y-4"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.7 }}
        >
          <h4 className="text-lg font-medium text-amber-400 flex items-center">
            <span className="w-6 h-6 bg-amber-500 rounded-full flex items-center justify-center mr-3">
              🎯
            </span>
            Areas for Growth
          </h4>
          <div className="space-y-2">
            {latestSession.improvements.map((improvement, index) => (
              <motion.div
                key={index}
                className="flex items-start space-x-3 p-3 bg-amber-500/10 rounded-xl border border-amber-500/20"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.8 + index * 0.1 }}
              >
                <span className="w-2 h-2 bg-amber-400 rounded-full mt-2 flex-shrink-0"></span>
                <p className="text-gray-300 text-sm leading-relaxed">{improvement}</p>
              </motion.div>
            ))}
          </div>
        </motion.div>
      )}

      {/* Detailed Feedback */}
      {latestSession.feedback && (
        <motion.div
          className="space-y-4"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1 }}
        >
          <h4 className="text-lg font-medium text-blue-400 flex items-center">
            <span className="w-6 h-6 bg-blue-500 rounded-full flex items-center justify-center mr-3">
              📋
            </span>
            Detailed Analysis
          </h4>
          <div className="grid gap-4">
            {Object.entries(latestSession.feedback).map(([skill, feedback], index) => (
              <motion.div
                key={skill}
                className="p-4 bg-blue-500/10 rounded-xl border border-blue-500/20"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 1.1 + index * 0.1 }}
              >
                <h5 className="text-white font-medium capitalize mb-2">{skill}</h5>
                <p className="text-gray-300 text-sm leading-relaxed">{feedback}</p>
              </motion.div>
            ))}
          </div>
        </motion.div>
      )}
    </div>
  )
} 