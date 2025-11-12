/**
 * Dashboard Page
 * Main dashboard with statistics and overview
 */

import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Header } from '../components/layout/Header';
import { Loading } from '../components/ui/Loading';
import { StatsCharts } from '../components/dashboard/StatsCharts';
import { statsService } from '../services/stats.service';
import { Stats } from '../types/api.types';

export const DashboardPage = () => {
  const { t } = useTranslation();
  const [stats, setStats] = useState<Stats | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      const data = await statsService.getStats();
      setStats(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load stats');
    } finally {
      setIsLoading(false);
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
          <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm font-medium">{t('dashboard.artStyles')}</p>
                <p className="text-3xl font-bold text-white mt-2">
                  {stats?.top_art_styles?.length || 0}
                </p>
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
          <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm font-medium">{t('dashboard.tags')}</p>
                <p className="text-3xl font-bold text-white mt-2">{stats?.top_tags?.length || 0}</p>
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
          <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm font-medium">{t('dashboard.nsfwCategories')}</p>
                <p className="text-3xl font-bold text-white mt-2">
                  {Object.keys(stats?.nsfw_distribution || {}).length}
                </p>
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
            <h3 className="text-xl font-semibold text-white mb-4">{t('dashboard.topTags')}</h3>
            <div className="space-y-3">
              {stats?.top_tags?.slice(0, 5).map((tag, index) => (
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
            <h3 className="text-xl font-semibold text-white mb-4">{t('dashboard.topStyles')}</h3>
            <div className="space-y-3">
              {stats?.top_art_styles?.slice(0, 5).map((style, index) => (
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
          <h3 className="text-xl font-semibold text-white mb-4">{t('dashboard.nsfwDistribution')}</h3>
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
        {stats && <StatsCharts stats={stats} />}

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
    </div>
  );
};
