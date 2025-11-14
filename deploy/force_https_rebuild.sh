#!/bin/bash
# Force HTTPS rebuild - Solución definitiva para Mixed Content

set -e

echo "🔧 FORCE HTTPS REBUILD - Solución Definitiva"
echo "=============================================="
echo ""

# Navegar al directorio
cd /var/www/diffusionprompt

echo "1️⃣ Limpiando configuración anterior..."
echo "   Eliminando TODOS los archivos .env del frontend"
rm -f frontend/.env
rm -f frontend/.env.local
rm -f frontend/.env.development
rm -f frontend/.env.production.local

# Mantener solo .env.production
echo "   Creando .env.production limpio"
cat > frontend/.env.production << 'EOF'
# Production Environment Configuration
# DO NOT set VITE_API_URL - Let the app auto-detect
# This ensures HTTPS is always used in production

# API Key for read-only operations
VITE_API_KEY=demo-read-key-12345
EOF

echo "✅ Configuración limpiada"
echo ""

echo "2️⃣ Actualizando api.ts con lógica robusta..."
cat > frontend/src/services/api.ts << 'EOF'
/**
 * API Configuration
 * Axios instance configured for the backend API
 */

import axios, { AxiosError, AxiosInstance, InternalAxiosRequestConfig } from 'axios';

// API Base URL - Force HTTPS in production, HTTP in development
// Simplified logic to avoid any configuration issues
const API_BASE_URL = (() => {
  // If running on localhost, use development URL
  if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    return import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';
  }
  
  // For any other hostname (production), force HTTPS
  // This ensures we ALWAYS use HTTPS in production, regardless of any config
  return `https://${window.location.hostname}/api/v1`;
})();

// Debug logging (will be removed in production build by most minifiers)
if (typeof console !== 'undefined' && console.log) {
  console.log('[API Config]', {
    hostname: window.location.hostname,
    protocol: window.location.protocol,
    apiUrl: API_BASE_URL,
    mode: import.meta.env.MODE,
    viteApiUrl: import.meta.env.VITE_API_URL
  });
}

// Create axios instance
const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
    'Cache-Control': 'no-cache',
    Pragma: 'no-cache',
  },
  timeout: 10000, // 10 seconds
});

// Request interceptor - Add JWT token AND API key to requests
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('auth_token');
    const apiKey = import.meta.env.VITE_API_KEY || 'demo-read-key-12345';

    if (config.headers) {
      // Always add API key for catalog/search endpoints
      config.headers['X-API-Key'] = apiKey;

      // Add JWT token if available (for write operations)
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
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
EOF

echo "✅ api.ts actualizado"
echo ""

echo "3️⃣ Limpiando builds anteriores..."
cd frontend
rm -rf dist
rm -rf node_modules/.cache
echo "✅ Limpieza completada"
echo ""

echo "4️⃣ Reconstruyendo frontend..."
npm run build

if [ ! -d "dist" ]; then
    echo "❌ Error: Build falló"
    exit 1
fi

echo "✅ Build completado"
echo ""

echo "5️⃣ Verificando el nuevo build..."
echo "   Buscando referencias HTTP incorrectas:"
if grep -r "http://www.diffusionprompt.net" dist/ 2>/dev/null; then
    echo "   ⚠️ ADVERTENCIA: Se encontraron referencias HTTP"
else
    echo "   ✅ No se encontraron referencias HTTP (BUENO!)"
fi
echo ""

echo "6️⃣ Limpiando caché de nginx..."
# Clear nginx cache if exists
rm -rf /var/cache/nginx/*
echo "✅ Caché limpiado"
echo ""

echo "7️⃣ Reiniciando servicios..."
systemctl restart nginx
echo "✅ Nginx reiniciado"
echo ""

echo "=============================================="
echo "✅ REBUILD COMPLETADO CON ÉXITO!"
echo "=============================================="
echo ""
echo "📋 Próximos pasos:"
echo "   1. Limpiar caché del navegador (Ctrl+Shift+Delete)"
echo "   2. Abrir en modo incógnito"
echo "   3. Visitar: https://www.diffusionprompt.net"
echo "   4. Verificar en DevTools > Console"
echo "      - Deberías ver: [API Config] con apiUrl: https://..."
echo "   5. Verificar en DevTools > Network"
echo "      - Todas las peticiones API deben usar HTTPS"
echo ""
echo "Si aún ves errores, ejecuta: ./deploy/diagnose_mixed_content.sh"
