import { ChangeEvent, FormEvent, useEffect, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import { Header } from '../components/layout/Header';
import { useToast } from '../hooks/useToast';
import { ingestionService } from '../services/ingestion.service';
import { BatchImageIngestionResponse, ImageIngestionResult } from '../types/api.types';
import { statsService } from '../services/stats.service';
import { logError } from '../utils/logger';
import { parseStableDiffusionMetadata } from '../utils/pngMetadata';
import { inferArtStyleFromMetadata, inferTagsFromPrompt } from '../utils/promptSuggestions';

const MAX_FILES = 5;

export const PromptIngestionPage = () => {
  const { t } = useTranslation();
  const toast = useToast();
  const navigate = useNavigate();

  const [files, setFiles] = useState<File[]>([]);
  const [tags, setTags] = useState('');
  const [category, setCategory] = useState('');
  const [artStyle, setArtStyle] = useState('');
  const [rating, setRating] = useState('');
  const [notes, setNotes] = useState('');
  const [results, setResults] = useState<ImageIngestionResult[]>([]);
  const [summary, setSummary] = useState<BatchImageIngestionResponse | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [artStyleOptions, setArtStyleOptions] = useState<string[]>([]);
  const [tagSuggestions, setTagSuggestions] = useState<string[]>([]);
  const [suggestedArtStyle, setSuggestedArtStyle] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisError, setAnalysisError] = useState('');
  const [tagsTouched, setTagsTouched] = useState(false);
  const [artStyleTouched, setArtStyleTouched] = useState(false);

  const previews = useMemo(() => files.map((file) => URL.createObjectURL(file)), [files]);

  useEffect(
    () => () => {
      previews.forEach((url) => URL.revokeObjectURL(url));
    },
    [previews]
  );

  const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    const selectedFiles = Array.from(event.target.files ?? []);
    if (selectedFiles.length > MAX_FILES) {
      toast.error(t('ingest.errors.maxFiles', { max: MAX_FILES }));
    }
    const limited = selectedFiles.slice(0, MAX_FILES);
    setFiles(limited);
    setResults([]);
    setSummary(null);
    analyzeFileSelection(limited, {
      canPrefillTags: !tagsTouched && !tags.trim(),
      canPrefillStyle: !artStyleTouched && !artStyle.trim(),
    });
  };

  const removeFile = (index: number) => {
    setFiles((prev) => {
      const next = prev.filter((_, idx) => idx !== index);
      analyzeFileSelection(next, {
        canPrefillTags: !tagsTouched && !tags.trim(),
        canPrefillStyle: !artStyleTouched && !artStyle.trim(),
      });
      return next;
    });
  };

  const analyzeFileSelection = (
    fileList: File[],
    options: { canPrefillTags: boolean; canPrefillStyle: boolean }
  ) => {
    if (!fileList.length) {
      setTagSuggestions([]);
      setSuggestedArtStyle('');
      setAnalysisError('');
      return;
    }
    void analyzeMetadata(fileList[0], options);
  };

  const analyzeMetadata = async (
    file: File,
    options: { canPrefillTags: boolean; canPrefillStyle: boolean }
  ) => {
    setIsAnalyzing(true);
    setAnalysisError('');
    try {
      const metadata = await parseStableDiffusionMetadata(file);
      const inferredTags = inferTagsFromPrompt(metadata.positivePrompt);
      setTagSuggestions(inferredTags);
      if (options.canPrefillTags && inferredTags.length) {
        setTags(inferredTags.join(', '));
      }

      const inferredStyle = inferArtStyleFromMetadata(metadata);
      setSuggestedArtStyle(inferredStyle);
      if (options.canPrefillStyle && inferredStyle) {
        setArtStyle(inferredStyle);
      }
    } catch (error) {
      setTagSuggestions([]);
      setSuggestedArtStyle('');
      setAnalysisError(t('ingest.suggestions.failed'));
      logError('Error parsing PNG metadata', error);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    if (files.length === 0) {
      toast.error(t('ingest.errors.selectFiles'));
      return;
    }

    setIsSubmitting(true);
    try {
      const response = await ingestionService.ingestImages({
        files,
        tags: tags.trim(),
        category: category.trim(),
        artStyle: artStyle.trim(),
        rating: rating ? Number(rating) : undefined,
        notes: notes.trim(),
      });
      setResults(response.results);
      setSummary(response);
      toast.success(
        t('ingest.messages.completed', {
          created: response.created,
          failed: response.failed,
        })
      );
      setFiles([]);
    } catch (error) {
      toast.error(error instanceof Error ? error.message : t('ingest.errors.generic'));
    } finally {
      setIsSubmitting(false);
    }
  };

  const clearSelection = () => {
    setFiles([]);
    setResults([]);
    setSummary(null);
    setTagSuggestions([]);
    setSuggestedArtStyle('');
    setAnalysisError('');
  };

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
    loadFilters();
  }, []);

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
                {files.length} / {MAX_FILES}
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
                    d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M9 19l3 3m0 0l3-3m-3 3V10"
                  />
                </svg>
                <p className="text-lg font-semibold text-white">{t('ingest.dropzone.title')}</p>
                <p className="text-sm text-gray-400 mb-4">{t('ingest.dropzone.hint')}</p>
                <label className="inline-flex items-center gap-2 px-5 py-2.5 bg-violet-600 hover:bg-violet-700 text-white rounded-full cursor-pointer transition-colors">
                  <input
                    type="file"
                    accept=".png"
                    multiple
                    className="hidden"
                    onChange={handleFileChange}
                  />
                  {t('ingest.dropzone.action')}
                </label>
                <p className="text-xs text-gray-500 mt-3">{t('ingest.dropzone.helper')}</p>
              </div>
            </div>

            {files.length > 0 && (
              <div className="bg-slate-900/60 border border-slate-700 rounded-2xl p-6 space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-semibold text-white">
                    {t('ingest.preview.title', { count: files.length })}
                  </h3>
                  <button
                    type="button"
                    onClick={clearSelection}
                    className="text-sm text-red-300 hover:text-red-200"
                  >
                    {t('ingest.preview.clear')}
                  </button>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {files.map((file, index) => (
                    <div
                      key={`${file.name}-${index}`}
                      className="bg-slate-800/80 border border-slate-700 rounded-xl p-3 flex flex-col gap-2"
                    >
                      {previews[index] && (
                        <img
                          src={previews[index]}
                          alt={file.name}
                          className="w-full h-36 object-cover rounded-lg border border-slate-700"
                        />
                      )}
                      <div className="flex items-start justify-between gap-2">
                        <div>
                          <p className="text-sm text-white truncate">{file.name}</p>
                          <p className="text-xs text-gray-500">
                            {(file.size / 1024 / 1024).toFixed(2)} MB
                          </p>
                        </div>
                        <button
                          type="button"
                          onClick={(event) => {
                            event.stopPropagation();
                            removeFile(index);
                          }}
                          className="text-xs text-red-300 hover:text-red-100"
                        >
                          {t('ingest.preview.remove')}
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {isAnalyzing && (
              <p className="text-sm text-violet-300">{t('ingest.suggestions.analyzing')}</p>
            )}
            {analysisError && <p className="text-sm text-red-400">{analysisError}</p>}

            {tagSuggestions.length > 0 && (
              <div className="bg-slate-900/40 border border-slate-700 rounded-xl p-4 space-y-2">
                <div className="flex items-center justify-between">
                  <h4 className="text-sm font-semibold text-gray-200">
                    {t('ingest.suggestions.tagsTitle')}
                  </h4>
                  <button
                    type="button"
                    onClick={() => {
                      setTags(tagSuggestions.join(', '));
                      setTagsTouched(true);
                    }}
                    className="text-xs text-violet-300 hover:text-violet-100"
                  >
                    {t('ingest.suggestions.applyTags')}
                  </button>
                </div>
                <div className="flex flex-wrap gap-1">
                  {tagSuggestions.slice(0, 15).map((tag) => (
                    <span
                      key={tag}
                      className="px-2 py-1 bg-slate-800 text-xs text-gray-200 rounded-full"
                    >
                      #{tag}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {suggestedArtStyle && (
              <div className="bg-slate-900/40 border border-slate-700 rounded-xl p-4 flex items-center justify-between">
                <div>
                  <p className="text-sm font-semibold text-gray-200">
                    {t('ingest.suggestions.styleTitle')}
                  </p>
                  <p className="text-gray-400 text-sm">{suggestedArtStyle}</p>
                </div>
                <button
                  type="button"
                  onClick={() => {
                    setArtStyle(suggestedArtStyle);
                    setArtStyleTouched(true);
                  }}
                  className="text-xs text-violet-300 hover:text-violet-100"
                >
                  {t('ingest.suggestions.applyStyle')}
                </button>
              </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  <span className="flex items-center gap-1">
                    <span>🏷️</span>
                    <span>{t('ingest.form.tags')}</span>
                  </span>
                </label>
                <input
                  type="text"
                  value={tags}
                  onChange={(e) => {
                    setTagsTouched(true);
                    setTags(e.target.value);
                  }}
                  placeholder={t('ingest.form.tagsPlaceholder')}
                  className="w-full px-4 py-2.5 bg-slate-800 border border-slate-600 rounded-lg text-white placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-violet-500 focus:border-transparent"
                />
                <p className="text-xs text-gray-500 mt-1">{t('ingest.form.tagsHelp')}</p>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    <span className="flex items-center gap-1">
                      <span>📁</span>
                      <span>{t('ingest.form.category')}</span>
                    </span>
                  </label>
                  <input
                    type="text"
                    value={category}
                    onChange={(e) => setCategory(e.target.value)}
                    placeholder={t('ingest.form.categoryPlaceholder')}
                    className="w-full px-4 py-2.5 bg-slate-800 border border-slate-600 rounded-lg text-white placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-violet-500 focus:border-transparent"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    <span className="flex items-center gap-1">
                      <span>🎨</span>
                      <span>{t('ingest.form.artStyle')}</span>
                    </span>
                  </label>
                  <div className="relative">
                    <select
                      value={artStyle}
                      onChange={(e) => {
                        setArtStyleTouched(true);
                        setArtStyle(e.target.value);
                      }}
                      className="w-full cursor-pointer appearance-none bg-slate-800 border border-slate-600 rounded-lg px-4 py-2.5 pr-10 text-white focus:outline-none focus:ring-2 focus:ring-violet-500 focus:border-transparent"
                    >
                      <option value="">{t('ingest.form.artStylePlaceholder')}</option>
                      {artStyleOptions.map((style) => (
                        <option key={style} value={style}>
                          {style}
                        </option>
                      ))}
                    </select>
                    <svg
                      className="w-4 h-4 text-gray-400 absolute top-1/2 right-3 -translate-y-1/2 pointer-events-none"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M19 9l-7 7-7-7"
                      />
                    </svg>
                  </div>
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  {t('ingest.form.rating')}
                </label>
                <select
                  value={rating}
                  onChange={(e) => setRating(e.target.value)}
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
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  {t('ingest.form.notes')}
                </label>
                <textarea
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  rows={3}
                  placeholder={t('ingest.form.notesPlaceholder')}
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2.5 text-white placeholder:text-gray-500 focus:outline-none focus:ring-2 focus:ring-violet-500"
                />
              </div>
            </div>

            <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
              <p className="text-sm text-gray-400">{t('ingest.form.helper', { max: MAX_FILES })}</p>
              <div className="flex items-center gap-3">
                <button
                  type="button"
                  onClick={clearSelection}
                  className="px-5 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg transition-colors"
                  disabled={files.length === 0 && !tags && !category && !artStyle && !notes}
                >
                  {t('ingest.actions.reset')}
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
                  key={`${result.filename}-${result.status}-${result.detail}`}
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
