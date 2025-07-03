'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { createClient } from '@/lib/supabase/client'
import { motion } from 'framer-motion'
import type { User } from '@supabase/supabase-js'

const countries = [
  { code: 'IN', name: 'India', flag: '🇮🇳' },
  { code: 'US', name: 'United States', flag: '🇺🇸' },
  { code: 'GB', name: 'United Kingdom', flag: '🇬🇧' },
  { code: 'CA', name: 'Canada', flag: '🇨🇦' },
  { code: 'AU', name: 'Australia', flag: '🇦🇺' },
  { code: 'NZ', name: 'New Zealand', flag: '🇳🇿' },
  { code: 'IE', name: 'Ireland', flag: '🇮🇪' },
  { code: 'DE', name: 'Germany', flag: '🇩🇪' },
  { code: 'FR', name: 'France', flag: '🇫🇷' },
  { code: 'CN', name: 'China', flag: '🇨🇳' },
  { code: 'JP', name: 'Japan', flag: '🇯🇵' },
  { code: 'KR', name: 'South Korea', flag: '🇰🇷' },
  { code: 'BR', name: 'Brazil', flag: '🇧🇷' },
  { code: 'MX', name: 'Mexico', flag: '🇲🇽' },
  { code: 'ZA', name: 'South Africa', flag: '🇿🇦' },
];

const targetScores = [5.0, 5.5, 6.0, 6.5, 7.0, 7.5, 8.0, 8.5, 9.0];
const previousScores = [4.0, 4.5, 5.0, 5.5, 6.0, 6.5, 7.0, 7.5, 8.0, 8.5, 9.0];

