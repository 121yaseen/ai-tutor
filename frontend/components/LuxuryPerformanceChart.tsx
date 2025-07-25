'use client'

import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import type { Profile } from '@prisma/client'
import { JsonValue } from '@prisma/client/runtime/library'

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
  profile,
  history,
}: {
  profile: Profile | null
  history: JsonValue[] | null
}) {
  const [chartData, setChartData] = useState<ChartData[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedPoint, setSelectedPoint] = useState<number | null>(null)

  useEffect(() => {
    function processChartData() {
      if (!history || history.length === 0) {
        setLoading(false)
        return
      }

      const testResults = history as unknown as TestResult[]
      const processedData = testResults
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
      setLoading(false)
    }

    processChartData()
  }, [history])

  if (loading) {
    return (
      <div className="space-y-4 sm:space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div className="h-6 sm:h-8 bg-gray-600 rounded w-1/2 sm:w-1/3 animate-pulse"></div>
          <div className="h-4 sm:h-6 bg-gray-600 rounded w-1/3 sm:w-1/4 animate-pulse"></div>
        </div>
        <div className="h-64 sm:h-80 lg:h-96 bg-gray-700/50 rounded-xl sm:rounded-2xl animate-pulse"></div>
      </div>
    )
  }

  if (chartData.length === 0) {
    return (
      <div className="text-center py-12 sm:py-16">
        <div className="w-20 h-20 sm:w-24 sm:h-24 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center mx-auto mb-4 sm:mb-6">
          <span className="text-2xl sm:text-3xl">📈</span>
        </div>
        <h3 className="text-xl sm:text-2xl font-light text-white mb-3">Ready to Start Your Journey?</h3>
        <p className="text-gray-400 max-w-md mx-auto text-sm sm:text-base px-4">
          Your performance data will appear here after you complete your first practice session.
        </p>
      </div>
    )
  }

  const targetScore = profile?.target_band_score || 7.5

  // Chart dimensions - responsive based on screen size
  const isMobile = typeof window !== 'undefined' && window.innerWidth < 640
  const isTablet = typeof window !== 'undefined' && window.innerWidth < 1024
  
  const chartWidth = isMobile ? 600 : isTablet ? 800 : 1200
  const chartHeight = isMobile ? 300 : isTablet ? 400 : 500
  const padding = isMobile ? 50 : isTablet ? 60 : 80

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
    <div className="space-y-6 sm:space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h3 className="text-2xl sm:text-3xl font-light text-white mb-2">Performance Analytics</h3>
          <p className="text-gray-400 text-sm sm:text-base">Your journey toward excellence</p>
        </div>
        <div className="flex flex-col sm:flex-row sm:items-center sm:space-x-6 gap-3 sm:gap-0 text-sm">
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-gradient-to-r from-blue-400 to-purple-500 rounded-full"></div>
            <span className="text-gray-300">Your Progress</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-6 h-0.5 bg-amber-400 rounded-full" style={{backgroundImage: 'repeating-linear-gradient(to right, #F59E0B 0, #F59E0B 12px, transparent 12px, transparent 20px)'}}></div>
            <span className="text-gray-300">Target: {targetScore}</span>
          </div>
        </div>
      </div>

      {/* Chart Container */}
      <div className="relative bg-gradient-to-br from-gray-800/50 to-gray-900/50 rounded-xl sm:rounded-2xl p-4 sm:p-6 backdrop-blur-sm border border-white/5">
        <svg
          viewBox={`0 0 ${chartWidth} ${chartHeight}`}
          className="w-full h-64 sm:h-80 lg:h-96 overflow-visible touch-manipulation"
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
                x={padding - (isMobile ? 10 : 15)}
                y={line.y + (isMobile ? 3 : 4)}
                fill="rgba(156, 163, 175, 0.6)"
                fontSize={isMobile ? "10" : "12"}
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
            stroke="#F59E0B"
            strokeWidth={isMobile ? "2" : "3"}
            strokeDasharray="8,4"
            initial={{ pathLength: 0 }}
            animate={{ pathLength: 1 }}
            transition={{ duration: 1.5, delay: 0.5 }}
          />
          
          {/* Target Label */}
          <text
            x={chartWidth - padding + (isMobile ? 5 : 10)}
            y={targetY + (isMobile ? 3 : 4)}
            fill="#F59E0B"
            fontSize={isMobile ? "10" : "12"}
            className="font-medium"
          >
            Target: {targetScore}
          </text>

          {/* Gradient Fill */}
          <defs>
            <linearGradient id="areaGradient" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor="rgba(59, 130, 246, 0.3)" />
              <stop offset="100%" stopColor="rgba(147, 51, 234, 0.1)" />
            </linearGradient>
          </defs>
          
          {areaPath && (
            <motion.path
              d={areaPath}
              fill="url(#areaGradient)"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 1, delay: 0.8 }}
            />
          )}

          {/* Main Line */}
          <motion.path
            d={mainPath}
            stroke="url(#lineGradient)"
            strokeWidth={isMobile ? "3" : "4"}
            fill="none"
            strokeLinecap="round"
            strokeLinejoin="round"
            initial={{ pathLength: 0 }}
            animate={{ pathLength: 1 }}
            transition={{ duration: 2, delay: 0.3, ease: "easeInOut" }}
          />

          <defs>
            <linearGradient id="lineGradient" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#3B82F6" />
              <stop offset="100%" stopColor="#9333EA" />
            </linearGradient>
          </defs>

          {/* Data Points */}
          {chartData.map((point, index) => {
            const x = padding + (index / (chartData.length - 1)) * (chartWidth - 2 * padding)
            const y = chartHeight - padding - ((point.score - minScore) / scoreRange) * (chartHeight - 2 * padding)
            
            return (
              <g key={index}>
                <motion.circle
                  cx={x}
                  cy={y}
                  r={isMobile ? "6" : "8"}
                  fill="white"
                  stroke="url(#lineGradient)"
                  strokeWidth={isMobile ? "2" : "3"}
                  className="cursor-pointer touch-manipulation"
                  initial={{ scale: 0, opacity: 0 }}
                  animate={{ scale: 1, opacity: 1 }}
                  transition={{ delay: 0.5 + (index * 0.1), duration: 0.3 }}
                  whileHover={{ scale: 1.3 }}
                  whileTap={{ scale: 1.1 }}
                  onClick={() => setSelectedPoint(selectedPoint === index ? null : index)}
                />
                
                {/* Date Label */}
                <text
                  x={x}
                  y={chartHeight - padding + (isMobile ? 15 : 20)}
                  fill="rgba(156, 163, 175, 0.8)"
                  fontSize={isMobile ? "9" : "11"}
                  textAnchor="middle"
                  className="font-light"
                >
                  {point.formattedDate}
                </text>

                {/* Tooltip */}
                {selectedPoint === index && (
                  <motion.g
                    initial={{ opacity: 0, scale: 0.8 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ duration: 0.2 }}
                  >
                    <rect
                      x={x - (isMobile ? 25 : 35)}
                      y={y - (isMobile ? 35 : 45)}
                      width={isMobile ? 50 : 70}
                      height={isMobile ? 25 : 30}
                      fill="rgba(0, 0, 0, 0.8)"
                      rx="4"
                    />
                    <text
                      x={x}
                      y={y - (isMobile ? 25 : 32)}
                      fill="white"
                      fontSize={isMobile ? "10" : "12"}
                      textAnchor="middle"
                      className="font-medium"
                    >
                      Score: {point.score}
                    </text>
                    <text
                      x={x}
                      y={y - (isMobile ? 15 : 20)}
                      fill="#F59E0B"
                      fontSize={isMobile ? "8" : "10"}
                      textAnchor="middle"
                      className="font-light"
                    >
                      Test #{point.testNumber}
                    </text>
                  </motion.g>
                )}
              </g>
            )
          })}
        </svg>
      </div>

      {/* Mobile-friendly detailed scores */}
      {selectedPoint !== null && chartData[selectedPoint]?.detailedScores && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white/5 backdrop-blur-xl rounded-xl p-4 border border-white/10"
        >
          <h4 className="text-white font-medium mb-3 text-sm sm:text-base">
            Test #{chartData[selectedPoint].testNumber} - Detailed Scores
          </h4>
          <div className="grid grid-cols-2 gap-3 sm:gap-4">
            {Object.entries(chartData[selectedPoint].detailedScores!).map(([skill, score]) => (
              <div key={skill} className="text-center">
                <div className="text-xs sm:text-sm text-gray-400 capitalize mb-1">{skill}</div>
                <div className="text-lg sm:text-xl font-bold text-white">{score}</div>
              </div>
            ))}
          </div>
        </motion.div>
      )}
    </div>
  )
} 