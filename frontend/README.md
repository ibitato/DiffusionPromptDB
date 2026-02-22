# DiffusionPromptDB Frontend

Modern, responsive, multilingual web interface for DiffusionPromptDB.

## 🎨 Features

- ✅ **Modern UI**: React 18 + TypeScript + Tailwind CSS
- ✅ **Responsive Design**: Mobile-first, works on all devices
- ✅ **Dark/Light Themes**: Elegant theme switching
- ✅ **Multilingual**: English, Spanish, German, French (i18next)
- ✅ **Secure Auth**: User/Admin roles with JWT
- ✅ **Real-time**: React Query for data synchronization
- ✅ **Minimalist**: Clean, elegant, usable interface

## 🚀 Quick Start

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build
```

Access: http://localhost:3000

## 🔐 User Roles

### Admin
- Full CRUD on prompts
- User management
- System statistics
- Catalog maintenance
- Analysis job monitoring

### User
- Read prompts
- Search catalog
- View statistics
- Personal dashboard

## 🌍 Supported Languages

1. **English** (default) - `en`
2. **Spanish** - `es`
3. **German** - `de`
4. **French** - `fr`

Translations in: `public/locales/{lang}/translation.json`

## 🎨 Themes

### Dark Theme (Default)
- Background: `#0f172a` (slate-900)
- Surface: `#1e293b` (slate-800)
- Primary: `#3b82f6` (blue-500)
- Accent: `#8b5cf6` (violet-500)

### Light Theme
- Background: `#ffffff`
- Surface: `#f8fafc` (slate-50)
- Primary: `#2563eb` (blue-600)
- Accent: `#7c3aed` (violet-600)

## 📁 Project Structure

```
frontend/
├── public/
│   └── locales/              # i18n translations
│       ├── en/translation.json
│       ├── es/translation.json
│       ├── de/translation.json
│       └── fr/translation.json
├── src/
│   ├── main.tsx              # Entry point
│   ├── App.tsx               # Main app component
│   ├── i18n.ts               # i18n configuration
│   ├── api/                  # API client layer
│   │   ├── client.ts         # Axios instance
│   │   ├── auth.ts           # Auth API calls
│   │   ├── prompts.ts        # Prompts API calls
│   │   └── catalog.ts        # Catalog API calls
│   ├── components/
│   │   ├── ui/               # Reusable UI components
│   │   │   ├── Button.tsx
│   │   │   ├── Input.tsx
│   │   │   ├── Card.tsx
│   │   │   ├── Modal.tsx
│   │   │   ├── Table.tsx
│   │   │   ├── Badge.tsx
│   │   │   └── Loading.tsx
│   │   ├── layout/           # Layout components
│   │   │   ├── Navbar.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   └── Footer.tsx
│   │   └── features/         # Feature-specific
│   │       ├── ThemeToggle.tsx
│   │       ├── LanguageSelector.tsx
│   │       ├── UserMenu.tsx
│   │       └── SearchFilters.tsx
│   ├── pages/                # Page components
│   │   ├── Login.tsx
│   │   ├── Dashboard.tsx
│   │   ├── prompts/
│   │   │   ├── PromptList.tsx
│   │   │   ├── PromptDetail.tsx
│   │   │   ├── PromptCreate.tsx
│   │   │   └── PromptEdit.tsx
│   │   ├── catalog/
│   │   │   ├── CatalogSearch.tsx
│   │   │   ├── CatalogDetail.tsx
│   │   │   └── AdvancedFilters.tsx
│   │   ├── stats/
│   │   │   └── StatsDashboard.tsx
│   │   └── admin/           # Admin only
│   │       ├── UserManagement.tsx
│   │       └── SystemSettings.tsx
│   ├── hooks/                # Custom React hooks
│   │   ├── useAuth.ts
│   │   ├── useTheme.ts
│   │   ├── usePrompts.ts
│   │   └── useCatalog.ts
│   ├── store/                # Zustand stores
│   │   ├── authStore.ts
│   │   └── themeStore.ts
│   ├── types/                # TypeScript definitions
│   │   ├── api.types.ts
│   │   ├── prompt.types.ts
│   │   ├── catalog.types.ts
│   │   └── user.types.ts
│   ├── utils/
│   │   ├── constants.ts
│   │   └── helpers.ts
│   └── styles/
│       └── globals.css
├── index.html
├── package.json
├── tsconfig.json
├── tailwind.config.js
├── postcss.config.js
└── README.md
```

## 🛠️ Required Backend Changes

### 1. Add Users Table (SQL)

```sql
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT CHECK(role IN ('admin', 'user')) DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    is_active BOOLEAN DEFAULT 1
);
```

### 2. New API Endpoints

