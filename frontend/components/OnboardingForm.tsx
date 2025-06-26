
'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { createClient } from '@/lib/supabase/client'
import type { User } from '@supabase/supabase-js'

const countries = [
  { code: 'IN', name: 'India 🇮🇳' },
  { code: 'US', name: 'United States 🇺🇸' },
  { code: 'GB', name: 'United Kingdom 🇬🇧' },
  { code: 'CA', name: 'Canada 🇨🇦' },
  { code: 'AU', name: 'Australia 🇦🇺' },
  { code: 'NZ', name: 'New Zealand 🇳🇿' },
  { code: 'IE', name: 'Ireland 🇮🇪' },
  { code: 'DE', name: 'Germany 🇩🇪' },
  { code: 'FR', name: 'France 🇫🇷' },
  { code: 'CN', name: 'China 🇨🇳' },
  { code: 'JP', name: 'Japan 🇯🇵' },
  { code: 'KR', name: 'South Korea 🇰🇷' },
  { code: 'BR', name: 'Brazil 🇧🇷' },
  { code: 'MX', name: 'Mexico 🇲🇽' },
  { code: 'ZA', name: 'South Africa 🇿🇦' },
];

export default function OnboardingForm({ user }: { user: User }) {
  const supabase = createClient()
  const router = useRouter()

  const [firstName, setFirstName] = useState('')
  const [lastName, setLastName] = useState('')
  const [phoneNumber, setPhoneNumber] = useState('')
  const [previouslyAttempted, setPreviouslyAttempted] = useState(false)
  const [previousBandScore, setPreviousBandScore] = useState<number | null>(null)
  const [examDate, setExamDate] = useState('')
  const [targetBandScore, setTargetBandScore] = useState<number | null>(null)
  const [country, setCountry] = useState('IN') // Default to India's code
  const [nativeLanguage, setNativeLanguage] = useState('')
  const [isLoading, setIsLoading] = useState(false) // New loading state

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    setIsLoading(true) // Set loading to true on submit

    const { error } = await supabase.from('profiles').update({
      first_name: firstName,
      last_name: lastName,
      phone_number: phoneNumber,
      previously_attempted_exam: previouslyAttempted,
      previous_band_score: previousBandScore,
      exam_date: examDate,
      target_band_score: targetBandScore,
      country,
      native_language: nativeLanguage,
      onboarding_completed: true,
    }).eq('id', user.id)

    if (error) {
      console.error('Error updating profile:', error)
    } else {
      router.push('/')
      router.refresh()
    }
    setIsLoading(false) // Set loading to false after operation
  }

  return (
    <div className="max-w-2xl mx-auto">
      <h1 className="text-3xl font-bold mb-6">Welcome! Let's get you set up.</h1>
      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label htmlFor="firstName" className="block text-sm font-medium text-gray-700">First Name</label>
            <input type="text" id="firstName" value={firstName} onChange={(e) => setFirstName(e.target.value)} required className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-yellow-500 focus:border-yellow-500 sm:text-sm" />
          </div>
          <div>
            <label htmlFor="lastName" className="block text-sm font-medium text-gray-700">Last Name</label>
            <input type="text" id="lastName" value={lastName} onChange={(e) => setLastName(e.target.value)} required className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-yellow-500 focus:border-yellow-500 sm:text-sm" />
          </div>
        </div>
        <div>
          <label htmlFor="phoneNumber" className="block text-sm font-medium text-gray-700">Phone Number</label>
          <input type="tel" id="phoneNumber" value={phoneNumber} onChange={(e) => setPhoneNumber(e.target.value)} required className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-yellow-500 focus:border-yellow-500 sm:text-sm" />
        </div>
        <div className="flex items-center">
          <input type="checkbox" id="previouslyAttempted" checked={previouslyAttempted} onChange={(e) => setPreviouslyAttempted(e.target.checked)} className="h-4 w-4 text-yellow-600 focus:ring-yellow-500 border-gray-300 rounded" />
          <label htmlFor="previouslyAttempted" className="ml-2 block text-sm text-gray-900">Have you previously attempted the IELTS exam?</label>
        </div>
        {previouslyAttempted && (
          <div>
            <label htmlFor="previousBandScore" className="block text-sm font-medium text-gray-700">Previous Band Score</label>
            <input type="number" id="previousBandScore" value={previousBandScore || ''} onChange={(e) => setPreviousBandScore(parseFloat(e.target.value))} step="0.5" min="0" max="10" className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-yellow-500 focus:border-yellow-500 sm:text-sm" />
          </div>
        )}
        <div>
          <label htmlFor="examDate" className="block text-sm font-medium text-gray-700">Exam Date</label>
          <input type="date" id="examDate" value={examDate} onChange={(e) => setExamDate(e.target.value)} className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-yellow-500 focus:border-yellow-500 sm:text-sm" />
        </div>
        <div>
          <label htmlFor="targetBandScore" className="block text-sm font-medium text-gray-700">Target Band Score</label>
          <input type="number" id="targetBandScore" value={targetBandScore || ''} onChange={(e) => setTargetBandScore(parseFloat(e.target.value))} step="0.5" min="0" max="10" className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-yellow-500 focus:border-yellow-500 sm:text-sm" />
        </div>
        <div>
          <label htmlFor="country" className="block text-sm font-medium text-gray-700">Country</label>
          <select id="country" value={country} onChange={(e) => setCountry(e.target.value)} className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-yellow-500 focus:border-yellow-500 sm:text-sm">
            {countries.map((c) => (
              <option key={c.code} value={c.code}>
                {c.name}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label htmlFor="nativeLanguage" className="block text-sm font-medium text-gray-700">Native Language</label>
          <input type="text" id="nativeLanguage" value={nativeLanguage} onChange={(e) => setNativeLanguage(e.target.value)} className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-yellow-500 focus:border-yellow-500 sm:text-sm" />
        </div>
        <div>
          <button type="submit" disabled={isLoading} className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-yellow-600 hover:bg-yellow-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-yellow-500">
            {isLoading ? (
              <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            ) : null}
            {isLoading ? 'Submitting...' : 'Submit'}
          </button>
        </div>
      </form>
    </div>
  )
}
