import { useEffect, useMemo, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { LanguageToggle } from '../components/ui/LanguageToggle';
import { authService } from '../services/auth.service';

type VerificationState = 'loading' | 'success' | 'error';

export const VerifyAccountPage = () => {
  const { t } = useTranslation();
  const [searchParams] = useSearchParams();
  const token = searchParams.get('token');
  const [status, setStatus] = useState<VerificationState>('loading');
  const [messageKey, setMessageKey] = useState('verifyAccount.messages.processing');
  const [customMessage, setCustomMessage] = useState<string | null>(null);

  useEffect(() => {
    if (!token) {
      setStatus('error');
      setMessageKey('verifyAccount.errors.missingToken');
      setCustomMessage(null);
      return;
    }

    let isMounted = true;
    const verify = async () => {
      try {
        await authService.verifyAccount(token);
        if (!isMounted) {
          return;
        }
        setStatus('success');
        setMessageKey('verifyAccount.messages.success');
        setCustomMessage(null);
      } catch (error) {
        if (!isMounted) {
          return;
        }
        setStatus('error');
        if (error instanceof Error && error.message) {
          setCustomMessage(error.message);
        } else {
          setMessageKey('verifyAccount.messages.genericError');
          setCustomMessage(null);
        }
      }
    };

    verify();
    return () => {
      isMounted = false;
    };
  }, [token]);

  const message = useMemo(() => customMessage ?? t(messageKey), [customMessage, messageKey, t]);

  return (
    <div className="relative min-h-screen bg-gradient-to-b from-gray-900 via-gray-800 to-black flex items-center justify-center px-4">
      <div className="absolute top-6 right-6">
        <LanguageToggle />
      </div>

      <div className="w-full max-w-md rounded-2xl border border-white/10 bg-white/5 p-8 text-center shadow-2xl backdrop-blur">
        <h1 className="text-2xl font-semibold text-white mb-2">{t('verifyAccount.title')}</h1>
        <p className="text-sm text-gray-400 mb-6">{t('verifyAccount.description')}</p>
        <p className="text-gray-200 mb-8">{message}</p>

        {status === 'loading' && (
          <div className="animate-pulse text-sm text-blue-300">{t('verifyAccount.status.validating')}</div>
        )}

        {status === 'success' && (
          <Link
            to="/login"
            className="inline-flex items-center justify-center rounded-lg bg-blue-500 px-4 py-2 text-white transition hover:bg-blue-600"
          >
            {t('verifyAccount.actions.goToLogin')}
          </Link>
        )}

        {status === 'error' && (
          <div className="space-y-4">
            <Link
              to="/register"
              className="inline-flex items-center justify-center rounded-lg border border-white/20 px-4 py-2 text-sm text-white transition hover:bg-white/10"
            >
              {t('verifyAccount.actions.requestNew')}
            </Link>
            <p className="text-xs text-gray-400">{t('verifyAccount.support')}</p>
          </div>
        )}
      </div>
    </div>
  );
};
