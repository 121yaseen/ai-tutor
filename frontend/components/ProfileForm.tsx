'use client'

import { useCallback, useEffect, useState } from 'react'
import { createClient } from '@/lib/supabase/client'
import type { User } from '@supabase/supabase-js'

export default function ProfileForm({
  user,
}: {
  user: User
}) {
  const supabase = createClient()
  const [loading, setLoading] = useState(true)
  const [fullName, setFullName] = useState<string | null>(null)
  const [message, setMessage] = useState<{ type: 'success' | 'error'; content: string } | null>(null)

  const getProfile = useCallback(async () => {
    try {
      setLoading(true)

      const { data, error, status } = await supabase
        .from('profiles')
        .select(`full_name`)
        .eq('id', user.id)
        .single()

      if (error && status !== 406) {
        throw error
      }

      if (data) {
        setFullName(data.full_name)
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
      full_name: fullName,
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
    <div className="max-w-md mx-auto bg-white p-8 rounded-lg shadow-md">
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
        <div>
          <label htmlFor="fullName" className="block text-sm font-medium text-gray-700">
            Display Name
          </label>
          <input
            id="fullName"
            type="text"
            value={fullName || ''}
            onChange={(e) => setFullName(e.target.value)}
            className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-yellow-500 focus:border-yellow-500 sm:text-sm"
          />
        </div>
        <div>
          <button
            className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-black bg-yellow-400 hover:bg-yellow-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-yellow-500 disabled:opacity-50"
            type="submit"
            disabled={loading}
          >
            {loading ? 'Saving ...' : 'Save Profile'}
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