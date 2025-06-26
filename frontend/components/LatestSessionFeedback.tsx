'use client'

import { useEffect, useState } from 'react'
import { createClient } from '@/lib/supabase/client'

interface TestResult {
  band_score: number
  test_date: string
  feedback: {
    fluency?: string
    vocabulary?: string
    grammar?: string
    pronunciation?: string
  }
  strengths: string[]
  improvements: string[]
  detailed_scores: {
    fluency: number
    vocabulary: number
    grammar: number
    pronunciation: number
  }
}

export default function LatestSessionFeedback({ userEmail }: { userEmail: string }) {
  const [latestTest, setLatestTest] = useState<TestResult | null>(null)
  const [loading, setLoading] = useState(true)
  const [expandedSection, setExpandedSection] = useState<string | null>(null)

  useEffect(() => {
    async function fetchLatestTest() {
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

        // Get the most recent test
        const latest = history[history.length - 1]
        setLatestTest(latest)
      } catch (error) {
        console.error('Error fetching latest test:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchLatestTest()
  }, [userEmail])

  if (loading) {
    return (
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <h3 className="text-xl font-semibold text-white mb-6">Latest Session Feedback</h3>
        <div className="space-y-4">
          <div className="h-4 bg-gray-600 rounded w-3/4 animate-pulse"></div>
          <div className="h-20 bg-gray-600 rounded animate-pulse"></div>
          <div className="h-20 bg-gray-600 rounded animate-pulse"></div>
        </div>
      </div>
    )
  }

  if (!latestTest) {
    return (
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <h3 className="text-xl font-semibold text-white mb-6">Latest Session Feedback</h3>
        <p className="text-gray-400">No test data available</p>
      </div>
    )
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    })
  }

  const criteriaData = [
    {
      name: 'Fluency & Coherence',
      score: latestTest.detailed_scores.fluency,
      feedback: latestTest.feedback.fluency || 'No feedback available',
      icon: '🗣️'
    },
    {
      name: 'Lexical Resource',
      score: latestTest.detailed_scores.vocabulary,
      feedback: latestTest.feedback.vocabulary || 'No feedback available',
      icon: '📚'
    },
    {
      name: 'Grammatical Range',
      score: latestTest.detailed_scores.grammar,
      feedback: latestTest.feedback.grammar || 'No feedback available',
      icon: '📝'
    },
    {
      name: 'Pronunciation',
      score: latestTest.detailed_scores.pronunciation,
      feedback: latestTest.feedback.pronunciation || 'No feedback available',
      icon: '🎤'
    }
  ]

  return (
    <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
      <div className="flex items-center mb-6">
        <div className="w-3 h-3 bg-blue-500 rounded-full mr-3"></div>
        <div>
          <h3 className="text-xl font-semibold text-white">Latest Session Feedback</h3>
          <p className="text-gray-400 text-sm">{formatDate(latestTest.test_date)}</p>
        </div>
      </div>

      {/* Key Areas for Improvement */}
      <div className="mb-6">
        <h4 className="text-orange-400 font-medium mb-3 flex items-center">
          <span className="mr-2">🎯</span>
          Key Areas for Improvement
        </h4>
        <div className="space-y-3">
          {latestTest.improvements.map((improvement, index) => (
            <div key={index} className="flex items-start">
              <div className="w-2 h-2 bg-orange-400 rounded-full mt-2 mr-3 flex-shrink-0"></div>
              <p className="text-gray-300 text-sm leading-relaxed">{improvement}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Strengths */}
      <div className="mb-6">
        <h4 className="text-green-400 font-medium mb-3 flex items-center">
          <span className="mr-2">✨</span>
          Strengths
        </h4>
        <div className="space-y-2">
          {latestTest.strengths.map((strength, index) => (
            <div key={index} className="flex items-start">
              <div className="w-2 h-2 bg-green-400 rounded-full mt-2 mr-3 flex-shrink-0"></div>
              <p className="text-gray-300 text-sm">{strength}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Detailed Analysis */}
      <div>
        <h4 className="text-purple-400 font-medium mb-3 flex items-center">
          <span className="mr-2">📊</span>
          Detailed Analysis
        </h4>
        <div className="space-y-2">
          {criteriaData.map((criteria, index) => (
            <div key={index} className="border border-gray-600 rounded-lg">
              <button
                onClick={() => setExpandedSection(
                  expandedSection === criteria.name ? null : criteria.name
                )}
                className="w-full px-4 py-3 flex items-center justify-between text-left hover:bg-gray-700/50 transition-colors rounded-lg"
              >
                <div className="flex items-center">
                  <span className="mr-3">{criteria.icon}</span>
                  <span className="text-white font-medium">{criteria.name}</span>
                  <span className="ml-3 text-sm bg-blue-600 text-white px-2 py-1 rounded">
                    {criteria.score}
                  </span>
                </div>
                <svg
                  className={`w-5 h-5 text-gray-400 transition-transform ${
                    expandedSection === criteria.name ? 'rotate-180' : ''
                  }`}
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </button>
              {expandedSection === criteria.name && (
                <div className="px-4 pb-4 pt-2">
                  <p className="text-gray-300 text-sm leading-relaxed border-t border-gray-600 pt-3">
                    {criteria.feedback}
                  </p>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  )
} 