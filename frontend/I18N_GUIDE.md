# Internationalization (i18n) Guide

Complete guide for the internationalization system in DiffusionPromptDB Frontend.

## 📋 Table of Contents

1. [Overview](#overview)
2. [Supported Languages](#supported-languages)
3. [Architecture](#architecture)
4. [Usage Guide](#usage-guide)
5. [Adding Translations](#adding-translations)
6. [Adding New Languages](#adding-new-languages)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)

## 🌍 Overview

The application uses `react-i18next` for internationalization, providing:
- Dynamic language switching without page reload
- Persistent language preferences
- Complete UI translation coverage
- Fallback language support
- Lazy loading of translation files

## 🗣️ Supported Languages

| Language | Code | File | Status |
|----------|------|------|--------|
| Spanish | `es` | `es.json` | ✅ Complete |
| English | `en` | `en.json` | ✅ Complete |
| French | `fr` | `fr.json` | ✅ Complete |
| German | `de` | `de.json` | ✅ Complete |

## 🏗️ Architecture

### Configuration
```typescript
// src/i18n/config.ts
import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';

i18n.use(initReactI18next).init({
  resources: { /* language resources */ },
  lng: localStorage.getItem('language') || 'es',
  fallbackLng: 'es',
  interpolation: {
    escapeValue: false // React already escapes
  }
});
```

### File Structure
```
src/i18n/
├── config.ts              # i18n configuration
└── locales/
    ├── en.json           # English translations
    ├── es.json           # Spanish translations
    ├── fr.json           # French translations
    └── de.json           # German translations
```

### Translation Structure
```json
{
  "app": {
    "title": "DiffusionPrompt",
    "subtitle": "Prompt Cataloging System"
  },
  "nav": {
    "dashboard": "Dashboard",
    "prompts": "Prompts",
    "search": "Search",
    "settings": "Settings",
    "logout": "Logout"
  },
  // ... more sections
}
```

## 📖 Usage Guide

### In Components

#### Basic Usage
```typescript
import { useTranslation } from 'react-i18next';

export const MyComponent = () => {
  const { t } = useTranslation();
  
  return (
    <div>
      <h1>{t('app.title')}</h1>
      <p>{t('app.subtitle')}</p>
    </div>
  );
};
```

#### With Interpolation
```typescript
// Translation file
{
  "search": {
    "results": {
      "foundResults": "Found {{count}} total results"
    }
  }
}

// Component
<p>{t('search.results.foundResults', { count: 42 })}</p>
// Output: "Found 42 total results"
```

#### Pluralization
```typescript
// Translation file
{
  "items": {
    "count_one": "{{count}} item",
    "count_other": "{{count}} items"
  }
}

// Component
<p>{t('items.count', { count: itemCount })}</p>
```

### Language Switching

#### LanguageToggle Component
```typescript
import { useTranslation } from 'react-i18next';

export const LanguageToggle = () => {
  const { i18n } = useTranslation();

  const handleLanguageChange = (lng: string) => {
    i18n.changeLanguage(lng);
    localStorage.setItem('language', lng);
  };

  return (
    <select 
      value={i18n.language} 
      onChange={(e) => handleLanguageChange(e.target.value)}
    >
      <option value="es">Español</option>
      <option value="en">English</option>
      <option value="fr">Français</option>
      <option value="de">Deutsch</option>
    </select>
  );
};
```

## ➕ Adding Translations

### Step 1: Add Key to All Language Files

Add the new key to all language files:

```json
// es.json
{
  "newFeature": {
    "title": "Nueva Funcionalidad",
    "description": "Descripción de la funcionalidad"
  }
}

// en.json
{
  "newFeature": {
    "title": "New Feature",
    "description": "Feature description"
  }
}

// fr.json
{
  "newFeature": {
    "title": "Nouvelle Fonctionnalité",
    "description": "Description de la fonctionnalité"
  }
}

// de.json
{
  "newFeature": {
    "title": "Neue Funktion",
    "description": "Funktionsbeschreibung"
  }
}
```

### Step 2: Use in Component

```typescript
const { t } = useTranslation();

return (
  <div>
    <h2>{t('newFeature.title')}</h2>
    <p>{t('newFeature.description')}</p>
  </div>
);
```

## 🌐 Adding New Languages

### Step 1: Create Translation File

Create new file `src/i18n/locales/[lang].json`:

```json
// Example: it.json for Italian
{
  "app": {
    "title": "DiffusionPrompt",
    "subtitle": "Sistema di Catalogazione Prompt"
  },
  // ... translate all keys
}
```

### Step 2: Update Configuration

```typescript
// src/i18n/config.ts
import it from './locales/it.json';

const resources = {
  // ... existing languages
  it: {
    translation: it,
  },
};
```

### Step 3: Add to Language Selector

```typescript
// src/components/ui/LanguageToggle.tsx
const languages = [
  { code: 'es', label: 'Español', flag: '🇪🇸' },
  { code: 'en', label: 'English', flag: '🇬🇧' },
  { code: 'fr', label: 'Français', flag: '🇫🇷' },
  { code: 'de', label: 'Deutsch', flag: '🇩🇪' },
  { code: 'it', label: 'Italiano', flag: '🇮🇹' }, // New
];
```

## ✅ Best Practices

### 1. Key Naming Conventions

Use nested structure for organization:
```json
{
  "page": {
    "section": {
      "element": "Text content"
    }
  }
}
```

Examples:
- `dashboard.charts.nsfwTitle`
- `promptForm.fields.textPlaceholder`
- `common.errors.loadingPreferences`

### 2. Common Translations

Keep common translations in a shared section:
```json
{
  "common": {
    "loading": "Loading...",
    "error": "Error",
    "success": "Success",
    "save": "Save",
    "cancel": "Cancel",
    "delete": "Delete"
  }
}
```

### 3. Error Messages

Centralize error messages:
```json
{
  "common": {
    "errors": {
      "network": "Network error",
      "unauthorized": "Unauthorized",
      "notFound": "Not found",
      "serverError": "Server error"
    }
  }
}
```

### 4. Form Validation

Structure form translations:
```json
{
  "form": {
    "fields": {
      "email": "Email",
      "emailRequired": "Email is required",
      "emailInvalid": "Invalid email format"
    }
  }
}
```

### 5. Dynamic Content

Use interpolation for dynamic values:
```json
{
  "user": {
    "welcome": "Welcome, {{name}}!",
    "itemCount": "You have {{count}} items"
  }
}
```

## 🔍 Troubleshooting

### Missing Translations

If a translation key is missing:
1. Check console for warnings
2. Verify key exists in all language files
3. Check for typos in key names
4. Ensure proper nesting structure

### Language Not Switching

If language doesn't change:
1. Check localStorage is accessible
2. Verify language code is correct
3. Ensure i18n is properly initialized
4. Check for console errors

### Fallback Issues

If fallback language isn't working:
1. Verify `fallbackLng` in config
2. Check fallback language file exists
3. Ensure key exists in fallback language

### Performance Issues

For better performance:
1. Use translation keys consistently
2. Avoid dynamic key generation
3. Implement lazy loading for large translation files
4. Use React.memo for components with translations

## 📚 Translation Coverage

### Current Coverage Status

| Section | ES | EN | FR | DE | Notes |
|---------|----|----|----|----|-------|
| App | ✅ | ✅ | ✅ | ✅ | Complete |
| Navigation | ✅ | ✅ | ✅ | ✅ | Complete |
| Login | ✅ | ✅ | ✅ | ✅ | Complete |
| Dashboard | ✅ | ✅ | ✅ | ✅ | Complete |
| Prompts | ✅ | ✅ | ✅ | ✅ | Complete |
| Search | ✅ | ✅ | ✅ | ✅ | Complete |
| Settings | ✅ | ✅ | ✅ | ✅ | Complete |
| Forms | ✅ | ✅ | ✅ | ✅ | Complete |
| Errors | ✅ | ✅ | ✅ | ✅ | Complete |
| Common | ✅ | ✅ | ✅ | ✅ | Complete |

## 🛠️ Development Tools

### VS Code Extensions

Recommended extensions for i18n development:
- **i18n Ally**: Inline translation preview and management
- **JSON Language Features**: JSON validation and formatting
- **Prettier**: Code formatting including JSON files

### Translation Management

For larger projects, consider:
- **Crowdin**: Translation management platform
- **Lokalise**: Collaborative translation tool
- **POEditor**: Online localization platform

## 📝 Checklist for New Features

When adding new features with UI text:

- [ ] Add translation keys to all language files
- [ ] Use `t()` function for all user-visible text
- [ ] Test with all supported languages
- [ ] Check for text overflow in different languages
- [ ] Verify pluralization rules work correctly
- [ ] Update this documentation if needed
- [ ] Add unit tests for translated components

## 🔗 Resources

- [react-i18next Documentation](https://react.i18next.com/)
- [i18next Documentation](https://www.i18next.com/)
- [Language Codes Reference](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes)
- [Pluralization Rules](https://www.i18next.com/translation-function/plurals)

---

**Version:** 1.0.0  
**Last Updated:** November 14, 2025  
**Maintained by:** Development Team
