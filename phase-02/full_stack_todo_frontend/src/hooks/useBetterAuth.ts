import { useRouter } from 'next/navigation';
import { useCallback } from 'react';
import apiClient from '../lib/api/client'; // ← Relative path fix

// For now, since BetterAuth uses atoms instead of standard hooks, we'll create a simple wrapper
// that works with our existing system but represents the BetterAuth integration

interface User {
  id: string;
  email: string;
  token?: string;
}

interface AuthState {
  user: User | null;
  loading: boolean;
  error: string | null;
  isAuthenticated: boolean;
}

interface AuthContextType extends AuthState {
  signIn: (email: string, password: string) => Promise<void>;
  signUp: (email: string, password: string) => Promise<void>;
  signOut: () => Promise<void>;
  refreshAuth: () => void;
}

export function useBetterAuth(): AuthContextType {
  const router = useRouter();

  const signInHandler = useCallback(async (email: string, password: string) => {
    try {
      const response = await apiClient.post('/auth/signin', {
        email,
        password
      });

      if (response.data.access_token) {
        localStorage.setItem('access_token', response.data.access_token);
        router.push('/tasks');
      } else {
        throw new Error('Sign in failed - no token received');
      }
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail?.message || error.response?.data?.error?.message || error.message || 'Sign in failed';
      throw new Error(errorMessage);
    }
  }, [router]);

  const signUpHandler = useCallback(async (email: string, password: string) => {
    try {
      const response = await apiClient.post('/auth/signup', {
        email,
        password
      });

      if (response.data.access_token) {
        localStorage.setItem('access_token', response.data.access_token);
        router.push('/tasks');
      } else {
        throw new Error('Sign up failed - no token received');
      }
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail?.message || error.response?.data?.error?.message || error.message || 'Sign up failed';
      throw new Error(errorMessage);
    }
  }, [router]);

  const signOutHandler = useCallback(async () => {
    try {
      localStorage.removeItem('access_token');
      router.push('/signin');
    } catch (error) {
      router.push('/signin');
    }
  }, [router]);

  const refreshAuth = useCallback(() => {
    // JWT refresh logic can be added here
  }, []);

  return {
    user: null,
    loading: false,
    error: null,
    isAuthenticated: false,
    signIn: signInHandler,
    signUp: signUpHandler,
    signOut: signOutHandler,
    refreshAuth,
  };
}
