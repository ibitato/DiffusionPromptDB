#!/bin/bash
# Fix Nginx config
cat > /etc/nginx/sites-available/diffusionprompt.net << 'NGINXEOF'
server {
    listen 80;
    server_name www.diffusionprompt.net diffusionprompt.net;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name www.diffusionprompt.net diffusionprompt.net;
    
    ssl_certificate /etc/letsencrypt/live/www.diffusionprompt.net/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/www.diffusionprompt.net/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    
    root /var/www/diffusionprompt/frontend/dist;
    index index.html;
    
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    location /api/ {
        proxy_pass http://localhost:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    add_header Strict-Transport-Security "max-age=31536000" always;
    gzip on;
}
NGINXEOF

nginx -t && systemctl reload nginx && echo "✅ Nginx corregido"
