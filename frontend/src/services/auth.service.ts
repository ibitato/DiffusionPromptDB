/**
 * Authentication Service
 * Handles login, logout, and token management
 */

import api, { handleApiError } from './api';
import { LoginRequest, LoginResponse, User } from '../types/api.types';

export const authService = {
  /**
   * Login user and get JWT token
   * Note: The actual API endpoint may need to be adjusted
   * Currently assuming POST /auth/login
   */
  login: async (credentials: LoginRequest): Promise<LoginResponse> => {
    try {
      const response = await api.post<LoginResponse>('/auth/login', credentials);
      return response.data;
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  },

  /**
   * Verify token is valid
   */
  verifyToken: async (): Promise<User | null> => {
    try {
      const response = await api.get<User>('/auth/me');
      return response.data;
    } catch (error) {
      return null;
    }
  },

  /**
   * Mock login for development
   * Remove this once the real API endpoint is available
   */
  mockLogin: async (credentials: LoginRequest): Promise<LoginResponse> => {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 1000));

    // Mock validation
    if (credentials.username === 'test' && credentials.password === 'test') {
      return {
        access_token: 'mock-jwt-token-' + Date.now(),
        token_type: 'bearer',
        user: {
          id: 1,
          username: credentials.username,
          email: 'test@example.com',
          role: 'admin',
        },
      };
    }

    throw new Error('Invalid credentials');
  },
};
