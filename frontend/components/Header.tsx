'use client'

import { useState, useEffect } from 'react'
import { useRouter, usePathname } from 'next/navigation'
import { createClient } from '@/lib/supabase/client'
import { motion, AnimatePresence } from 'framer-motion'
import type { User } from '@supabase/supabase-js'

const navigationItems = [
  { name: 'Practice', href: '/', icon: '🎯' },
  { name: 'Progress', href: '/results', icon: '📊' },
  { name: 'Profile', href: '/profile', icon: '👤' },
]

export default function Header() {
  const [user, setUser] = useState<User | null>(null)
  const [isScrolled, setIsScrolled] = useState(false)
  const [activeItem, setActiveItem] = useState('')
  const router = useRouter()
  const pathname = usePathname()
  const supabase = createClient()

  useEffect(() => {
    const getUser = async () => {
      const { data: { user } } = await supabase.auth.getUser()
      setUser(user)
    }
    getUser()

    const handleScroll = () => {
      setIsScrolled(window.scrollY > 20)
    }
    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  useEffect(() => {
    const currentItem = navigationItems.find(item => item.href === pathname)
    setActiveItem(currentItem?.name || '')
  }, [pathname])

  const handleSignOut = async () => {
    await supabase.auth.signOut()
    router.push('/login')
    router.refresh()
  }

  if (!user) return null

  return (
    <motion.header
      initial={{ y: -100, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.6, ease: [0.215, 0.61, 0.355, 1] }}
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-500 ease-in-out ${
        isScrolled 
          ? 'bg-gray-900/95 backdrop-blur-xl border-b border-gray-800/50 shadow-2xl' 
          : 'bg-transparent'
      }`}
    >
      <div className="max-w-7xl mx-auto px-6 lg:px-8">
        <div className="flex items-center justify-between h-20">
          {/* Premium Logo */}
          <motion.div 
            className="flex items-center space-x-3"
            whileHover={{ scale: 1.02 }}
            transition={{ duration: 0.2 }}
          >
            <div className="w-10 h-10 bg-gradient-to-br from-amber-400 via-amber-500 to-orange-500 rounded-2xl flex items-center justify-center shadow-lg">
              <span className="text-gray-900 font-bold text-lg">AI</span>
            </div>
            <div className="hidden sm:block">
              <h1 className="text-2xl font-light text-white tracking-tight">
                IELTS <span className="font-medium bg-gradient-to-r from-amber-400 to-orange-500 bg-clip-text text-transparent">Examiner</span>
              </h1>
              <p className="text-xs text-gray-400 font-light tracking-wider uppercase">Premium AI Learning</p>
            </div>
          </motion.div>

          {/* Navigation */}
          <nav className="hidden md:flex items-center space-x-1">
            {navigationItems.map((item, index) => (
              <motion.button
                key={item.name}
                onClick={() => router.push(item.href)}
                className={`relative px-6 py-3 rounded-2xl text-sm font-medium transition-all duration-300 ${
                  activeItem === item.name
                    ? 'text-white bg-white/10 backdrop-blur-sm'
                    : 'text-gray-300 hover:text-white hover:bg-white/5'
                }`}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
              >
                <span className="mr-2">{item.icon}</span>
                {item.name}
                {activeItem === item.name && (
                  <motion.div
                    className="absolute inset-0 bg-gradient-to-r from-amber-400/20 to-orange-500/20 rounded-2xl border border-amber-400/30"
                    layoutId="activeTab"
                    transition={{ duration: 0.3, ease: [0.215, 0.61, 0.355, 1] }}
                  />
                )}
              </motion.button>
            ))}
          </nav>

          {/* User Profile & Actions */}
          <div className="flex items-center space-x-4">
            {/* User Avatar */}
            <motion.div 
              className="hidden sm:flex items-center space-x-3"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.3 }}
            >
              <div className="text-right">
                <p className="text-sm font-medium text-white">{user.email?.split('@')[0]}</p>
                <p className="text-xs text-gray-400">Premium Member</p>
              </div>
              <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center shadow-lg ring-2 ring-white/20">
                <span className="text-white font-semibold text-sm">
                  {user.email?.charAt(0).toUpperCase()}
                </span>
              </div>
            </motion.div>

            {/* Logout Button */}
            <motion.button
              onClick={handleSignOut}
              className="group relative px-4 py-2 bg-red-500/10 hover:bg-red-500/20 border border-red-500/30 rounded-xl text-red-400 hover:text-red-300 transition-all duration-300 backdrop-blur-sm"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <span className="flex items-center space-x-2">
                <svg className="w-4 h-4 group-hover:rotate-12 transition-transform duration-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                </svg>
                <span className="hidden sm:inline text-sm font-medium">Exit</span>
              </span>
            </motion.button>
          </div>
        </div>
      </div>

      {/* Mobile Navigation */}
      <AnimatePresence>
        <motion.div 
          className="md:hidden bg-gray-900/95 backdrop-blur-xl border-t border-gray-800/50"
          initial={{ height: 0, opacity: 0 }}
          animate={{ height: 'auto', opacity: 1 }}
          exit={{ height: 0, opacity: 0 }}
        >
          <div className="px-6 py-4 space-y-2">
            {navigationItems.map((item, index) => (
              <motion.button
                key={item.name}
                onClick={() => router.push(item.href)}
                className={`w-full flex items-center space-x-3 px-4 py-3 rounded-xl text-left transition-all duration-300 ${
                  activeItem === item.name
                    ? 'bg-white/10 text-white border border-amber-400/30'
                    : 'text-gray-300 hover:bg-white/5 hover:text-white'
                }`}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
              >
                <span>{item.icon}</span>
                <span className="font-medium">{item.name}</span>
              </motion.button>
            ))}
          </div>
        </motion.div>
      </AnimatePresence>
    </motion.header>
  )
} 