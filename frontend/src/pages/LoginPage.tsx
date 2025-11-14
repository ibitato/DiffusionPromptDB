/**
 * Login Page
 * User authentication page
 */

import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuthStore } from '../store/authStore';
import { authService } from '../services/auth.service';
import { Loading } from '../components/ui/Loading';
import { LanguageToggle } from '../components/ui/LanguageToggle';

export const LoginPage = () => {
  const { t } = useTranslation();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const setAuth = useAuthStore((state) => state.setAuth);
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(''); // Clear any previous errors
    setIsLoading(true);

    try {
      // Using real API login endpoint
      const response = await authService.login({ username, password });

      setAuth(response.user, response.access_token);
      navigate('/dashboard');
    } catch (err) {
      // Show error directly on the page
      console.error('Login error:', err);
      const errorMessage = err instanceof Error ? err.message : 'Login failed';
      
      // Set error to display on page
      setError(errorMessage);
      
      // Clear password for security but keep username
      setPassword('');
    } finally {
      // Always stop loading indicator
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-900 flex items-center justify-center px-4">
      <div className="max-w-md w-full space-y-8">
        {/* Language Toggle - Centered */}
        <div className="flex justify-center mb-4">
          <LanguageToggle />
        </div>

        {/* Header */}
        <div className="text-center">
          <h1 className="text-4xl font-bold text-white mb-2">{t('app.title')}</h1>
          <p className="text-gray-400">{t('app.subtitle')}</p>
        </div>

        {/* Login Form */}
        <div className="bg-slate-800 rounded-lg shadow-xl p-8">
          <h2 className="text-2xl font-semibold text-white mb-6">{t('login.title')}</h2>

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Username */}
            <div>
              <label htmlFor="username" className="block text-sm font-medium text-gray-300 mb-2">
                {t('login.username')}
              </label>
              <input
                id="username"
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
                className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-violet-600 focus:border-transparent"
                placeholder={t('login.usernamePlaceholder')}
                disabled={isLoading}
              />
            </div>

            {/* Password */}
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-300 mb-2">
                {t('login.password')}
              </label>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-violet-600 focus:border-transparent"
                placeholder={t('login.passwordPlaceholder')}
                disabled={isLoading}
              />
            </div>

            {/* Error Message */}
            {error && (
              <div className="bg-red-500/10 border border-red-500 rounded-lg p-3">
                <p className="text-red-400 text-sm font-medium">{error}</p>
              </div>
            )}

            {/* Submit Button */}
            <button
              type="submit"
              disabled={isLoading}
              className="w-full py-3 px-4 bg-violet-600 hover:bg-violet-700 disabled:bg-slate-600 disabled:cursor-not-allowed text-white font-medium rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-violet-600 focus:ring-offset-2 focus:ring-offset-slate-800"
            >
              {isLoading ? (
                <div className="flex items-center justify-center">
                  <Loading size="sm" />
                  <span className="ml-2">{t('login.loggingIn')}</span>
                </div>
              ) : (
                t('login.submit')
              )}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};
