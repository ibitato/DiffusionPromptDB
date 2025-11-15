import { TFunction } from 'i18next';

export const landingPageLabels = (t: TFunction) => [
  { value: 'dashboard' as const, label: t('profile.landing.dashboard') },
  { value: 'search' as const, label: t('profile.landing.search') },
];
