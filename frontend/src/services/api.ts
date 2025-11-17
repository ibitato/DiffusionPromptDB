import axios, { AxiosError, AxiosInstance, InternalAxiosRequestConfig } from 'axios';
import { logDebug, logWarn } from '../utils/logger';

const DEFAULT_PROD_API_URL = 'https://www.diffusionprompt.net/api/v1';
const DEFAULT_DEV_API_URL = 'http://localhost:8000/api/v1';

const shouldForceHttps = (): boolean =>
  (typeof window !== 'undefined' && window.location.protocol === 'https:') || import.meta.env.PROD;

const sanitizeUrlProtocol = (url: string): string => {
  if (shouldForceHttps() && url.startsWith('http://')) {
    return url.replace(/^http:\/\//i, 'https://');
  }
  return url;
};

const resolveApiBaseUrl = (): string => {
  const envUrl = import.meta.env.VITE_API_URL?.trim();
  if (envUrl) {
    return sanitizeUrlProtocol(envUrl);
  }

  if (typeof window !== 'undefined') {
    const protocol = shouldForceHttps() ? 'https:' : window.location.protocol;
    return `${protocol}//${window.location.host}/api/v1`;
  }

  // Fallbacks for non-browser contexts (tests/build scripts)
  if (import.meta.env.DEV) {
    return DEFAULT_DEV_API_URL;
  }

  return DEFAULT_PROD_API_URL;
};

const API_BASE_URL = resolveApiBaseUrl();
logDebug('[API Base URL]', API_BASE_URL);

const API_KEY = (() => {
  const key = import.meta.env.VITE_API_KEY;
  if (!key) {
    logWarn('[API] Missing VITE_API_KEY environment variable. Requests may be rejected.');
  }
  return key ?? '';
})();

const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,
});

api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('auth_token');

    if (config.headers) {
      if (API_KEY) {
        config.headers['X-API-Key'] = API_KEY;
      }
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    }

    logDebug('[API Request]', config.method?.toUpperCase(), config.url);
    if (config.baseURL) {
      logDebug('[API Base]', config.baseURL);
    }
    return config;
  },
  (error) => Promise.reject(error)
);

api.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    const status = error.response?.status;
    const requestUrl = error.config?.url ?? '';

    if (status === 401 && !requestUrl.includes('/auth/login')) {
      localStorage.removeItem('auth_token');
      localStorage.removeItem('user');
      window.location.href = '/login';
      return Promise.reject(error);
    }

    return Promise.reject(error);
  }
);

export const handleApiError = (error: unknown): string => {
  if (axios.isAxiosError(error)) {
    if (error.response?.data?.detail) {
      return error.response.data.detail;
    }
    return error.message;
  }
  return 'An unexpected error occurred';
};

export default api;
