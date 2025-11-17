/**
 * Advanced Search Page
 * Search prompts with multiple filters
 */

import { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Header } from '../components/layout/Header';
import { Loading } from '../components/ui/Loading';
import { ConfirmModal } from '../components/ui/Modal';
import { useToast } from '../hooks/useToast';
import { PromptDetailModal } from '../components/prompts/PromptDetailModal';
import { PromptFormModal } from '../components/prompts/PromptFormModal';
import { searchService } from '../services/search.service';
import { statsService } from '../services/stats.service';
import { promptsService } from '../services/prompts.service';
import { preferencesService } from '../services/preferences.service';
import { useAuthStore } from '../store/authStore';
import { CatalogPrompt, Prompt, CreatePromptRequest } from '../types/api.types';
import { exportToCSV, exportToJSON, getExportFilename } from '../utils/exportPrompts';
import { logDebug, logError } from '../utils/logger';

export const SearchPage = () => {
  const { t } = useTranslation();
  const { user } = useAuthStore();
  const [searchParams] = useSearchParams();
  const [results, setResults] = useState<CatalogPrompt[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isLoadingFilters, setIsLoadingFilters] = useState(true);
  const [hasSearched, setHasSearched] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalResults, setTotalResults] = useState(0);
  const [allResultsCount, setAllResultsCount] = useState(0);
  const pageSize = 20;

  // Filters state
  const [nsfwLevel, setNsfwLevel] = useState('');
  const [artStyle, setArtStyle] = useState('');
  const [numberOfPeople, setNumberOfPeople] = useState('');
  const [searchText, setSearchText] = useState('');
  const [searchTag, setSearchTag] = useState('');
  const [myPromptsOnly, setMyPromptsOnly] = useState(false);

  // Modal states
  const [selectedPrompt, setSelectedPrompt] = useState<Prompt | null>(null);
  const [editingPrompt, setEditingPrompt] = useState<Prompt | null>(null); // Separate state for editing
  const [isDetailModalOpen, setIsDetailModalOpen] = useState(false);
  const [isFormModalOpen, setIsFormModalOpen] = useState(false);
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [promptToDelete, setPromptToDelete] = useState<Prompt | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Available filter options (loaded from database)
  const [nsfwLevels, setNsfwLevels] = useState<string[]>([]);
  const [artStyles, setArtStyles] = useState<Array<{ style: string; count: number }>>([]);

  const toast = useToast();
  const isAdmin = user?.role === 'admin';

  // Load user preferences and available filters on mount
  useEffect(() => {
    loadPreferences();
    loadFilters();
  }, []);

  const loadPreferences = async () => {
    try {
      const prefs = await preferencesService.getPreferences();
      setMyPromptsOnly(prefs.my_prompts_only);
    } catch (err) {
      logError('Error loading preferences', err);
    }
  };

  useEffect(() => {
    // Check for text search from SearchBar
    const textParam = searchParams.get('text');
    if (textParam) {
      setSearchText(textParam);
    }

    // Check for tag search (legacy)
    const tag = searchParams.get('tag');
    if (tag && !textParam) {
      performTagSearch(tag);
    }
  }, [searchParams]);

  const loadFilters = async () => {
    try {
      const filters = await statsService.getFilters();
      setNsfwLevels(filters.nsfw_levels);
      setArtStyles(filters.art_styles);
    } catch (err) {
      logError(t('common.errors.loadingFilters'), err);
      toast.error(t('common.errors.loadingFilters'));
    } finally {
      setIsLoadingFilters(false);
    }
  };

  // Auto-search when searchText changes from URL parameter
  useEffect(() => {
    if (searchText && !hasSearched) {
      performSearch(1);
    }
  }, [searchText]);

  const performTagSearch = async (tag: string) => {
    setIsLoading(true);
    setHasSearched(true);

    try {
      const response = await searchService.searchByTag(tag, 20, 0);
      setResults(response.results);
      setAllResultsCount(response.total);

      if (response.results.length === 0) {
        toast.info(`No se encontraron prompts con el tag "${tag}"`);
      } else {
        toast.success(`Encontrados ${response.total} prompts con el tag "${tag}"`);
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Error en la búsqueda';
      toast.error(message);
      setResults([]);
    } finally {
      setIsLoading(false);
    }
  };

  const performSearch = async (page: number = 1) => {
    setIsLoading(true);
    setHasSearched(true);
    setCurrentPage(page);

    try {
      // If searching by tag only AND not filtering by my_prompts, use simple tag search endpoint
      if (
        searchTag &&
        !searchText &&
        !nsfwLevel &&
        !artStyle &&
        !numberOfPeople &&
        !myPromptsOnly
      ) {
        const response = await searchService.searchByTag(
          searchTag,
          pageSize,
          (page - 1) * pageSize
        );

        setResults(response.results);
        setTotalResults(response.results.length);
        setAllResultsCount(response.total);

        if (response.total === 0) {
          toast.info(`No se encontraron prompts con el tag "${searchTag}"`);
        } else {
          toast.success(`Encontrados ${response.total} prompts totales`);
        }
      } else {
        // Complex search with filters
        const params: any = {};

        // Text search in prompt content
        if (searchText) params.text = searchText;

        // Tag search
        if (searchTag) params.tags = searchTag;

        // Other filters
        if (nsfwLevel) params.nsfw_level = nsfwLevel;
        if (artStyle) params.art_style = artStyle;
        if (numberOfPeople) params.number_of_people = parseInt(numberOfPeople);

        // My prompts only filter
        if (myPromptsOnly && user) {
          params.my_prompts = true;
          logDebug('Search: applying my_prompts filter', { userId: user.id });
        }

        // Pagination
        params.limit = pageSize;
        params.offset = (page - 1) * pageSize;

        const response = await searchService.complexSearch(params);
        setResults(response.results);
        setTotalResults(response.results.length);
        setAllResultsCount(response.total);

        if (response.results.length === 0) {
          toast.info('No se encontraron resultados');
        } else {
          toast.success(`Encontrados ${response.total} resultados totales`);
        }
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Error en la búsqueda';
      toast.error(message);
      setResults([]);
      setAllResultsCount(0);
    } finally {
      setIsLoading(false);
    }
  };

  const clearFilters = () => {
    setNsfwLevel('');
    setArtStyle('');
    setNumberOfPeople('');
    setSearchText('');
    setSearchTag('');
    setMyPromptsOnly(false);
    setResults([]);
    setHasSearched(false);
    setCurrentPage(1);
  };

  const activeFiltersCount = [
    nsfwLevel,
    artStyle,
    numberOfPeople,
    searchText,
    searchTag,
    myPromptsOnly,
  ].filter(Boolean).length;

  // Convert CatalogPrompt to full Prompt for modal with rich data
  const convertToPrompt = (catalogPrompt: CatalogPrompt): Prompt => {
    // Build notes from available metadata
    let notes = '';
    if (catalogPrompt.number_of_people) {
      notes += `Number of People: ${catalogPrompt.number_of_people}\n`;
    }

    // Create a rich category string combining available metadata
    const categoryParts = [];
    if (catalogPrompt.nsfw_level) {
      categoryParts.push(
        catalogPrompt.nsfw_level.charAt(0).toUpperCase() + catalogPrompt.nsfw_level.slice(1)
      );
    }
    if (catalogPrompt.art_style) {
      categoryParts.push(
        catalogPrompt.art_style.charAt(0).toUpperCase() + catalogPrompt.art_style.slice(1)
      );
    }
    const category = categoryParts.join(' - ');

    return {
      id: catalogPrompt.id,
      text: catalogPrompt.original_prompt,
      negative_prompt: '', // Not available in CatalogPrompt
      model: '', // Not available in CatalogPrompt
      category: catalogPrompt.nsfw_level
        ? catalogPrompt.nsfw_level.charAt(0).toUpperCase() + catalogPrompt.nsfw_level.slice(1)
        : '', // Use NSFW level as main category
      art_style: catalogPrompt.art_style || '',
      tags: catalogPrompt.tags ? catalogPrompt.tags.join(', ') : '',
      rating: undefined, // Not available in CatalogPrompt
      notes: notes.trim(), // Include metadata in notes
      parameters: '', // Not available in CatalogPrompt
      created_at: new Date().toISOString(), // Not available in CatalogPrompt
      updated_at: new Date().toISOString(), // Not available in CatalogPrompt
      created_by: null, // Not available in CatalogPrompt - treat as preloaded for safety
    };
  };

  const getExportablePrompts = (): Prompt[] => results.map((result) => convertToPrompt(result));

  // Check if user can edit/delete a prompt
  const canModify = (prompt: Prompt): boolean => {
    if (!user) return false;

    // Admins can modify everything
    if (isAdmin) return true;

    // For catalog prompts (created_by is null), only admins can modify
    // For user prompts, check ownership
    if (prompt.created_by === null) {
      return isAdmin; // Only admins can modify catalog prompts
    }

    // User can modify their own prompts
    return prompt.created_by === user.id;
  };

  const handleEdit = (prompt: Prompt) => {
    logDebug('Editing prompt', { promptId: prompt.id });
    // Set the editing prompt separately
    setEditingPrompt(prompt);
    // Close detail modal
    setIsDetailModalOpen(false);
    // Open form modal after a brief delay to ensure proper transition
    setTimeout(() => {
      setIsFormModalOpen(true);
    }, 50);
  };

  const handleDelete = (prompt: Prompt) => {
    setPromptToDelete(prompt);
    setIsDetailModalOpen(false);
    setIsDeleteModalOpen(true);
  };

  const handleFormSubmit = async (data: CreatePromptRequest) => {
    if (!editingPrompt) {
      logError('No prompt selected for editing');
      return;
    }

    setIsSubmitting(true);
    try {
      logDebug('Updating prompt', { promptId: editingPrompt.id });
      const updatedPrompt = await promptsService.updatePrompt(editingPrompt.id, data);
      toast.success(t('promptForm.messages.updated'));

      // Update the prompt in results
      const updatedResults = results.map((r) =>
        r.id === editingPrompt.id
          ? {
              ...r,
              original_prompt: updatedPrompt.text,
              art_style: data.art_style || r.art_style,
              tags: data.tags ? data.tags.split(',').map((t) => t.trim()) : r.tags,
            }
          : r
      );
      setResults(updatedResults);

      setIsFormModalOpen(false);
      setEditingPrompt(null);
      setSelectedPrompt(null);
    } catch (err) {
      logError('Error updating prompt', err);
      const message = err instanceof Error ? err.message : t('search.errors.update');

      // Check if it's a permission error
      if (message.includes('403') || message.includes('Forbidden')) {
        toast.error(t('search.errors.permissionEdit'));
      } else {
        toast.error(message);
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  const confirmDelete = async () => {
    if (!promptToDelete) {
      logError('No prompt selected for deletion');
      return;
    }

    setIsSubmitting(true);
    try {
      logDebug('Deleting prompt', { promptId: promptToDelete.id });
      await promptsService.deletePrompt(promptToDelete.id);
      toast.success(t('deleteConfirm.success'));

      // Remove from results
      setResults(results.filter((r) => r.id !== promptToDelete.id));
      setTotalResults((prev) => Math.max(0, prev - 1));
      setAllResultsCount((prev) => Math.max(0, prev - 1));

      setIsDeleteModalOpen(false);
      setPromptToDelete(null);
    } catch (err) {
      logError('Error deleting prompt', err);
      const message = err instanceof Error ? err.message : t('search.errors.delete');

      // Check if it's a permission error
      if (message.includes('403') || message.includes('Forbidden')) {
        toast.error(t('search.errors.permissionDelete'));
      } else {
        toast.error(message);
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleCopyPrompt = async (prompt: Prompt) => {
    try {
      await promptsService.copyPrompt(prompt.id);
      toast.success(t('search.messages.copySuccess'));
    } catch (err) {
      const message = err instanceof Error ? err.message : t('search.messages.copyError');
      toast.error(message);
    }
  };

  const handleExport = (format: 'json' | 'csv') => {
    if (!results.length) return;
    const exportData = getExportablePrompts();
    if (format === 'json') {
      exportToJSON(exportData, getExportFilename('json'));
      toast.success(t('search.export.successJson'));
    } else {
      exportToCSV(exportData, getExportFilename('csv'));
      toast.success(t('search.export.successCsv'));
    }
  };

  return (
    <div className="min-h-screen bg-slate-900">
      <Header />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Page Header */}
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-white mb-2">{t('search.title')}</h2>
          <p className="text-gray-400">{t('search.subtitle')}</p>
        </div>

        {/* Filters Section */}
        <div className="bg-slate-800 rounded-lg p-6 border border-slate-700 mb-8">
          {/* Main Filters */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
            {/* NSFW Level Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                {t('search.filters.nsfwLevel')}
              </label>
              <select
                value={nsfwLevel}
                onChange={(e) => setNsfwLevel(e.target.value)}
                className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-violet-600"
              >
                <option value="">{t('search.filters.all')}</option>
                {nsfwLevels.map((level) => (
                  <option key={level} value={level}>
                    {level.charAt(0).toUpperCase() + level.slice(1)}
                  </option>
                ))}
              </select>
            </div>

            {/* Art Style Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                {t('search.filters.artStyle')}
              </label>
              <select
                value={artStyle}
                onChange={(e) => setArtStyle(e.target.value)}
                className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-violet-600"
              >
                <option value="">{t('search.filters.all')}</option>
                {artStyles.map((item) => (
                  <option key={item.style} value={item.style}>
                    {item.style.charAt(0).toUpperCase() + item.style.slice(1)}
                  </option>
                ))}
              </select>
            </div>

            {/* Number of People Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                {t('search.filters.numberOfPeople')}
              </label>
              <input
                type="number"
                min="0"
                max="10"
                value={numberOfPeople}
                onChange={(e) => setNumberOfPeople(e.target.value)}
                placeholder={t('search.filters.peoplePlaceholder')}
                className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-violet-600"
              />
            </div>
          </div>

          {/* Text Search */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-300 mb-2">
              {t('search.filters.textSearch')}
            </label>
            <input
              type="text"
              value={searchText}
              onChange={(e) => setSearchText(e.target.value)}
              placeholder={t('search.filters.textPlaceholder')}
              className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-violet-600"
            />
            <p className="text-xs text-gray-500 mt-1">{t('search.filters.textHelp')}</p>
          </div>

          {/* Tag Search */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-300 mb-2">
              {t('search.filters.tagSearch')}
            </label>
            <input
              type="text"
              value={searchTag}
              onChange={(e) => setSearchTag(e.target.value)}
              placeholder={t('search.filters.tagPlaceholder')}
              className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-violet-600"
            />
            <p className="text-xs text-gray-500 mt-1">{t('search.filters.tagHelp')}</p>
          </div>

          {/* My Prompts Only Checkbox */}
          {user && (
            <div className="mb-6">
              <label className="flex items-center space-x-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={myPromptsOnly}
                  onChange={(e) => setMyPromptsOnly(e.target.checked)}
                  className="w-5 h-5 bg-slate-700 border border-slate-600 rounded text-violet-600 focus:ring-2 focus:ring-violet-600"
                />
                <span className="text-sm font-medium text-gray-300">
                  📝 {t('search.filters.myPrompts')}
                </span>
              </label>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <button
                onClick={() => performSearch(1)}
                disabled={isLoading || activeFiltersCount === 0}
                className="px-6 py-2 bg-violet-600 hover:bg-violet-700 disabled:bg-slate-600 disabled:cursor-not-allowed text-white rounded-lg font-medium transition-colors flex items-center gap-2"
              >
                {isLoading && <Loading size="sm" />}
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                  />
                </svg>
                {t('search.actions.search')}
              </button>

              {activeFiltersCount > 0 && (
                <button
                  onClick={clearFilters}
                  className="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg font-medium transition-colors"
                >
                  {t('search.actions.clear')}
                </button>
              )}
            </div>

            {activeFiltersCount > 0 && (
              <span className="text-sm text-gray-400">
                {activeFiltersCount}{' '}
                {activeFiltersCount === 1
                  ? t('search.activeFilters')
                  : t('search.activeFiltersPlural')}
              </span>
            )}
          </div>

          {/* Active Filters Chips */}
          {activeFiltersCount > 0 && (
            <div className="flex flex-wrap gap-2 mt-4 pt-4 border-t border-slate-700">
              {nsfwLevel && (
                <span className="px-3 py-1 bg-orange-600/20 text-orange-400 rounded-full text-sm flex items-center gap-2">
                  {t('search.chips.nsfw')}: {nsfwLevel}
                  <button onClick={() => setNsfwLevel('')} className="hover:text-orange-300">
                    ×
                  </button>
                </span>
              )}
              {artStyle && (
                <span className="px-3 py-1 bg-blue-600/20 text-blue-400 rounded-full text-sm flex items-center gap-2">
                  {t('search.chips.style')}: {artStyle}
                  <button onClick={() => setArtStyle('')} className="hover:text-blue-300">
                    ×
                  </button>
                </span>
              )}
              {numberOfPeople && (
                <span className="px-3 py-1 bg-green-600/20 text-green-400 rounded-full text-sm flex items-center gap-2">
                  {t('search.chips.people')}: {numberOfPeople}
                  <button onClick={() => setNumberOfPeople('')} className="hover:text-green-300">
                    ×
                  </button>
                </span>
              )}
              {searchText && (
                <span className="px-3 py-1 bg-violet-600/20 text-violet-400 rounded-full text-sm flex items-center gap-2">
                  {t('search.chips.text')}: "{searchText}"
                  <button onClick={() => setSearchText('')} className="hover:text-violet-300">
                    ×
                  </button>
                </span>
              )}
              {searchTag && (
                <span className="px-3 py-1 bg-indigo-600/20 text-indigo-400 rounded-full text-sm flex items-center gap-2">
                  {t('search.chips.tag')}: "{searchTag}"
                  <button onClick={() => setSearchTag('')} className="hover:text-indigo-300">
                    ×
                  </button>
                </span>
              )}
              {myPromptsOnly && (
                <span className="px-3 py-1 bg-purple-600/20 text-purple-400 rounded-full text-sm flex items-center gap-2">
                  📝 {t('search.chips.myPrompts')}
                  <button onClick={() => setMyPromptsOnly(false)} className="hover:text-purple-300">
                    ×
                  </button>
                </span>
              )}
            </div>
          )}
        </div>

        {/* Results Section */}
        {isLoading ? (
          <div className="flex items-center justify-center py-12">
            <Loading size="lg" text={t('search.actions.searching')} />
          </div>
        ) : hasSearched ? (
          <>
            {/* Results Header */}
            <div className="mb-4 flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
              <div>
                <h3 className="text-xl font-semibold text-white">
                  {results.length > 0 ? (
                    <>
                      {allResultsCount > 0 && (
                        <span className="text-violet-400">
                          {allResultsCount} {t('search.results.total')}
                        </span>
                      )}
                      {allResultsCount > 0 && ' - '}
                      {t('search.results.page')} {currentPage}
                    </>
                  ) : (
                    t('search.results.noResults')
                  )}
                </h3>
                {results.length > 0 && (
                  <span className="text-sm text-gray-400">
                    {t('search.results.showing')} {(currentPage - 1) * pageSize + 1} -{' '}
                    {Math.min(
                      currentPage * pageSize,
                      (currentPage - 1) * pageSize + results.length
                    )}{' '}
                    {t('search.results.of')} {allResultsCount}
                  </span>
                )}
              </div>
              {results.length > 0 && (
                <div className="flex flex-wrap items-center gap-2">
                  <button
                    onClick={() => handleExport('json')}
                    className="px-3 py-2 bg-green-600 hover:bg-green-700 text-white text-sm rounded-lg font-medium transition-colors flex items-center gap-2"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M9 19l3 3m0 0l3-3m-3 3V10"
                      />
                    </svg>
                    {t('search.export.json')}
                  </button>
                  <button
                    onClick={() => handleExport('csv')}
                    className="px-3 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm rounded-lg font-medium transition-colors flex items-center gap-2"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M9 19l3 3m0 0l3-3m-3 3V10"
                      />
                    </svg>
                    {t('search.export.csv')}
                  </button>
                </div>
              )}
            </div>

            {/* Results Grid */}
            {results.length > 0 ? (
              <>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                  {results.map((result, index) => (
                    <div
                      key={result.id || index}
                      onClick={() => {
                        const fullPrompt = convertToPrompt(result);
                        setSelectedPrompt(fullPrompt);
                        setIsDetailModalOpen(true);
                      }}
                      className="bg-slate-800 rounded-lg p-6 border border-slate-700 hover:border-violet-600 hover:shadow-lg transition-all cursor-pointer transform hover:scale-[1.02]"
                    >
                      <div className="mb-4">
                        <div className="flex items-center gap-2 mb-2">
                          <h4 className="text-lg font-semibold text-white">Prompt #{result.id}</h4>
                          {result.nsfw_level && (
                            <span className="px-2 py-1 bg-orange-600/20 text-orange-400 text-xs rounded-full">
                              {result.nsfw_level}
                            </span>
                          )}
                          {result.art_style && (
                            <span className="px-2 py-1 bg-blue-600/20 text-blue-400 text-xs rounded-full">
                              {result.art_style}
                            </span>
                          )}
                        </div>
                        <p className="text-gray-300 text-sm leading-relaxed">
                          {result.original_prompt.substring(0, 200)}
                          {result.original_prompt.length > 200 && '...'}
                        </p>
                      </div>

                      {result.tags && result.tags.length > 0 && (
                        <div className="flex flex-wrap gap-2">
                          {result.tags.slice(0, 5).map((tag, i) => (
                            <span
                              key={i}
                              className="px-2 py-1 bg-slate-700 text-gray-300 text-xs rounded"
                            >
                              {tag}
                            </span>
                          ))}
                          {result.tags.length > 5 && (
                            <span className="px-2 py-1 bg-slate-700 text-gray-400 text-xs rounded">
                              +{result.tags.length - 5} más
                            </span>
                          )}
                        </div>
                      )}
                    </div>
                  ))}
                </div>

                {/* Pagination */}
                {results.length === pageSize && (
                  <div className="flex items-center justify-center gap-2">
                    <button
                      onClick={() => performSearch(currentPage - 1)}
                      disabled={currentPage === 1 || isLoading}
                      className="px-4 py-2 bg-slate-800 hover:bg-slate-700 disabled:bg-slate-800 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-lg transition-colors"
                    >
                      {t('search.results.previous')}
                    </button>

                    <span className="text-gray-400 px-4">
                      {t('search.results.page')} {currentPage}
                    </span>

                    <button
                      onClick={() => performSearch(currentPage + 1)}
                      disabled={results.length < pageSize || isLoading}
                      className="px-4 py-2 bg-slate-800 hover:bg-slate-700 disabled:bg-slate-800 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-lg transition-colors"
                    >
                      {t('search.results.next')}
                    </button>
                  </div>
                )}
              </>
            ) : (
              <div className="text-center py-12">
                <svg
                  className="w-16 h-16 text-gray-600 mx-auto mb-4"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
                <p className="text-gray-400 text-lg">{t('search.results.noResultsMessage')}</p>
                <p className="text-gray-500 text-sm mt-2">{t('search.results.tryDifferent')}</p>
              </div>
            )}
          </>
        ) : (
          <div className="text-center py-12">
            <svg
              className="w-16 h-16 text-gray-600 mx-auto mb-4"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
              />
            </svg>
            <p className="text-gray-400 text-lg">{t('search.results.selectFilters')}</p>
          </div>
        )}
      </main>

      {/* Detail Modal */}
      {selectedPrompt && (
        <PromptDetailModal
          isOpen={isDetailModalOpen}
          onClose={() => {
            setIsDetailModalOpen(false);
            setSelectedPrompt(null);
          }}
          prompt={selectedPrompt}
          onEdit={handleEdit}
          onDelete={handleDelete}
          canModify={canModify(selectedPrompt)}
          canCopy={Boolean(user && selectedPrompt.created_by !== user.id)}
          onCopy={handleCopyPrompt}
        />
      )}

      {/* Form Modal for Editing */}
      {editingPrompt && (
        <PromptFormModal
          isOpen={isFormModalOpen}
          onClose={() => {
            setIsFormModalOpen(false);
            setEditingPrompt(null);
          }}
          onSubmit={handleFormSubmit}
          prompt={editingPrompt}
          isLoading={isSubmitting}
        />
      )}

      {/* Delete Confirmation Modal */}
      <ConfirmModal
        isOpen={isDeleteModalOpen}
        onClose={() => {
          setIsDeleteModalOpen(false);
          setPromptToDelete(null);
        }}
        onConfirm={confirmDelete}
        title={t('deleteConfirm.title')}
        message={`${t('deleteConfirm.message')} #${promptToDelete?.id}? ${t('deleteConfirm.warning')}`}
        confirmText={t('deleteConfirm.confirm')}
        cancelText={t('deleteConfirm.cancel')}
        isLoading={isSubmitting}
      />
    </div>
  );
};
