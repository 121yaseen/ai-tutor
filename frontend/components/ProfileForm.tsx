'use client'

import { useCallback, useEffect, useState } from 'react'
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

export default function ProfileForm({
  user,
}: {
  user: User
}) {
  const supabase = createClient()
  const [loading, setLoading] = useState(true)
  const [firstName, setFirstName] = useState<string | null>(null)
  const [lastName, setLastName] = useState<string | null>(null)
  const [phoneNumber, setPhoneNumber] = useState<string | null>(null)
  const [previouslyAttempted, setPreviouslyAttempted] = useState<boolean | null>(null)
  const [previousBandScore, setPreviousBandScore] = useState<number | null>(null)
  const [examDate, setExamDate] = useState<string | null>(null)
  const [targetBandScore, setTargetBandScore] = useState<number | null>(null)
  const [country, setCountry] = useState<string | null>(null)
  const [nativeLanguage, setNativeLanguage] = useState<string | null>(null)
  const [message, setMessage] = useState<{ type: 'success' | 'error'; content: string } | null>(null)

  const getProfile = useCallback(async () => {
    try {
      setLoading(true)

      const { data, error, status } = await supabase
        .from('profiles')
        .select(`first_name, last_name, phone_number, previously_attempted_exam, previous_band_score, exam_date, target_band_score, country, native_language`)
        .eq('id', user.id)
        .single()

      if (error && status !== 406) {
        throw error
      }

      if (data) {
        setFirstName(data.first_name)
        setLastName(data.last_name)
        setPhoneNumber(data.phone_number)
        setPreviouslyAttempted(data.previously_attempted_exam)
        setPreviousBandScore(data.previous_band_score)
        setExamDate(data.exam_date)
        setTargetBandScore(data.target_band_score)
        setCountry(data.country)
        setNativeLanguage(data.native_language)
      }
    } catch (error: any) {
      setMessage({ type: 'error', content: 'Error loading user data!' })
    } finally {
      setLoading(false)
    }
  }, [user, supabase])

  useEffect(() => {
    getProfile()
  }, [user, getProfile])

  async function updateProfile(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setLoading(true)
    setMessage(null)

    const { error } = await supabase.from('profiles').upsert({
      id: user.id,
      first_name: firstName,
      last_name: lastName,
      phone_number: phoneNumber,
      previously_attempted_exam: previouslyAttempted,
      previous_band_score: previousBandScore,
      exam_date: examDate,
      target_band_score: targetBandScore,
      country,
      native_language: nativeLanguage,
      updated_at: new Date().toISOString(),
    })

    if (error) {
      setMessage({ type: 'error', content: 'Error updating the data!' })
    } else {
      setMessage({ type: 'success', content: 'Profile updated successfully!' })
    }
    setLoading(false)
  }

  return (
    <div className="max-w-2xl mx-auto bg-white p-8 rounded-lg shadow-md">
      <h2 className="text-xl font-semibold mb-6">Profile Details</h2>
      <form onSubmit={updateProfile} className="space-y-6">
        <div>
          <label htmlFor="email" className="block text-sm font-medium text-gray-700">
            Email
          </label>
          <input
            id="email"
            type="text"
            value={user?.email}
            disabled
            className="mt-1 block w-full px-3 py-2 bg-gray-100 border border-gray-300 rounded-md shadow-sm focus:outline-none sm:text-sm"
          />
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label htmlFor="firstName" className="block text-sm font-medium text-gray-700">First Name</label>
            <input type="text" id="firstName" value={firstName || ''} onChange={(e) => setFirstName(e.target.value)} className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-yellow-500 focus:border-yellow-500 sm:text-sm" />
          </div>
          <div>
            <label htmlFor="lastName" className="block text-sm font-medium text-gray-700">Last Name</label>
            <input type="text" id="lastName" value={lastName || ''} onChange={(e) => setLastName(e.target.value)} className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-yellow-500 focus:border-yellow-500 sm:text-sm" />
          </div>
        </div>
        <div>
          <label htmlFor="phoneNumber" className="block text-sm font-medium text-gray-700">Phone Number</label>
          <input type="tel" id="phoneNumber" value={phoneNumber || ''} onChange={(e) => setPhoneNumber(e.target.value)} className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-yellow-500 focus:border-yellow-500 sm:text-sm" />
        </div>
        <div className="flex items-center">
          <input type="checkbox" id="previouslyAttempted" checked={previouslyAttempted || false} onChange={(e) => setPreviouslyAttempted(e.target.checked)} className="h-4 w-4 text-yellow-600 focus:ring-yellow-500 border-gray-300 rounded" />
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
          <input type="date" id="examDate" value={examDate || ''} onChange={(e) => setExamDate(e.target.value)} className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-yellow-500 focus:border-yellow-500 sm:text-sm" />
        </div>
        <div>
          <label htmlFor="targetBandScore" className="block text-sm font-medium text-gray-700">Target Band Score</label>
          <input type="number" id="targetBandScore" value={targetBandScore || ''} onChange={(e) => setTargetBandScore(parseFloat(e.target.value))} step="0.5" min="0" max="10" className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-yellow-500 focus:border-yellow-500 sm:text-sm" />
        </div>
        <div>
          <label htmlFor="country" className="block text-sm font-medium text-gray-700">Country</label>
          <select id="country" value={country || ''} onChange={(e) => setCountry(e.target.value)} className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-yellow-500 focus:border-yellow-500 sm:text-sm">
            {countries.map((c) => (
              <option key={c.code} value={c.code}>
                {c.name}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label htmlFor="nativeLanguage" className="block text-sm font-medium text-gray-700">Native Language</label>
          <input type="text" id="nativeLanguage" value={nativeLanguage || ''} onChange={(e) => setNativeLanguage(e.target.value)} className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-yellow-500 focus:border-yellow-500 sm:text-sm" />
        </div>
        <div>
          <button
            className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-black bg-yellow-400 hover:bg-yellow-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-yellow-500 disabled:opacity-50"
            type="submit"
            disabled={loading}
          >
            {loading ? (
              <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            ) : null}
            {loading ? 'Saving...' : 'Save Profile'}
          </button>
        </div>
      </form>
      {message && (
        <p
          className={`mt-4 text-sm text-center ${
            message.type === 'error' ? 'text-red-500' : 'text-green-500'
          }`}
        >
          {message.content}
        </p>
      )}
    </div>
  )
}