```python
# Authentication & onboarding
POST /api/v1/auth/register         # Self-service registration
POST /api/v1/auth/verify           # Activate account via token
POST /api/v1/auth/login            # Login → JWT + user info
POST /api/v1/auth/password/expired # Force password rotation
GET  /api/v1/auth/me               # Current user info + rolling token

# Profile & preferences
GET  /api/v1/user/profile              # Profile + preferences
PUT  /api/v1/user/profile              # Update profile fields
PUT  /api/v1/user/profile/preferences  # Persist "Only my prompts", excluded tags, etc.

# User Management (Admin only)
GET    /api/v1/admin/users         # List users
POST   /api/v1/admin/users         # Create user
PUT    /api/v1/admin/users/{id}    # Update user / role / status
DELETE /api/v1/admin/users/{id}    # Delete user
POST   /api/v1/admin/users/{id}/reset-password  # Force reset
```

## 💻 Installation

```bash
# Install dependencies
npm install

# Copy environment template
cp .env.example .env

# Configure API URL in .env
VITE_API_URL=http://localhost:8000

# Start development server
npm run dev
```

## 🎯 Pages & Routes

### Public Routes
- `/login` - Login page (password rotation included)
- `/register` - Self-service onboarding & verification

> La ruta `/` redirige automáticamente según el landing configurado del usuario cuando la sesión está activa.

### Protected Routes
- `/dashboard` - Overview cards + charts
- `/prompts` - Prompt table + CRUD modals
- `/search` - Advanced search workspace
- `/profile` - User profile, preferences, account deletion
- `/admin/users` - Admin-only console (creación, bloqueo, reset)

## 🔑 Authentication Flow

1. **Registro**: el usuario completa `/register` (`POST /auth/register`) y recibe un correo con el enlace de verificación (solo se muestra el token en pantalla cuando `EMAIL_DEBUG_MODE=True`).
2. **Verificación**: el enlace del correo llama internamente a `/auth/verify` y activa la cuenta (`is_active=True`).
3. **Login**: ya verificada, la cuenta llama a `/auth/login` y obtiene JWT + perfil.
4. **Persistencia**: `authService` guarda `auth_token` + usuario en `localStorage` y los interceptores adjuntan el Bearer token.
5. **Refresco silencioso**: `/auth/me` renueva el JWT en segundo plano mientras la sesión es válida; si vence, se limpia el store y se redirige a `/login`.

```typescript
// Login example
POST /api/v1/auth/login
{
  "username": "admin",
  "password": "<your-password>"
}

// Response
{
  "access_token": "jwt-token...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "admin",
    "role": "admin"
  }
}

// Persist on the client
localStorage.setItem('auth_token', response.access_token);
localStorage.setItem('user', JSON.stringify(response.user));

// Axios automatically sends Authorization header afterwards
```

## 🌐 i18n Implementation

### Setup (src/i18n.ts)
```typescript
import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import Backend from 'i18next-http-backend';
import LanguageDetector from 'i18next-browser-languagedetector';

i18n
  .use(Backend)
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    fallbackLng: 'en',
    supportedLngs: ['en', 'es', 'de', 'fr'],
    backend: {
      loadPath: '/locales/{{lng}}/translation.json'
    }
  });
```

### Usage in Components
```typescript
import { useTranslation } from 'react-i18next';

function MyComponent() {
  const { t, i18n } = useTranslation();
  
  return (
    <div>
      <h1>{t('dashboard.welcome')}</h1>
      <button onClick={() => i18n.changeLanguage('es')}>
        Español
      </button>
    </div>
  );
}
```

### Translation Files Structure

```json
// public/locales/en/translation.json
{
  "nav": {
    "dashboard": "Dashboard",
    "prompts": "Prompts",
    "catalog": "Catalog",
    "stats": "Statistics"
  },
  "auth": {
    "login": "Login",
    "logout": "Logout",
    "username": "Username",
    "password": "Password"
  },
  "prompts": {
    "list": "Prompt List",
    "create": "Create New Prompt",
    "edit": "Edit Prompt",
    "delete_confirm": "Are you sure you want to delete this prompt?"
  },
  "catalog": {
    "search": "Search Catalog",
    "filters": "Filters",
    "nsfw_level": "NSFW Level",
    "art_style": "Art Style",
    "characters": "Characters"
  }
}
```

## 🎨 Component Examples

### Button Component
```typescript
interface ButtonProps {
  children: React.ReactNode;
  variant?: 'primary' | 'secondary' | 'danger';
  onClick?: () => void;
}

export function Button({ children, variant = 'primary', onClick }: ButtonProps) {
  const baseStyles = 'px-4 py-2 rounded-lg font-medium transition-colors';
  const variants = {
    primary: 'bg-blue-500 hover:bg-blue-600 text-white',
    secondary: 'bg-gray-200 hover:bg-gray-300 dark:bg-gray-700',
    danger: 'bg-red-500 hover:bg-red-600 text-white'
  };
  
  return (
    <button 
      className={`${baseStyles} ${variants[variant]}`}
      onClick={onClick}
    >
      {children}
    </button>
  );
}
```

