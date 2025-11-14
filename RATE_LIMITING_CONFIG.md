# 📊 Rate Limiting - Configuración Completa

## ✅ RATE LIMITING TOTALMENTE CONFIGURABLE

Fecha: 14 de Noviembre de 2024

---

## 🔧 CONFIGURACIÓN A TRAVÉS DE VARIABLES DE ENTORNO

Todos los límites de rate limiting ahora son **100% configurables** a través del archivo `.env`.

### 📝 Variables Disponibles

| Variable | Valor por Defecto | Descripción |
|----------|-------------------|-------------|
| `RATE_LIMIT_AUTH_LOGIN` | `5/minute` | Intentos de login (prevenir fuerza bruta) |
| `RATE_LIMIT_AUTH_REGISTER` | `3/minute` | Intentos de registro |
| `RATE_LIMIT_AUTH_RESET` | `3/hour` | Solicitudes de reset de contraseña |
| `RATE_LIMIT_SEARCH` | `30/minute` | Operaciones de búsqueda |
| `RATE_LIMIT_PUBLIC_READ` | `100/minute` | Acceso de lectura público |
| `RATE_LIMIT_CATALOG` | `60/minute` | Navegación del catálogo |
| `RATE_LIMIT_PROMPT_CREATE` | `10/minute` | Creación de prompts |
| `RATE_LIMIT_PROMPT_UPDATE` | `20/minute` | Actualización de prompts |
| `RATE_LIMIT_PROMPT_DELETE` | `10/minute` | Eliminación de prompts |
| `RATE_LIMIT_ADMIN` | `100/minute` | Operaciones de administrador |
| `RATE_LIMIT_HEALTH` | `10/minute` | Health checks |
| `RATE_LIMIT_DEFAULT` | `60/minute` | Límite por defecto |

---

## 🚀 CÓMO CONFIGURAR

### 1. **Editar el archivo `.env`**

```env
# Rate Limiting Configuration
RATE_LIMIT_AUTH_LOGIN="5/minute"        # Puedes cambiar a "10/minute" si quieres ser menos estricto
RATE_LIMIT_SEARCH="50/minute"           # Aumentar para más búsquedas
RATE_LIMIT_PUBLIC_READ="200/minute"     # Aumentar para más tráfico
```

### 2. **Formatos Soportados**

```env
# Por minuto
RATE_LIMIT_AUTH_LOGIN="5/minute"

# Por hora
RATE_LIMIT_AUTH_RESET="3/hour"

# Por día
RATE_LIMIT_BULK_EXPORT="100/day"

# Por segundo (para testing)
RATE_LIMIT_TEST="1/second"
```

### 3. **Reiniciar el Backend**

Después de cambiar los valores:
```bash
cd src/api
# Detener el servidor (Ctrl+C)
# Reiniciar
python start_server.py
```

---

## 📊 CONFIGURACIONES RECOMENDADAS

### Para Desarrollo
```env
RATE_LIMIT_AUTH_LOGIN="100/minute"      # Sin restricciones para testing
RATE_LIMIT_SEARCH="100/minute"          # Testing frecuente
RATE_LIMIT_PUBLIC_READ="1000/minute"    # Sin límites prácticamente
```

### Para Producción (Estricto)
```env
RATE_LIMIT_AUTH_LOGIN="3/minute"        # Muy estricto contra brute force
RATE_LIMIT_AUTH_REGISTER="1/minute"     # Prevenir spam de cuentas
RATE_LIMIT_SEARCH="20/minute"           # Limitar operaciones costosas
```

### Para API Pública
```env
RATE_LIMIT_PUBLIC_READ="60/hour"        # Límite por hora para usuarios gratuitos
RATE_LIMIT_AUTH_LOGIN="3/minute"        # Protección contra ataques
RATE_LIMIT_SEARCH="10/hour"             # Búsquedas limitadas
```

---

## 🎯 CASOS DE USO

### 1. **Aumentar límites para un evento**
Si esperas más tráfico temporal:
```env
RATE_LIMIT_PUBLIC_READ="500/minute"
RATE_LIMIT_SEARCH="100/minute"
```

