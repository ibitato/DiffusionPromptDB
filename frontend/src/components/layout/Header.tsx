/**
 * Header Component
 * Navigation header with user menu
 */

import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';
import { SearchBar } from '../search/SearchBar';
import { LanguageToggle } from '../ui/LanguageToggle';

export const Header = () => {
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
            <h1 className="text-xl font-bold text-white">
              DiffusionPromptDB
            </h1>
          </div>

          {/* Navigation */}
          <nav className="flex items-center space-x-4">
            <button
              onClick={() => navigate('/dashboard')}
              className="text-gray-300 hover:text-white px-3 py-2 rounded-md text-sm font-medium transition-colors"
            >
              Dashboard
            </button>
            <button
              onClick={() => navigate('/prompts')}
              className="text-gray-300 hover:text-white px-3 py-2 rounded-md text-sm font-medium transition-colors"
            >
              Prompts
            </button>
            <button
              onClick={() => navigate('/search')}
              className="text-gray-300 hover:text-white px-3 py-2 rounded-md text-sm font-medium transition-colors"
            >
              Búsqueda
            </button>
          </nav>

          {/* Search Bar */}
          <SearchBar />

          {/* User Menu */}
          <div className="flex items-center space-x-4">
            <LanguageToggle />
            <span className="text-gray-400 text-sm">
              {user?.username}
            </span>
            <button
              onClick={handleLogout}
              className="bg-slate-700 hover:bg-slate-600 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors"
            >
              Cerrar Sesión
            </button>
          </div>
        </div>
      </div>
    </header>
  );
};
