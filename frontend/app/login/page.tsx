'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { createClient } from '@/lib/supabase/client'
import { GoogleIcon } from '@/components/GoogleIcon'
import { AppleIcon } from '@/components/AppleIcon'
import { FacebookIcon } from '@/components/FacebookIcon'

export default function LoginPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [view, setView] = useState('sign-in')
  const [error, setError] = useState<string | null>(null)
  const router = useRouter()
  const supabase = createClient()

  const handleSignUp = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    setError(null)
    const { error } = await supabase.auth.signUp({
      email,
      password,
    })
    if (error) {
      setError(error.message)
    } else {
      setView('check-email')
    }
  }

  const handleSignIn = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    setError(null)
    const { error } = await supabase.auth.signInWithPassword({
      email,
      password,
    })
    if (error) {
      setError(error.message)
    } else {
      router.push('/')
      router.refresh()
    }
  }

  return (
    <div className="flex flex-col min-h-screen bg-[#FDFBF7]">
      <header className="flex justify-end p-6">
        <button
          onClick={() => setView(view === 'sign-in' ? 'sign-up' : 'sign-in')}
          className="px-6 py-2 text-black bg-yellow-400 rounded-md hover:bg-yellow-500 transition"
        >
          {view === 'sign-in' ? 'Sign up' : 'Sign in'}
        </button>
      </header>
      <main className="flex items-center justify-center flex-1">
        <div className="w-full max-w-sm p-8 space-y-6 bg-white rounded-2xl shadow-lg">
          {view === 'check-email' ? (
            <p className="text-center text-gray-500">
              Check your email at <span className="font-bold text-gray-700">{email}</span> to continue
            </p>
          ) : (
            <>
              <div className="text-center">
                <h1 className="text-3xl font-bold">
                  {view === 'sign-in' ? 'Login' : 'Create an account'}
                </h1>
                <p className="text-gray-500">
                  {view === 'sign-in'
                    ? 'Hey, Enter your details to sign in'
                    : 'Create an account to get started'}
                </p>
              </div>

              <form
                onSubmit={view === 'sign-in' ? handleSignIn : handleSignUp}
                className="space-y-4"
              >
                <input
                  type="email"
                  placeholder="Enter Email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  className="w-full px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-yellow-400"
                />
                <input
                  type="password"
                  placeholder="Enter Password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  className="w-full px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-yellow-400"
                />

                {view === 'sign-in' && (
                  <div className="text-sm text-right">
                    <a href="#" className="font-medium text-yellow-600 hover:text-yellow-500">
                      Having trouble signing in?
                    </a>
                  </div>
                )}

                <button
                  type="submit"
                  className="w-full px-4 py-3 font-semibold text-black bg-yellow-400 rounded-md hover:bg-yellow-500 transition"
                >
                  {view === 'sign-in' ? 'Sign In' : 'Sign Up'}
                </button>
              </form>

              {error && <p className="text-sm text-center text-red-500">{error}</p>}

              <div className="relative">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full border-t border-gray-300" />
                </div>
                <div className="relative flex justify-center text-sm">
                  <span className="px-2 bg-white text-gray-500">Or Sign in with</span>
                </div>
              </div>

              <div className="flex justify-center space-x-4">
                <button className="flex items-center justify-center w-1/3 py-2 border border-gray-300 rounded-md hover:bg-gray-50 transition">
                  <GoogleIcon />
                </button>
                <button className="flex items-center justify-center w-1/3 py-2 border border-gray-300 rounded-md hover:bg-gray-50 transition">
                  <AppleIcon />
                </button>
                <button className="flex items-center justify-center w-1/3 py-2 border border-gray-300 rounded-md hover:bg-gray-50 transition">
                  <FacebookIcon />
                </button>
              </div>

              <p className="text-sm text-center text-gray-500">
                {view === 'sign-in'
                  ? "Don't have and account? "
                  : 'Already have an account? '}
                <button
                  onClick={() => setView(view === 'sign-in' ? 'sign-up' : 'sign-in')}
                  className="font-medium text-yellow-600 hover:text-yellow-500"
                >
                  {view === 'sign-in' ? 'Sign up here' : 'Sign in here'}
                </button>
              </p>
            </>
          )}
        </div>
      </main>
      <footer className="py-4 text-center text-gray-500">
        <p>© AI IELTS Examiner | 2024</p>
      </footer>
    </div>
  )
} 