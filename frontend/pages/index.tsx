import { useEffect } from 'react';
import { useRouter } from 'next/router';
import { useAuth } from '@/hooks/useAuth';

const IndexPage = () => {
  const { user, isLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading) {
      if (user) {
        router.replace('/ai-tutor');
      } else {
        router.replace('/login');
      }
    }
  }, [isLoading, user, router]);

  return <div>Loading...</div>; // Or a splash screen
};

export default IndexPage;
