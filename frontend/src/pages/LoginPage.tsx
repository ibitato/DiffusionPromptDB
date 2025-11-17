/**
 * Login Page
 * User authentication page
 */

import { FormEvent, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuthStore } from '../store/authStore';
import { authService, PasswordExpiredError } from '../services/auth.service';
import { Loading } from '../components/ui/Loading';
import { LanguageToggle } from '../components/ui/LanguageToggle';
import { logError } from '../utils/logger';

export const LoginPage = () => {
  const { t } = useTranslation();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showPasswordReset, setShowPasswordReset] = useState(false);
  const [resetForm, setResetForm] = useState({ current: '', next: '', confirm: '' });
  const [resetError, setResetError] = useState('');
  const [isResetting, setIsResetting] = useState(false);
  const [forcedUsername, setForcedUsername] = useState('');

  const setAuth = useAuthStore((state) => state.setAuth);
  const navigate = useNavigate();

  const handleInvalid = (
    event: FormEvent<HTMLInputElement>,
    message: { required: string }
  ) => {
    event.currentTarget.setCustomValidity(message.required);
  };

  const clearValidity = (event: FormEvent<HTMLInputElement>) => {
    event.currentTarget.setCustomValidity('');
  };

  const translateLoginError = (message: string): string => {
    const translations: Record<string, string> = {
      'Invalid username or password': 'login.errors.invalidCredentials',
      'Incorrect username or password': 'login.errors.invalidCredentials',
      'Account disabled. Contact administrator.': 'login.errors.disabled',
      'Account disabled. Contact administrator': 'login.errors.disabled',
      'login.errors.generic': 'login.errors.generic',
    };

    const key = translations[message] ?? 'login.errors.generic';
    return t(key);
  };

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
      if (err instanceof PasswordExpiredError) {
        setForcedUsername(err.username);
        setShowPasswordReset(true);
        setResetForm({ current: '', next: '', confirm: '' });
        setResetError('');
        setError(err.message);
        setPassword('');
        return;
      }
      logError('Login error', err);
      const rawMessage = err instanceof Error ? err.message : 'login.errors.generic';
      const translatedMessage = translateLoginError(rawMessage);

      // Set error to display on page
      setError(translatedMessage);

      // Clear password for security but keep username
      setPassword('');
    } finally {
      // Always stop loading indicator
      setIsLoading(false);
    }
  };

  const handlePasswordReset = async (e: React.FormEvent) => {
    e.preventDefault();
    setResetError('');

    if (resetForm.next !== resetForm.confirm) {
      setResetError(t('login.passwordMismatch'));
      return;
    }

    setIsResetting(true);
    const targetUsername = forcedUsername || username;

    try {
      await authService.forcePasswordChange({
        username: targetUsername,
        current_password: resetForm.current,
        new_password: resetForm.next,
      });

      const response = await authService.login({
        username: targetUsername,
        password: resetForm.next,
      });

      setAuth(response.user, response.access_token);
      navigate('/dashboard');
    } catch (err) {
      logError('Password reset error', err);
      setResetError(
        err instanceof Error ? err.message : t('login.passwordUpdateError')
      );
    } finally {
      setIsResetting(false);
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
        <div className="bg-slate-800 rounded-lg shadow-xl p-8 space-y-6">
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
                onInvalid={(e) =>
                  handleInvalid(e, { required: t('login.validation.usernameRequired') })
                }
                onInput={clearValidity}
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
                onInvalid={(e) =>
                  handleInvalid(e, { required: t('login.validation.passwordRequired') })
                }
                onInput={clearValidity}
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

          <div className="space-y-3">
            <div className="text-center text-sm text-gray-400">
              {t('login.noAccount')}{' '}
              <Link to="/register" className="text-violet-400 hover:text-violet-300">
                {t('login.goToRegister')}
              </Link>
            </div>

            <Link
              to="/register"
              className="inline-flex w-full justify-center rounded-lg border border-violet-500 px-4 py-3 text-sm font-semibold text-violet-100 transition hover:bg-violet-600/10 focus:outline-none focus:ring-2 focus:ring-violet-500 focus:ring-offset-2 focus:ring-offset-slate-800"
            >
              {t('login.requestAccessButton')}
            </Link>
          </div>

          {showPasswordReset && (
            <div className="mt-8 border-t border-slate-700 pt-6">
              <h3 className="text-xl font-semibold text-white mb-2">
                {t('login.passwordExpiredTitle')}
              </h3>
              <p className="text-sm text-gray-400 mb-4">{t('login.passwordExpiredDescription')}</p>

              <form onSubmit={handlePasswordReset} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    {t('profile.password.current')}
                  </label>
                  <input
                    type="password"
                    value={resetForm.current}
                    onChange={(e) => setResetForm({ ...resetForm, current: e.target.value })}
                    className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-violet-600 focus:border-transparent"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    {t('login.newPassword')}
                  </label>
                  <input
                    type="password"
                    value={resetForm.next}
                    onChange={(e) => setResetForm({ ...resetForm, next: e.target.value })}
                    className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-violet-600 focus:border-transparent"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    {t('login.confirmPassword')}
                  </label>
                  <input
                    type="password"
                    value={resetForm.confirm}
                    onChange={(e) => setResetForm({ ...resetForm, confirm: e.target.value })}
                    className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-violet-600 focus:border-transparent"
                    required
                  />
                </div>

                {resetError && (
                  <div className="bg-red-500/10 border border-red-500 rounded-lg p-3">
                    <p className="text-red-400 text-sm font-medium">{resetError}</p>
                  </div>
                )}

                <button
                  type="submit"
                  disabled={isResetting}
                  className="w-full py-3 px-4 bg-emerald-600 hover:bg-emerald-700 disabled:bg-slate-600 disabled:cursor-not-allowed text-white font-medium rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-emerald-600 focus:ring-offset-2 focus:ring-offset-slate-800"
                >
                  {isResetting ? t('login.updatingPassword') : t('login.updatePassword')}
                </button>
              </form>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
