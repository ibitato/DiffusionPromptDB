/**
 * Settings Page
 * User preferences and configuration
 */

import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Header } from '../components/layout/Header';
import { Loading } from '../components/ui/Loading';
import { useToast } from '../components/ui/Toast';
import { preferencesService, UserPreferences } from '../services/preferences.service';

export const SettingsPage = () => {
  const { t } = useTranslation();
  const [preferences, setPreferences] = useState<UserPreferences | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [showUnspecified, setShowUnspecified] = useState(true);
  const [excludedTags, setExcludedTags] = useState<string[]>([]);
  const [newTag, setNewTag] = useState('');
  const toast = useToast();

  useEffect(() => {
    loadPreferences();
  }, []);

  const loadPreferences = async () => {
    try {
      const prefs = await preferencesService.getPreferences();
      setPreferences(prefs);
      setShowUnspecified(prefs.show_unspecified);
      setExcludedTags(prefs.excluded_tags);
    } catch (err) {
      console.error(t('common.errors.loadingPreferences'), err);
      toast.error(t('common.errors.loadingPreferences'));
    } finally {
      setIsLoading(false);
    }
  };

  const handleSave = async () => {
    setIsSaving(true);
    try {
      const updated = await preferencesService.updatePreferences({
        show_unspecified: showUnspecified,
        excluded_tags: excludedTags,
      });
      setPreferences(updated);
      toast.success(t('settings.messages.saved'));
    } catch (err) {
      console.error(t('common.errors.savingPreferences'), err);
      toast.error(t('settings.messages.saveError'));
    } finally {
      setIsSaving(false);
    }
  };

  const addTag = () => {
    const trimmed = newTag.trim();
    if (trimmed && !excludedTags.includes(trimmed)) {
      setExcludedTags([...excludedTags, trimmed]);
      setNewTag('');
    }
  };

  const removeTag = (tagToRemove: string) => {
    setExcludedTags(excludedTags.filter(tag => tag !== tagToRemove));
  };

  const resetToDefaults = () => {
    setShowUnspecified(true);
    setExcludedTags(['high quality', 'masterpiece', 'best quality']);
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-slate-900">
        <Header />
        <div className="flex items-center justify-center h-[calc(100vh-4rem)]">
          <Loading size="lg" text={t('settings.loading')} />
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-900">
      <Header />

      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Page Header */}
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-white mb-2">{t('settings.title')}</h2>
          <p className="text-gray-400">{t('settings.subtitle')}</p>
        </div>

        {/* Settings Sections */}
        <div className="space-y-6">
          {/* Display Preferences */}
          <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
            <h3 className="text-xl font-semibold text-white mb-4">{t('settings.display.title')}</h3>
            
            <div className="space-y-4">
              {/* Show Unspecified Toggle */}
              <div className="flex items-center justify-between p-4 bg-slate-700/50 rounded-lg">
                <div>
                  <h4 className="text-white font-medium">{t('settings.display.showUnspecified')}</h4>
                  <p className="text-sm text-gray-400 mt-1">
                    {t('settings.display.showUnspecifiedDesc')}
                  </p>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={showUnspecified}
                    onChange={(e) => setShowUnspecified(e.target.checked)}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-slate-600 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-800 rounded-full peer peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                </label>
              </div>
            </div>
          </div>

          {/* Tag Blacklist */}
          <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
            <h3 className="text-xl font-semibold text-white mb-4">{t('settings.blacklist.title')}</h3>
            <p className="text-sm text-gray-400 mb-4">{t('settings.blacklist.description')}</p>
            
            {/* Add New Tag */}
            <div className="flex gap-2 mb-4">
              <input
                type="text"
                value={newTag}
                onChange={(e) => setNewTag(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && addTag()}
                placeholder={t('settings.blacklist.addPlaceholder')}
                className="flex-1 px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-violet-600"
              />
              <button
                onClick={addTag}
                className="px-4 py-2 bg-violet-600 hover:bg-violet-700 text-white rounded-lg font-medium transition-colors"
              >
                {t('settings.blacklist.add')}
              </button>
            </div>

            {/* Excluded Tags List */}
            <div className="space-y-2">
              {excludedTags.length > 0 ? (
                <div className="flex flex-wrap gap-2">
                  {excludedTags.map((tag, index) => (
                    <span
                      key={index}
                      className="inline-flex items-center gap-2 px-3 py-1 bg-slate-700 text-gray-300 rounded-full"
                    >
                      {tag}
                      <button
                        onClick={() => removeTag(tag)}
                        className="hover:text-red-400 transition-colors"
                      >
                        ×
                      </button>
                    </span>
                  ))}
                </div>
              ) : (
                <p className="text-gray-500 text-sm italic">{t('settings.blacklist.noTags')}</p>
              )}
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex justify-between">
            <button
              onClick={resetToDefaults}
              className="px-6 py-3 bg-slate-700 hover:bg-slate-600 text-white rounded-lg font-medium transition-colors"
            >
              {t('settings.actions.reset')}
            </button>
            
            <button
              onClick={handleSave}
              disabled={isSaving}
              className="px-6 py-3 bg-violet-600 hover:bg-violet-700 disabled:bg-slate-600 disabled:cursor-not-allowed text-white rounded-lg font-medium transition-colors flex items-center gap-2"
            >
              {isSaving && <Loading size="sm" />}
              {isSaving ? t('settings.actions.saving') : t('settings.actions.save')}
            </button>
          </div>
        </div>
      </main>
    </div>
  );
};
