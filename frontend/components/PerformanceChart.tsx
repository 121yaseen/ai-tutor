'use client'

import { useEffect, useState } from 'react'
import { createClient } from '@/lib/supabase/client'

interface TestResult {
  band_score: number
  test_date: string
  test_number: number
}

interface ChartData {
  date: string
  score: number
  formattedDate: string
}

export default function PerformanceChart({ 
  userEmail, 
  targetScore 
}: { 
  userEmail: string
  targetScore: number 
}) {
  const [chartData, setChartData] = useState<ChartData[]>([])
  const [loading, setLoading] = useState(true)

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
            formattedDate: new Date(test.test_date).toLocaleDateString('en-US', {
              month: 'short',
              day: 'numeric'
            })
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
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <h3 className="text-xl font-semibold text-white mb-6">Performance Over Time</h3>
        <div className="h-64 bg-gray-700 rounded animate-pulse"></div>
      </div>
    )
  }

  if (chartData.length === 0) {
    return (
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <h3 className="text-xl font-semibold text-white mb-6">Performance Over Time</h3>
        <div className="h-64 flex items-center justify-center text-gray-400">
          No test data available
        </div>
      </div>
    )
  }

  // Chart dimensions - responsive
  const chartWidth = 800
  const chartHeight = 400
  const padding = 80

  // Data processing for chart
  const minScore = Math.min(4, Math.min(...chartData.map(d => d.score)) - 0.5)
  const maxScore = Math.max(9, targetScore + 0.5)
  const scoreRange = maxScore - minScore

  // Create SVG path for the line
  const pathData = chartData.map((point, index) => {
    const x = padding + (index / (chartData.length - 1)) * (chartWidth - 2 * padding)
    const y = chartHeight - padding - ((point.score - minScore) / scoreRange) * (chartHeight - 2 * padding)
    return `${index === 0 ? 'M' : 'L'} ${x} ${y}`
  }).join(' ')

  // Target line Y position
  const targetY = chartHeight - padding - ((targetScore - minScore) / scoreRange) * (chartHeight - 2 * padding)

  // Grid lines
  const gridLines = []
  for (let i = Math.ceil(minScore); i <= Math.floor(maxScore); i++) {
    const y = chartHeight - padding - ((i - minScore) / scoreRange) * (chartHeight - 2 * padding)
    gridLines.push(
      <g key={i}>
        <line
          x1={padding}
          y1={y}
          x2={chartWidth - padding}
          y2={y}
          stroke="#374151"
          strokeWidth="1"
          strokeDasharray="3,3"
        />
        <text
          x={padding - 10}
          y={y + 4}
          fill="#9CA3AF"
          fontSize="14"
          textAnchor="end"
        >
          {i}
        </text>
      </g>
    )
  }

  return (
    <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-6 gap-4">
        <h3 className="text-xl font-semibold text-white">Performance Over Time</h3>
        <div className="flex items-center text-sm text-gray-400 flex-wrap gap-4">
          <div className="flex items-center">
            <div className="w-3 h-3 bg-blue-500 rounded-full mr-2"></div>
            Band Score
          </div>
          <div className="flex items-center">
            <div className="w-3 h-3 bg-purple-500 rounded-full mr-2"></div>
            Target: {targetScore}
          </div>
        </div>
      </div>

      <div className="w-full">
        <svg
          viewBox={`0 0 ${chartWidth} ${chartHeight}`}
          className="w-full h-72 sm:h-80 md:h-96"
          preserveAspectRatio="xMidYMid meet"
        >
          {/* Grid lines */}
          {gridLines}

          {/* Target line */}
          <line
            x1={padding}
            y1={targetY}
            x2={chartWidth - padding}
            y2={targetY}
            stroke="#8B5CF6"
            strokeWidth="2"
            strokeDasharray="5,5"
          />

          {/* Chart line */}
          <path
            d={pathData}
            fill="none"
            stroke="#3B82F6"
            strokeWidth="3"
            strokeLinecap="round"
            strokeLinejoin="round"
          />

          {/* Data points */}
          {chartData.map((point, index) => {
            const x = padding + (index / (chartData.length - 1)) * (chartWidth - 2 * padding)
            const y = chartHeight - padding - ((point.score - minScore) / scoreRange) * (chartHeight - 2 * padding)
            
            return (
              <g key={index}>
                <circle
                  cx={x}
                  cy={y}
                  r="6"
                  fill="#3B82F6"
                  stroke="#1E40AF"
                  strokeWidth="2"
                />
                {/* Date labels */}
                <text
                  x={x}
                  y={chartHeight - padding + 25}
                  fill="#9CA3AF"
                  fontSize="12"
                  textAnchor="middle"
                >
                  {point.formattedDate}
                </text>
              </g>
            )
          })}

          {/* Y-axis */}
          <line
            x1={padding}
            y1={padding}
            x2={padding}
            y2={chartHeight - padding}
            stroke="#4B5563"
            strokeWidth="2"
          />

          {/* X-axis */}
          <line
            x1={padding}
            y1={chartHeight - padding}
            x2={chartWidth - padding}
            y2={chartHeight - padding}
            stroke="#4B5563"
            strokeWidth="2"
          />
        </svg>
      </div>
    </div>
  )
} 