export default function ProfileForm({ user }: { user: User }) {
  const supabase = createClient()
  const router = useRouter()

  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    phoneNumber: '',
    previouslyAttempted: false,
    previousBandScore: null as number | null,
    examDate: '',
    targetBandScore: null as number | null,
    country: 'IN',
    nativeLanguage: '',
  })
  
  const [isLoading, setIsLoading] = useState(false)
  const [currentStep, setCurrentStep] = useState(0)

  useEffect(() => {
    // Load existing profile data
    async function loadProfile() {
      const { data } = await supabase
        .from('profiles')
        .select('*')
        .single()

      if (data) {
        setFormData({
          firstName: data.first_name || '',
          lastName: data.last_name || '',
          phoneNumber: data.phone_number || '',
          previouslyAttempted: data.previously_attempted_exam || false,
          previousBandScore: data.previous_band_score,
          examDate: data.exam_date || '',
          targetBandScore: data.target_band_score,
          country: data.country || 'IN',
          nativeLanguage: data.native_language || '',
        })
      }
    }
    loadProfile()
  }, [supabase])

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    
    // Prevent submission if not on the last step
    if (currentStep !== steps.length - 1) {
      console.warn('Form submission attempted on non-final step')
      return
    }
    
    // Ensure final step is valid before submitting
    if (!isStepValid(currentStep)) {
      console.warn('Form submission attempted with invalid data')
      return
    }
    
    await submitProfile()
  }

  const submitProfile = async () => {
    setIsLoading(true)

    try {
      const { error } = await supabase.from('profiles').update({
        first_name: formData.firstName,
        last_name: formData.lastName,
        phone_number: formData.phoneNumber,
        previously_attempted_exam: formData.previouslyAttempted,
        previous_band_score: formData.previousBandScore,
        exam_date: formData.examDate,
        target_band_score: formData.targetBandScore,
        country: formData.country,
        native_language: formData.nativeLanguage,
        onboarding_completed: true,
      }).eq('id', user.id)

      if (error) {
        console.error('Error updating profile:', error)
      } else {
        router.push('/')
        router.refresh()
      }
    } catch (error) {
      console.error('Error:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleCompleteProfile = async () => {
    // Prevent submission if not on the last step
    if (currentStep !== steps.length - 1) {
      console.warn('Profile completion attempted on non-final step')
      return
    }
    
    // Ensure final step is valid before submitting
    if (!isStepValid(currentStep)) {
      console.warn('Profile completion attempted with invalid data')
      return
    }
    
    await submitProfile()
  }

  const steps = [
    {
      title: 'Personal Information',
      description: 'Tell us about yourself',
      icon: '👤',
      fields: ['firstName', 'lastName', 'phoneNumber', 'country', 'nativeLanguage']
    },
    {
      title: 'IELTS Background',
      description: 'Your testing experience',
      icon: '📚',
      fields: ['previouslyAttempted', 'previousBandScore']
    },
    {
      title: 'Goals & Timeline',
      description: 'Your learning objectives',
      icon: '🎯',
      fields: ['targetBandScore', 'examDate']
    }
  ]

  const isStepValid = (stepIndex: number) => {
    const step = steps[stepIndex]
    return step.fields.every(field => {
      if (field === 'previousBandScore' && !formData.previouslyAttempted) return true
      if (field === 'examDate') return true // Optional
      
      const value = formData[field as keyof typeof formData]
      
      // Special handling for targetBandScore (number field)
      if (field === 'targetBandScore') {
        return value !== null && value !== undefined && value !== ''
      }
      
      // Regular validation for string fields
      return value !== '' && value !== null && value !== undefined
    })
  }

  const nextStep = () => {
    if (currentStep < steps.length - 1 && isStepValid(currentStep)) {
      setCurrentStep(currentStep + 1)
    }
  }

  const prevStep = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 py-16">
      <div className="max-w-4xl mx-auto px-6">
        {/* Header */}
        <motion.div 
          className="text-center mb-12"
          initial={{ opacity: 0, y: -30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <h1 className="text-5xl font-light text-white mb-4 tracking-tight">
            Perfect Your <span className="font-medium bg-gradient-to-r from-amber-400 to-orange-500 bg-clip-text text-transparent">Profile</span>
          </h1>
          <p className="text-xl text-gray-400 max-w-2xl mx-auto">
            Personalize your IELTS learning experience with premium AI coaching
          </p>
        </motion.div>

        {/* Progress Steps */}
        <motion.div 
          className="mb-12"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
        >
          <div className="flex justify-center items-center space-x-8">
            {steps.map((step, index) => (
              <div key={index} className="flex items-center">
                <div className={`relative flex items-center justify-center w-16 h-16 rounded-2xl transition-all duration-500 ${
                  index <= currentStep 
                    ? 'bg-gradient-to-r from-amber-500 to-orange-500 shadow-lg shadow-amber-500/25' 
                    : 'bg-gray-800 border border-gray-700'
                }`}>
                  <span className="text-2xl">{step.icon}</span>
                  {index <= currentStep && (
                    <motion.div
                      className="absolute inset-0 bg-gradient-to-r from-amber-400 to-orange-500 rounded-2xl"
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      transition={{ duration: 0.3 }}
                      style={{ zIndex: -1 }}
                    />
                  )}
                </div>
                {index < steps.length - 1 && (
                  <div className={`w-16 h-1 mx-4 rounded-full transition-all duration-500 ${
                    index < currentStep ? 'bg-gradient-to-r from-amber-500 to-orange-500' : 'bg-gray-700'
                  }`} />
                )}
              </div>
            ))}
          </div>
          <div className="text-center mt-6">
            <h3 className="text-2xl font-light text-white mb-2">{steps[currentStep].title}</h3>
            <p className="text-gray-400">{steps[currentStep].description}</p>
          </div>
        </motion.div>

        {/* Form */}
        <motion.div
          className="bg-white/5 backdrop-blur-xl rounded-3xl border border-white/10 p-8 shadow-2xl"
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
        >
          <form onSubmit={handleSubmit} className="space-y-8">
            {/* Step 1: Personal Information */}
            {currentStep === 0 && (
              <motion.div
                initial={{ opacity: 0, x: 50 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.5 }}
                className="space-y-6"
              >
                <div className="grid md:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <label className="block text-sm font-medium text-gray-300">First Name</label>
                    <input
                      type="text"
                      value={formData.firstName}
                      onChange={(e) => setFormData({...formData, firstName: e.target.value})}
                      className="w-full px-4 py-3 bg-gray-800/50 border border-gray-600 rounded-xl text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-transparent transition-all duration-300"
                      placeholder="Enter your first name"
                      required
                    />
                  </div>
                  <div className="space-y-2">
                    <label className="block text-sm font-medium text-gray-300">Last Name</label>
                    <input
                      type="text"
                      value={formData.lastName}
                      onChange={(e) => setFormData({...formData, lastName: e.target.value})}
                      className="w-full px-4 py-3 bg-gray-800/50 border border-gray-600 rounded-xl text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-transparent transition-all duration-300"
                      placeholder="Enter your last name"
                      required
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <label className="block text-sm font-medium text-gray-300">Phone Number</label>
                  <input
                    type="tel"
                    value={formData.phoneNumber}
                    onChange={(e) => setFormData({...formData, phoneNumber: e.target.value})}
                    className="w-full px-4 py-3 bg-gray-800/50 border border-gray-600 rounded-xl text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-transparent transition-all duration-300"
                    placeholder="Enter your phone number"
                    required
                  />
                </div>

                <div className="space-y-2">
                  <label className="block text-sm font-medium text-gray-300">Country</label>
                  <select
                    value={formData.country}
                    onChange={(e) => setFormData({...formData, country: e.target.value})}
                    className="w-full px-4 py-3 bg-gray-800/50 border border-gray-600 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-transparent transition-all duration-300"
                  >
                    {countries.map((country) => (
                      <option key={country.code} value={country.code} className="bg-gray-800">
                        {country.flag} {country.name}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="space-y-2">
                  <label className="block text-sm font-medium text-gray-300">Native Language</label>
                  <input
                    type="text"
                    value={formData.nativeLanguage}
                    onChange={(e) => setFormData({...formData, nativeLanguage: e.target.value})}
                    className="w-full px-4 py-3 bg-gray-800/50 border border-gray-600 rounded-xl text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-transparent transition-all duration-300"
                    placeholder="Enter your native language"
                    required
                  />
                </div>
              </motion.div>
            )}

            {/* Step 2: IELTS Background */}
            {currentStep === 1 && (
              <motion.div
                initial={{ opacity: 0, x: 50 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.5 }}
                className="space-y-6"
              >
                <div className="flex items-center p-6 bg-gradient-to-r from-blue-500/10 to-purple-500/10 rounded-xl border border-blue-500/20">
                  <input
                    type="checkbox"
                    id="previouslyAttempted"
                    checked={formData.previouslyAttempted}
                    onChange={(e) => setFormData({...formData, previouslyAttempted: e.target.checked, previousBandScore: e.target.checked ? formData.previousBandScore : null})}
                    className="w-5 h-5 text-amber-600 bg-gray-800 border-gray-600 rounded focus:ring-amber-500 focus:ring-2"
                  />
                  <label htmlFor="previouslyAttempted" className="ml-4 block text-lg text-white">
                    I have previously attempted the IELTS exam
                  </label>
                </div>

                {formData.previouslyAttempted && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    transition={{ duration: 0.3 }}
                    className="space-y-2"
                  >
                    <label className="block text-sm font-medium text-gray-300">Previous Band Score</label>
                    <select
                      value={formData.previousBandScore || ''}
                      onChange={(e) => setFormData({...formData, previousBandScore: parseFloat(e.target.value)})}
                      className="w-full px-4 py-3 bg-gray-800/50 border border-gray-600 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-transparent transition-all duration-300"
                      required={formData.previouslyAttempted}
                    >
                      <option value="">Select your previous score</option>
                      {previousScores.map((score) => (
                        <option key={score} value={score} className="bg-gray-800">
                          {score}
                        </option>
                      ))}
                    </select>
                  </motion.div>
                )}
              </motion.div>
            )}

            {/* Step 3: Goals & Timeline */}
            {currentStep === 2 && (
              <motion.div
                initial={{ opacity: 0, x: 50 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.5 }}
                className="space-y-6"
              >
                <div className="space-y-2">
                  <label className="block text-sm font-medium text-gray-300">Target Band Score</label>
                  <div className="grid grid-cols-3 md:grid-cols-5 gap-3">
                    {targetScores.map((score) => (
                      <button
                        key={score}
                        type="button"
                        onClick={() => setFormData({...formData, targetBandScore: score})}
                        className={`py-3 px-4 rounded-xl border transition-all duration-300 ${
                          formData.targetBandScore === score
                            ? 'bg-gradient-to-r from-amber-500 to-orange-500 border-amber-400 text-white shadow-lg'
                            : 'bg-gray-800/50 border-gray-600 text-gray-300 hover:border-amber-500/50'
                        }`}
                      >
                        {score}
                      </button>
                    ))}
                  </div>
                </div>

                <div className="space-y-2">
                  <label className="block text-sm font-medium text-gray-300">Exam Date (Optional)</label>
                  <input
                    type="date"
                    value={formData.examDate}
                    onChange={(e) => setFormData({...formData, examDate: e.target.value})}
                    className="w-full px-4 py-3 bg-gray-800/50 border border-gray-600 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-transparent transition-all duration-300"
                  />
                </div>
              </motion.div>
            )}

            {/* Navigation Buttons */}
            <div className="flex justify-between pt-8">
              <button
                type="button"
                onClick={prevStep}
                disabled={currentStep === 0}
                className={`px-8 py-3 rounded-xl font-medium transition-all duration-300 ${
                  currentStep === 0 
                    ? 'opacity-50 cursor-not-allowed' 
                    : 'bg-gray-700 hover:bg-gray-600 text-white'
                }`}
              >
                Previous
              </button>

              {currentStep < steps.length - 1 ? (
                <button
                  type="button"
                  onClick={nextStep}
                  disabled={!isStepValid(currentStep)}
                  className={`px-8 py-3 rounded-xl font-medium transition-all duration-300 ${
                    isStepValid(currentStep)
                      ? 'bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-400 hover:to-orange-400 text-white shadow-lg'
                      : 'opacity-50 cursor-not-allowed bg-gray-700'
                  }`}
                >
                  Next Step
                </button>
              ) : (
                <button
                  type="button"
                  onClick={handleCompleteProfile}
                  disabled={isLoading || !isStepValid(currentStep)}
                  className={`px-8 py-3 rounded-xl font-medium transition-all duration-300 flex items-center space-x-2 ${
                    !isLoading && isStepValid(currentStep)
                      ? 'bg-gradient-to-r from-green-500 to-emerald-500 hover:from-green-400 hover:to-emerald-400 text-white shadow-lg'
                      : 'opacity-50 cursor-not-allowed bg-gray-700'
                  }`}
                >
                  {isLoading && (
                    <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                  )}
                  <span>{isLoading ? 'Saving...' : 'Complete Profile'}</span>
                </button>
              )}
            </div>
          </form>
        </motion.div>
      </div>
    </div>
  )
}