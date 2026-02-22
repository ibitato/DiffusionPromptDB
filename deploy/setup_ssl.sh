#!/bin/bash
# Setup Let's Encrypt SSL con auto-renovación
set -e

echo "🔒 Configurando Let's Encrypt SSL..."

# Verificar que el dominio apunte al servidor
echo "Verificando DNS..."
IP=$(curl -s https://api.ipify.org)
DNS_IP=$(dig +short www.diffusionprompt.net | tail -n1)

if [ "$DNS_IP" != "$IP" ]; then
    echo "⚠️ ADVERTENCIA: DNS no apunta a este servidor"
    echo "   Servidor IP: $IP"
    echo "   DNS apunta a: $DNS_IP"
    echo ""
    echo "Por favor configura el DNS primero:"
    echo "   A Record: www.diffusionprompt.net -> $IP"
    echo "   A Record: diffusionprompt.net -> $IP"
    echo ""
    read -p "¿Continuar de todos modos? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Obtener certificado Let's Encrypt
echo "📩 Solicitando certificado Let's Encrypt..."
certbot --nginx \
    -d www.diffusionprompt.net \
    -d diffusionprompt.net \
    --non-interactive \
    --agree-tos \
    --email "${SSL_EMAIL:?Set SSL_EMAIL env var}" \
    --redirect

# Configurar auto-renovación (certbot ya lo hace automáticamente)
echo "🔄 Verificando auto-renovación..."
certbot renew --dry-run

# Configurar Nginx para SOLO HTTPS (443)
echo "🔧 Configurando Nginx para SOLO HTTPS (443)..."
cat > /etc/nginx/sites-available/diffusionprompt.net << 'EOF'
# HTTP - Solo redirect a HTTPS
server {
    listen 80;
    listen [::]:80;
    server_name www.diffusionprompt.net diffusionprompt.net;
    
    # Redirect TODO a HTTPS
    return 301 https://$server_name$request_uri;
}

# HTTPS 443 - Aplicación principal
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name www.diffusionprompt.net diffusionprompt.net;

    # Certificados Let's Encrypt (auto-configurados por certbot)
    ssl_certificate /etc/letsencrypt/live/www.diffusionprompt.net/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/www.diffusionprompt.net/privkey.pem;
    
    # SSL Configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Frontend
    location / {
        root /var/www/diffusionprompt/frontend/dist;
        try_files $uri $uri/ /index.html;
        
        # Cache static assets
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Security Headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
}
EOF

# Test y reload
nginx -t
systemctl reload nginx

echo ""
echo "✅ ¡SSL configurado exitosamente!"
echo ""
echo "================================================="
echo "📊 ESTADO DEL SISTEMA"
echo "================================================="
echo ""
echo "🔒 Certificado: Let's Encrypt VÁLIDO"
echo "🔄 Auto-renovación: Activa (cada 60 días)"
echo "🌐 Protocolo: SOLO HTTPS (puerto 443)"
echo "🔥 HTTP (80): Redirect a HTTPS"
echo ""
echo "================================================="
echo "🚀 ACCEDER A LA APLICACIÓN"
echo "================================================="
echo ""
echo "✅ https://www.diffusionprompt.net"
echo "✅ https://diffusionprompt.net"
echo "✅ API: https://www.diffusionprompt.net/api/docs"
echo ""
echo "================================================="
echo ""
