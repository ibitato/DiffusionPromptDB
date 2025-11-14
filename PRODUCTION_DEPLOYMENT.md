# 🚀 Guía de Despliegue a Producción - DiffusionPrompt.net

## 📌 Información del Dominio

- **Dominio Principal**: `www.diffusionprompt.net`
- **Dominio Secundario**: `diffusionprompt.net`
- **SSL/HTTPS**: Requerido

---

## ✅ CHECKLIST PRE-DESPLIEGUE

### 1. **Variables de Entorno** 🔐
```bash
# Generar nuevo SECRET_KEY para producción
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Actualizar `src/api/.env`:
```env
JWT_SECRET_KEY="[NUEVO-SECRET-KEY-GENERADO]"
ENVIRONMENT="production"
CORS_ORIGINS='["https://www.diffusionprompt.net","https://diffusionprompt.net"]'
```

### 2. **Frontend Configuration** 🎨
Actualizar `frontend/.env`:
```env
VITE_API_URL=https://api.diffusionprompt.net
VITE_APP_URL=https://www.diffusionprompt.net
```

### 3. **Base de Datos** 💾
Para producción, considerar PostgreSQL:
```env
DATABASE_URL="postgresql://user:password@localhost:5432/diffusionpromptdb"
```

### 4. **Certificado SSL** 🔒
```bash
# Con Let's Encrypt (gratuito)
sudo certbot --nginx -d www.diffusionprompt.net -d diffusionprompt.net
```

---

## 📦 CONFIGURACIÓN DEL SERVIDOR

### Nginx Configuration
```nginx
# /etc/nginx/sites-available/diffusionprompt.net
server {
    listen 80;
    server_name www.diffusionprompt.net diffusionprompt.net;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name www.diffusionprompt.net diffusionprompt.net;

    ssl_certificate /etc/letsencrypt/live/www.diffusionprompt.net/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/www.diffusionprompt.net/privkey.pem;

    # Frontend
    location / {
        root /var/www/diffusionprompt.net/frontend/dist;
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
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
}
```

### Systemd Service (Backend)
```ini
# /etc/systemd/system/diffusionprompt-api.service
[Unit]
Description=DiffusionPrompt API
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/diffusionprompt.net/src/api
Environment="PATH=/var/www/diffusionprompt.net/venv/bin"
ExecStart=/var/www/diffusionprompt.net/venv/bin/python start_server.py
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

---

## 🚀 PASOS DE DESPLIEGUE

### 1. Preparar el Servidor
```bash
# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar dependencias
sudo apt install python3-pip python3-venv nginx certbot python3-certbot-nginx postgresql -y
```

### 2. Clonar y Configurar
```bash
# Clonar repositorio
cd /var/www
sudo git clone https://github.com/yourusername/DiffusionPromptDB.git diffusionprompt.net
cd diffusionprompt.net

# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
cd frontend && npm install && npm run build
```

### 3. Configurar Variables de Entorno
```bash
# Backend
cd /var/www/diffusionprompt.net/src/api
cp .env.example .env
nano .env  # Actualizar con valores de producción

# Frontend (si necesario)
cd /var/www/diffusionprompt.net/frontend
cp .env.example .env
nano .env
```

### 4. Iniciar Servicios
```bash
# Habilitar y arrancar backend
sudo systemctl enable diffusionprompt-api
sudo systemctl start diffusionprompt-api

# Configurar Nginx
sudo ln -s /etc/nginx/sites-available/diffusionprompt.net /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 5. Configurar SSL
```bash
sudo certbot --nginx -d www.diffusionprompt.net -d diffusionprompt.net
```

---

## 🔒 SEGURIDAD ADICIONAL

### Firewall (UFW)
```bash
sudo ufw allow 22/tcp  # SSH
sudo ufw allow 80/tcp  # HTTP
sudo ufw allow 443/tcp # HTTPS
sudo ufw enable
```

### Fail2ban
```bash
sudo apt install fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

### Monitoreo
```bash
# Instalar herramientas de monitoreo
sudo apt install htop nethogs iotop

# Logs
tail -f /var/log/nginx/access.log
tail -f /var/www/diffusionprompt.net/src/api/api.log
```

---

## 📊 VERIFICACIÓN POST-DESPLIEGUE

### 1. Test de Conectividad
```bash
# HTTPS redirect
curl -I http://www.diffusionprompt.net
# Should return 301 redirect to HTTPS

# API endpoint
curl https://www.diffusionprompt.net/api/v1/health
# Should return {"status": "healthy"}
```

### 2. Test de Seguridad
- SSL Labs: https://www.ssllabs.com/ssltest/analyze.html?d=www.diffusionprompt.net
- Security Headers: https://securityheaders.com/?q=www.diffusionprompt.net

### 3. Test de Funcionalidad
- [ ] Login funciona correctamente
- [ ] CORS permite requests desde www.diffusionprompt.net
- [ ] JWT tokens funcionan
- [ ] Rate limiting activo
- [ ] Logs registrándose correctamente

---

## 🔧 MANTENIMIENTO

### Actualizar Código
```bash
cd /var/www/diffusionprompt.net
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
cd frontend && npm install && npm run build
sudo systemctl restart diffusionprompt-api
sudo systemctl restart nginx
```

### Backup Base de Datos
```bash
# Si usas PostgreSQL
pg_dump diffusionpromptdb > backup_$(date +%Y%m%d).sql

# Si usas SQLite
cp database/prompts_catalog.db backups/prompts_catalog_$(date +%Y%m%d).db
```

### Renovar SSL
```bash
# Se renueva automáticamente con certbot
# Verificar con:
sudo certbot renew --dry-run
```

---

## 📞 CONTACTO Y SOPORTE

- **Dominio**: www.diffusionprompt.net
- **API**: https://www.diffusionprompt.net/api
- **Documentación API**: https://www.diffusionprompt.net/api/docs

---

**Última actualización**: 14 de Noviembre de 2024
**Estado**: Listo para despliegue
