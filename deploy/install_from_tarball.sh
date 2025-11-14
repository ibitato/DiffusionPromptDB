#!/bin/bash
# Install from tarball (sin necesidad de GitHub)
set -e

echo "🚀 Instalando desde tarball..."

# Extraer
cd /var/www
tar -xzf /root/diffusionpromptdb.tar.gz
mv /var/www /var/www/diffusionprompt 2>/dev/null || mkdir -p diffusionprompt && tar -xzf /root/diffusionpromptdb.tar.gz -C diffusionprompt
cd /var/www/diffusionprompt

echo "✅ Código extraído. Continuando con setup..."

# Python venv
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -r src/batch_analyzer/requirements.txt

# Secrets
JWT=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
API=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")

# Backend .env
cd src/api
cat > .env << EOF
JWT_SECRET_KEY="$JWT"
API_KEYS='["$API"]'
CORS_ORIGINS='["https://www.diffusionprompt.net"]'
HOST="0.0.0.0"
PORT=8000
RELOAD=false
LOG_LEVEL="WARNING"
EOF

# Frontend
cd ../../frontend
npm install
cat > .env << EOF
VITE_API_URL=https://www.diffusionprompt.net/api
EOF
npm run build

# Nginx
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/nginx/ssl/temp.key \
    -out /etc/nginx/ssl/temp.crt \
    -subj "/C=ES/CN=www.diffusionprompt.net"

cat > /etc/nginx/sites-available/diffusionprompt.net << 'EOF'
server {
    listen 80; listen [::]:80;
    server_name www.diffusionprompt.net diffusionprompt.net;
    location /.well-known/acme-challenge/ { root /var/www/html; }
    location / { return 301 https://$server_name$request_uri; }
}
server {
    listen 443 ssl http2; listen [::]:443 ssl http2;
    server_name www.diffusionprompt.net diffusionprompt.net;
    ssl_certificate /etc/nginx/ssl/temp.crt;
    ssl_certificate_key /etc/nginx/ssl/temp.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    location / {
        root /var/www/diffusionprompt/frontend/dist;
        try_files $uri /index.html;
    }
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
EOF

ln -sf /etc/nginx/sites-available/diffusionprompt.net /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Systemd
cat > /etc/systemd/system/diffusionprompt-api.service << EOF
[Unit]
Description=DiffusionPrompt API
[Service]
User=www-data
WorkingDirectory=/var/www/diffusionprompt/src/api
Environment="PATH=/var/www/diffusionprompt/.venv/bin"
ExecStart=/var/www/diffusionprompt/.venv/bin/python start_server.py
Restart=on-failure
[Install]
WantedBy=multi-user.target
EOF

chown -R www-data:www-data /var/www/diffusionprompt
systemctl daemon-reload
systemctl enable diffusionprompt-api
systemctl start diffusionprompt-api
systemctl restart nginx

echo "✅ ¡Completado!"
echo "Secrets generados:"
echo "JWT: $JWT"
echo "API: $API"