### 2. **Modo mantenimiento**
Reducir límites durante mantenimiento:
```env
RATE_LIMIT_PUBLIC_READ="10/minute"
RATE_LIMIT_AUTH_LOGIN="1/minute"
```

### 3. **Testing de carga**
Desactivar límites para pruebas:
```env
RATE_LIMIT_DEFAULT="10000/minute"
RATE_LIMIT_AUTH_LOGIN="10000/minute"
```

---

## 🔒 SEGURIDAD

### Límites Mínimos Recomendados
```env
# NUNCA pongas estos valores más altos en producción
RATE_LIMIT_AUTH_LOGIN="10/minute"       # Máximo 10 intentos por minuto
RATE_LIMIT_AUTH_REGISTER="5/minute"     # Máximo 5 registros por minuto
RATE_LIMIT_AUTH_RESET="5/hour"          # Máximo 5 resets por hora
```

### Monitoreo
Los intentos bloqueados se registran en `api.log`:
```
WARNING: Rate limit exceeded for /api/v1/auth/login from IP 192.168.1.100
```

---

## 🛠️ TROUBLESHOOTING

### Problema: "429 Too Many Requests"
**Solución**: Aumentar el límite correspondiente en `.env`

### Problema: Los cambios no se aplican
**Solución**: 
1. Verificar que guardaste el archivo `.env`
2. Reiniciar el servidor
3. Verificar que no hay errores de sintaxis en `.env`

### Problema: Quiero límites diferentes por usuario
**Extensión futura** en `rate_limiting.py`:
```python
def get_custom_rate_limit(request):
    if user.is_premium:
        return "200/minute"
    return "60/minute"
```

---

## 📈 VENTAJAS DE LA CONFIGURABILIDAD

1. **Sin tocar código**: Cambios solo en `.env`
2. **Sin redeploy**: Solo reiniciar el servidor
3. **Por ambiente**: Diferentes valores para dev/staging/prod
4. **Respuesta rápida**: Ajustar límites ante ataques
5. **Testing fácil**: Cambiar valores para pruebas

---

## 🔄 VALORES POR DEFECTO

Si no configuras una variable, se usan estos valores:

```python
"auth_login": "5/minute"
"auth_register": "3/minute"
"auth_reset": "3/hour"
"public_read": "100/minute"
"search": "30/minute"
"catalog": "60/minute"
"prompt_create": "10/minute"
"prompt_update": "20/minute"
"prompt_delete": "10/minute"
"admin_operations": "100/minute"
"health": "10/minute"
"default": "60/minute"
```

---

## 📝 EJEMPLO COMPLETO

`.env` para producción en www.diffusionprompt.net:
```env
# Rate Limiting para Producción
RATE_LIMIT_AUTH_LOGIN="5/minute"        # Estricto contra brute force
RATE_LIMIT_AUTH_REGISTER="2/minute"     # Limitar creación de cuentas
RATE_LIMIT_AUTH_RESET="3/hour"          # Prevenir spam de reset
RATE_LIMIT_SEARCH="30/minute"           # Búsquedas moderadas
RATE_LIMIT_PUBLIC_READ="100/minute"     # Lectura pública normal
RATE_LIMIT_CATALOG="60/minute"          # Navegación normal
RATE_LIMIT_PROMPT_CREATE="5/minute"     # Limitar creación de contenido
RATE_LIMIT_PROMPT_UPDATE="10/minute"    # Actualizaciones moderadas
RATE_LIMIT_PROMPT_DELETE="5/minute"     # Limitar eliminaciones
RATE_LIMIT_ADMIN="200/minute"           # Admins con más libertad
RATE_LIMIT_HEALTH="10/minute"           # Health checks limitados
RATE_LIMIT_DEFAULT="60/minute"          # Por defecto moderado
```

---

**Configuración implementada**: 14 de Noviembre de 2024
**Sistema**: 100% Configurable vía variables de entorno
