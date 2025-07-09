'use client'

import { useState, useEffect, Suspense } from 'react'
import { createClient } from '@/lib/supabase/client'
import { motion } from 'framer-motion'
import { useSearchParams } from 'next/navigation'

function LoginForm() {
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  
  const supabase = createClient()
  const searchParams = useSearchParams()

  // Handle URL error parameters
  useEffect(() => {
    const urlError = searchParams.get('error')
    if (urlError === 'auth_failed') {
      setError('Authentication failed. Please try again.')
    }
  }, [searchParams])

  const handleGoogleLogin = async () => {
    setError('')
    setIsLoading(true)
    
    try {
      await supabase.auth.signInWithOAuth({
        provider: 'google',
        options: {
          redirectTo: `${window.location.origin}/auth/callback`
        }
      })
    } catch (err) {
      setError('An unexpected error occurred')
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 flex items-start justify-center pt-16 sm:pt-20 py-8 sm:py-12 px-4 sm:px-6 lg:px-8">
      {/* Background Elements */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute top-1/4 left-1/4 w-72 h-72 sm:w-96 sm:h-96 bg-gradient-to-r from-amber-500/10 to-orange-500/10 rounded-full blur-3xl"></div>
        <div className="absolute bottom-1/4 right-1/4 w-72 h-72 sm:w-96 sm:h-96 bg-gradient-to-r from-purple-500/10 to-blue-500/10 rounded-full blur-3xl"></div>
      </div>

      <div className="relative max-w-md w-full space-y-6 sm:space-y-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -50 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="text-center"
        >
          <div className="flex justify-center mb-4 sm:mb-6">
            <div className="w-16 h-16 sm:w-20 sm:h-20 bg-gradient-to-br from-amber-400 via-amber-500 to-orange-500 rounded-2xl sm:rounded-3xl flex items-center justify-center shadow-2xl">
              <span className="text-gray-900 font-bold text-xl sm:text-3xl">AI</span>
            </div>
          </div>
          <h2 className="text-3xl sm:text-4xl font-light text-white mb-2 tracking-tight">
            Welcome to <span className="font-medium bg-gradient-to-r from-amber-400 to-orange-500 bg-clip-text text-transparent">IELTS Examiner</span>
          </h2>
          <p className="text-gray-400 text-base sm:text-lg px-2">
            Continue with your Google account to get started
          </p>
        </motion.div>

        {/* Auth Card */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="bg-white/5 backdrop-blur-xl rounded-2xl sm:rounded-3xl border border-white/10 p-6 sm:p-8 shadow-2xl"
        >
          {error && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="p-4 bg-red-500/10 border border-red-500/20 rounded-xl mb-6"
            >
              <p className="text-red-400 text-sm text-center">{error}</p>
            </motion.div>
          )}

          {/* Google Login Button */}
          <motion.button
            onClick={handleGoogleLogin}
            disabled={isLoading}
            className={`group relative w-full flex justify-center items-center py-4 sm:py-5 px-4 border border-transparent text-base sm:text-lg font-medium rounded-xl text-white transition-all duration-300 touch-manipulation ${
              isLoading
                ? 'opacity-50 cursor-not-allowed'
                : 'bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-400 hover:to-orange-400 shadow-lg hover:shadow-amber-500/25 transform hover:scale-105'
            }`}
            whileHover={{ scale: isLoading ? 1 : 1.02 }}
            whileTap={{ scale: isLoading ? 1 : 0.98 }}
          >
            {isLoading ? (
              <svg className="animate-spin -ml-1 mr-3 h-5 w-5 sm:h-6 sm:w-6 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            ) : (
              <svg className="w-5 h-5 mr-3 flex-shrink-0" viewBox="0 0 24 24">
                <path fill="currentColor" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                <path fill="currentColor" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                <path fill="currentColor" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                <path fill="currentColor" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
              </svg>
            )}
            {isLoading ? 'Connecting...' : 'Continue with Google'}
          </motion.button>

          {/* Info Text */}
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.5 }}
            className="mt-6 text-xs text-gray-400 text-center leading-relaxed px-2"
          >
            By continuing, you agree to our{' '}
            <a href="#" className="text-amber-400 hover:text-amber-300 transition-colors underline">
              Terms of Service
            </a>{' '}
            and{' '}
            <a href="#" className="text-amber-400 hover:text-amber-300 transition-colors underline">
              Privacy Policy
            </a>
          </motion.p>
        </motion.div>
      </div>
    </div>
  )
}

export default function LoginPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 flex items-center justify-center">
        <div className="text-white text-xl">Loading...</div>
      </div>
    }>
      <LoginForm />
    </Suspense>
  )
}