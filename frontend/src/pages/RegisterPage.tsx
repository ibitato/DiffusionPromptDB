/**
 * Register Page
 * Handles self-service account registration and verification
 */

import { FormEvent, useState } from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { LanguageToggle } from '../components/ui/LanguageToggle';
import { Loading } from '../components/ui/Loading';
import { authService } from '../services/auth.service';

export const RegisterPage = () => {
  const { t } = useTranslation();
  const [form, setForm] = useState({ username: '', email: '', password: '' });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [registerMessage, setRegisterMessage] = useState('');
  const [registerError, setRegisterError] = useState('');
  const [verificationToken, setVerificationToken] = useState<string | null>(null);
  const [registrationComplete, setRegistrationComplete] = useState(false);

  const handleInvalidInput = (
    event: FormEvent<HTMLInputElement>,
    messages: { required: string; typeMismatch?: string }
  ) => {
    const { validity } = event.currentTarget;
    if (validity.valueMissing) {
      event.currentTarget.setCustomValidity(messages.required);
    } else if (validity.typeMismatch && messages.typeMismatch) {
      event.currentTarget.setCustomValidity(messages.typeMismatch);
    } else {
      event.currentTarget.setCustomValidity('');
    }
  };

  const clearValidity = (event: FormEvent<HTMLInputElement>) => {
    event.currentTarget.setCustomValidity('');
  };

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setRegisterError('');
    setRegisterMessage('');
    setVerificationToken(null);
     setRegistrationComplete(false);
    setIsSubmitting(true);
    try {
      const response = await authService.register(form);
      setRegisterMessage(response.detail);
      if (response.warning) {
        setRegisterMessage((prev) => `${prev}\n${response.warning}`);
      }
      if (response.verification_token) {
        setVerificationToken(response.verification_token);
      }
      setRegistrationComplete(true);
    } catch (error) {
      setRegisterError(error instanceof Error ? error.message : t('register.errors.generic'));
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-900 flex items-center justify-center px-4">
      <div className="max-w-2xl w-full space-y-8">
        <div className="flex justify-center mb-4">
          <LanguageToggle />
        </div>

        <div className="text-center space-y-2">
          <h1 className="text-4xl font-bold text-white">{t('register.title')}</h1>
          <p className="text-gray-400">{t('register.subtitle')}</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-slate-800 rounded-lg shadow-xl p-6 space-y-4 border border-slate-700">
            <h2 className="text-xl font-semibold text-white">{t('register.createHeading')}</h2>
            <p className="text-sm text-gray-400">{t('register.createDescription')}</p>

            <form onSubmit={handleRegister} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  {t('register.username')}
                </label>
              <input
                type="text"
                value={form.username}
                onChange={(e) => setForm({ ...form, username: e.target.value })}
                required
                onInvalid={(e) =>
                  handleInvalidInput(e, { required: t('register.validation.usernameRequired') })
                }
                onInput={clearValidity}
                className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-violet-600"
                placeholder={t('register.usernamePlaceholder')}
                disabled={isSubmitting}
              />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  {t('register.email')}
                </label>
              <input
                type="email"
                value={form.email}
                onChange={(e) => setForm({ ...form, email: e.target.value })}
                required
                onInvalid={(e) =>
                  handleInvalidInput(e, {
                    required: t('register.validation.emailRequired'),
                    typeMismatch: t('register.validation.emailInvalid'),
                  })
                }
                onInput={clearValidity}
                className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-violet-600"
                placeholder={t('register.emailPlaceholder')}
                disabled={isSubmitting}
              />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  {t('register.password')}
                </label>
              <input
                type="password"
                value={form.password}
                onChange={(e) => setForm({ ...form, password: e.target.value })}
                required
                onInvalid={(e) =>
                  handleInvalidInput(e, { required: t('register.validation.passwordRequired') })
                }
                onInput={clearValidity}
                className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-violet-600"
                placeholder={t('register.passwordPlaceholder')}
                disabled={isSubmitting}
              />
                <p className="text-xs text-gray-500 mt-1">{t('register.passwordHint')}</p>
              </div>

              {registerError && (
                <div className="bg-red-500/10 border border-red-500 rounded-lg p-3 text-sm text-red-400">
                  {registerError}
                </div>
              )}

              {registerMessage && (
                <div className="bg-emerald-500/10 border border-emerald-500 rounded-lg p-3 text-sm text-emerald-300 whitespace-pre-line">
                  {registerMessage}
                </div>
              )}

              <button
                type="submit"
                disabled={isSubmitting}
                className="w-full py-3 px-4 bg-violet-600 hover:bg-violet-700 disabled:bg-slate-600 disabled:cursor-not-allowed text-white font-medium rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-violet-600 focus:ring-offset-2 focus:ring-offset-slate-800"
              >
                {isSubmitting ? (
                  <div className="flex items-center justify-center gap-2">
                    <Loading size="sm" />
                    {t('register.creating')}
                  </div>
                ) : (
                  t('register.createAccount')
                )}
              </button>
            </form>
          </div>

          <div className="bg-slate-800 rounded-lg shadow-xl p-6 space-y-4 border border-slate-700">
            <h2 className="text-xl font-semibold text-white">{t('register.verifyHeading')}</h2>
            <p className="text-sm text-gray-400 whitespace-pre-line">{t('register.verifyDescription')}</p>

            <ul className="list-disc list-inside text-sm text-gray-300 space-y-1">
              <li>{t('register.verifySteps.email')}</li>
              <li>{t('register.verifySteps.link')}</li>
              <li>{t('register.verifySteps.login')}</li>
            </ul>

            <div
              className={`rounded-lg border p-3 text-sm ${
                registrationComplete
                  ? 'border-emerald-500 bg-emerald-500/10 text-emerald-200'
                  : 'border-slate-600 bg-slate-700/50 text-gray-300'
              }`}
            >
              {registrationComplete ? t('register.messages.verifySuccess') : t('register.verifyPending')}
            </div>

            {verificationToken && (
              <div className="bg-yellow-500/10 border border-yellow-500 rounded-lg p-3 text-sm text-yellow-300 space-y-1">
                <p className="font-semibold">{t('register.debugTitle')}</p>
                <p className="text-xs break-words">{verificationToken}</p>
                <p className="text-xs text-yellow-200">{t('register.debugDescription')}</p>
              </div>
            )}

            <Link
              to="/login"
              className={`w-full inline-flex justify-center py-3 px-4 rounded-lg font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-slate-800 ${
                registrationComplete
                  ? 'bg-emerald-600 text-white hover:bg-emerald-700 focus:ring-emerald-600'
                  : 'bg-slate-700 text-gray-400 cursor-not-allowed'
              }`}
              aria-disabled={!registrationComplete}
            >
              {t('register.backToLogin')}
            </Link>
          </div>
        </div>

        <div className="text-center text-sm text-gray-400">
          {t('register.haveAccount')}{' '}
          <Link to="/login" className="text-violet-400 hover:text-violet-300">
            {t('register.backToLogin')}
          </Link>
        </div>
      </div>
    </div>
  );
};
