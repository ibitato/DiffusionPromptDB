/**
 * Info Page
 * Public description of user-facing features
 */

import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { LanguageToggle } from '../components/ui/LanguageToggle';

type InfoSection = {
  title: string;
  description: string;
  bullets: string[];
};

export const InfoPage = () => {
  const { t } = useTranslation();
  const sections = t('info.sections', { returnObjects: true }) as Record<string, InfoSection>;
  const highlights = t('info.highlights', { returnObjects: true }) as string[];

  return (
    <div className="min-h-screen bg-slate-950 text-white px-4 py-10">
      <div className="mx-auto max-w-5xl space-y-10">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="space-y-4">
            <p className="text-xs font-semibold uppercase tracking-[0.3em] text-violet-300">
              {t('info.audience')}
            </p>
            <h1 className="text-3xl font-bold md:text-4xl">{t('info.title')}</h1>
            <p className="text-base text-slate-300 md:text-lg">{t('info.subtitle')}</p>
          </div>
          <LanguageToggle />
        </div>

        <div className="grid gap-4 md:grid-cols-3">
          {highlights.map((item) => (
            <div
              key={item}
              className="rounded-2xl border border-slate-800 bg-slate-900/70 p-4 text-sm text-slate-200 shadow-lg shadow-black/20"
            >
              {item}
            </div>
          ))}
        </div>

        <div className="space-y-6">
          {Object.entries(sections).map(([key, section]) => (
            <section
              key={key}
              className="rounded-3xl border border-slate-900/80 bg-slate-900/50 p-6 shadow-inner shadow-black/40"
            >
              <div className="space-y-2">
                <h2 className="text-2xl font-semibold text-white">{section.title}</h2>
                <p className="text-sm text-slate-300">{section.description}</p>
              </div>
              <ul className="mt-4 space-y-3 text-sm text-slate-100">
                {section.bullets.map((bullet) => (
                  <li key={bullet} className="flex gap-3">
                    <span className="mt-1 h-2 w-2 rounded-full bg-violet-400" />
                    <span className="leading-relaxed text-slate-200">{bullet}</span>
                  </li>
                ))}
              </ul>
            </section>
          ))}
        </div>

        <div className="flex flex-wrap items-center justify-center gap-4 border-t border-slate-900 pt-6">
          <Link
            to="/login"
            className="inline-flex items-center justify-center rounded-xl border border-slate-700 px-6 py-3 text-sm font-semibold text-slate-100 transition hover:border-violet-500 hover:text-white"
          >
            {t('info.actions.backToLogin')}
          </Link>
          <Link
            to="/register"
            className="inline-flex items-center justify-center rounded-xl bg-violet-600 px-6 py-3 text-sm font-semibold text-white transition hover:bg-violet-500"
          >
            {t('info.actions.requestAccess')}
          </Link>
        </div>
      </div>
    </div>
  );
};
