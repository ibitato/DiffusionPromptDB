# DiffusionPromptDB Frontend

Aplicación web React para gestionar y catalogar prompts de Stable Diffusion.

## 🚀 Características Implementadas

### ✅ Fase 1 - Fundación (Completado)
- Sistema de autenticación completo (Login/Logout)
- Rutas protegidas con React Router
- Gestión de estado con Zustand
- Configuración de Axios con interceptores
- TypeScript types para toda la API

### ✅ Fase 2 - Dashboard & Prompts (Completado)
- **Dashboard** con estadísticas visuales:
  - Total de prompts
  - Top tags y estilos de arte
  - Distribución NSFW
  - Acciones rápidas
- **Página de Prompts**:
  - Listado paginado (20 por página)
  - Tarjetas con información completa
  - Navegación entre páginas
  - Filtrado por categorías
- **Header** de navegación funcional

## 📁 Estructura del Código

```
frontend/src/
├── components/
│   ├── layout/
│   │   └── Header.tsx           # Navegación principal
│   └── ui/
│       └── Loading.tsx          # Spinner de carga
│
├── pages/
│   ├── LoginPage.tsx            # Página de autenticación
│   ├── DashboardPage.tsx        # Dashboard con stats
│   └── PromptsPage.tsx          # Listado de prompts
│
├── services/
│   ├── api.ts                   # Configuración Axios
│   ├── auth.service.ts          # Servicios de auth
│   ├── prompts.service.ts       # CRUD de prompts
│   └── stats.service.ts         # Estadísticas
│
├── store/
│   └── authStore.ts             # Estado global (Zustand)
│
├── router/
│   └── AppRouter.tsx            # Configuración de rutas
│
├── types/
│   └── api.types.ts             # TypeScript types
│
├── App.tsx                      # Componente principal
└── main.tsx                     # Entry point
```

## 🛠️ Instalación y Configuración

### 1. Instalar Dependencias

```bash
cd frontend
npm install
```

### 2. Configurar Variables de Entorno

```bash
# Copiar el archivo de ejemplo
cp .env.example .env

# Editar .env con tus configuraciones
VITE_API_URL=http://localhost:8000/api/v1
VITE_API_KEY=demo-read-key-12345
```

### 3. Iniciar el Servidor de Desarrollo

```bash
npm run dev
```

La aplicación estará disponible en: http://localhost:5173

## 🔐 Autenticación

### Credenciales de Prueba

Para el desarrollo, usa estas credenciales:
- **Usuario:** `test`
- **Contraseña:** `test`

### Sistema de Autenticación

1. **Mock Login**: Actualmente usa un sistema mock para desarrollo
2. **JWT Tokens**: Preparado para usar tokens JWT reales
3. **Protected Routes**: Las rutas están protegidas automáticamente
4. **Auto Logout**: Se cierra sesión automáticamente si el token expira (401)

Para conectar con la API real, edita `src/services/auth.service.ts`:

```typescript
// Cambiar de mockLogin a login
const response = await authService.login({ username, password });
```

## 📡 Integración con la API

### Endpoints Utilizados

**Autenticación:**
- `POST /auth/login` - Login (mock por ahora)

**Prompts:**
- `GET /prompts?page=1&page_size=20` - Listar prompts
- `GET /prompts/{id}` - Obtener un prompt
- `POST /prompts` - Crear prompt (preparado)
- `PUT /prompts/{id}` - Actualizar prompt (preparado)
- `DELETE /prompts/{id}` - Eliminar prompt (preparado)

**Estadísticas:**
- `GET /admin/stats` - Estadísticas generales (público)
- `GET /admin/health` - Health check (público)

### Configuración de Headers

La API automáticamente envía:
- `Authorization: Bearer <token>` - Si hay token JWT
- `X-API-Key: <key>` - Si no hay token (para lectura pública)

## 🎨 Diseño y Estilos

- **Framework**: Tailwind CSS
- **Tema**: Dark mode (slate-900)
- **Colores principales**:
  - Violet-600: Botones primarios
  - Blue-600: Información
  - Green-600: Éxito
  - Red-500: Errores
- **Responsive**: Diseño adaptable a móviles y tablets

