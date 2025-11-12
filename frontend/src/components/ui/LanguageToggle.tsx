/**
 * Language Toggle Component
 * Switch between Spanish and English
 */

import { useTranslation } from 'react-i18next';

export const LanguageToggle = () => {
  const { i18n } = useTranslation();

  const changeLanguage = (lng: string) => {
    i18n.changeLanguage(lng);
    localStorage.setItem('language', lng);
  };

  const currentLang = i18n.language;

  return (
    <div className="flex items-center gap-1 bg-slate-700 rounded-lg p-1">
      <button
        onClick={() => changeLanguage('es')}
        className={`px-3 py-1 rounded-md text-sm font-medium transition-colors ${
          currentLang === 'es'
            ? 'bg-violet-600 text-white'
            : 'text-gray-300 hover:text-white'
        }`}
      >
        ES
      </button>
      <button
        onClick={() => changeLanguage('en')}
        className={`px-3 py-1 rounded-md text-sm font-medium transition-colors ${
          currentLang === 'en'
            ? 'bg-violet-600 text-white'
            : 'text-gray-300 hover:text-white'
        }`}
      >
        EN
      </button>
    </div>
  );
};
