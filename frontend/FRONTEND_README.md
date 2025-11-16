# DiffusionPromptDB Frontend

Modern React application for managing and cataloging Stable Diffusion prompts with full internationalization support.

## 🚀 Features

### ✅ Core Features (Completed)
- **Multi-language Support**: Full internationalization (ES, EN, FR, DE)
- **Authentication System**: JWT-based login/logout with protected routes
- **Self-service Onboarding**: Public registration + verification flow tied to backend tokens
- **Dashboard**: Real-time statistics with interactive charts
- **Prompts Management**: Complete CRUD operations
- **Advanced Search**: Multi-filter search with complex queries
- **User Preferences**: Customizable settings and tag blacklisting
- **Export Functionality**: Export prompts to JSON/CSV formats

### 🌍 Internationalization
- **4 Languages Supported**: Spanish, English, French, German
- **Dynamic Language Switching**: Real-time UI updates
- **Complete Coverage**: All UI elements, messages, and errors translated
- **Persisted Preferences**: Language selection saved in localStorage

## 📁 Project Structure

```
frontend/src/
├── components/
│   ├── dashboard/
│   │   └── StatsCharts.tsx      # Interactive charts (Recharts)
│   ├── layout/
│   │   └── Header.tsx            # Main navigation with language toggle
│   ├── prompts/
│   │   ├── PromptFormModal.tsx  # Create/Edit prompt modal
│   │   └── PromptDetailModal.tsx # View prompt details
│   ├── search/
│   │   └── SearchBar.tsx         # Quick search component
│   └── ui/
│       ├── LanguageToggle.tsx   # Language selector
│       ├── Loading.tsx           # Loading spinner
│       ├── Modal.tsx             # Reusable modal component
│       └── Toast.tsx             # Notification system
│
├── hooks/
│   └── usePrompts.ts             # Custom hooks for prompt operations
│
├── i18n/
│   ├── config.ts                 # i18n configuration
│   └── locales/
│       ├── en.json               # English translations
│       ├── es.json               # Spanish translations
│       ├── fr.json               # French translations
│       └── de.json               # German translations
│
├── pages/
│   ├── RegisterPage.tsx          # Self-service onboarding
│   ├── LoginPage.tsx             # Authentication page
│   ├── DashboardPage.tsx         # Statistics dashboard
│   ├── PromptsPage.tsx           # Prompts management
│   ├── SearchPage.tsx            # Advanced search
│   ├── ProfilePage.tsx           # Preferences + password rotation
│   └── AdminUsersPage.tsx        # Admin console
│
├── providers/
│   └── QueryProvider.tsx         # TanStack Query provider
│
├── router/
│   └── AppRouter.tsx             # Route configuration
│
├── services/
│   ├── api.ts                    # Axios configuration
│   ├── auth.service.ts           # Authentication services
│   ├── preferences.service.ts    # User preferences
│   ├── prompts.service.ts        # Prompts CRUD
│   ├── search.service.ts         # Search operations
│   └── stats.service.ts          # Statistics data
│
├── store/
│   └── authStore.ts              # Global state (Zustand)
│
├── types/
│   └── api.types.ts              # TypeScript definitions
│
├── utils/
│   └── exportPrompts.ts          # Export utilities
│
├── App.tsx                       # Main component
└── main.tsx                      # Entry point
```

## 🛠️ Installation & Setup

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your settings
VITE_API_URL=http://localhost:8000/api/v1
VITE_API_KEY=your-public-api-key
```

### 3. Start Development Server

```bash
npm run dev
```

Application will be available at: http://localhost:5173

## 🔐 Authentication

### Demo Credentials

- **Admin**: `admin` / `1302Quiter@#` (full access)
- **User**: `user` / `1302Quiter@#` (read/write)
- **Test**: `test` / `1302Quiter@#` (limited access)

### Authentication & onboarding flow

1. **Self-service register (`/register`)**: users submit username/email/password; the backend stores the request, sends the verification email, and only surfaces the token in a debug banner when `EMAIL_DEBUG_MODE=True`.
2. **Token verification**: users click the link inside the email (or call `/auth/verify` manually during debugging) and the account becomes active.
3. **Login (`/login`)**: once verified, credentials are submitted to `/auth/login` and the JWT is persisted in localStorage.
4. **Protected routes**: `AppRouter` prevents access to `/dashboard`, `/prompts`, `/search`, `/profile` and `/admin/users` until the token is validated via `/auth/me`.
5. **Password rotation**: expired passwords trigger the forced-change dialog connected to `/auth/password/expired`.

> Configure `SMTP_*` variables + `PUBLIC_APP_URL` in the backend `.env` so verification messages are emailed from your domain. When SMTP is not available, leave `EMAIL_DEBUG_MODE=True` to expose the token in the API/UI for manual onboarding.

## 📡 API Integration

### Endpoints Used

**Authentication:**
- `POST /auth/login` - User login
- `POST /auth/logout` - User logout

**Prompts:**
- `GET /prompts` - List prompts (paginated)
- `GET /prompts/{id}` - Get single prompt
- `POST /prompts` - Create new prompt
- `PUT /prompts/{id}` - Update prompt
- `DELETE /prompts/{id}` - Delete prompt

**Search:**
- `GET /search/complex` - Advanced multi-filter search
- `GET /search/tag/{tag}` - Search by specific tag
- `GET /search/text` - Full-text search

**Statistics:**
- `GET /admin/stats` - Dashboard statistics
- `GET /admin/filters` - Available filter options

