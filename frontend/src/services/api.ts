/**
 * API Configuration
 * Axios instance configured for the backend API
 */

import axios, { AxiosError, AxiosInstance, InternalAxiosRequestConfig } from 'axios';

// API Base URL - can be overridden by environment variable
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

// Create axios instance
const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000, // 10 seconds
});

// Request interceptor - Add JWT token to requests
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('auth_token');

    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    // Add API key for read operations if no token
    if (!token && config.headers) {
      const apiKey = import.meta.env.VITE_API_KEY || 'REDACTED_API_KEY';
      config.headers['X-API-Key'] = apiKey;
    }

    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor - Handle errors globally
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error: AxiosError) => {
    // Handle 401 Unauthorized - token expired
    if (error.response?.status === 401) {
      localStorage.removeItem('auth_token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }

    // Handle 403 Forbidden
    if (error.response?.status === 403) {
      console.error('Access forbidden');
    }

    // Handle 429 Rate Limit
    if (error.response?.status === 429) {
      console.error('Rate limit exceeded. Please try again later.');
    }

    // Handle 500 Server Error
    if (error.response?.status === 500) {
      console.error('Server error. Please try again later.');
    }

    return Promise.reject(error);
  }
);

// Helper function to handle API errors
export const handleApiError = (error: unknown): string => {
  if (axios.isAxiosError(error)) {
    // Server responded with error
    if (error.response?.data?.detail) {
      return error.response.data.detail;
    }

    // Request timeout
    if (error.code === 'ECONNABORTED') {
      return 'Request timeout. Please try again.';
    }

    // Network error
    if (error.message === 'Network Error') {
      return 'Network error. Please check your connection.';
    }

    return error.message;
  }

  return 'An unexpected error occurred';
};

export default api;
