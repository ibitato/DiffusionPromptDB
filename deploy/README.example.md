# 🚀 Guía de Deployment - Servidor Ubuntu

## 📋 Información del Servidor

- **IP**: [TU-IP-AQUÍ]
- **User**: root
- **Password Inicial**: [CAMBIAR-EN-PRIMER-LOGIN]
- **OS**: Ubuntu 22.04
- **RAM**: 4GB+
- **Location**: [TU-LOCATION]

---

## 🎯 PASOS DE DEPLOYMENT

### Paso 1: Conectar al Servidor

```bash
ssh root@[TU-IP-AQUÍ]
# Cambiar contraseña en el primer login
```

### Paso 2: Ejecutar Script de Setup

```bash
# Descargar script desde GitHub
cd /root
wget https://raw.githubusercontent.com/ibitato/DiffusionPromptDB/master/deploy/server_setup.sh

# Dar permisos
chmod +x server_setup.sh

# Ejecutar (toma ~15 minutos)
sudo ./server_setup.sh
```

### Paso 3: El Script Hará Automáticamente

1. ✅ Actualizar sistema Ubuntu
2. ✅ Instalar Python, Node.js, Nginx, certbot, etc.
3. ✅ Configurar firewall (UFW)
4. ✅ Clonar repositorio
5. ✅ Instalar dependencias Python y Node
6. ✅ Generar secrets seguros (JWT, API keys)
7. ✅ Configurar backend .env
8. ✅ Build frontend
9. ✅ Configurar Nginx con HTTPS (443)
10. ✅ Crear systemd service

**Tiempo**: 10-15 minutos

### Paso 4: Configurar DNS

En tu proveedor de dominio:

```
Tipo: A
Host: www
Valor: [TU-IP-AQUÍ]

Tipo: A  
Host: @
Valor: [TU-IP-AQUÍ]
```

Espera 5-30 min para propagación.

### Paso 5: Configurar SSL (DESPUÉS de DNS)

```bash
# En el servidor
sudo certbot --nginx -d www.diffusionprompt.net -d diffusionprompt.net

# Seguir wizard:
# 1. Email
# 2. Aceptar términos
# 3. Redirect HTTP a HTTPS
```

### Paso 6: Verificar

```bash
# Servicios
systemctl status diffusionprompt-api
systemctl status nginx

# Logs
tail -f /var/www/diffusionprompt/src/api/api.log

# Abrir navegador
https://www.diffusionprompt.net
```

---

## 🔧 COMANDOS ÚTILES

### Gestión de Servicios

```bash
systemctl restart diffusionprompt-api
systemctl restart nginx
systemctl status diffusionprompt-api
```

### Logs

```bash
tail -f /var/www/diffusionprompt/src/api/api.log
tail -f /var/log/nginx/error.log
journalctl -u diffusionprompt-api -f
```

### Actualizar Código

```bash
cd /var/www/diffusionprompt
git pull
source .venv/bin/activate
pip install -r requirements.txt
cd frontend && npm install && npm run build
systemctl restart diffusionprompt-api
```

---

## 🆘 TROUBLESHOOTING

**API no arranca:**
```bash
journalctl -u diffusionprompt-api -n 50
```

**Nginx 502:**
```bash
systemctl restart diffusionprompt-api
systemctl restart nginx
```

**SSL falla:**
```bash
# Verificar DNS primero
nslookup www.diffusionprompt.net
sudo certbot --nginx -d www.diffusionprompt.net -d diffusionprompt.net
```

---

## 📊 VERIFICACIÓN FINAL

- [ ] API: https://www.diffusionprompt.net/api/docs
- [ ] Frontend: https://www.diffusionprompt.net
- [ ] Login funciona
- [ ] SSL válido (candado verde)
- [ ] Servicios auto-arrancan

---

**Versión**: 1.0.0
