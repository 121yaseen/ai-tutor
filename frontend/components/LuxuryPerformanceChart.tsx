'use client'

import { useEffect, useState } from 'react'
import { createClient } from '@/lib/supabase/client'
import { motion } from 'framer-motion'

interface TestResult {
  band_score: number
  test_date: string
  test_number: number
  detailed_scores?: {
    fluency: number
    vocabulary: number
    grammar: number
    pronunciation: number
  }
}

interface ChartData {
  date: string
  score: number
  formattedDate: string
  testNumber: number
  detailedScores?: {
    fluency: number
    vocabulary: number
    grammar: number
    pronunciation: number
  }
}

export default function LuxuryPerformanceChart({ 
  userEmail, 
  targetScore 
}: { 
  userEmail: string
  targetScore: number 
}) {
  const [chartData, setChartData] = useState<ChartData[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedPoint, setSelectedPoint] = useState<number | null>(null)

  useEffect(() => {
    async function fetchChartData() {
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
        
        const processedData = history
          .filter(test => test.band_score > 0)
          .map(test => ({
            date: test.test_date,
            score: test.band_score,
            testNumber: test.test_number,
            formattedDate: new Date(test.test_date).toLocaleDateString('en-US', {
              month: 'short',
              day: 'numeric'
            }),
            detailedScores: test.detailed_scores
          }))
          .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime())

        setChartData(processedData)
      } catch (error) {
        console.error('Error fetching chart data:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchChartData()
  }, [userEmail])

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div className="h-8 bg-gray-600 rounded w-1/3 animate-pulse"></div>
          <div className="h-6 bg-gray-600 rounded w-1/4 animate-pulse"></div>
        </div>
        <div className="h-80 bg-gray-700/50 rounded-2xl animate-pulse"></div>
      </div>
    )
  }

  if (chartData.length === 0) {
    return (
      <div className="text-center py-16">
        <div className="w-24 h-24 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center mx-auto mb-6">
          <span className="text-3xl">📈</span>
        </div>
        <h3 className="text-2xl font-light text-white mb-3">Ready to Start Your Journey?</h3>
        <p className="text-gray-400 max-w-md mx-auto">
          Your performance data will appear here after you complete your first practice session.
        </p>
      </div>
    )
  }

  // Chart dimensions
  const chartWidth = 800
  const chartHeight = 400
  const padding = 80

  // Data processing
  const minScore = Math.max(0, Math.min(...chartData.map(d => d.score)) - 1)
  const maxScore = Math.min(9, Math.max(targetScore + 1, Math.max(...chartData.map(d => d.score)) + 1))
  const scoreRange = maxScore - minScore

  // Create paths
  const mainPath = chartData.map((point, index) => {
    const x = padding + (index / (chartData.length - 1)) * (chartWidth - 2 * padding)
    const y = chartHeight - padding - ((point.score - minScore) / scoreRange) * (chartHeight - 2 * padding)
    return `${index === 0 ? 'M' : 'L'} ${x} ${y}`
  }).join(' ')

  // Create area path for gradient fill
  const areaPath = chartData.length > 0 ? `${mainPath} L ${padding + (chartData.length - 1) / (chartData.length - 1) * (chartWidth - 2 * padding)} ${chartHeight - padding} L ${padding} ${chartHeight - padding} Z` : ''

  // Target line
  const targetY = chartHeight - padding - ((targetScore - minScore) / scoreRange) * (chartHeight - 2 * padding)

  // Grid lines
  const gridLines = []
  for (let i = Math.ceil(minScore); i <= Math.floor(maxScore); i += 0.5) {
    const y = chartHeight - padding - ((i - minScore) / scoreRange) * (chartHeight - 2 * padding)
    gridLines.push({ score: i, y })
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h3 className="text-3xl font-light text-white mb-2">Performance Analytics</h3>
          <p className="text-gray-400">Your journey toward excellence</p>
        </div>
        <div className="flex items-center space-x-6 text-sm">
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-gradient-to-r from-blue-400 to-purple-500 rounded-full"></div>
            <span className="text-gray-300">Your Progress</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-amber-400 rounded-full"></div>
            <span className="text-gray-300">Target: {targetScore}</span>
          </div>
        </div>
      </div>

      {/* Chart Container */}
      <div className="relative bg-gradient-to-br from-gray-800/50 to-gray-900/50 rounded-2xl p-6 backdrop-blur-sm border border-white/5">
        <svg
          viewBox={`0 0 ${chartWidth} ${chartHeight}`}
          className="w-full h-80 overflow-visible"
          preserveAspectRatio="xMidYMid meet"
        >
          {/* Grid */}
          {gridLines.map((line, index) => (
            <g key={index}>
              <line
                x1={padding}
                y1={line.y}
                x2={chartWidth - padding}
                y2={line.y}
                stroke="rgba(156, 163, 175, 0.1)"
                strokeWidth="1"
                strokeDasharray={line.score % 1 === 0 ? "none" : "3,3"}
              />
              <text
                x={padding - 15}
                y={line.y + 4}
                fill="rgba(156, 163, 175, 0.6)"
                fontSize="12"
                textAnchor="end"
                className="font-light"
              >
                {line.score}
              </text>
            </g>
          ))}

          {/* Target Line */}
          <motion.line
            x1={padding}
            y1={targetY}
            x2={chartWidth - padding}
            y2={targetY}
            stroke="url(#targetGradient)"
            strokeWidth="2"
            strokeDasharray="8,4"
            initial={{ pathLength: 0 }}
            animate={{ pathLength: 1 }}
            transition={{ duration: 1.5, delay: 0.5 }}
          />

          {/* Area Fill */}
          <defs>
            <linearGradient id="areaGradient" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor="rgba(59, 130, 246, 0.3)" />
              <stop offset="100%" stopColor="rgba(147, 51, 234, 0.1)" />
            </linearGradient>
            <linearGradient id="lineGradient" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#3B82F6" />
              <stop offset="100%" stopColor="#9333EA" />
            </linearGradient>
            <linearGradient id="targetGradient" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#F59E0B" />
              <stop offset="100%" stopColor="#EF4444" />
            </linearGradient>
          </defs>

          {/* Area */}
          <motion.path
            d={areaPath}
            fill="url(#areaGradient)"
            initial={{ pathLength: 0, opacity: 0 }}
            animate={{ pathLength: 1, opacity: 1 }}
            transition={{ duration: 2, delay: 0.8 }}
          />

          {/* Main Line */}
          <motion.path
            d={mainPath}
            fill="none"
            stroke="url(#lineGradient)"
            strokeWidth="3"
            strokeLinecap="round"
            strokeLinejoin="round"
            initial={{ pathLength: 0 }}
            animate={{ pathLength: 1 }}
            transition={{ duration: 2, delay: 0.3 }}
          />

          {/* Data Points */}
          {chartData.map((point, index) => {
            const x = padding + (index / (chartData.length - 1)) * (chartWidth - 2 * padding)
            const y = chartHeight - padding - ((point.score - minScore) / scoreRange) * (chartHeight - 2 * padding)
            
            return (
              <g key={index}>
                <motion.circle
                  cx={x}
                  cy={y}
                  r={selectedPoint === index ? "8" : "6"}
                  fill="url(#lineGradient)"
                  stroke="white"
                  strokeWidth="2"
                  className="cursor-pointer"
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ delay: 0.5 + index * 0.1, type: "spring" }}
                  whileHover={{ scale: 1.3 }}
                  onClick={() => setSelectedPoint(selectedPoint === index ? null : index)}
                />
                
                {/* Date Label */}
                <text
                  x={x}
                  y={chartHeight - padding + 25}
                  fill="rgba(156, 163, 175, 0.8)"
                  fontSize="12"
                  textAnchor="middle"
                  className="font-light"
                >
                  {point.formattedDate}
                </text>

                {/* Score Tooltip */}
                {selectedPoint === index && (
                  <motion.g
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.3 }}
                  >
                    <rect
                      x={x - 40}
                      y={y - 60}
                      width="80"
                      height="45"
                      fill="rgba(0, 0, 0, 0.9)"
                      rx="8"
                      stroke="rgba(255, 255, 255, 0.2)"
                    />
                    <text
                      x={x}
                      y={y - 35}
                      fill="white"
                      fontSize="14"
                      textAnchor="middle"
                      className="font-semibold"
                    >
                      {point.score}
                    </text>
                    <text
                      x={x}
                      y={y - 20}
                      fill="rgba(156, 163, 175, 0.8)"
                      fontSize="10"
                      textAnchor="middle"
                    >
                      Test #{point.testNumber}
                    </text>
                  </motion.g>
                )}
              </g>
            )
          })}
        </svg>

        {/* Detailed Breakdown */}
        {selectedPoint !== null && chartData[selectedPoint]?.detailedScores && (
          <motion.div
            className="mt-6 p-4 bg-black/30 rounded-xl border border-white/10"
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            transition={{ duration: 0.3 }}
          >
            <h4 className="text-white font-medium mb-3">Test #{chartData[selectedPoint].testNumber} Breakdown</h4>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {Object.entries(chartData[selectedPoint].detailedScores!).map(([skill, score]) => (
                <div key={skill} className="text-center">
                  <div className="text-2xl font-bold text-white">{score}</div>
                  <div className="text-sm text-gray-400 capitalize">{skill}</div>
                </div>
              ))}
            </div>
          </motion.div>
        )}
      </div>
    </div>
  )
} 