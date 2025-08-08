'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { motion, AnimatePresence } from 'framer-motion'
import { PhoneInput } from 'react-international-phone'
import 'react-international-phone/style.css'
import { getNames, getCode } from 'country-list'
import { updateProfile } from '@/lib/actions'
import type { Profile } from '@prisma/client'

const countries = getNames().map((name: string) => ({
  name,
  code: getCode(name),
}))

const targetScores = [5.0, 5.5, 6.0, 6.5, 7.0, 7.5, 8.0, 8.5, 9.0];
const previousScores = [4.0, 4.5, 5.0, 5.5, 6.0, 6.5, 7.0, 7.5, 8.0, 8.5, 9.0];

export default function ProfileForm({
  isOnboarding = false,
  profile
}: {
  isOnboarding?: boolean,
  profile: Profile | null
}) {
  const router = useRouter()

  const [formData, setFormData] = useState({
    first_name: profile?.first_name || '',
    last_name: profile?.last_name || '',
    phone_number: profile?.phone_number || '',
    previously_attempted_exam: profile?.previously_attempted_exam || false,
    previous_band_score: profile?.previous_band_score || null,
    exam_date: profile?.exam_date ? new Date(profile.exam_date).toISOString().split('T')[0] : '',
    target_band_score: profile?.target_band_score || null,
    country: profile?.country || 'US',
    native_language: profile?.native_language || '',
  })
  
  const [isLoading, setIsLoading] = useState(false)
  const [currentStep, setCurrentStep] = useState(0)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)
  const [dateError, setDateError] = useState<string | null>(null)

  const validateExamDate = (date: string) => {
    if (!date) {
      setDateError(null)
      return true
    }
    const selectedDate = new Date(date)
    const today = new Date()
    today.setHours(0, 0, 0, 0)

    if (selectedDate < today) {
      setDateError('Exam date cannot be in the past.')
      return false
    } else {
      setDateError(null)
      return true
    }
  }

  useEffect(() => {
    // Re-validate the date whenever the user navigates to the final step
    if (currentStep === 2) {
      validateExamDate(formData.exam_date)
    }
  }, [currentStep, formData.exam_date])

  const handleDateChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newDate = e.target.value
    setFormData({ ...formData, exam_date: newDate })
    validateExamDate(newDate)
  }

  const submitProfile = async () => {
    if (!validateExamDate(formData.exam_date)) return

    setIsLoading(true)
    setError(null)
    setSuccess(null)

    try {
      // Construct full_name from first_name and last_name
      const fullName = [formData.first_name, formData.last_name]
        .filter(name => name && name.trim())
        .join(' ')
        .trim()

      await updateProfile({
        ...formData,
        full_name: fullName || undefined,
        exam_date: formData.exam_date ? new Date(formData.exam_date) : null,
        onboarding_completed: true,
      })
      
      setSuccess('Profile saved successfully!')
      setTimeout(() => {
        router.push(isOnboarding ? '/' : '/results')
        router.refresh()
      }, 1500)

    } catch (err: unknown) {
      const error = err as { message?: string }
      console.error('Error updating profile:', error)
      setError(error.message || 'An unexpected error occurred. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  const steps = [
    {
      title: 'Personal Information',
      description: 'Tell us a bit about yourself.',
      icon: '👤',
    },
    {
      title: 'IELTS Background',
      description: 'Your testing experience helps us tailor your sessions.',
      icon: '📚',
    },
    {
      title: 'Goals & Contact',
      description: 'Your objectives and how we can reach you.',
      icon: '🎯',
    }
  ]

  const nextStep = () => {
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1)
    }
  }

  const prevStep = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1)
    }
  }

  const renderStep = (stepIndex: number) => {
    const todayString = new Date().toISOString().split('T')[0]

    switch (stepIndex) {
      case 0:
        return (
          <div className="space-y-4 sm:space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 sm:gap-6">
              <div className="space-y-2">
                <label className="block text-sm font-medium text-gray-300">First Name</label>
                <input type="text" value={formData.first_name} onChange={(e) => setFormData({...formData, first_name: e.target.value})} className="w-full px-4 py-3 bg-gray-800/50 border border-gray-600 rounded-xl text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-transparent transition-all duration-300 text-base" placeholder="Your first name" />
              </div>
              <div className="space-y-2">
                <label className="block text-sm font-medium text-gray-300">Last Name</label>
                <input type="text" value={formData.last_name} onChange={(e) => setFormData({...formData, last_name: e.target.value})} className="w-full px-4 py-3 bg-gray-800/50 border border-gray-600 rounded-xl text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-transparent transition-all duration-300 text-base" placeholder="Your last name" />
              </div>
            </div>
            <div className="space-y-2">
              <label className="block text-sm font-medium text-gray-300">Country</label>
              <select value={formData.country} onChange={(e) => setFormData({...formData, country: e.target.value})} className="w-full px-4 py-3 bg-gray-800/50 border border-gray-600 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-transparent transition-all duration-300 text-base">
                {countries.map((c: { name: string; code: string | undefined }) => (c && c.code && <option key={c.code} value={c.code} className="bg-gray-800">{c.name}</option>))}
              </select>
            </div>
            <div className="space-y-2">
              <label className="block text-sm font-medium text-gray-300">Native Language</label>
              <input type="text" value={formData.native_language} onChange={(e) => setFormData({...formData, native_language: e.target.value})} className="w-full px-4 py-3 bg-gray-800/50 border border-gray-600 rounded-xl text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-transparent transition-all duration-300 text-base" placeholder="e.g., Spanish" />
            </div>
          </div>
        )
      case 1:
        return (
          <div className="space-y-4 sm:space-y-6">
            <div className="flex items-start sm:items-center p-4 sm:p-6 bg-gradient-to-r from-blue-500/10 to-purple-500/10 rounded-xl border border-blue-500/20">
              <input type="checkbox" id="previouslyAttempted" checked={formData.previously_attempted_exam} onChange={(e) => setFormData({...formData, previously_attempted_exam: e.target.checked, previous_band_score: e.target.checked ? formData.previous_band_score : null})} className="w-5 h-5 mt-1 sm:mt-0 text-amber-600 bg-gray-800 border-gray-600 rounded focus:ring-amber-500 focus:ring-2" />
              <label htmlFor="previouslyAttempted" className="ml-3 sm:ml-4 block text-base sm:text-lg text-white leading-relaxed">I have previously attempted the IELTS exam</label>
            </div>
            {formData.previously_attempted_exam && (
              <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }} transition={{ duration: 0.3 }} className="space-y-2">
                <label className="block text-sm font-medium text-gray-300">Previous Band Score</label>
                <select value={formData.previous_band_score || ''} onChange={(e) => setFormData({...formData, previous_band_score: parseFloat(e.target.value)})} className="w-full px-4 py-3 bg-gray-800/50 border border-gray-600 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-transparent transition-all duration-300 text-base">
                  <option value="">Select your previous score</option>
                  {previousScores.map((score) => (<option key={score} value={score} className="bg-gray-800">{score}</option>))}
                </select>
              </motion.div>
            )}
          </div>
        )
      case 2:
        return (
          <div className="space-y-4 sm:space-y-6">
            <div className="space-y-2">
              <label className="block text-sm font-medium text-gray-300">Target Band Score</label>
              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-2 sm:gap-3">
                {targetScores.map((score) => (
                  <button key={score} type="button" onClick={() => setFormData({...formData, target_band_score: score})} className={`py-3 sm:py-4 px-3 sm:px-4 rounded-xl border transition-all duration-300 text-sm sm:text-base font-medium ${formData.target_band_score === score ? 'bg-gradient-to-r from-amber-500 to-orange-500 border-amber-400 text-white shadow-lg' : 'bg-gray-800/50 border-gray-600 text-gray-300 hover:border-amber-500/50'}`}>
                    {score}
                  </button>
                ))}
              </div>
            </div>
            <div className="space-y-2">
              <label className="block text-sm font-medium text-gray-300">Exam Date (Optional)</label>
              <input type="date" value={formData.exam_date} onChange={handleDateChange} min={todayString} className="w-full px-4 py-3 bg-gray-800/50 border border-gray-600 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-transparent transition-all duration-300 text-base" />
              {dateError && <p className="mt-2 text-sm text-red-400">{dateError}</p>}
            </div>
            <div className="space-y-2">
              <label className="block text-sm font-medium text-gray-300">Phone Number</label>
              <PhoneInput
                defaultCountry="us"
                value={formData.phone_number}
                onChange={(phone) => setFormData({...formData, phone_number: phone})}
                className="w-full"
              />
            </div>
          </div>
        )
      default:
        return null
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 py-8 sm:py-12 lg:py-16">
      <div className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div 
          className="text-center mb-8 sm:mb-12"
          initial={{ opacity: 0, y: -30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <h1 className="text-2xl sm:text-3xl lg:text-4xl font-light text-white mb-4 tracking-tight">
            {isOnboarding ? "Welcome! Let's Set Up Your Profile" : "Edit Your Profile"}
          </h1>
          <p className="text-base sm:text-lg lg:text-xl text-gray-400 max-w-2xl mx-auto px-4">
            {isOnboarding ? "This will help us personalize your AI coaching experience." : "Keep your information up to date."}
          </p>
        </motion.div>

        <motion.div 
          className="mb-8 sm:mb-12"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
        >
          <div className="flex justify-center items-center space-x-4 lg:space-x-8">
            {steps.map((step, index) => (
              <div key={index} className="flex items-center">
                <div className={`relative flex items-center justify-center w-12 h-12 lg:w-16 lg:h-16 rounded-xl lg:rounded-2xl transition-all duration-500 ${
                  index <= currentStep 
                    ? 'bg-gradient-to-r from-amber-500 to-orange-500 shadow-lg shadow-amber-500/25' 
                    : 'bg-gray-800 border border-gray-700'
                }`}>
                  <span className="text-lg lg:text-2xl">{step.icon}</span>
                  {index <= currentStep && (
                    <motion.div
                      className="absolute inset-0 bg-gradient-to-r from-amber-400 to-orange-500 rounded-xl lg:rounded-2xl"
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      transition={{ duration: 0.3 }}
                      style={{ zIndex: -1 }}
                    />
                  )}
                </div>
                {index < steps.length - 1 && (
                  <div className={`w-8 lg:w-16 h-0.5 lg:h-1 mx-2 lg:mx-4 rounded-full transition-all duration-500 ${
                    index < currentStep ? 'bg-gradient-to-r from-amber-500 to-orange-500' : 'bg-gray-700'
                  }`} />
                )}
              </div>
            ))}
          </div>
          <div className="text-center mt-4 sm:mt-6">
            <h3 className="text-xl sm:text-2xl font-light text-white mb-2">{steps[currentStep].title}</h3>
            <p className="text-gray-400 text-sm sm:text-base">{steps[currentStep].description}</p>
          </div>
        </motion.div>

        <motion.div
          className="bg-white/5 backdrop-blur-xl rounded-2xl sm:rounded-3xl border border-white/10 p-6 sm:p-8 shadow-2xl"
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
        >
          <form onSubmit={(e) => { e.preventDefault(); submitProfile(); }}>
            <AnimatePresence mode="wait">
              <motion.div
                key={currentStep}
                initial={{ opacity: 0, x: 50 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -50 }}
                transition={{ duration: 0.3 }}
              >
                {renderStep(currentStep)}
              </motion.div>
            </AnimatePresence>

            <AnimatePresence>
              {error && (
                <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto'}} exit={{ opacity: 0, height: 0 }} className="mt-4 text-center p-3 bg-red-500/10 border border-red-500/20 rounded-xl">
                  <p className="text-red-400 text-sm">{error}</p>
                </motion.div>
              )}
              {success && (
                <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto'}} exit={{ opacity: 0, height: 0 }} className="mt-4 text-center p-3 bg-green-500/10 border border-green-500/20 rounded-xl">
                  <p className="text-green-400 text-sm">{success}</p>
                </motion.div>
              )}
            </AnimatePresence>

            <div className="flex flex-col-reverse sm:flex-row justify-between items-center gap-4 pt-6 sm:pt-8">
              <div className="flex w-full sm:w-auto sm:justify-start">
                {isOnboarding && (
                  <button type="button" onClick={() => router.push('/')} className="text-sm text-gray-400 hover:text-white transition-colors">
                    Skip for now
                  </button>
                )}
              </div>
              <div className="flex w-full sm:w-auto gap-4">
                <button type="button" onClick={prevStep} disabled={currentStep === 0} className={`w-full sm:w-auto px-6 py-3 rounded-xl font-medium transition-all duration-300 text-base ${currentStep === 0 ? 'opacity-50 cursor-not-allowed bg-gray-800' : 'bg-gray-700 hover:bg-gray-600 text-white'}`}>
                  Previous
                </button>
                {currentStep < steps.length - 1 ? (
                  <button type="button" onClick={nextStep} disabled={!!dateError} className={`w-full sm:w-auto px-6 py-3 rounded-xl font-medium transition-all duration-300 text-base ${!dateError ? 'bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-400 hover:to-orange-400 text-white shadow-lg' : 'opacity-50 cursor-not-allowed bg-gray-800'}`}>
                    Next Step
                  </button>
                ) : (
                  <button type="button" onClick={submitProfile} disabled={isLoading || !!dateError} className={`w-full sm:w-auto px-6 py-3 rounded-xl font-medium transition-all duration-300 flex items-center justify-center space-x-2 text-base ${isLoading || dateError ? 'opacity-50 cursor-not-allowed bg-gray-800' : 'bg-gradient-to-r from-green-500 to-emerald-500 hover:from-green-400 hover:to-emerald-400 text-white shadow-lg'}`}>
                    {isLoading && (<svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>)}
                    <span>{isLoading ? 'Saving...' : (isOnboarding ? 'Complete Profile' : 'Save Changes')}</span>
                  </button>
                )}
              </div>
            </div>
          </form>
        </motion.div>
      </div>
    </div>
  )
}