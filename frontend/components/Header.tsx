 'use client'

import { useState, useEffect, useRef } from 'react'
import { useRouter, usePathname } from 'next/navigation'
import { createClient } from '@/lib/supabase/client'
import { motion, AnimatePresence } from 'framer-motion'
import type { User } from '@supabase/supabase-js'
import { getProfile } from '@/lib/actions'
import type { Profile } from '@prisma/client'

const navigationItems = [
  { name: 'Practice', href: '/', icon: '🎯' },
  { name: 'Progress', href: '/results', icon: '📊' },
  { name: 'Profile', href: '/profile', icon: '👤' },
]

export default function Header() {
  const [user, setUser] = useState<User | null>(null)
  const [profile, setProfile] = useState<Profile | null>(null)
  const [isScrolled, setIsScrolled] = useState(false)
  const [activeItem, setActiveItem] = useState('')
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)
  const [isProfileMenuOpen, setIsProfileMenuOpen] = useState(false)
  const router = useRouter()
  const pathname = usePathname()
  const supabase = createClient()
  const profileContainerRef = useRef<HTMLDivElement | null>(null)

  useEffect(() => {
    const getUser = async () => {
      const { data: { user } } = await supabase.auth.getUser()
      setUser(user)
      
      if (user) {
        // Get user profile using server action
        const profileData = await getProfile()
        setProfile(profileData)
      }
    }
    getUser()

    const handleScroll = () => {
      setIsScrolled(window.scrollY > 20)
    }
    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [supabase.auth])

  useEffect(() => {
    const currentItem = navigationItems.find(item => item.href === pathname)
    setActiveItem(currentItem?.name || '')
  }, [pathname])

  const handleSignOut = async () => {
    await supabase.auth.signOut()
    setUser(null)
    setProfile(null)
    router.push('/login')
    router.refresh()
  }

  const toggleMobileMenu = () => {
    setIsMobileMenuOpen(!isMobileMenuOpen)
  }

  const toggleProfileMenu = () => {
    setIsProfileMenuOpen((prev) => !prev)
  }

  // Close profile menu on outside click or Escape
  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (
        isProfileMenuOpen &&
        profileContainerRef.current &&
        !profileContainerRef.current.contains(e.target as Node)
      ) {
        setIsProfileMenuOpen(false)
      }
    }

    function handleKeyDown(e: KeyboardEvent) {
      if (e.key === 'Escape') setIsProfileMenuOpen(false)
    }

    document.addEventListener('mousedown', handleClickOutside)
    document.addEventListener('keydown', handleKeyDown)
    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
      document.removeEventListener('keydown', handleKeyDown)
    }
  }, [isProfileMenuOpen])

  const handleMobileNavigation = (href: string) => {
    router.push(href)
    setIsMobileMenuOpen(false)
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
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16 sm:h-20">
          {/* Premium Logo */}
          <motion.div 
            className="flex items-center space-x-2 sm:space-x-3"
            whileHover={{ scale: 1.02 }}
            transition={{ duration: 0.2 }}
          >
            <div className="w-12 h-12 sm:w-14 sm:h-14 bg-gradient-to-br from-amber-400 via-amber-500 to-orange-500 rounded-xl sm:rounded-2xl flex items-center justify-center shadow-lg">
              <span className="text-gray-900 font-bold text-lg sm:text-xl">AI</span>
            </div>
            <div className="block">
              <h1 className="text-lg sm:text-xl lg:text-2xl font-light text-white tracking-tight">
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
                className={`relative px-4 lg:px-6 py-2 lg:py-3 rounded-xl lg:rounded-2xl text-sm font-medium transition-all duration-300 touch-manipulation ${
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
                <span className="mr-1.5 lg:mr-2">{item.icon}</span>
                {item.name}
                {activeItem === item.name && (
                  <motion.div
                    className="absolute inset-0 bg-gradient-to-r from-amber-400/20 to-orange-500/20 rounded-xl lg:rounded-2xl border border-amber-400/30"
                    layoutId="activeTab"
                    transition={{ duration: 0.3, ease: [0.215, 0.61, 0.355, 1] }}
                  />
                )}
              </motion.button>
            ))}
          </nav>

          {/* User Profile & Actions */}
          <div className="flex items-center space-x-2 sm:space-x-4 h-full relative">
            {/* Profile container wraps trigger + dropdown so outside-click ignores trigger */}
            <div ref={profileContainerRef} className="relative">
              {/* Profile (click to open glassy dropdown) */}
              <motion.button
                onClick={toggleProfileMenu}
                className="hidden sm:flex items-center space-x-3 h-12 sm:h-14 px-3 sm:px-4 rounded-xl bg-white/5 hover:bg-white/10 text-left transition-all duration-300 backdrop-blur-sm border border-white/10"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.3 }}
              >
                <div className="text-right flex flex-col justify-center">
                  <p className="text-sm font-medium text-white leading-tight">
                    {profile?.full_name ||
                      (profile?.first_name && profile?.last_name
                        ? `${profile.first_name} ${profile.last_name}`
                        : user.email?.split('@')[0])}
                  </p>
                </div>
                <div className="w-10 h-10 sm:w-12 sm:h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center shadow-lg ring-2 ring-white/20 flex-shrink-0">
                  <span className="text-white font-semibold text-sm sm:text-base">
                    {profile?.first_name?.charAt(0).toUpperCase() ||
                      profile?.full_name?.charAt(0).toUpperCase() ||
                      user.email?.charAt(0).toUpperCase()}
                  </span>
                </div>
                <svg className={`w-4 h-4 text-gray-300 transition-transform ${isProfileMenuOpen ? 'rotate-180' : ''}`} viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M5.23 7.21a.75.75 0 011.06.02L10 10.94l3.71-3.71a.75.75 0 011.08 1.04l-4.25 4.25a.75.75 0 01-1.06 0L5.25 8.27a.75.75 0 01-.02-1.06z" clipRule="evenodd" />
                </svg>
              </motion.button>

              {/* Glassy Profile Dropdown */}
              <AnimatePresence>
                {isProfileMenuOpen && (
                  <motion.div
                    initial={{ opacity: 0, y: -6, scale: 0.98 }}
                    animate={{ opacity: 1, y: 8, scale: 1 }}
                    exit={{ opacity: 0, y: -6, scale: 0.98 }}
                    transition={{ duration: 0.18 }}
                    className="absolute right-0 top-full z-50 w-64 sm:w-72"
                  >
                    <div className="bg-white/10 backdrop-blur-xl border border-white/20 rounded-2xl shadow-2xl shadow-black/30 overflow-hidden">
                      {/* Header */}
                      <div className="px-4 py-3 bg-white/5 flex items-center gap-3">
                        <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center ring-2 ring-white/20">
                          <span className="text-white font-semibold">
                            {profile?.first_name?.charAt(0).toUpperCase() ||
                              profile?.full_name?.charAt(0).toUpperCase() ||
                              user.email?.charAt(0).toUpperCase()}
                          </span>
                        </div>
                        <div className="min-w-0">
                          <p className="text-sm text-white font-medium truncate">
                            {profile?.full_name ||
                              (profile?.first_name && profile?.last_name
                                ? `${profile.first_name} ${profile.last_name}`
                                : user.email?.split('@')[0])}
                          </p>
                          <p className="text-xs text-gray-300/80 truncate">{user.email}</p>
                        </div>
                      </div>
                      <div className="h-px bg-white/10" />
                      <div className="py-2">
                        <button
                          className="w-full text-left px-4 py-2.5 text-sm text-red-400 hover:text-red-300 hover:bg-red-500/10 transition-colors flex items-center gap-2"
                          onClick={() => {
                            setIsProfileMenuOpen(false)
                            handleSignOut()
                          }}
                        >🚶‍♂️ Logout
                        </button>
                      </div>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>

            {/* Mobile Menu Button */}
            <motion.button
              onClick={toggleMobileMenu}
              className="md:hidden w-12 h-12 sm:w-14 sm:h-14 rounded-lg sm:rounded-xl bg-gray-800/50 text-gray-300 hover:text-white hover:bg-gray-700/50 transition-colors duration-300 touch-manipulation flex items-center justify-center flex-shrink-0"
              whileTap={{ scale: 0.95 }}
            >
              <svg className="w-6 h-6 sm:w-7 sm:h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                {isMobileMenuOpen ? (
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                ) : (
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                )}
              </svg>
            </motion.button>
          </div>
        </div>
      </div>

      {/* Mobile Navigation */}
      <AnimatePresence>
        {isMobileMenuOpen && (
          <motion.div 
            className="md:hidden bg-gray-900/95 backdrop-blur-xl border-t border-gray-800/50"
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3, ease: [0.215, 0.61, 0.355, 1] }}
          >
            <div className="px-4 py-4 space-y-2">
              {/* Mobile User Info */}
              <div className="flex items-center space-x-3 px-4 py-3 rounded-xl bg-gray-800/50 mb-4 sm:hidden">
                <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center shadow-lg">
                  <span className="text-white font-semibold text-sm">
                    {profile?.first_name?.charAt(0).toUpperCase() || 
                     profile?.full_name?.charAt(0).toUpperCase() || 
                     user.email?.charAt(0).toUpperCase()}
                  </span>
                </div>
                <div>
                  <p className="text-sm font-medium text-white">
                    {profile?.full_name || 
                     (profile?.first_name && profile?.last_name 
                       ? `${profile.first_name} ${profile.last_name}`
                       : user.email?.split('@')[0])
                    }
                  </p>
                  
                </div>
              </div>

              {/* Navigation Items */}
              {navigationItems.map((item, index) => (
                <motion.button
                  key={item.name}
                  onClick={() => handleMobileNavigation(item.href)}
                  className={`w-full flex items-center space-x-3 px-4 py-3 rounded-xl text-left transition-all duration-300 touch-manipulation ${
                    activeItem === item.name
                      ? 'bg-white/10 text-white border border-amber-400/30'
                      : 'text-gray-300 hover:bg-white/5 hover:text-white'
                  }`}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                >
                  <span className="text-lg">{item.icon}</span>
                  <span className="font-medium">{item.name}</span>
                </motion.button>
              ))}

              {/* Mobile Logout Button */}
              <div className="pt-2 mt-2 border-t border-gray-800/50">
                <motion.button
                  onClick={() => {
                    setIsMobileMenuOpen(false)
                    handleSignOut()
                  }}
                  className="w-full flex items-center space-x-3 px-4 py-3 rounded-xl text-left transition-all duration-300 touch-manipulation text-red-400 hover:bg-red-500/10 hover:text-red-300"
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: navigationItems.length * 0.1 }}
                >
                  <span className="text-lg">🚶‍♂️</span>
                  <span className="font-medium">Logout</span>
                </motion.button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.header>
  )
} 