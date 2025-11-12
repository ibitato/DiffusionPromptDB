# 🔐 Sistema de Autenticación - Configuración Completa

Este documento explica la configuración completa del sistema de autenticación entre frontend y backend.

## ✅ Backend - API de Login Implementada

### Archivos Creados

1. **`src/api/models/auth_models.py`** - Modelos Pydantic para autenticación
2. **`src/api/routers/auth.py`** - Endpoints de autenticación
3. **`src/api/main.py`** - Actualizado para incluir el router de auth

### Endpoint de Login

**URL:** `POST /api/v1/auth/login`

**Request Body:**
```json
{
  "username": "test",
  "password": "test"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "test",
    "email": "test@example.com",
    "role": "admin"
  }
}
```

### Usuarios Disponibles

El backend incluye 3 usuarios de prueba (en memoria):

| Usuario | Contraseña | Rol   | Email              |
|---------|-----------|-------|--------------------|
| test    | test      | admin | test@example.com   |
| admin   | admin     | admin | admin@example.com  |
| user    | user      | user  | user@example.com   |

⚠️ **IMPORTANTE:** En producción, usar una base de datos real y contraseñas hasheadas (bcrypt/argon2).

### Configuración JWT

Los tokens JWT se configuran en `src/api/config.py`:

```python
JWT_SECRET_KEY: str = "your-secret-key-here-change-in-production"
JWT_ALGORITHM: str = "HS256"
JWT_EXPIRE_MINUTES: int = 60  # Token expira en 60 minutos
```

## ✅ Frontend - Conectado a API Real

### Cambios Realizados

**`frontend/src/pages/LoginPage.tsx`:**
- ✅ Cambiado de `authService.mockLogin()` a `authService.login()`
- ✅ Ahora usa el endpoint real `/api/v1/auth/login`
- ✅ Maneja errores del servidor correctamente

### Flujo de Autenticación

1. **Usuario ingresa credenciales** → LoginPage
2. **Frontend envía POST** → `http://localhost:8000/api/v1/auth/login`
3. **Backend valida** → Verifica usuario y contraseña
4. **Backend responde** → Token JWT + información de usuario
5. **Frontend guarda** → Token en localStorage + usuario en Zustand
6. **Axios interceptor** → Añade token a todas las requests
7. **Navegación protegida** → Solo usuarios autenticados acceden

### Interceptores de Axios

**`frontend/src/services/api.ts`** incluye interceptores automáticos:

```typescript
// Request Interceptor - Añade token a headers
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response Interceptor - Maneja expiración
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expirado - logout automático
      localStorage.removeItem('auth_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);
```

## 🚀 Cómo Usar

### 1. Iniciar el Backend

```bash
cd src/api

# Instalar dependencias (si no están)
pip install -r requirements.txt

# Iniciar servidor
python main.py
```

Backend disponible en: **http://localhost:8000**

### 2. Iniciar el Frontend

```bash
cd frontend

# Instalar dependencias (si no están)
npm install

# Configurar variables de entorno
cp .env.example .env

# Iniciar servidor de desarrollo
npm run dev
```

Frontend disponible en: **http://localhost:5173**

### 3. Probar el Login

1. Abre el navegador en `http://localhost:5173`
2. Serás redirigido automáticamente a `/login`
3. Ingresa credenciales:
   - Usuario: `test`
   - Contraseña: `test`
4. Click en "Iniciar Sesión"
5. Serás redirigido al Dashboard con stats reales

## 🔍 Verificación del Login

### Usando cURL

```bash
# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test"}'

# Respuesta esperada:
{
  "access_token": "eyJ0eXAiOi...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "test",
    "email": "test@example.com",
    "role": "admin"
  }
}
```

### Usando el Token

```bash
# Obtener prompts con el token
curl http://localhost:8000/api/v1/prompts \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### En el Frontend

Abre la consola del navegador (F12) y verifica:

```javascript
// Ver token guardado
localStorage.getItem('auth_token')

// Ver usuario guardado
localStorage.getItem('user')
```

## 🔒 Seguridad

### Configuración Actual (Desarrollo)

- ✅ JWT tokens con expiración
- ✅ CORS configurado
- ✅ Interceptores para auth automática
- ✅ Protected routes
- ✅ Auto-logout en token expirado

### Para Producción (TODO)

- [ ] Usar base de datos real (PostgreSQL/MySQL)
- [ ] Hashear contraseñas con bcrypt/argon2
- [ ] Cambiar JWT secret key
- [ ] Implementar refresh tokens
- [ ] Rate limiting en login endpoint
- [ ] HTTPS obligatorio
- [ ] Implementar 2FA (opcional)
- [ ] Logs de actividad de usuarios

## 📝 Endpoints Disponibles

### Públicos (Sin Auth)
- `GET /api/v1/admin/stats` - Estadísticas
- `GET /api/v1/admin/health` - Health check
- `POST /api/v1/auth/login` - Login

### Requieren API Key
- `GET /api/v1/prompts` - Listar prompts (lectura)
- `GET /api/v1/prompts/{id}` - Obtener prompt (lectura)
- `GET /api/v1/catalog/*` - Endpoints de catálogo
- `GET /api/v1/search/*` - Búsquedas

### Requieren JWT Token
- `POST /api/v1/prompts` - Crear prompt
- `PUT /api/v1/prompts/{id}` - Actualizar prompt
- `DELETE /api/v1/prompts/{id}` - Eliminar prompt

## 🐛 Troubleshooting

### Error: "Invalid username or password"
- Verifica que estés usando uno de los usuarios disponibles
- Revisa que el backend esté corriendo

### Error: "Network Error"
- Verifica que el backend esté en `http://localhost:8000`
- Revisa CORS en `src/api/config.py`

### Error: "401 Unauthorized"
- Token expirado - vuelve a hacer login
- Token inválido - limpia localStorage y reintenta

### Error: CORS
- Verifica `cors_origins` en `src/api/config.py`
- Asegúrate de incluir `http://localhost:5173`

## 📚 Documentación API

Con el backend corriendo, visita:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

Aquí puedes probar el endpoint de login directamente.

## ✅ Checklist de Implementación

- [x] Crear modelos de auth en backend
- [x] Crear router de auth con endpoint /login
- [x] Registrar router en main.py
- [x] Implementar generación de JWT tokens
- [x] Crear usuarios de prueba
- [x] Conectar frontend al endpoint real
- [x] Configurar interceptores de Axios
- [x] Probar flujo completo de login
- [x] Documentar sistema de autenticación

## 🎯 Próximos Pasos

1. **Migrar a base de datos real:**
   ```python
   # Reemplazar USERS_DB con queries a PostgreSQL
   user = db.query(User).filter(User.username == username).first()
   ```

2. **Implementar hashing de contraseñas:**
   ```python
   from passlib.context import CryptContext
   pwd_context = CryptContext(schemes=["bcrypt"])
   ```

3. **Añadir refresh tokens:**
   - Token de acceso: 15 minutos
   - Refresh token: 7 días
   - Endpoint `/auth/refresh`

4. **Registro de usuarios:**
   - Endpoint `POST /auth/register`
   - Validación de email
   - Confirmación por email

---

**Estado:** ✅ Completamente funcional  
**Versión:** 1.0.0  
**Fecha:** 12 de Noviembre, 2025
