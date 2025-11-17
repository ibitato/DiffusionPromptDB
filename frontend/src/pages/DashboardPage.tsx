/**
 * Dashboard Page
 * Main dashboard with statistics and overview
 */

import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Header } from '../components/layout/Header';
import { Loading } from '../components/ui/Loading';
import { Modal } from '../components/ui/Modal';
import { StatsCharts } from '../components/dashboard/StatsCharts';
import { statsService } from '../services/stats.service';
import { searchService } from '../services/search.service';
import { preferencesService } from '../services/preferences.service';
import { ComplexSearchParams, Stats } from '../types/api.types';
import { useAuthStore } from '../store/authStore';
import { logError } from '../utils/logger';

export const DashboardPage = () => {
  const { t } = useTranslation();
  const user = useAuthStore((state) => state.user);
  const [stats, setStats] = useState<Stats | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [showArtStylesModal, setShowArtStylesModal] = useState(false);
  const [showTagsModal, setShowTagsModal] = useState(false);
  const [showNsfwModal, setShowNsfwModal] = useState(false);
  const [allArtStyles, setAllArtStyles] = useState<Array<{ style: string; count: number }>>([]);
  const [allTags, setAllTags] = useState<Array<{ tag: string; count: number }>>([]);
  const [showUnspecified, setShowUnspecified] = useState(true);
  const [excludedTags, setExcludedTags] = useState<string[]>([]);
  const [myPromptsOnly, setMyPromptsOnly] = useState(false);
  const [preferencesLoaded, setPreferencesLoaded] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    let isMounted = true;

    const fetchPreferences = async () => {
      try {
        const prefs = await preferencesService.getPreferences();
        if (!isMounted) return;
        setShowUnspecified(prefs.show_unspecified);
        setExcludedTags(prefs.excluded_tags);
        setMyPromptsOnly(prefs.my_prompts_only);
      } catch (err) {
        if (!isMounted) return;
        logError(t('common.errors.loadingPreferences'), err);
        setShowUnspecified(true);
        setExcludedTags(['high quality', 'masterpiece', 'best quality']);
      } finally {
        if (isMounted) {
          setPreferencesLoaded(true);
        }
      }
    };

    fetchPreferences();
    return () => {
      isMounted = false;
    };
  }, [t]);

  useEffect(() => {
    if (!preferencesLoaded) return;
    let isMounted = true;

    const fetchStats = async () => {
      setIsLoading(true);
      try {
        const data = await statsService.getStats(myPromptsOnly);
        if (!isMounted) return;
        setStats(data);
        setError('');
      } catch (err) {
        if (!isMounted) return;
        setError(err instanceof Error ? err.message : t('dashboard.errors.load'));
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    };

    fetchStats();
    return () => {
      isMounted = false;
    };
  }, [preferencesLoaded, myPromptsOnly, t]);

  // Filter function to exclude unspecified
  const filterUnspecified = (styles: Array<{ style: string; count: number }>) => {
    if (showUnspecified) return styles;
    return styles.filter((s) => s.style.toLowerCase() !== 'unspecified');
  };

  // Filter function to exclude blacklisted tags
  const filterBlacklistedTags = (tags: Array<{ tag: string; count: number }>) => {
    return tags.filter((t) => !excludedTags.includes(t.tag.toLowerCase()));
  };

  const loadAllArtStyles = async () => {
    try {
      const filters = await statsService.getFilters();
      setAllArtStyles(filters.art_styles);
    } catch (err) {
      logError(t('common.errors.loadingArtStyles'), err);
    }
  };

  const loadAllTags = async () => {
    try {
      // Get all tags by querying with empty filters
      const params: ComplexSearchParams = { limit: 1000 };
      if (myPromptsOnly && user) {
        params.my_prompts = true;
      }
      const response = await searchService.complexSearch(params);
      // Extract unique tags from results
      const tagCounts = new Map<string, number>();
      response.results.forEach((result) => {
        if (result.tags) {
          result.tags.forEach((tag) => {
            tagCounts.set(tag, (tagCounts.get(tag) || 0) + 1);
          });
        }
      });
      const sortedTags = Array.from(tagCounts.entries())
        .map(([tag, count]) => ({ tag, count }))
        .sort((a, b) => b.count - a.count);
      setAllTags(sortedTags);
    } catch (err) {
      logError(t('common.errors.loadingTags'), err);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-slate-900">
        <Header />
        <div className="flex items-center justify-center h-[calc(100vh-4rem)]">
          <Loading size="lg" text={t('dashboard.loadingStats')} />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-slate-900">
        <Header />
        <div className="max-w-7xl mx-auto px-4 py-8">
          <div className="bg-red-500/10 border border-red-500 rounded-lg p-4">
            <p className="text-red-400">{error}</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-900">
      <Header />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Page Header */}
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-white mb-2">{t('dashboard.title')}</h2>
          <p className="text-gray-400">{t('dashboard.subtitle')}</p>
        </div>

        {user && (
          <div className="mb-8">
            <label className="flex items-start gap-3 p-4 bg-slate-800 border border-slate-700 rounded-lg cursor-pointer">
              <input
                type="checkbox"
                checked={myPromptsOnly}
                onChange={(e) => setMyPromptsOnly(e.target.checked)}
                className="mt-1 w-5 h-5 bg-slate-700 border border-slate-600 rounded text-violet-600 focus:ring-2 focus:ring-violet-600"
              />
              <div>
                <p className="text-sm font-semibold text-white">
                  {t('dashboard.filters.myPrompts')}
                </p>
                <p className="text-xs text-gray-400 mt-1">
                  {t('dashboard.filters.myPromptsDesc')}
                </p>
              </div>
            </label>
          </div>
        )}

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {/* Total Prompts */}
          <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm font-medium">{t('dashboard.totalPrompts')}</p>
                <p className="text-3xl font-bold text-white mt-2">{stats?.total_prompts || 0}</p>
              </div>
              <div className="bg-violet-600/10 p-3 rounded-lg">
                <svg
                  className="w-8 h-8 text-violet-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                  />
                </svg>
              </div>
            </div>
          </div>

          {/* Top Art Styles */}
          <div
            onClick={() => {
              setShowArtStylesModal(true);
              loadAllArtStyles();
            }}
            className="bg-slate-800 rounded-lg p-6 border border-slate-700 cursor-pointer hover:bg-slate-750 hover:border-blue-600 transition-all duration-200 hover:shadow-lg hover:shadow-blue-600/20"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm font-medium">{t('dashboard.artStyles')}</p>
                <p className="text-3xl font-bold text-white mt-2">
                  {stats?.total_art_styles || stats?.top_art_styles?.length || 0}
                </p>
                <p className="text-xs text-blue-400 mt-2">{t('dashboard.clickToViewAll')}</p>
              </div>
              <div className="bg-blue-600/10 p-3 rounded-lg">
                <svg
                  className="w-8 h-8 text-blue-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01"
                  />
                </svg>
              </div>
            </div>
          </div>

          {/* Top Tags */}
          <div
            onClick={() => {
              setShowTagsModal(true);
              if (stats?.top_tags && stats.top_tags.length > 0) {
                setAllTags(stats.top_tags);
              }
              loadAllTags();
            }}
            className="bg-slate-800 rounded-lg p-6 border border-slate-700 cursor-pointer hover:bg-slate-750 hover:border-green-600 transition-all duration-200 hover:shadow-lg hover:shadow-green-600/20"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm font-medium">{t('dashboard.tags')}</p>
                <p className="text-3xl font-bold text-white mt-2">
                  {stats?.total_tags || stats?.top_tags?.length || 0}
                </p>
                <p className="text-xs text-green-400 mt-2">{t('dashboard.clickToViewAll')}</p>
              </div>
              <div className="bg-green-600/10 p-3 rounded-lg">
                <svg
                  className="w-8 h-8 text-green-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z"
                  />
                </svg>
              </div>
            </div>
          </div>

          {/* NSFW Categories */}
          <div
            onClick={() => setShowNsfwModal(true)}
            className="bg-slate-800 rounded-lg p-6 border border-slate-700 cursor-pointer hover:bg-slate-750 hover:border-orange-600 transition-all duration-200 hover:shadow-lg hover:shadow-orange-600/20"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm font-medium">{t('dashboard.nsfwCategories')}</p>
                <p className="text-3xl font-bold text-white mt-2">
                  {Object.keys(stats?.nsfw_distribution || {}).length}
                </p>
                <p className="text-xs text-orange-400 mt-2">{t('dashboard.clickToViewAll')}</p>
              </div>
              <div className="bg-orange-600/10 p-3 rounded-lg">
                <svg
                  className="w-8 h-8 text-orange-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                  />
                </svg>
              </div>
            </div>
          </div>
        </div>

        {/* Top Tags Table */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xl font-semibold text-white">{t('dashboard.topTags')}</h3>
              <span className="text-xs text-gray-500 bg-slate-700 px-2 py-1 rounded">
                Top 5 de {stats?.total_tags || 0}
              </span>
            </div>
            <div className="space-y-3">
              {filterBlacklistedTags(stats?.top_tags || [])
                .slice(0, 5)
                .map((tag, index) => (
                  <div
                    key={index}
                    className="flex items-center justify-between p-3 bg-slate-700/50 rounded-lg"
                  >
                    <span className="text-gray-300">{tag.tag}</span>
                    <span className="text-violet-400 font-semibold">{tag.count}</span>
                  </div>
                ))}
            </div>
          </div>

          {/* Top Art Styles */}
          <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-3">
                <h3 className="text-xl font-semibold text-white">{t('dashboard.topStyles')}</h3>
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={showUnspecified}
                    onChange={(e) => setShowUnspecified(e.target.checked)}
                    className="w-4 h-4 text-blue-600 bg-slate-700 border-slate-600 rounded focus:ring-blue-500"
                  />
                  <span className="text-xs text-gray-400">
                    {t('dashboard.display.showUnspecified')}
                  </span>
                </label>
              </div>
              <span className="text-xs text-gray-500 bg-slate-700 px-2 py-1 rounded">
                {t('dashboard.modals.showing')} 5 {t('dashboard.modals.of')}{' '}
                {filterUnspecified(stats?.top_art_styles || []).length}
              </span>
            </div>
            <div className="space-y-3">
              {filterUnspecified(stats?.top_art_styles || [])
                .slice(0, 5)
                .map((style, index) => (
                  <div
                    key={index}
                    className="flex items-center justify-between p-3 bg-slate-700/50 rounded-lg"
                  >
                    <span className="text-gray-300">{style.style}</span>
                    <span className="text-blue-400 font-semibold">{style.count}</span>
                  </div>
                ))}
            </div>
          </div>
        </div>

        {/* NSFW Distribution */}
        <div className="bg-slate-800 rounded-lg p-6 border border-slate-700 mb-8">
          <h3 className="text-xl font-semibold text-white mb-4">
            {t('dashboard.nsfwDistribution')}
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {Object.entries(stats?.nsfw_distribution || {}).map(([level, count]) => (
              <div key={level} className="p-4 bg-slate-700/50 rounded-lg text-center">
                <p className="text-gray-400 text-sm mb-1 capitalize">{level}</p>
                <p className="text-2xl font-bold text-white">{count}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Charts Section */}
        {stats && (
          <StatsCharts
            stats={{
              ...stats,
              top_tags: filterBlacklistedTags(stats.top_tags || []),
            }}
            showUnspecified={showUnspecified}
          />
        )}

        {/* Quick Actions */}
        <div className="bg-slate-800 rounded-lg p-6 border border-slate-700 mt-8">
          <h3 className="text-xl font-semibold text-white mb-4">{t('dashboard.quickActions')}</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <button
              onClick={() => navigate('/prompts')}
              className="p-4 bg-violet-600 hover:bg-violet-700 rounded-lg text-white font-medium transition-colors text-left"
            >
              <div className="flex items-center justify-between">
                <span>{t('dashboard.viewAllPrompts')}</span>
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 5l7 7-7 7"
                  />
                </svg>
              </div>
            </button>

            <button
              onClick={() => navigate('/prompts')}
              className="p-4 bg-blue-600 hover:bg-blue-700 rounded-lg text-white font-medium transition-colors text-left"
            >
              <div className="flex items-center justify-between">
                <span>{t('dashboard.createNewPrompt')}</span>
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 4v16m8-8H4"
                  />
                </svg>
              </div>
            </button>
          </div>
        </div>
      </main>

      {/* Art Styles Modal */}
      <Modal
        isOpen={showArtStylesModal}
        onClose={() => setShowArtStylesModal(false)}
        title={`${t('dashboard.modals.allArtStyles')} (${filterUnspecified(allArtStyles.length > 0 ? allArtStyles : stats?.top_art_styles || []).length} de ${stats?.total_art_styles || 0})`}
        size="lg"
      >
        <div className="mb-4 flex items-center gap-2">
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              checked={showUnspecified}
              onChange={(e) => setShowUnspecified(e.target.checked)}
              className="w-4 h-4 text-blue-600 bg-slate-700 border-slate-600 rounded focus:ring-blue-500"
            />
            <span className="text-sm text-gray-300">{t('dashboard.display.showUnspecified')}</span>
          </label>
        </div>
        <div className="max-h-96 overflow-y-auto">
          <table className="w-full">
            <thead className="sticky top-0 bg-slate-800 border-b border-slate-700">
              <tr>
                <th className="text-left py-3 px-4 text-gray-400 font-medium">
                  {t('dashboard.modals.style')}
                </th>
                <th className="text-right py-3 px-4 text-gray-400 font-medium">
                  {t('dashboard.modals.count')}
                </th>
              </tr>
            </thead>
            <tbody>
              {filterUnspecified(
                allArtStyles.length > 0 ? allArtStyles : stats?.top_art_styles || []
              ).map((style, index) => (
                <tr
                  key={index}
                  className="border-b border-slate-700/50 hover:bg-slate-700/30 transition-colors"
                >
                  <td className="py-3 px-4 text-gray-300">{style.style}</td>
                  <td className="py-3 px-4 text-right text-blue-400 font-semibold">
                    {style.count}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="mt-4 flex justify-end">
          <button
            onClick={() => setShowArtStylesModal(false)}
            className="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg transition-colors"
          >
            {t('common.close')}
          </button>
        </div>
      </Modal>

      {/* Tags Modal */}
      <Modal
        isOpen={showTagsModal}
        onClose={() => setShowTagsModal(false)}
        title={`${t('dashboard.modals.allTags')} (${t('dashboard.modals.showingTop', { count: 200 })} ${stats?.total_tags || 0})`}
        size="lg"
      >
        <div className="max-h-96 overflow-y-auto">
          <table className="w-full">
            <thead className="sticky top-0 bg-slate-800 border-b border-slate-700">
              <tr>
                <th className="text-left py-3 px-4 text-gray-400 font-medium">
                  {t('dashboard.modals.tag')}
                </th>
                <th className="text-right py-3 px-4 text-gray-400 font-medium">
                  {t('dashboard.modals.count')}
                </th>
              </tr>
            </thead>
            <tbody>
              {filterBlacklistedTags(allTags.length > 0 ? allTags : stats?.top_tags || []).map(
                (tag, index) => (
                  <tr
                    key={index}
                    className="border-b border-slate-700/50 hover:bg-slate-700/30 transition-colors"
                  >
                    <td className="py-3 px-4 text-gray-300">{tag.tag}</td>
                    <td className="py-3 px-4 text-right text-green-400 font-semibold">
                      {tag.count}
                    </td>
                  </tr>
                )
              )}
            </tbody>
          </table>
        </div>
        <div className="mt-4 flex justify-end">
          <button
            onClick={() => setShowTagsModal(false)}
            className="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg transition-colors"
          >
            {t('common.close')}
          </button>
        </div>
      </Modal>

      {/* NSFW Categories Modal */}
      <Modal
        isOpen={showNsfwModal}
        onClose={() => setShowNsfwModal(false)}
        title={t('dashboard.modals.allNsfwCategories')}
        size="lg"
      >
        <div className="max-h-96 overflow-y-auto">
          <table className="w-full">
            <thead className="sticky top-0 bg-slate-800 border-b border-slate-700">
              <tr>
                <th className="text-left py-3 px-4 text-gray-400 font-medium">
                  {t('dashboard.modals.category')}
                </th>
                <th className="text-right py-3 px-4 text-gray-400 font-medium">
                  {t('dashboard.modals.count')}
                </th>
              </tr>
            </thead>
            <tbody>
              {Object.entries(stats?.nsfw_distribution || {}).map(([level, count]) => (
                <tr
                  key={level}
                  className="border-b border-slate-700/50 hover:bg-slate-700/30 transition-colors"
                >
                  <td className="py-3 px-4 text-gray-300 capitalize">{level}</td>
                  <td className="py-3 px-4 text-right text-orange-400 font-semibold">{count}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="mt-4 flex justify-end">
          <button
            onClick={() => setShowNsfwModal(false)}
            className="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg transition-colors"
          >
            {t('common.close')}
          </button>
        </div>
      </Modal>
    </div>
  );
};
