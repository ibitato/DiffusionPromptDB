# 🚀 Guía de Deployment - Servidor Ubuntu

## 📋 Información del Servidor

- **IP**: 77.42.30.232
- **User**: root
- **Password Inicial**: 7nqtkXjEPfN4ghcHsg7g
- **OS**: Ubuntu 22.04
- **RAM**: 4GB
- **Location**: Helsinki

---

## 🎯 PASOS DE DEPLOYMENT

### Paso 1: Conectar al Servidor

```bash
ssh root@77.42.30.232
# Password: 7nqtkXjEPfN4ghcHsg7g
# Te pedirá cambiar la contraseña en el primer login
```

### Paso 2: Subir y Ejecutar el Script

#### Opción A: Desde tu máquina local

```bash
# Subir el script al servidor
scp deploy/server_setup.sh root@77.42.30.232:/root/

# Conectar y ejecutar
ssh root@77.42.30.232
cd /root
chmod +x server_setup.sh
sudo ./server_setup.sh
```

#### Opción B: Directamente en el servidor

```bash
# Ya conectado al servidor
cd /root

# Descargar el script desde GitHub
wget https://raw.githubusercontent.com/ibitato/DiffusionPromptDB/master/deploy/server_setup.sh

# O crear el archivo manualmente
nano server_setup.sh
# Copiar y pegar el contenido de server_setup.sh

# Dar permisos de ejecución
chmod +x server_setup.sh

# Ejecutar
sudo ./server_setup.sh
```

### Paso 3: El Script Hará Automáticamente

1. ✅ Actualizar sistema Ubuntu
2. ✅ Instalar Python, Node.js, Nginx, etc.
3. ✅ Configurar firewall (UFW)
4. ✅ Clonar repositorio desde GitHub
5. ✅ Crear virtualenv e instalar dependencias
6. ✅ Generar JWT secret y API key seguros
7. ✅ Configurar backend .env
8. ✅ Instalar y build frontend
9. ✅ Configurar Nginx
10. ✅ Crear systemd service

**Tiempo estimado**: 10-15 minutos

### Paso 4: Configurar DNS

En tu proveedor de dominio (donde compraste diffusionprompt.net):

```
Tipo: A
Host: www
Valor: 77.42.30.232
TTL: 3600

Tipo: A  
Host: @
Valor: 77.42.30.232
TTL: 3600
```

**Espera**: 5-30 minutos para propagación DNS

### Paso 5: Verificar DNS

```bash
# Desde tu máquina local
nslookup www.diffusionprompt.net
# Debe devolver: 77.42.30.232

ping www.diffusionprompt.net
# Debe responder desde 77.42.30.232
```

### Paso 6: Configurar SSL (DESPUÉS de DNS)

```bash
# En el servidor
sudo certbot --nginx -d www.diffusionprompt.net -d diffusionprompt.net

# Seguir el wizard:
# 1. Ingresar email
# 2. Aceptar términos
# 3. Elegir opción 2 (redirect HTTP a HTTPS)
```

### Paso 7: Verificar Servicios

```bash
# Verificar API backend
systemctl status diffusionprompt-api
# Debe mostrar: active (running)

# Verificar Nginx
systemctl status nginx
# Debe mostrar: active (running)

# Ver logs en tiempo real
tail -f /var/www/diffusionprompt/src/api/api.log
```

### Paso 8: Probar la Aplicación

```bash
# Desde tu máquina local

# Test sin SSL (antes de DNS)
curl http://77.42.30.232

# Test con SSL (después de DNS y SSL)
curl https://www.diffusionprompt.net

# Abrir en navegador
https://www.diffusionprompt.net
```

---

## 🔧 COMANDOS ÚTILES

### Gestión de Servicios

```bash
# Backend API
systemctl start diffusionprompt-api
systemctl stop diffusionprompt-api
systemctl restart diffusionprompt-api
systemctl status diffusionprompt-api

# Nginx
systemctl restart nginx
systemctl status nginx
nginx -t  # Test de configuración
```

### Logs

```bash
# API logs
tail -f /var/www/diffusionprompt/src/api/api.log

# Nginx access
tail -f /var/log/nginx/access.log

# Nginx errors
tail -f /var/log/nginx/error.log

# System logs del servicio
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
systemctl restart nginx
```

---

## 🆘 TROUBLESHOOTING

### Si el API no arranca:

```bash
# Ver logs del servicio
journalctl -u diffusionprompt-api -n 50

# Ver si el puerto está en uso
netstat -tulpn | grep 8000

# Probar manualmente
cd /var/www/diffusionprompt/src/api
source ../../.venv/bin/activate
python start_server.py
```

### Si Nginx muestra 502 Bad Gateway:

```bash
# Verificar que el API esté corriendo
systemctl status diffusionprompt-api

# Reiniciar ambos servicios
systemctl restart diffusionprompt-api
systemctl restart nginx
```

### Si SSL falla:

```bash
# Verificar DNS primero
nslookup www.diffusionprompt.net

# Reintentar certbot
sudo certbot --nginx -d www.diffusionprompt.net -d diffusionprompt.net

# Ver logs de certbot
tail -f /var/log/letsencrypt/letsencrypt.log
```

---

## 📊 VERIFICACIÓN FINAL

Después de completar todos los pasos, verifica:

- [ ] API responde en: https://www.diffusionprompt.net/api/docs
- [ ] Frontend carga en: https://www.diffusionprompt.net
- [ ] Login funciona correctamente
- [ ] Dashboard muestra estadísticas
- [ ] Búsqueda funciona
- [ ] SSL válido (candado verde en navegador)
- [ ] Servicios auto-arrancan después de reboot

---

## 🔐 CREDENCIALES GENERADAS

El script genera automáticamente:
- **JWT_SECRET_KEY**: Se mostrará en el output del script
- **API_KEY**: Se mostrará en el output del script

**⚠️ IMPORTANTE**: Guarda estas credenciales en un lugar seguro (no en el repositorio).

---

## 📞 SOPORTE

Si tienes problemas:
1. Revisa logs: `tail -f /var/www/diffusionprompt/src/api/api.log`
2. Verifica servicios: `systemctl status diffusionprompt-api`
3. Test de Nginx: `nginx -t`
4. Contacta al equipo de desarrollo

---

**Creado**: 14 de Noviembre de 2025
**Versión**: 1.0.0
