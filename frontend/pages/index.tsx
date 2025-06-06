import type { NextPage } from 'next'
import Head from 'next/head'
import Script from 'next/script'
import { useAuth } from '@/hooks/useAuth'
import AuthLayout from '@/components/auth/AuthLayout'
import ChatInterface from '@/components/chat/ChatInterface'

const Home: NextPage = () => {
  const { user, isLoading } = useAuth()

  if (isLoading) {
    return <div>Loading...</div>
  }

  return (
    <>
      <Head>
        <title>AI Tutor Voice Assistant</title>
      </Head>

      {user ? (
        <ChatInterface />
      ) : (
        <AuthLayout />
      )}

      <Script src="/js/voiceWave.js" strategy="lazyOnload" />
    </>
  )
}

export default Home
