#!/bin/bash
# 🚀 DiffusionPromptDB - Production Server Setup Script
# Server: ubuntu-4gb-hel1-1
# IP: REDACTED_SERVER_IP

set -e  # Exit on error

echo "================================================================================"
echo "🚀 DiffusionPromptDB - Production Server Setup"
echo "================================================================================"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Variables
DOMAIN="www.diffusionprompt.net"
PROJECT_DIR="/var/www/diffusionprompt"
REPO_URL="https://github.com/ibitato/DiffusionPromptDB.git"

# Step 1: Update system
echo -e "\n${GREEN}[1/10] Actualizando sistema...${NC}"
apt update && apt upgrade -y

# Step 2: Install basic dependencies
echo -e "\n${GREEN}[2/10] Instalando dependencias básicas...${NC}"
apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    nginx \
    git \
    curl \
    ufw \
    certbot \
    python3-certbot-nginx \
    nodejs \
    npm \
    build-essential

# Step 3: Configure firewall
echo -e "\n${GREEN}[3/10] Configurando firewall...${NC}"
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
echo "y" | ufw enable

# Step 4: Clone repository
echo -e "\n${GREEN}[4/10] Clonando repositorio...${NC}"
mkdir -p /var/www
cd /var/www
if [ -d "$PROJECT_DIR" ]; then
    echo "Directorio ya existe, actualizando..."
    cd $PROJECT_DIR
    git pull
else
    git clone $REPO_URL $PROJECT_DIR
    cd $PROJECT_DIR
fi

# Step 5: Setup Python virtual environment
echo -e "\n${GREEN}[5/10] Configurando entorno Python...${NC}"
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install -r src/batch_analyzer/requirements.txt

# Step 6: Generate secrets
echo -e "\n${GREEN}[6/10] Generando secrets...${NC}"
JWT_SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
API_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")

echo "JWT_SECRET_KEY: $JWT_SECRET"
echo "API_KEY: $API_KEY"

# Step 7: Configure backend .env
echo -e "\n${GREEN}[7/10] Configurando backend .env...${NC}"
cd $PROJECT_DIR/src/api
cat > .env << EOF
# Production Configuration
JWT_SECRET_KEY="$JWT_SECRET"
JWT_ALGORITHM="HS256"
JWT_EXPIRE_MINUTES=60

# API Keys (cambiar en producción)
API_KEYS='["$API_KEY"]'

# CORS
CORS_ORIGINS='["https://www.diffusionprompt.net","https://diffusionprompt.net"]'

# Server
HOST="0.0.0.0"
PORT=8000
RELOAD=false

# Database
PROMPTS_DB_PATH="database/prompts_catalog.db"
CATALOG_DB_PATH="database/prompts_catalog.db"

# Rate Limiting
RATE_LIMIT_PER_MINUTE=100
RATE_LIMIT_PER_HOUR=1000

# Logging
LOG_LEVEL="WARNING"
LOG_FILE="api.log"
EOF

echo "✅ Backend .env configurado"

# Step 8: Setup frontend
echo -e "\n${GREEN}[8/10] Configurando y building frontend...${NC}"
cd $PROJECT_DIR/frontend
npm install
cat > .env << EOF
VITE_API_URL=https://www.diffusionprompt.net/api
VITE_APP_URL=https://www.diffusionprompt.net
EOF
npm run build

# Step 9: Configure Nginx
echo -e "\n${GREEN}[9/10] Configurando Nginx...${NC}"
cat > /etc/nginx/sites-available/diffusionprompt.net << 'EOF'
server {
    listen 80;
    server_name www.diffusionprompt.net diffusionprompt.net;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name www.diffusionprompt.net diffusionprompt.net;

    # SSL certificates (configurar después con certbot)
    # ssl_certificate /etc/letsencrypt/live/www.diffusionprompt.net/fullchain.pem;
    # ssl_certificate_key /etc/letsencrypt/live/www.diffusionprompt.net/privkey.pem;

    # Frontend
    location / {
        root /var/www/diffusionprompt/frontend/dist;
        try_files $uri $uri/ /index.html;
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
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
}
EOF

ln -sf /etc/nginx/sites-available/diffusionprompt.net /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t

# Step 10: Create systemd service
echo -e "\n${GREEN}[10/10] Configurando systemd service...${NC}"
cat > /etc/systemd/system/diffusionprompt-api.service << EOF
[Unit]
Description=DiffusionPrompt API
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=$PROJECT_DIR/src/api
Environment="PATH=$PROJECT_DIR/.venv/bin"
ExecStart=$PROJECT_DIR/.venv/bin/python start_server.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Set permissions
chown -R www-data:www-data $PROJECT_DIR
chmod -R 755 $PROJECT_DIR

# Enable and start services
systemctl daemon-reload
systemctl enable diffusionprompt-api
systemctl start diffusionprompt-api
systemctl restart nginx

echo -e "\n${GREEN}✅ Setup completado!${NC}"
echo ""
echo "================================================================================"
echo "📋 PRÓXIMOS PASOS:"
echo "================================================================================"
echo ""
echo "1. Configurar DNS:"
echo "   A Record: www.diffusionprompt.net -> REDACTED_SERVER_IP"
echo "   A Record: diffusionprompt.net -> REDACTED_SERVER_IP"
echo ""
echo "2. Configurar SSL (después de DNS):"
echo "   sudo certbot --nginx -d www.diffusionprompt.net -d diffusionprompt.net"
echo ""
echo "3. Verificar servicios:"
echo "   systemctl status diffusionprompt-api"
echo "   systemctl status nginx"
echo ""
echo "4. Verificar logs:"
echo "   tail -f $PROJECT_DIR/src/api/api.log"
echo "   tail -f /var/log/nginx/error.log"
echo ""
echo "5. Acceder a la aplicación:"
echo "   http://REDACTED_SERVER_IP (temporal, hasta que DNS esté configurado)"
echo "   https://www.diffusionprompt.net (después de SSL)"
echo ""
echo "================================================================================"
echo "🎉 ¡Servidor listo!"
echo "================================================================================"
