#!/bin/bash
# Diagnóstico del problema de Mixed Content en producción

echo "🔍 Diagnóstico de Mixed Content en Producción"
echo "=============================================="
echo ""

# Verificar archivos .env
echo "📁 Archivos .env encontrados:"
ls -la /var/www/diffusionprompt/frontend/.env* 2>/dev/null || echo "  No .env files found in frontend"
echo ""

# Verificar contenido de .env files
echo "📄 Contenido de archivos .env:"
for file in /var/www/diffusionprompt/frontend/.env*; do
    if [ -f "$file" ]; then
        echo "  File: $file"
        grep -E "VITE_API_URL|API_URL" "$file" 2>/dev/null || echo "    No API URL config found"
        echo ""
    fi
done

# Verificar el build actual
echo "🔨 Verificando build actual:"
echo "  Fecha de build:"
ls -la /var/www/diffusionprompt/frontend/dist/ | head -5
echo ""

# Buscar referencias HTTP en el build
echo "🔗 Buscando referencias HTTP en el build:"
echo "  Buscando 'http://www.diffusionprompt.net':"
grep -r "http://www.diffusionprompt.net" /var/www/diffusionprompt/frontend/dist/ 2>/dev/null | head -3 || echo "    No encontrado"
echo ""
echo "  Buscando 'http://' general:"
grep -r "http://.*api/v1" /var/www/diffusionprompt/frontend/dist/assets/*.js 2>/dev/null | head -3 || echo "    No encontrado"
echo ""

# Verificar el archivo api.ts actual
echo "📝 Verificando api.ts:"
if [ -f "/var/www/diffusionprompt/frontend/src/services/api.ts" ]; then
    echo "  Primeras líneas relevantes de api.ts:"
    grep -A 5 "API_BASE_URL" /var/www/diffusionprompt/frontend/src/services/api.ts | head -10
else
    echo "  api.ts no encontrado"
fi
echo ""

# Verificar nginx config
echo "⚙️ Configuración de Nginx:"
grep -E "proxy_pass|location /api" /etc/nginx/sites-enabled/* 2>/dev/null | head -5
echo ""

# Estado de servicios
echo "✅ Estado de servicios:"
systemctl status diffusionprompt-api --no-pager | head -5
systemctl status nginx --no-pager | head -5
echo ""

echo "=============================================="
echo "📊 Resumen:"
echo ""
echo "Si ves referencias a 'http://' en el build, necesitas reconstruir."
echo "Si ves archivos .env con VITE_API_URL, podrían estar interfiriendo."
echo ""
echo "Para arreglar, ejecuta: ./deploy/force_https_rebuild.sh"
