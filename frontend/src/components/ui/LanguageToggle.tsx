/**
 * Language Toggle Component
 * Switch between Spanish, English, French, and German
 */

import { useTranslation } from 'react-i18next';

export const LanguageToggle = () => {
  const { i18n } = useTranslation();

  const changeLanguage = (lng: string) => {
    i18n.changeLanguage(lng);
    localStorage.setItem('language', lng);
  };

  const currentLang = i18n.language;

  const languages = [
    { code: 'es', label: 'ES', flag: '🇪🇸' },
    { code: 'en', label: 'EN', flag: '🇬🇧' },
    { code: 'fr', label: 'FR', flag: '🇫🇷' },
    { code: 'de', label: 'DE', flag: '🇩🇪' },
  ];

  return (
    <div className="flex items-center gap-1 bg-slate-700 rounded-lg p-1">
      {languages.map((lang) => (
        <button
          key={lang.code}
          onClick={() => changeLanguage(lang.code)}
          className={`px-3 py-1 rounded-md text-sm font-medium transition-colors flex items-center gap-1 ${
            currentLang === lang.code ? 'bg-violet-600 text-white' : 'text-gray-300 hover:text-white'
          }`}
          title={lang.label}
        >
          <span className="text-xs">{lang.flag}</span>
          <span>{lang.label}</span>
        </button>
      ))}
    </div>
  );
};
