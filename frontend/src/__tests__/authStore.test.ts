import { describe, expect, it, beforeEach } from 'vitest';
import { useAuthStore } from '../store/authStore';
import type { User } from '../types/api.types';

describe('auth store', () => {
  beforeEach(() => {
    useAuthStore.setState({
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,
      setAuth: useAuthStore.getState().setAuth,
      logout: useAuthStore.getState().logout,
      setLoading: useAuthStore.getState().setLoading,
      initAuth: useAuthStore.getState().initAuth,
      updateUser: useAuthStore.getState().updateUser,
      getDefaultLanding: useAuthStore.getState().getDefaultLanding
    });
    localStorage.clear();
  });

  it('returns dashboard landing when user missing', () => {
    expect(useAuthStore.getState().getDefaultLanding()).toBe('dashboard');
  });

  it('updates user profile data and landing preference', () => {
    const user: User = {
      id: 1,
      username: 'tester',
      role: 'user',
      default_landing_page: 'dashboard'
    };

    useAuthStore.getState().setAuth(user, 'token');
    useAuthStore.getState().updateUser({ default_landing_page: 'search' });

    expect(useAuthStore.getState().user?.default_landing_page).toBe('search');
    expect(useAuthStore.getState().getDefaultLanding()).toBe('search');
  });
});
