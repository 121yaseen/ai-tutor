import type { NextPage } from 'next';
import Head from 'next/head';
import Script from 'next/script';
import ChatInterface from '@/components/chat/ChatInterface';
import { useAuth } from '@/hooks/useAuth';
import { useRouter } from 'next/router';
import { useEffect } from 'react';

const AiTutorPage: NextPage = () => {
  const { user, isLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && !user) {
      router.push('/login');
    }
  }, [isLoading, user, router]);

  if (isLoading || !user) {
    return <div>Loading...</div>; // Or a proper loading spinner
  }

  return (
    <>
      <Head>
        <title>AI Tutor Voice Assistant</title>
      </Head>
      <ChatInterface />
      <Script src="/js/voiceWave.js" strategy="lazyOnload" />
    </>
  );
};

export default AiTutorPage; 