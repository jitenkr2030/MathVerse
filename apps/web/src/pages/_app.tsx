import type { AppProps } from 'next/app';
import { useEffect } from 'react';
import { useRouter } from 'next/router';
import { useAuthStore } from '../store';

export default function App({ Component, pageProps }: AppProps) {
  const router = useRouter();
  const { checkAuth, isAuthenticated } = useAuthStore();

  useEffect(() => {
    // Check authentication on app load
    checkAuth();
  }, [checkAuth]);

  // Routes that don't require authentication
  const publicRoutes = ['/', '/login', '/register', '/courses', '/pricing', '/features', '/about'];

  // Check if current route is public
  const isPublicRoute = publicRoutes.some(
    (route) => router.pathname === route || router.pathname.startsWith('/courses/')
  );

  // Redirect to login if trying to access protected route without authentication
  useEffect(() => {
    if (!isAuthenticated && !isPublicRoute) {
      router.push('/login');
    }
  }, [isAuthenticated, isPublicRoute, router]);

  return <Component {...pageProps} />;
}
