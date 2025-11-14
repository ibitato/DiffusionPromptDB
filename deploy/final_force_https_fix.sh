#!/bin/bash
# FINAL Force HTTPS Fix - Elimina TODA configuración y reconstruye desde cero

set -e

SERVER_USER="root"
SERVER_IP="77.42.30.232"

echo "🚨 FINAL FORCE HTTPS FIX - COMPLETE REBUILD"
echo "============================================"
echo ""

# Execute directly on server
ssh "$SERVER_USER@$SERVER_IP" << 'ENDSSH'
set -e

cd /var/www/diffusionprompt

echo "1️⃣ ELIMINANDO TODA CONFIGURACIÓN ANTERIOR..."
echo "   Eliminando TODOS los archivos .env"
rm -f frontend/.env
rm -f frontend/.env.*
echo "   ✅ Archivos .env eliminados"
echo ""

echo "2️⃣ CREANDO SOLO .env.production..."
cat > frontend/.env.production << 'EOF'
# Production - NO API URL OVERRIDE
# The app will auto-detect HTTPS
VITE_API_KEY=demo-read-key-12345
EOF
echo "   ✅ .env.production creado (sin VITE_API_URL)"
echo ""

echo "3️⃣ ACTUALIZANDO api.ts CON LÓGICA ULTRA-SIMPLE..."
cat > frontend/src/services/api.ts << 'EOF'
/**
 * API Configuration - FORCE HTTPS VERSION
 */

import axios, { AxiosError, AxiosInstance, InternalAxiosRequestConfig } from 'axios';

// ULTRA SIMPLE: Always use HTTPS except on localhost
const isLocalhost = window.location.hostname === 'localhost' || 
                   window.location.hostname === '127.0.0.1';

const API_BASE_URL = isLocalhost 
  ? 'http://localhost:8000/api/v1'
  : `https://${window.location.hostname}/api/v1`;

// Debug log
console.log('[API Config FINAL]', {
  hostname: window.location.hostname,
  isLocalhost: isLocalhost,
  apiUrl: API_BASE_URL
});

// Create axios instance
const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
    'Cache-Control': 'no-cache',
    Pragma: 'no-cache',
  },
  timeout: 10000,
});

// Request interceptor
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('auth_token');
    const apiKey = 'demo-read-key-12345';

    if (config.headers) {
      config.headers['X-API-Key'] = apiKey;
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

// Response interceptor
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('auth_token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }

    if (error.response?.status === 403) {
      console.error('Access forbidden');
    }

    if (error.response?.status === 429) {
      console.error('Rate limit exceeded. Please try again later.');
    }

    if (error.response?.status === 500) {
      console.error('Server error. Please try again later.');
    }

    return Promise.reject(error);
  }
);

export const handleApiError = (error: unknown): string => {
  if (axios.isAxiosError(error)) {
    if (error.response?.data?.detail) {
      return error.response.data.detail;
    }

    if (error.code === 'ECONNABORTED') {
      return 'Request timeout. Please try again.';
    }

    if (error.message === 'Network Error') {
      return 'Network error. Please check your connection.';
    }

    return error.message;
  }

  return 'An unexpected error occurred';
};

export default api;
EOF
echo "   ✅ api.ts actualizado con lógica ultra-simple"
echo ""

echo "4️⃣ LIMPIEZA TOTAL..."
cd frontend
rm -rf dist
rm -rf node_modules/.cache
rm -rf .parcel-cache
echo "   ✅ Limpieza completada"
echo ""

echo "5️⃣ VERIFICANDO QUE NO HAY .env..."
echo "   Archivos .env* actuales:"
ls -la .env* 2>/dev/null || echo "   Ninguno (PERFECTO!)"
echo ""

echo "6️⃣ REBUILD COMPLETO..."
NODE_ENV=production npm run build

if [ ! -d "dist" ]; then
    echo "❌ Build falló!"
    exit 1
fi
echo "   ✅ Build completado"
echo ""

echo "7️⃣ VERIFICACIÓN FINAL..."
echo "   Buscando 'http://www' en el build:"
if grep -r "http://www" dist/ 2>/dev/null | grep -v "https://www"; then
    echo "   ⚠️ TODAVÍA HAY REFERENCIAS HTTP"
else
    echo "   ✅ NO HAY REFERENCIAS HTTP (EXCELENTE!)"
fi
echo ""

echo "8️⃣ LIMPIANDO CACHÉS..."
rm -rf /var/cache/nginx/*
# Clear any CDN/browser cache headers
find dist -name "*.js" -exec touch {} \;
echo "   ✅ Cachés limpiados"
echo ""

echo "9️⃣ REINICIANDO TODO..."
systemctl restart diffusionprompt-api
systemctl restart nginx
echo "   ✅ Servicios reiniciados"
echo ""

echo "============================================"
echo "✅ FINAL FIX COMPLETADO!"
echo "============================================"
echo ""
echo "IMPORTANTE: El navegador DEBE limpiar su caché:"
echo ""
echo "1. Cierra TODAS las pestañas de diffusionprompt.net"
echo "2. Abre Chrome/Edge"
echo "3. Presiona: Ctrl+Shift+Delete"
echo "4. Selecciona: TODO el tiempo"
echo "5. Marca: Cookies y Caché"
echo "6. Click en Borrar datos"
echo "7. Abre en modo incógnito"
echo "8. Visita: https://www.diffusionprompt.net"
echo ""
ENDSSH

echo ""
echo "✅ Script ejecutado en el servidor"
echo ""
echo "🎯 PRÓXIMO PASO CRÍTICO:"
echo "   1. Limpia COMPLETAMENTE el caché del navegador"
echo "   2. Usa modo incógnito"
echo "   3. Visita: https://www.diffusionprompt.net"
echo "   4. Abre DevTools inmediatamente (F12)"
echo "   5. Busca en Console: [API Config FINAL]"
echo "      Debe mostrar: apiUrl: 'https://www.diffusionprompt.net/api/v1'"