### Theme Toggle
```typescript
import { MoonIcon, SunIcon } from '@heroicons/react/24/outline';
import { useTheme } from '../hooks/useTheme';

export function ThemeToggle() {
  const { theme, toggleTheme } = useTheme();
  
  return (
    <button
      onClick={toggleTheme}
      className="p-2 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-700"
    >
      {theme === 'dark' ? <SunIcon className="w-6 h-6" /> : <MoonIcon className="w-6 h-6" />}
    </button>
  );
}
```

## 🔌 API Integration

### API Client (src/api/client.ts)
```typescript
import axios from 'axios';

export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  }
});

// Add auth token to requests
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
```

### Prompts API (src/api/prompts.ts)
```typescript
import { apiClient } from './client';

export const promptsAPI = {
  list: (page = 1, pageSize = 20) =>
    apiClient.get(`/api/v1/prompts?page=${page}&page_size=${pageSize}`),
  
  get: (id: number) =>
    apiClient.get(`/api/v1/prompts/${id}`),
  
  create: (data: PromptCreate) =>
    apiClient.post('/api/v1/prompts', data),
  
  update: (id: number, data: PromptUpdate) =>
    apiClient.put(`/api/v1/prompts/${id}`, data),
  
  delete: (id: number) =>
    apiClient.delete(`/api/v1/prompts/${id}`)
};
```

## 📊 State Management

### Auth Store (Zustand)
```typescript
import create from 'zustand';

interface AuthState {
  user: User | null;
  token: string | null;
  login: (user: User, token: string) => void;
  logout: () => void;
  isAdmin: () => boolean;
}

export const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  token: localStorage.getItem('token'),
  
  login: (user, token) => {
    localStorage.setItem('token', token);
    set({ user, token });
  },
  
  logout: () => {
    localStorage.removeItem('token');
    set({ user: null, token: null });
  },
  
  isAdmin: () => get().user?.role === 'admin'
}));
```

## 🧩 Key Pages

### Dashboard
- Welcome message with user name
- Quick stats cards
- Recent activity
- Quick actions

### Prompt List
- Paginated table
- Search and filters
- Sort by date, rating, category
- Create new prompt button
- Actions: View, Edit, Delete

### Catalog Search
- Advanced filters panel:
  - NSFW level
  - Art style
  - Number of characters
  - Hair color
  - Tags
  - References
- Results grid/list toggle
- Detailed view modal

### Stats Dashboard
- Total prompts counter
- NSFW distribution (pie chart)
- Top tags (bar chart)
- Art styles distribution
- Character count histogram
- Timeline of analyses

### Admin: User Management
- User list table
- Create/Edit user modal
- Role management
- Activate/Deactivate users

## 🎯 Implementation Guide

### Step 1: Backend Changes (Required)

Before frontend works, update backend:

```bash
cd src/api

# 1. Add users table to database
# 2. Implement auth endpoints (register, login, me)
# 3. Add user management endpoints (admin only)
# 4. Update auth.py to include user info in JWT
```

### Step 2: Install Frontend

```bash
cd frontend
npm install
```

### Step 3: Configure

Create `.env`:
```
VITE_API_URL=http://localhost:8000
```

### Step 4: Create Translation Files

```bash
mkdir -p public/locales/{en,es,de,fr}
# Create translation.json in each
```

### Step 5: Implement Core

Priority order:
1. Auth flow (login, token management)
2. Theme system
3. i18n setup
4. API client
5. Basic UI components
6. Main pages
7. Advanced features

### Step 6: Run

```bash
# Terminal 1: Backend
cd src/api
python main.py

# Terminal 2: Frontend
cd frontend
npm run dev
```

## 📦 Build & Deploy

```bash
# Build
npm run build

# Preview build
npm run preview

# Deploy
# Output in dist/ can be served by any static host
```

## 🔧 Configuration Files

### .env.example
```
VITE_API_URL=http://localhost:8000
VITE_APP_NAME=DiffusionPromptDB
VITE_DEFAULT_LANGUAGE=en
```

### postcss.config.js
```javascript
export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
```

## 🧪 Testing

```bash
# Add to package.json
npm install -D vitest @testing-library/react @testing-library/jest-dom

# Run tests
npm test
```

## 🎨 Design Principles

1. **Minimalist**: Less is more, focus on content
2. **Consistent**: Same patterns throughout
3. **Accessible**: WCAG 2.1 AA compliant
4. **Responsive**: Mobile-first approach
5. **Fast**: Optimized loading and rendering
6. **Intuitive**: Clear navigation and actions

## 📝 Next Steps

To complete the frontend implementation:

1. **Backend**: Add user authentication system
2. **Frontend**: Install dependencies (`npm install`)
3. **Translations**: Create 4 language files
4. **Components**: Implement UI components
5. **Pages**: Build main pages
6. **Integration**: Connect to API
7. **Test**: End-to-end testing

See [IMPLEMENTATION.md](IMPLEMENTATION.md) for detailed step-by-step guide.

## 🔗 Links

- Backend API: http://localhost:8000/docs
- Frontend Dev: http://localhost:3000
- GitHub: https://github.com/ibitato/DiffusionPromptDB

## Version

1.0.0 - Initial architecture
