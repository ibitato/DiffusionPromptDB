/**
 * Header Component
 * Navigation header with user menu
 */

import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuthStore } from '../../store/authStore';
import { SearchBar } from '../search/SearchBar';
import { LanguageToggle } from '../ui/LanguageToggle';

export const Header = () => {
  const { t } = useTranslation();
  const { user, logout } = useAuthStore();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <header className="bg-slate-800 border-b border-slate-700">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <div className="flex items-center">
            <h1 className="text-xl font-bold text-white">{t('app.title')}</h1>
          </div>

          {/* Navigation */}
          <nav className="flex items-center space-x-4">
            <HeaderLink label={t('nav.dashboard')} onClick={() => navigate('/dashboard')} />
            <HeaderLink label={t('nav.prompts')} onClick={() => navigate('/prompts')} />
            <HeaderLink label={t('nav.ingest')} onClick={() => navigate('/ingest')} />
            <HeaderLink label={t('nav.search')} onClick={() => navigate('/search')} />
            <HeaderLink label={t('nav.profile')} onClick={() => navigate('/profile')} />
            {user?.role === 'admin' && (
              <HeaderLink label={t('nav.admin')} onClick={() => navigate('/admin/users')} />
            )}
          </nav>

          {/* Search Bar */}
          <SearchBar />

          {/* User Menu */}
          <div className="flex items-center space-x-4">
            <LanguageToggle />
            <span className="text-gray-400 text-sm">{user?.username}</span>
            <button
              onClick={handleLogout}
              className="bg-slate-700 hover:bg-slate-600 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors"
            >
              {t('nav.logout')}
            </button>
          </div>
        </div>
      </div>
    </header>
  );
};

interface HeaderLinkProps {
  label: string;
  onClick: () => void;
}

const HeaderLink = ({ label, onClick }: HeaderLinkProps) => (
  <button
    onClick={onClick}
    className="text-gray-300 hover:text-white px-3 py-2 rounded-md text-sm font-medium transition-colors"
  >
    {label}
  </button>
);
