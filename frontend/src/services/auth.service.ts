/**
 * Authentication Service
 *
 * @module services/auth
 * @description Handles secure authentication operations including login,
 * logout, and token management. Always uses the real API backend with
 * bcrypt-hashed passwords for maximum security.
 *
 * Features:
 * - JWT token management with secure storage
 * - Bcrypt password hashing on backend
 * - Automatic token cleanup on logout
 * - Session persistence
 * - No mocking - always uses real authentication
 *
 * Demo credentials (shared strong pass for HTTPS testing):
 * - test / 1302Quiter@#
 * - admin / 1302Quiter@#
 * - user / 1302Quiter@#
 */

import axios from 'axios';
import api, { handleApiError } from './api';
import {
  LoginRequest,
  LoginResponse,
  RegistrationRequest,
  RegistrationResponse,
  User,
} from '../types/api.types';

export class PasswordExpiredError extends Error {
  constructor(public username: string, message: string) {
    super(message);
    this.name = 'PasswordExpiredError';
  }
}

interface ForcePasswordChangePayload {
  username: string;
  current_password: string;
  new_password: string;
}

/**
 * Secure authentication service
 * Always connects to the real backend API for authentication
 */
export const authService = {
  /**
   * Authenticates user against the secure backend API
   * Uses bcrypt-hashed password verification
   *
   * @param {LoginRequest} credentials - User login credentials
   * @returns {Promise<LoginResponse>} Login response with JWT token and user data
   * @throws {Error} If authentication fails or network error occurs
   *
   * @example
   * ```typescript
   * try {
   *   const response = await authService.login({
   *     username: 'admin',
   *     password: '1302Quiter@#'
   *   });
   *   // Store token securely
   *   localStorage.setItem('auth_token', response.access_token);
   * } catch (error) {
   *   // Handle authentication error
   *   console.error('Login failed:', error);
   * }
   * ```
   */
  login: async (credentials: LoginRequest): Promise<LoginResponse> => {
    try {
      // Always use the real API endpoint with secure authentication
      const response = await api.post<LoginResponse>('/auth/login', credentials);

      // Store token securely for subsequent requests
      if (response.data.access_token) {
        localStorage.setItem('auth_token', response.data.access_token);
        localStorage.setItem('user', JSON.stringify(response.data.user));
      }

      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const expiredHeader = error.response?.headers?.['x-password-expired'];
        if (error.response?.status === 403 && expiredHeader === 'true') {
          throw new PasswordExpiredError(credentials.username, handleApiError(error));
        }
      }
      // Clear any existing auth data on login failure
      localStorage.removeItem('auth_token');
      localStorage.removeItem('user');
      throw new Error(handleApiError(error));
    }
  },

  /**
   * Verifies if current JWT token is still valid
   *
   * @returns {Promise<User | null>} User data if token is valid, null otherwise
   *
   * @description
   * - Sends request to /auth/me endpoint with current token
   * - Returns user data if token is valid
   * - Returns null if token is invalid or expired
   * - Used for session persistence and route protection
   */
  verifyToken: async (): Promise<User | null> => {
    try {
      const token = localStorage.getItem('auth_token');
      if (!token) {
        return null;
      }

      const response = await api.get<LoginResponse>('/auth/me');
      if (response.data.access_token) {
        localStorage.setItem('auth_token', response.data.access_token);
        localStorage.setItem('user', JSON.stringify(response.data.user));
      }
      return response.data.user;
    } catch (error) {
      // Token is invalid or expired
      localStorage.removeItem('auth_token');
      localStorage.removeItem('user');
      return null;
    }
  },

  /**
   * Updates an expired password before allowing login.
   */
  forcePasswordChange: async (payload: ForcePasswordChangePayload): Promise<void> => {
    try {
      await api.post('/auth/password/expired', payload);
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  },

  /**
   * Logs out the user by clearing authentication data
   */
  logout: () => {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user');
    // Redirect to login page
    window.location.href = '/login';
  },

  /**
   * Gets the currently logged in user from localStorage
   *
   * @returns {User | null} Current user or null if not logged in
   */
  getCurrentUser: (): User | null => {
    const userStr = localStorage.getItem('user');
    if (!userStr) return null;

    try {
      return JSON.parse(userStr);
    } catch {
      return null;
    }
  },

  /**
   * Checks if user is currently authenticated
   *
   * @returns {boolean} True if user has valid token
   */
  isAuthenticated: (): boolean => {
    return !!localStorage.getItem('auth_token');
  },

  /**
   * Registers a new account (requires email verification).
   */
  register: async (payload: RegistrationRequest): Promise<RegistrationResponse> => {
    try {
      const response = await api.post<RegistrationResponse>('/auth/register', payload);
      return response.data;
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  },

  /**
   * Completes account verification using a token.
   */
  verifyAccount: async (token: string): Promise<void> => {
    try {
      await api.post('/auth/verify', { token });
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  },
};
