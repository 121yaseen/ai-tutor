import { createClient } from '@/lib/supabase/server'
import Link from 'next/link'
import { redirect } from 'next/navigation'

export default async function Header() {
  const supabase = createClient()

  const {
    data: { user },
  } = await supabase.auth.getUser()

  const signOut = async () => {
    'use server'

    const supabase = createClient()
    await supabase.auth.signOut()
    return redirect('/login')
  }

  return (
    <header className="flex items-center justify-between p-4 bg-gray-800 shadow-md border-b border-gray-700">
      <Link href="/">
        <h1 className="text-xl font-bold cursor-pointer text-white hover:text-yellow-400 transition-colors">AI IELTS Examiner</h1>
      </Link>
      {user && (
        <div className="flex items-center gap-4">
          <Link
            href="/results"
            className="px-4 py-2 text-sm text-gray-300 bg-gray-700 rounded-md hover:bg-gray-600 hover:text-white transition-colors"
          >
            Results
          </Link>
          <Link
            href="/profile"
            className="px-4 py-2 text-sm text-gray-300 bg-gray-700 rounded-md hover:bg-gray-600 hover:text-white transition-colors"
          >
            Profile
          </Link>
          <form action={signOut}>
            <button className="px-4 py-2 text-sm text-white bg-red-600 rounded-md hover:bg-red-700 transition-colors">
              Logout
            </button>
          </form>
        </div>
      )}
    </header>
  )
} 