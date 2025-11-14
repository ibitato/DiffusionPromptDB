import axios, {
  AxiosError,
  AxiosInstance,
  InternalAxiosRequestConfig,
} from 'axios';

const DEFAULT_PROD_API_URL = 'https://www.diffusionprompt.net/api/v1';
const DEFAULT_DEV_API_URL = 'http://localhost:8000/api/v1';

const shouldForceHttps = (): boolean =>
  typeof window !== 'undefined' && window.location.protocol === 'https:';

const sanitizeUrlProtocol = (url: string): string => {
  if (shouldForceHttps()) {
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

console.log('[API Base URL]', API_BASE_URL);

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
    const apiKey = 'REDACTED_API_KEY';

    if (config.headers) {
      config.headers['X-API-Key'] = apiKey;
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    }

    console.log('[API Request]', config.method?.toUpperCase(), config.url);
    return config;
  },
  (error) => Promise.reject(error)
);

api.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('auth_token');
      localStorage.removeItem('user');
      window.location.href = '/login';
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
