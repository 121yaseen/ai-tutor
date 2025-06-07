import type { NextPage } from 'next';
import Head from 'next/head';
import AuthLayout from '@/components/auth/AuthLayout';
import { useAuth } from '@/hooks/useAuth';
import { useRouter } from 'next/router';
import { useEffect } from 'react';

const LoginPage: NextPage = () => {
  const { user, isLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && user) {
      router.push('/ai-tutor');
    }
  }, [isLoading, user, router]);

  if (isLoading || user) {
    return <div>Loading...</div>; // Or a proper loading spinner
  }

  return (
    <>
      <Head>
        <title>Login - AI Tutor</title>
      </Head>
      <AuthLayout />
    </>
  );
};

export default LoginPage; 