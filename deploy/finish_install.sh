#!/bin/bash
# Completar instalación
cd /var/www/diffusionprompt

# Nginx config
cat > /etc/nginx/sites-available/diffusionprompt.net << 'EOF'
server {
    listen 80 default_server;
    listen [::]:80 default_server;
    server_name _;
    location / { return 301 https://$host$request_uri; }
}
server {
    listen 443 ssl http2 default_server;
    listen [::]:443 ssl http2 default_server;
    server_name _;
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
    }
    gzip on;
}
EOF

ln -sf /etc/nginx/sites-available/diffusionprompt.net /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl restart nginx

# Systemd
cat > /etc/systemd/system/diffusionprompt-api.service << 'EOF'
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

echo "✅ ¡Deployment completado!"
echo "Accede a: http://77.42.30.232"
systemctl status diffusionprompt-api --no-pager
systemctl status nginx --no-pager
