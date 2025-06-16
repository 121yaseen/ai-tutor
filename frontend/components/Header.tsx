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
    <header className="flex items-center justify-between p-4 bg-white shadow-md">
      <Link href="/">
        <h1 className="text-xl font-bold cursor-pointer">AI IELTS Examiner</h1>
      </Link>
      {user && (
        <div className="flex items-center gap-4">
          <Link
            href="/profile"
            className="px-4 py-2 text-sm text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200"
          >
            Profile
          </Link>
          <form action={signOut}>
            <button className="px-4 py-2 text-sm text-white bg-red-500 rounded-md hover:bg-red-600">
              Logout
            </button>
          </form>
        </div>
      )}
    </header>
  )
} 