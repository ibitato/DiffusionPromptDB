/**
 * Profile Page
 * User profile, security controls, and preferences
 */

import { useEffect, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Header } from '../components/layout/Header';
import { Loading } from '../components/ui/Loading';
import { useToast } from '../hooks/useToast';
import { useAuthStore } from '../store/authStore';
import { preferencesService } from '../services/preferences.service';
import { profileService } from '../services/profile.service';
import { landingPageLabels } from '../utils/landingPageLabels';
import { DeleteAccountPayload, UserProfile } from '../types/api.types';
import { logError } from '../utils/logger';

export const ProfilePage = () => {
  const { t } = useTranslation();
  const toast = useToast();
  const { updateUser } = useAuthStore();

  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [profileForm, setProfileForm] = useState({
    full_name: '',
    location: '',
    language: 'en',
  });
  const [defaultLanding, setDefaultLanding] = useState<'dashboard' | 'search'>('dashboard');
  const [passwordForm, setPasswordForm] = useState({ current: '', next: '', confirm: '' });
  const [passwordVisible, setPasswordVisible] = useState(false);
  const [deletionForm, setDeletionForm] = useState({ password: '', confirm: false });

  const [showUnspecified, setShowUnspecified] = useState(true);
  const [myPromptsOnly, setMyPromptsOnly] = useState(false);
  const [excludedTags, setExcludedTags] = useState<string[]>([]);
  const [newTag, setNewTag] = useState('');

  const [isLoading, setIsLoading] = useState(true);
  const [savingProfile, setSavingProfile] = useState(false);
  const [savingPassword, setSavingPassword] = useState(false);
  const [savingPreferences, setSavingPreferences] = useState(false);
  const [deletingAccount, setDeletingAccount] = useState(false);

  useEffect(() => {
    const load = async () => {
      try {
        const [profileData, prefs] = await Promise.all([
          profileService.getProfile(),
          preferencesService.getPreferences(),
        ]);
        setProfile(profileData);
        setProfileForm({
          full_name: profileData.full_name ?? '',
          location: profileData.location ?? '',
          language: profileData.language ?? 'en',
        });
        setDefaultLanding(profileData.default_landing_page ?? 'dashboard');
        setShowUnspecified(prefs.show_unspecified);
        setMyPromptsOnly(prefs.my_prompts_only);
        setExcludedTags(prefs.excluded_tags);
        updateUser(profileData);
      } catch (error) {
        logError('Failed to load profile data', error);
        toast.error(t('profile.errors.load'));
      } finally {
        setIsLoading(false);
      }
    };

    load();
  }, [t, toast, updateUser]);

  const handleProfileSave = async () => {
    if (!profile) return;
    setSavingProfile(true);
    try {
      const updated = await profileService.updateProfile(profileForm);
      setProfile(updated);
      updateUser(updated);
      toast.success(t('profile.messages.profileUpdated'));
    } catch (error) {
      toast.error(t('profile.errors.profileUpdate'));
    } finally {
      setSavingProfile(false);
    }
  };

  const handleDefaultLandingChange = async (value: 'dashboard' | 'search') => {
    setDefaultLanding(value);
    try {
      const updated = await profileService.updateDefaultLanding(value);
      setProfile(updated);
      updateUser(updated);
      toast.success(t('profile.messages.landingUpdated'));
    } catch (error) {
      toast.error(t('profile.errors.landingUpdate'));
    }
  };

  const handlePasswordChange = async () => {
    if (passwordForm.next !== passwordForm.confirm) {
      toast.error(t('profile.errors.passwordMismatch'));
      return;
    }
    setSavingPassword(true);
    try {
      await profileService.updatePassword({
        current_password: passwordForm.current,
        new_password: passwordForm.next,
      });
      setPasswordForm({ current: '', next: '', confirm: '' });
      toast.success(t('profile.messages.passwordUpdated'));
    } catch (error) {
      toast.error(t('profile.errors.passwordUpdate'));
    } finally {
      setSavingPassword(false);
    }
  };

  const handlePreferencesSave = async () => {
    setSavingPreferences(true);
    try {
      await preferencesService.updatePreferences({
        show_unspecified: showUnspecified,
        my_prompts_only: myPromptsOnly,
        excluded_tags: excludedTags,
      });
      toast.success(t('profile.messages.preferencesUpdated'));
    } catch (error) {
      toast.error(t('profile.errors.preferencesUpdate'));
    } finally {
      setSavingPreferences(false);
    }
  };

  const handleDeleteAccount = async () => {
    if (!deletionForm.confirm) {
      toast.error(t('profile.errors.confirmDeletion'));
      return;
    }
    setDeletingAccount(true);
    const payload: DeleteAccountPayload = {
      password: deletionForm.password,
      confirm: true,
    };
    try {
      await profileService.deleteAccount(payload);
      toast.success(t('profile.messages.accountDeleted'));
      localStorage.clear();
      window.location.href = '/login';
    } catch (error) {
      toast.error(t('profile.errors.accountDeletion'));
    } finally {
      setDeletingAccount(false);
    }
  };

  const addTag = () => {
    const trimmed = newTag.trim();
    if (trimmed && !excludedTags.includes(trimmed)) {
      setExcludedTags([...excludedTags, trimmed]);
      setNewTag('');
    }
  };

  const landingOptions = useMemo(() => landingPageLabels(t), [t]);

  if (isLoading || !profile) {
    return (
      <div className="min-h-screen bg-slate-900">
        <Header />
        <div className="flex items-center justify-center h-[calc(100vh-4rem)]">
          <Loading size="lg" text={t('profile.loading')} />
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-900">
      <Header />
      <main className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
        <section className="bg-slate-800 rounded-lg p-6 border border-slate-700">
          <h2 className="text-2xl font-semibold text-white mb-4">{t('profile.title')}</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm text-gray-400 mb-2">{t('profile.username')}</label>
              <input
                value={profile.username}
                disabled
                className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white"
              />
            </div>
            <div>
              <label className="block text-sm text-gray-400 mb-2">{t('profile.email')}</label>
              <input
                value={profile.email ?? ''}
                disabled
                className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white"
              />
            </div>
            <div>
              <label className="block text-sm text-gray-400 mb-2">{t('profile.fullName')}</label>
              <input
                value={profileForm.full_name}
                onChange={(e) => setProfileForm({ ...profileForm, full_name: e.target.value })}
                className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white"
              />
            </div>
            <div>
              <label className="block text-sm text-gray-400 mb-2">{t('profile.location')}</label>
              <input
                value={profileForm.location}
                onChange={(e) => setProfileForm({ ...profileForm, location: e.target.value })}
                className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white"
              />
            </div>
            <div>
              <label className="block text-sm text-gray-400 mb-2">{t('profile.language')}</label>
              <input
                value={profileForm.language}
                onChange={(e) => setProfileForm({ ...profileForm, language: e.target.value })}
                className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white"
              />
            </div>
          </div>
          <div className="flex justify-end mt-6">
            <button
              onClick={handleProfileSave}
              disabled={savingProfile}
              className="px-4 py-2 bg-violet-600 hover:bg-violet-700 disabled:opacity-50 text-white rounded-lg"
            >
              {savingProfile ? t('profile.saving') : t('profile.save')}
            </button>
          </div>
        </section>

        <section className="bg-slate-800 rounded-lg p-6 border border-slate-700">
          <h3 className="text-xl font-semibold text-white mb-4">{t('profile.defaultLanding')}</h3>
          <div className="flex gap-6">
            {landingOptions.map((option) => (
              <label key={option.value} className="flex items-center space-x-2 text-gray-300">
                <input
                  type="radio"
                  value={option.value}
                  checked={defaultLanding === option.value}
                  onChange={() => handleDefaultLandingChange(option.value)}
                />
                <span>{option.label}</span>
              </label>
            ))}
          </div>
        </section>

        <section className="bg-slate-800 rounded-lg p-6 border border-slate-700">
          <h3 className="text-xl font-semibold text-white mb-4">{t('profile.password.title')}</h3>
          <div className="grid md:grid-cols-3 gap-4">
            {['current', 'next', 'confirm'].map((field) => (
              <div key={field}>
                <label className="block text-sm text-gray-400 mb-2">
                  {t(`profile.password.${field}`)}
                </label>
                <input
                  type={passwordVisible ? 'text' : 'password'}
                  value={passwordForm[field as keyof typeof passwordForm]}
                  onChange={(e) =>
                    setPasswordForm({ ...passwordForm, [field]: e.target.value })
                  }
                  className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white"
                />
              </div>
            ))}
          </div>
          <div className="flex items-center justify-between mt-4">
            <label className="flex items-center space-x-2 text-gray-400 text-sm">
              <input
                type="checkbox"
                checked={passwordVisible}
                onChange={(e) => setPasswordVisible(e.target.checked)}
              />
              <span>{t('profile.password.show')}</span>
            </label>
            <button
              onClick={handlePasswordChange}
              disabled={savingPassword}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg disabled:opacity-50"
            >
              {savingPassword ? t('profile.saving') : t('profile.password.update')}
            </button>
          </div>
        </section>

        <section className="bg-slate-800 rounded-lg p-6 border border-slate-700">
          <h3 className="text-xl font-semibold text-white mb-4">{t('profile.preferences.title')}</h3>
          <div className="grid md:grid-cols-2 gap-4">
            <PreferenceCard
              title={t('profile.preferences.showUnspecified')}
              description={t('profile.preferences.showUnspecifiedDesc')}
              value={showUnspecified}
              onChange={setShowUnspecified}
            />
            <PreferenceCard
              title={t('profile.preferences.myPrompts')}
              description={t('profile.preferences.myPromptsDesc')}
              value={myPromptsOnly}
              onChange={setMyPromptsOnly}
            />
          </div>
          <div className="mt-6">
            <label className="block text-sm text-gray-400 mb-2">
              {t('profile.preferences.excludedTags')}
            </label>
            <div className="flex gap-2 mb-3">
              <input
                value={newTag}
                onChange={(e) => setNewTag(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && addTag()}
                placeholder={t('profile.preferences.tagPlaceholder')}
                className="flex-1 px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white"
              />
              <button
                onClick={addTag}
                className="px-4 py-2 bg-violet-600 hover:bg-violet-700 text-white rounded-lg"
              >
                {t('profile.preferences.addTag')}
              </button>
            </div>
            <div className="flex flex-wrap gap-2">
              {excludedTags.map((tag) => (
                <span
                  key={tag}
                  className="px-3 py-1 rounded-full bg-slate-700 text-gray-300 flex items-center gap-2"
                >
                  {tag}
                  <button
                    onClick={() =>
                      setExcludedTags(excludedTags.filter((existing) => existing !== tag))
                    }
                    className="text-red-400 hover:text-red-300"
                  >
                    ×
                  </button>
                </span>
              ))}
            </div>
          </div>
          <div className="flex justify-end mt-6">
            <button
              onClick={handlePreferencesSave}
              disabled={savingPreferences}
              className="px-4 py-2 bg-violet-600 hover:bg-violet-700 text-white rounded-lg disabled:opacity-50"
            >
              {savingPreferences ? t('profile.saving') : t('profile.save')}
            </button>
          </div>
        </section>

        <section className="bg-red-950/40 border border-red-700 rounded-lg p-6">
          <h3 className="text-xl font-semibold text-red-300 mb-2">{t('profile.danger.title')}</h3>
          <p className="text-sm text-red-200 mb-4">{t('profile.danger.description')}</p>
          <div className="grid md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm text-red-200 mb-2">
                {t('profile.danger.password')}
              </label>
              <input
                type="password"
                value={deletionForm.password}
                onChange={(e) => setDeletionForm({ ...deletionForm, password: e.target.value })}
                className="w-full px-4 py-2 bg-slate-900 border border-red-700 rounded-lg text-white"
              />
            </div>
            <label className="flex items-center space-x-2 text-red-200 text-sm mt-6">
              <input
                type="checkbox"
                checked={deletionForm.confirm}
                onChange={(e) => setDeletionForm({ ...deletionForm, confirm: e.target.checked })}
              />
              <span>{t('profile.danger.confirm')}</span>
            </label>
          </div>
          <button
            onClick={handleDeleteAccount}
            disabled={deletingAccount}
            className="mt-4 px-4 py-2 bg-red-700 hover:bg-red-600 text-white rounded-lg disabled:opacity-50"
          >
            {deletingAccount ? t('profile.danger.deleting') : t('profile.danger.delete')}
          </button>
        </section>
      </main>
    </div>
  );
};

interface PreferenceCardProps {
  title: string;
  description: string;
  value: boolean;
  onChange: (value: boolean) => void;
}

const PreferenceCard = ({ title, description, value, onChange }: PreferenceCardProps) => (
  <div className="p-4 bg-slate-700/40 rounded-lg border border-slate-600">
    <div className="flex items-center justify-between">
      <div>
        <h4 className="text-white font-medium">{title}</h4>
        <p className="text-sm text-gray-400 mt-1">{description}</p>
      </div>
      <label className="relative inline-flex items-center cursor-pointer">
        <input
          type="checkbox"
          checked={value}
          onChange={(e) => onChange(e.target.checked)}
          className="sr-only peer"
        />
        <div className="w-11 h-6 bg-slate-600 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-violet-800 rounded-full peer peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-violet-600"></div>
      </label>
    </div>
  </div>
);
