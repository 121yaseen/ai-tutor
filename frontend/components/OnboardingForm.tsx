
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
  const [phoneError, setPhoneError] = useState('')
  const [previouslyAttempted, setPreviouslyAttempted] = useState(false)
  const [previousBandScore, setPreviousBandScore] = useState<number | null>(null)
  const [examDate, setExamDate] = useState('')
  const [targetBandScore, setTargetBandScore] = useState<number | null>(null)
  const [country, setCountry] = useState('IN') // Default to India's code
  const [nativeLanguage, setNativeLanguage] = useState('')
  const [isLoading, setIsLoading] = useState(false) // New loading state

  const validatePhoneNumber = (phone: string) => {
    const phoneRegex = /^\d{10}$/
    if (!phone) {
      setPhoneError('Phone number is required')
      return false
    }
    if (!phoneRegex.test(phone)) {
      setPhoneError('Phone number must be exactly 10 digits')
      return false
    }
    setPhoneError('')
    return true
  }

  const handlePhoneChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value.replace(/\D/g, '') // Remove non-digits
    if (value.length <= 10) {
      setPhoneNumber(value)
      if (value.length === 10) {
        validatePhoneNumber(value)
      } else if (value.length > 0) {
        setPhoneError('Phone number must be exactly 10 digits')
      } else {
        setPhoneError('')
      }
    }
  }

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    
    // Validate phone number before submission
    if (!validatePhoneNumber(phoneNumber)) {
      return
    }
    
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
      <h1 className="text-3xl font-bold mb-6 text-white">Welcome! Let&apos;s get you set up.</h1>
      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label htmlFor="firstName" className="block text-sm font-medium text-gray-300">First Name</label>
            <input type="text" id="firstName" value={firstName} onChange={(e) => setFirstName(e.target.value)} required className="mt-1 block w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md shadow-sm text-white placeholder-gray-400 focus:outline-none focus:ring-yellow-500 focus:border-yellow-500 sm:text-sm" />
          </div>
          <div>
            <label htmlFor="lastName" className="block text-sm font-medium text-gray-300">Last Name</label>
            <input type="text" id="lastName" value={lastName} onChange={(e) => setLastName(e.target.value)} required className="mt-1 block w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md shadow-sm text-white placeholder-gray-400 focus:outline-none focus:ring-yellow-500 focus:border-yellow-500 sm:text-sm" />
          </div>
        </div>
        <div>
          <label htmlFor="phoneNumber" className="block text-sm font-medium text-gray-300">Phone Number</label>
          <div className="mt-1 flex rounded-md shadow-sm">
            <span className="inline-flex items-center px-3 rounded-l-md border border-r-0 border-gray-600 bg-gray-600 text-gray-300 text-sm">
              🇮🇳+91
            </span>
            <input 
              type="tel" 
              id="phoneNumber" 
              value={phoneNumber} 
              onChange={handlePhoneChange}
              placeholder="1234567890"
              maxLength={10}
              required 
              className={`flex-1 block w-full px-3 py-2 bg-gray-700 border rounded-none rounded-r-md shadow-sm text-white placeholder-gray-400 focus:outline-none focus:ring-yellow-500 sm:text-sm ${
                phoneError ? 'border-red-500 focus:border-red-500' : 'border-gray-600 focus:border-yellow-500'
              }`}
            />
          </div>
          {phoneError && (
            <p className="mt-1 text-sm text-red-400">{phoneError}</p>
          )}
          <p className="mt-1 text-xs text-gray-400">Enter your 10-digit mobile number</p>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-3">Have you previously attempted the IELTS exam?</label>
          <div className="flex space-x-6">
            <div className="flex items-center">
              <input 
                type="radio" 
                id="previouslyAttempted-yes" 
                name="previouslyAttempted"
                checked={previouslyAttempted === true} 
                onChange={() => setPreviouslyAttempted(true)} 
                className="h-4 w-4 text-yellow-600 focus:ring-yellow-500 border-gray-600 bg-gray-700" 
              />
              <label htmlFor="previouslyAttempted-yes" className="ml-2 block text-sm text-gray-300 cursor-pointer">Yes</label>
            </div>
            <div className="flex items-center">
              <input 
                type="radio" 
                id="previouslyAttempted-no" 
                name="previouslyAttempted"
                checked={previouslyAttempted === false} 
                onChange={() => setPreviouslyAttempted(false)} 
                className="h-4 w-4 text-yellow-600 focus:ring-yellow-500 border-gray-600 bg-gray-700" 
              />
              <label htmlFor="previouslyAttempted-no" className="ml-2 block text-sm text-gray-300 cursor-pointer">No</label>
            </div>
          </div>
        </div>
        {previouslyAttempted && (
          <div>
            <label htmlFor="previousBandScore" className="block text-sm font-medium text-gray-300">Previous Band Score</label>
            <input type="number" id="previousBandScore" value={previousBandScore || ''} onChange={(e) => setPreviousBandScore(parseFloat(e.target.value))} step="0.5" min="0" max="10" className="mt-1 block w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md shadow-sm text-white placeholder-gray-400 focus:outline-none focus:ring-yellow-500 focus:border-yellow-500 sm:text-sm" />
          </div>
        )}
        <div>
          <label htmlFor="examDate" className="block text-sm font-medium text-gray-300">Exam Date</label>
          <input type="date" id="examDate" value={examDate} onChange={(e) => setExamDate(e.target.value)} className="mt-1 block w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md shadow-sm text-white placeholder-gray-400 focus:outline-none focus:ring-yellow-500 focus:border-yellow-500 sm:text-sm" />
        </div>
        <div>
          <label htmlFor="targetBandScore" className="block text-sm font-medium text-gray-300">Target Band Score</label>
          <input type="number" id="targetBandScore" value={targetBandScore || ''} onChange={(e) => setTargetBandScore(parseFloat(e.target.value))} step="0.5" min="0" max="10" className="mt-1 block w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md shadow-sm text-white placeholder-gray-400 focus:outline-none focus:ring-yellow-500 focus:border-yellow-500 sm:text-sm" />
        </div>
        <div>
          <label htmlFor="country" className="block text-sm font-medium text-gray-300">Country</label>
          <select id="country" value={country} onChange={(e) => setCountry(e.target.value)} className="mt-1 block w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md shadow-sm text-white focus:outline-none focus:ring-yellow-500 focus:border-yellow-500 sm:text-sm">
            {countries.map((c) => (
              <option key={c.code} value={c.code} className="bg-gray-700 text-white">
                {c.name}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label htmlFor="nativeLanguage" className="block text-sm font-medium text-gray-300">Native Language</label>
          <input type="text" id="nativeLanguage" value={nativeLanguage} onChange={(e) => setNativeLanguage(e.target.value)} className="mt-1 block w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md shadow-sm text-white placeholder-gray-400 focus:outline-none focus:ring-yellow-500 focus:border-yellow-500 sm:text-sm" />
        </div>
        <div>
          <button type="submit" disabled={isLoading} className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-black bg-yellow-500 hover:bg-yellow-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-yellow-500 disabled:opacity-50">
            {isLoading ? (
              <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-black" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
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
