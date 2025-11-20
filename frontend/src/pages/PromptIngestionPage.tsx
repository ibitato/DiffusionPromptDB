import { ChangeEvent, FormEvent, useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import { Header } from '../components/layout/Header';
import { useToast } from '../hooks/useToast';
import {
  ingestionService,
  AggregatedIngestionResponse,
  IngestionFilePayload,
} from '../services/ingestion.service';
import { ImageIngestionResult } from '../types/api.types';
import { statsService } from '../services/stats.service';
import { logError } from '../utils/logger';
import { parseStableDiffusionMetadata } from '../utils/pngMetadata';
import { inferArtStyleFromMetadata, inferTagsFromPrompt } from '../utils/promptSuggestions';

const MAX_FILES = 5;

type FileEntry = {
  id: string;
  file: File;
  previewUrl: string;
  tags: string;
  category: string;
  artStyle: string;
  rating: string;
  notes: string;
  suggestions: { tags: string[]; artStyle: string };
  isAnalyzing: boolean;
  analysisError: string;
  touched: { tags: boolean; artStyle: boolean };
};

const createClientId = () =>
  typeof crypto !== 'undefined' && crypto.randomUUID
    ? crypto.randomUUID()
    : `entry-${Date.now()}-${Math.random().toString(16).slice(2)}`;

const revokePreviews = (entries: FileEntry[]) => {
  entries.forEach((entry) => URL.revokeObjectURL(entry.previewUrl));
};

export const PromptIngestionPage = () => {
  const { t } = useTranslation();
  const toast = useToast();
  const navigate = useNavigate();

  const [entries, setEntries] = useState<FileEntry[]>([]);
  const [batchDefaults, setBatchDefaults] = useState({
    tags: '',
    category: '',
    artStyle: '',
    rating: '',
    notes: '',
  });
  const [results, setResults] = useState<
    Array<ImageIngestionResult & { clientId: string }>
  >([]);
  const [summary, setSummary] = useState<AggregatedIngestionResponse | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [artStyleOptions, setArtStyleOptions] = useState<string[]>([]);

  useEffect(() => {
    const loadFilters = async () => {
      try {
        const filters = await statsService.getFilters();
        const styles = filters.art_styles?.map((entry) => entry.style) ?? [];
        setArtStyleOptions(Array.from(new Set(styles)));
      } catch (error) {
        logError('Error loading art styles', error);
      }
    };
    void loadFilters();
  }, []);

  useEffect(() => {
    return () => revokePreviews(entries);
  }, [entries]);

  const buildEntry = (file: File): FileEntry => ({
    id: createClientId(),
    file,
    previewUrl: URL.createObjectURL(file),
    tags: batchDefaults.tags,
    category: batchDefaults.category,
    artStyle: batchDefaults.artStyle,
    rating: batchDefaults.rating,
    notes: batchDefaults.notes,
    suggestions: { tags: [], artStyle: '' },
    isAnalyzing: false,
    analysisError: '',
    touched: {
      tags: Boolean(batchDefaults.tags.trim()),
      artStyle: Boolean(batchDefaults.artStyle.trim()),
    },
  });

  const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    const selectedFiles = Array.from(event.target.files ?? []);
    if (!selectedFiles.length) {
      return;
    }
    if (selectedFiles.length > MAX_FILES) {
      toast.error(t('ingest.errors.maxFiles', { max: MAX_FILES }));
    }

    const limited = selectedFiles.slice(0, MAX_FILES);
    revokePreviews(entries);
    const newEntries = limited.map(buildEntry);
    setEntries(newEntries);
    setResults([]);
    setSummary(null);
    newEntries.forEach((entry) => {
      void analyzeEntry(entry.id, entry.file);
    });
  };

  const removeEntry = (id: string) => {
    setEntries((prev) => {
      const entry = prev.find((item) => item.id === id);
      if (entry) {
        URL.revokeObjectURL(entry.previewUrl);
      }
      return prev.filter((item) => item.id !== id);
    });
  };

  const clearSelection = () => {
    revokePreviews(entries);
    setEntries([]);
    setResults([]);
    setSummary(null);
  };

  const clearEverything = () => {
    clearSelection();
    setBatchDefaults({
      tags: '',
      category: '',
      artStyle: '',
      rating: '',
      notes: '',
    });
  };

  const updateEntry = (id: string, updater: (entry: FileEntry) => FileEntry) => {
    setEntries((prev) => prev.map((entry) => (entry.id === id ? updater(entry) : entry)));
  };

  const handleEntryFieldChange = (
    id: string,
    field: 'tags' | 'category' | 'artStyle' | 'rating' | 'notes',
    value: string
  ) => {
    updateEntry(id, (entry) => {
      const next: FileEntry = { ...entry, [field]: value };
      if (field === 'tags') {
        next.touched = { ...next.touched, tags: true };
      }
      if (field === 'artStyle') {
        next.touched = { ...next.touched, artStyle: true };
      }
      return next;
    });
  };

  const handleBatchDefaultChange = (
    field: keyof typeof batchDefaults,
    value: string
  ) => {
    setBatchDefaults((prev) => ({ ...prev, [field]: value }));
  };

  const applyDefaultsToAllEntries = () => {
    if (!entries.length) return;
    setEntries((prev) =>
      prev.map((entry) => ({
        ...entry,
        tags: batchDefaults.tags,
        category: batchDefaults.category,
        artStyle: batchDefaults.artStyle,
        rating: batchDefaults.rating,
        notes: batchDefaults.notes,
        touched: {
          ...entry.touched,
          tags: entry.touched.tags || Boolean(batchDefaults.tags.trim()),
          artStyle: entry.touched.artStyle || Boolean(batchDefaults.artStyle.trim()),
        },
      }))
    );
  };

  const applyDefaultsToEntry = (id: string) => {
    updateEntry(id, (entry) => ({
      ...entry,
      tags: batchDefaults.tags,
      category: batchDefaults.category,
      artStyle: batchDefaults.artStyle,
      rating: batchDefaults.rating,
      notes: batchDefaults.notes,
      touched: {
        ...entry.touched,
        tags: entry.touched.tags || Boolean(batchDefaults.tags.trim()),
        artStyle: entry.touched.artStyle || Boolean(batchDefaults.artStyle.trim()),
      },
    }));
  };

  const applySuggestionToEntry = (id: string, type: 'tags' | 'artStyle') => {
    updateEntry(id, (entry) => {
      if (type === 'tags' && entry.suggestions.tags.length) {
        return {
          ...entry,
          tags: entry.suggestions.tags.join(', '),
          touched: { ...entry.touched, tags: true },
        };
      }
      if (type === 'artStyle' && entry.suggestions.artStyle) {
        return {
          ...entry,
          artStyle: entry.suggestions.artStyle,
          touched: { ...entry.touched, artStyle: true },
        };
      }
      return entry;
    });
  };

  const analyzeEntry = async (entryId: string, file: File) => {
    updateEntry(entryId, (entry) => ({ ...entry, isAnalyzing: true, analysisError: '' }));
    try {
      const metadata = await parseStableDiffusionMetadata(file);
      const inferredTags = inferTagsFromPrompt(metadata.positivePrompt);
      const inferredStyle = inferArtStyleFromMetadata(metadata);

      setEntries((prev) =>
        prev.map((entry) => {
          if (entry.id !== entryId) return entry;
          let tags = entry.tags;
          let artStyle = entry.artStyle;

          if (!entry.touched.tags && !entry.tags.trim() && inferredTags.length) {
            tags = inferredTags.join(', ');
          }
          if (!entry.touched.artStyle && !entry.artStyle.trim() && inferredStyle) {
            artStyle = inferredStyle;
          }

          return {
            ...entry,
            tags,
            artStyle,
            isAnalyzing: false,
            suggestions: {
              tags: inferredTags,
              artStyle: inferredStyle ?? '',
            },
          };
        })
      );
    } catch (error) {
      updateEntry(entryId, (entry) => ({
        ...entry,
        isAnalyzing: false,
        suggestions: { tags: [], artStyle: '' },
        analysisError: t('ingest.suggestions.failed'),
      }));
      logError('Error parsing PNG metadata', error);
    }
  };

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    if (!entries.length) {
      toast.error(t('ingest.errors.selectFiles'));
      return;
    }

    setIsSubmitting(true);
    setResults([]);
    setSummary(null);

    const payload: IngestionFilePayload[] = entries.map((entry) => ({
      clientId: entry.id,
      file: entry.file,
      tags: entry.tags.trim() || undefined,
      category: entry.category.trim() || undefined,
      artStyle: entry.artStyle.trim() || undefined,
      rating: entry.rating ? Number(entry.rating) : undefined,
      notes: entry.notes.trim() || undefined,
    }));

    try {
      const response = await ingestionService.ingestImages(payload);
      setResults(response.results);
      setSummary(response);
      toast.success(
        t('ingest.messages.completed', {
          created: response.created,
          failed: response.failed,
        })
      );
      revokePreviews(entries);
      setEntries([]);
    } catch (error) {
      toast.error(error instanceof Error ? error.message : t('ingest.errors.generic'));
    } finally {
      setIsSubmitting(false);
    }
  };

  const renderSuggestionBlock = (entry: FileEntry) => {
    if (entry.isAnalyzing) {
      return <p className="text-sm text-gray-400">{t('ingest.suggestions.analyzing')}</p>;
    }

    if (entry.analysisError) {
      return <p className="text-sm text-red-400">{entry.analysisError}</p>;
    }

    if (!entry.suggestions.tags.length && !entry.suggestions.artStyle) {
      return <p className="text-sm text-gray-400">{t('ingest.perFile.noMetadata')}</p>;
    }

    return (
      <div className="space-y-3">
        {entry.suggestions.tags.length > 0 && (
          <div>
            <div className="flex items-center justify-between text-sm text-gray-300 mb-1">
              <p>{t('ingest.suggestions.tagsTitle')}</p>
              <button
                type="button"
                className="text-violet-300 hover:text-violet-100 text-xs"
                onClick={() => applySuggestionToEntry(entry.id, 'tags')}
              >
                {t('ingest.suggestions.applyTags')}
              </button>
            </div>
            <div className="flex flex-wrap gap-2">
              {entry.suggestions.tags.map((tag) => (
                <span
                  key={`${entry.id}-${tag}`}
                  className="px-2 py-1 rounded-full bg-slate-900/60 border border-slate-700 text-xs text-gray-200"
                >
                  {tag}
                </span>
              ))}
            </div>
          </div>
        )}
        {entry.suggestions.artStyle && (
          <div className="flex items-center justify-between text-sm text-gray-300">
            <div>
              <p>{t('ingest.suggestions.styleTitle')}</p>
              <p className="text-white font-medium">{entry.suggestions.artStyle}</p>
            </div>
            <button
              type="button"
              className="text-violet-300 hover:text-violet-100 text-xs"
              onClick={() => applySuggestionToEntry(entry.id, 'artStyle')}
            >
              {t('ingest.suggestions.applyStyle')}
            </button>
          </div>
        )}
      </div>
    );
  };

  const renderEntryCard = (entry: FileEntry, index: number) => (
    <div
      key={entry.id}
      className="bg-slate-900/40 border border-slate-700 rounded-2xl p-5 space-y-4"
    >
      <div className="flex flex-col lg:flex-row gap-4">
        <div className="flex items-center gap-3 flex-1">
          <img
            src={entry.previewUrl}
            alt={entry.file.name}
            className="w-24 h-24 rounded-xl object-cover border border-slate-700"
          />
          <div>
            <p className="text-sm text-gray-400">
              {t('ingest.preview.title', { count: index + 1 })}
            </p>
            <p className="text-lg font-semibold text-white">{entry.file.name}</p>
            <p className="text-xs text-gray-500">{(entry.file.size / 1024).toFixed(1)} KB</p>
          </div>
        </div>
        <button
          type="button"
          onClick={() => removeEntry(entry.id)}
          className="self-start text-sm text-red-300 hover:text-red-100"
        >
          {t('ingest.perFile.remove')}
        </button>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-1">
            {t('ingest.form.tags')}
          </label>
          <input
            type="text"
            value={entry.tags}
            onChange={(e) => handleEntryFieldChange(entry.id, 'tags', e.target.value)}
            placeholder={t('ingest.form.tagsPlaceholder')}
            className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2.5 text-white placeholder:text-gray-500 focus:outline-none focus:ring-2 focus:ring-violet-500"
          />
          <p className="text-xs text-gray-500 mt-1">{t('ingest.form.tagsHelp')}</p>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-1">
            {t('ingest.form.category')}
          </label>
          <input
            type="text"
            value={entry.category}
            onChange={(e) => handleEntryFieldChange(entry.id, 'category', e.target.value)}
            placeholder={t('ingest.form.categoryPlaceholder')}
            className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2.5 text-white placeholder:text-gray-500 focus:outline-none focus:ring-2 focus:ring-violet-500"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-1">
            {t('ingest.form.artStyle')}
          </label>
          <select
            value={entry.artStyle}
            onChange={(e) => handleEntryFieldChange(entry.id, 'artStyle', e.target.value)}
            className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2.5 text-white focus:outline-none focus:ring-2 focus:ring-violet-500"
          >
            <option value="">{t('ingest.form.artStylePlaceholder')}</option>
            {artStyleOptions.map((style) => (
              <option key={style} value={style}>
                {style}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-1">
            {t('ingest.form.rating')}
          </label>
          <select
            value={entry.rating}
            onChange={(e) => handleEntryFieldChange(entry.id, 'rating', e.target.value)}
            className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2.5 text-white focus:outline-none focus:ring-2 focus:ring-violet-500"
          >
            <option value="">{t('ingest.form.ratingPlaceholder')}</option>
            {[1, 2, 3, 4, 5].map((value) => (
              <option key={value} value={value}>
                {value}
              </option>
            ))}
          </select>
        </div>
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-300 mb-1">
          {t('ingest.form.notes')}
        </label>
        <textarea
          value={entry.notes}
          onChange={(e) => handleEntryFieldChange(entry.id, 'notes', e.target.value)}
          rows={3}
          placeholder={t('ingest.form.notesPlaceholder')}
          className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2.5 text-white placeholder:text-gray-500 focus:outline-none focus:ring-2 focus:ring-violet-500"
        />
      </div>
      <div>
        <div className="flex items-center justify-between">
          <p className="text-sm font-medium text-gray-300">{t('ingest.perFile.metadata')}</p>
          <button
            type="button"
            className="text-xs text-violet-300 hover:text-violet-100"
            onClick={() => applyDefaultsToEntry(entry.id)}
          >
            {t('ingest.perFile.applyDefaults')}
          </button>
        </div>
        <div className="mt-2 rounded-xl border border-slate-700 bg-slate-900/50 p-3">
          {renderSuggestionBlock(entry)}
        </div>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-slate-900">
      <Header />
      <main className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-8">
        <section className="bg-slate-800 border border-slate-700 rounded-2xl p-6 shadow-2xl shadow-violet-500/10">
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-6 mb-8">
            <div>
              <p className="text-sm uppercase tracking-widest text-violet-400 font-semibold mb-2">
                {t('ingest.badge')}
              </p>
              <h1 className="text-3xl font-bold text-white mb-3">{t('ingest.title')}</h1>
              <p className="text-gray-300 max-w-3xl">{t('ingest.subtitle')}</p>
            </div>
            <div className="bg-slate-900/40 border border-slate-700 rounded-xl p-4 min-w-[220px]">
              <p className="text-sm text-gray-400">{t('ingest.limitLabel')}</p>
              <p className="text-2xl font-semibold text-white">
                {entries.length} / {MAX_FILES}
              </p>
            </div>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="border-2 border-dashed border-slate-600 rounded-2xl p-8 bg-slate-900/40">
              <div className="flex flex-col items-center text-center">
                <svg
                  className="w-12 h-12 text-violet-300 mb-4"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={1.5}
                    d="M12 16V4m0 0L8 8m4-4l4 4M6 20h12"
                  />
                </svg>
                <h3 className="text-xl font-semibold text-white mb-2">
                  {t('ingest.dropzone.title')}
                </h3>
                <p className="text-gray-400 mb-4">{t('ingest.dropzone.hint')}</p>
                <label className="inline-flex items-center gap-2 px-5 py-2 bg-violet-600 hover:bg-violet-700 text-white rounded-lg cursor-pointer transition-colors">
                  <input
                    type="file"
                    accept=".png"
                    multiple
                    className="hidden"
                    onChange={handleFileChange}
                  />
                  <span>{t('ingest.dropzone.action')}</span>
                </label>
                <p className="text-xs text-gray-500 mt-4">{t('ingest.dropzone.helper')}</p>
              </div>
            </div>

            <div className="bg-slate-900/40 border border-slate-700 rounded-2xl p-5 space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-400">{t('ingest.defaults.description')}</p>
                  <h3 className="text-lg font-semibold text-white">
                    {t('ingest.defaults.title')}
                  </h3>
                </div>
                <button
                  type="button"
                  className="text-sm text-violet-300 hover:text-violet-100"
                  onClick={applyDefaultsToAllEntries}
                  disabled={!entries.length}
                >
                  {t('ingest.defaults.apply')}
                </button>
              </div>
              <div className="grid gap-4 md:grid-cols-2">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-1">
                    {t('ingest.form.tags')}
                  </label>
                  <input
                    type="text"
                    value={batchDefaults.tags}
                    onChange={(e) => handleBatchDefaultChange('tags', e.target.value)}
                    placeholder={t('ingest.form.tagsPlaceholder')}
                    className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2.5 text-white placeholder:text-gray-500 focus:outline-none focus:ring-2 focus:ring-violet-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-1">
                    {t('ingest.form.category')}
                  </label>
                  <input
                    type="text"
                    value={batchDefaults.category}
                    onChange={(e) => handleBatchDefaultChange('category', e.target.value)}
                    placeholder={t('ingest.form.categoryPlaceholder')}
                    className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2.5 text-white placeholder:text-gray-500 focus:outline-none focus:ring-2 focus:ring-violet-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-1">
                    {t('ingest.form.artStyle')}
                  </label>
                  <input
                    type="text"
                    value={batchDefaults.artStyle}
                    onChange={(e) => handleBatchDefaultChange('artStyle', e.target.value)}
                    placeholder={t('ingest.form.artStylePlaceholder')}
                    className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2.5 text-white placeholder:text-gray-500 focus:outline-none focus:ring-2 focus:ring-violet-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-1">
                    {t('ingest.form.rating')}
                  </label>
                  <select
                    value={batchDefaults.rating}
                    onChange={(e) => handleBatchDefaultChange('rating', e.target.value)}
                    className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2.5 text-white focus:outline-none focus:ring-2 focus:ring-violet-500"
                  >
                    <option value="">{t('ingest.form.ratingPlaceholder')}</option>
                    {[1, 2, 3, 4, 5].map((value) => (
                      <option key={value} value={value}>
                        {value}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">
                  {t('ingest.form.notes')}
                </label>
                <textarea
                  rows={3}
                  value={batchDefaults.notes}
                  onChange={(e) => handleBatchDefaultChange('notes', e.target.value)}
                  placeholder={t('ingest.form.notesPlaceholder')}
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2.5 text-white placeholder:text-gray-500 focus:outline-none focus:ring-2 focus:ring-violet-500"
                />
              </div>
            </div>

            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-400">{t('ingest.perFile.description')}</p>
                  <h3 className="text-lg font-semibold text-white">
                    {t('ingest.perFile.title')}
                  </h3>
                </div>
              </div>
              {entries.length === 0 ? (
                <div className="text-center py-10 text-gray-500">
                  {t('ingest.results.empty')}
                </div>
              ) : (
                <div className="space-y-4">
                  {entries.map((entry, index) => renderEntryCard(entry, index))}
                </div>
              )}
            </div>

            <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
              <p className="text-sm text-gray-400">{t('ingest.form.helper', { max: MAX_FILES })}</p>
              <div className="flex items-center gap-3">
                <button
                  type="button"
                  onClick={clearSelection}
                  className="px-5 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg transition-colors disabled:opacity-50"
                  disabled={!entries.length && Object.values(batchDefaults).every((value) => !value)}
                >
                  {t('ingest.actions.reset')}
                </button>
                <button
                  type="button"
                  onClick={clearEverything}
                  className="px-5 py-2 bg-slate-900 border border-slate-700 hover:border-slate-500 text-white rounded-lg transition-colors disabled:opacity-50"
                  disabled={
                    !entries.length &&
                    Object.values(batchDefaults).every((value) => !value) &&
                    results.length === 0 &&
                    !summary
                  }
                >
                  {t('ingest.actions.clearAll')}
                </button>
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="px-5 py-2 bg-violet-600 hover:bg-violet-700 disabled:bg-violet-900 text-white rounded-lg font-semibold transition-colors flex items-center gap-2"
                >
                  {isSubmitting ? (
                    <>
                      <svg
                        className="w-5 h-5 animate-spin text-white"
                        fill="none"
                        viewBox="0 0 24 24"
                      >
                        <circle
                          className="opacity-25"
                          cx="12"
                          cy="12"
                          r="10"
                          stroke="currentColor"
                          strokeWidth="4"
                        />
                        <path
                          className="opacity-75"
                          fill="currentColor"
                          d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"
                        />
                      </svg>
                      {t('ingest.actions.submitting')}
                    </>
                  ) : (
                    <>
                      <svg
                        className="w-5 h-5"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={1.5}
                          d="M9 12h6m-3-3v6m9-3A9 9 0 1112 3a9 9 0 0118 9z"
                        />
                      </svg>
                      {t('ingest.actions.submit')}
                    </>
                  )}
                </button>
              </div>
            </div>
          </form>
        </section>

        <section className="bg-slate-800 border border-slate-700 rounded-2xl p-6">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-6">
            <div>
              <p className="text-sm text-gray-400">{t('ingest.results.title')}</p>
              <h2 className="text-2xl font-semibold text-white">{t('ingest.results.subtitle')}</h2>
            </div>
            <div className="flex gap-3">
              <div className="px-4 py-2 rounded-lg bg-emerald-600/10 border border-emerald-500/30">
                <p className="text-xs text-emerald-300">{t('ingest.results.created')}</p>
                <p className="text-lg font-semibold text-white">
                  {summary ? summary.created : '--'}
                </p>
              </div>
              <div className="px-4 py-2 rounded-lg bg-red-600/10 border border-red-500/30">
                <p className="text-xs text-red-300">{t('ingest.results.failed')}</p>
                <p className="text-lg font-semibold text-white">
                  {summary ? summary.failed : '--'}
                </p>
              </div>
            </div>
          </div>

          {results.length === 0 ? (
            <div className="text-center py-10 text-gray-500">{t('ingest.results.empty')}</div>
          ) : (
            <div className="space-y-3">
              {results.map((result) => (
                <div
                  key={`${result.clientId}-${result.filename}`}
                  className="flex flex-col md:flex-row md:items-center md:justify-between gap-3 bg-slate-900/60 border border-slate-700 rounded-xl px-4 py-3"
                >
                  <div>
                    <p className="text-sm text-white">{result.filename}</p>
                    <p
                      className={`text-xs ${
                        result.status === 'created'
                          ? 'text-emerald-300'
                          : result.status === 'failed'
                          ? 'text-red-300'
                          : 'text-yellow-300'
                      }`}
                    >
                      {t(`ingest.results.status.${result.status}`)}
                    </p>
                    <p className="text-xs text-gray-400 mt-1">{result.detail}</p>
                  </div>
                  {result.prompt_id && (
                    <button
                      type="button"
                      onClick={() => navigate('/prompts')}
                      className="text-sm text-violet-300 hover:text-violet-100"
                    >
                      {t('ingest.results.viewPrompt')} #{result.prompt_id}
                    </button>
                  )}
                </div>
              ))}
            </div>
          )}
        </section>
      </main>
    </div>
  );
};