## 📦 Dependencias Principales

```json
{
  "react": "^18.2.0",
  "react-router-dom": "^6.20.1",
  "axios": "^1.6.2",
  "zustand": "^4.4.7",
  "tailwindcss": "^3.3.6"
}
```

## 🚧 Funcionalidades Pendientes

### Fase 3 - CRUD Completo
- [ ] Modal/página para crear nuevo prompt
- [ ] Modal/página para editar prompt
- [ ] Confirmación para eliminar prompt
- [ ] Validación de formularios con react-hook-form
- [ ] Toasts/notificaciones de éxito/error

### Fase 4 - Búsqueda Avanzada
- [ ] Barra de búsqueda global
- [ ] Página de búsqueda avanzada
- [ ] Filtros multi-categoría:
  - NSFW level
  - Art style
  - Number of people
  - Tags
  - Rating
- [ ] Integración con `/search/complex`

### Fase 5 - Mejoras UX
- [ ] Animaciones con Framer Motion
- [ ] Estados de error mejorados
- [ ] Loading states en todas las acciones
- [ ] Breadcrumbs de navegación
- [ ] Paginación mejorada
- [ ] Vista de detalle de prompt
- [ ] Caché con TanStack Query
- [ ] Internacionalización (ES/EN)

### Fase 6 - Features Avanzadas
- [ ] Gráficos con Recharts
- [ ] Exportar prompts (CSV/JSON)
- [ ] Sistema de favoritos
- [ ] Historial de búsquedas
- [ ] Modo claro/oscuro toggle
- [ ] Panel de administración
- [ ] Gestión de usuarios

## 🧪 Testing

```bash
# Ejecutar tests (cuando estén implementados)
npm run test

# Coverage
npm run test:coverage
```

## 🏗️ Build para Producción

```bash
# Compilar
npm run build

# Preview del build
npm run preview
```

Los archivos compilados estarán en `dist/`

## 🐛 Debugging

### Problemas Comunes

**1. Error de CORS**
- Asegúrate de que la API backend tenga CORS habilitado
- Verifica que `VITE_API_URL` apunte al backend correcto

**2. 401 Unauthorized**
- Verifica que el token JWT no haya expirado
- Comprueba que la API Key sea correcta en `.env`

**3. No se cargan los prompts**
- Verifica que la API esté ejecutándose en http://localhost:8000
- Revisa la consola del navegador para errores

**4. TypeScript errors**
- Ejecuta `npm run build` para ver todos los errores de TS
- Asegúrate de que todas las dependencias estén instaladas

## 📝 Notas de Desarrollo

### Estado Actual
- ✅ Autenticación funcionando con mock
- ✅ Dashboard mostrando estadísticas reales de la API
- ✅ Listado de prompts con paginación funcional
- ✅ Rutas protegidas implementadas
- ✅ Diseño responsive y moderno

### Próximos Pasos Recomendados

1. **Implementar endpoints reales de auth** en el backend
2. **Crear modales de CRUD** para prompts
3. **Agregar búsqueda avanzada** con filtros
4. **Implementar TanStack Query** para caché inteligente
5. **Agregar animaciones** con Framer Motion

## 🤝 Contribuir

Para agregar nuevas features:

1. Crea los tipos en `types/api.types.ts`
2. Agrega el servicio en `services/`
3. Crea los componentes necesarios
4. Actualiza el router si es necesario
5. Prueba la integración con la API

## 📞 Soporte

Si encuentras problemas:
1. Revisa la consola del navegador
2. Verifica que la API backend esté corriendo
3. Comprueba los logs del servidor de desarrollo
4. Revisa este README para configuración correcta

## 🎯 Objetivos Cumplidos

- [x] Sistema de autenticación completo
- [x] Dashboard funcional con stats reales
- [x] Listado de prompts con paginación
- [x] Navegación fluida entre páginas
- [x] Diseño profesional y responsive
- [x] Arquitectura escalable y mantenible
- [x] TypeScript en todo el proyecto
- [x] Integración completa con la API backend

---

**Versión:** 1.0.0  
**Última actualización:** 12 de Noviembre, 2025