**Preferences:**
- `GET /preferences` - Get user preferences
- `PUT /preferences` - Update preferences

## 🎨 UI/UX Features

### Design System
- **Framework**: Tailwind CSS
- **Theme**: Dark mode with slate-900 base
- **Color Palette**:
  - Primary: Violet-600
  - Info: Blue-600
  - Success: Green-600
  - Warning: Orange-600
  - Error: Red-500
- **Responsive**: Mobile-first design
- **Animations**: Smooth transitions

### Components
- **Modals**: Reusable modal system
- **Toasts**: Non-intrusive notifications
- **Charts**: Interactive Recharts visualizations
- **Forms**: React Hook Form validation
- **Tables**: Responsive data tables
- **Loading States**: Skeleton loaders

## 📊 Dashboard Features

### Statistics Display
- Total prompts count
- Art styles distribution
- Tags frequency analysis
- NSFW content breakdown
- Interactive charts and graphs

### Quick Actions
- View all prompts
- Create new prompt
- Export data
- Access settings

### Customizable Views
- Toggle "unspecified" styles
- Exclude blacklisted tags
- Filter preferences
- Chart type selection

## 🔍 Search Capabilities

### Search Filters
- **Text Search**: Full-text prompt search
- **Tag Search**: Search by specific tags
- **NSFW Level**: Filter by content rating
- **Art Style**: Filter by artistic style
- **Number of People**: Filter by character count
- **Complex Queries**: Combine multiple filters

### Search Features
- Real-time results
- Pagination support
- Result highlighting
- Search history
- Filter chips display

## ⚙️ Settings & Preferences

### User Preferences
- Language selection
- Display preferences
- Tag blacklisting
- Dashboard customization
- Export settings

### System Settings
- API configuration
- Cache management
- Performance tuning
- Debug options

## 📦 Dependencies

### Core
```json
{
  "react": "^18.3.1",
  "react-dom": "^18.3.1",
  "react-router-dom": "^6.28.0",
  "typescript": "~5.6.2"
}
```

### State Management
```json
{
  "@tanstack/react-query": "^5.59.20",
  "zustand": "^5.0.1"
}
```

### UI/UX
```json
{
  "react-i18next": "^15.1.1",
  "i18next": "^24.0.0",
  "recharts": "^2.13.3",
  "react-hook-form": "^7.54.0",
  "tailwindcss": "^3.4.15"
}
```

### Utilities
```json
{
  "axios": "^1.7.8",
  "react-icons": "^5.3.0",
  "date-fns": "^4.1.0",
  "clsx": "^2.1.1"
}
```

## 🧪 Testing

```bash
# Run tests
npm run test

# Run tests with coverage
npm run test:coverage

# Run tests in watch mode
npm run test:watch
```

## 🏗️ Build for Production

```bash
# Build application
npm run build

# Preview production build
npm run preview

# Analyze bundle size
npm run build --analyze
```

Output will be in `dist/` directory.

## 🚀 Deployment

### Docker
```bash
# Build Docker image
docker build -t diffusion-prompt-frontend .

# Run container
docker run -p 3000:80 diffusion-prompt-frontend
```

### Static Hosting
The build output can be deployed to any static hosting service:
- Vercel
- Netlify
- GitHub Pages
- AWS S3 + CloudFront

## 🐛 Troubleshooting

### Common Issues

**CORS Errors**
- Ensure backend CORS is configured
- Check `VITE_API_URL` in `.env`

**Authentication Issues**
- Verify JWT token is valid
- Check API key configuration
- Clear localStorage and retry

**Missing Translations**
- Check language files in `src/i18n/locales/`
- Ensure all keys are present in all languages
- Clear cache and reload

**Build Errors**
- Run `npm run build` to see TypeScript errors
- Check for missing dependencies
- Verify environment variables

## 📈 Performance Optimization

### Implemented
- ✅ Code splitting with React.lazy
- ✅ TanStack Query caching
- ✅ Image lazy loading
- ✅ Memoized components
- ✅ Virtual scrolling for large lists
- ✅ Debounced search inputs

### Best Practices
- Use production builds for deployment
- Enable gzip compression
- Implement CDN for static assets
- Monitor bundle size
- Use performance profiler

## 🔄 Version History

### v2.0.0 (Current)
- Full internationalization (4 languages)
- Advanced search implementation
- User preferences system
- Export functionality
- Chart visualizations
- Complete CRUD operations

### v1.0.0
- Initial release
- Basic authentication
- Dashboard with stats
- Prompts listing
- Pagination

## 🤝 Contributing

### Development Workflow
1. Create feature branch
2. Add translations for new UI text
3. Update TypeScript types
4. Write tests for new features
5. Update documentation
6. Submit pull request

### Code Style
- ESLint configuration
- Prettier formatting
- TypeScript strict mode
- Component naming conventions
- File organization standards

## 📞 Support

For issues or questions:
1. Check browser console for errors
2. Verify API backend is running
3. Review this documentation
4. Check GitHub issues
5. Contact development team

## 🎯 Roadmap

### Next Features
- [ ] Batch operations
- [ ] Advanced analytics
- [ ] AI-powered suggestions
- [ ] Collaborative features
- [ ] Mobile app version
- [ ] Offline support
- [ ] WebSocket real-time updates

---

**Version:** 2.0.0  
**Last Updated:** November 14, 2025  
**License:** Apache 2.0
