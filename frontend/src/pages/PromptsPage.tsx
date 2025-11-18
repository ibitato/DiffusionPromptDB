/**
 * Prompts Page with Full CRUD
 * List and manage prompts with create, edit, delete functionality
 */

import { useEffect, useRef, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Header } from '../components/layout/Header';
import { Loading } from '../components/ui/Loading';
import { ConfirmModal } from '../components/ui/Modal';
import { PromptFormModal } from '../components/prompts/PromptFormModal';
import { PromptDetailModal } from '../components/prompts/PromptDetailModal';
import { useToast } from '../hooks/useToast';
import { useAuthStore } from '../store/authStore';
import { promptsService } from '../services/prompts.service';
import { preferencesService } from '../services/preferences.service';
import { Prompt, CreatePromptRequest } from '../types/api.types';
import { exportToCSV, exportToJSON, getExportFilename } from '../utils/exportPrompts';
import { logError, logDebug } from '../utils/logger';
import { buildMediaUrl } from '../services/api';

export const PromptsPage = () => {
  const { t } = useTranslation();
  const { user } = useAuthStore();
  const [prompts, setPrompts] = useState<Prompt[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPrompts, setTotalPrompts] = useState(0);
  const [myPromptsOnly, setMyPromptsOnly] = useState(false);
  const pageSize = 20;

  const isAdmin = user?.role === 'admin';

  // Modal states
  const [isFormModalOpen, setIsFormModalOpen] = useState(false);
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [isDetailModalOpen, setIsDetailModalOpen] = useState(false);
  const [selectedPrompt, setSelectedPrompt] = useState<Prompt | null>(null);
  const [promptToDelete, setPromptToDelete] = useState<Prompt | null>(null);
  const [promptToView, setPromptToView] = useState<Prompt | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const latestRequestRef = useRef(0);

  const toast = useToast();

  useEffect(() => {
    loadPreferences();
  }, []);

  useEffect(() => {
    loadPrompts();
  }, [currentPage, myPromptsOnly]);

  const loadPreferences = async () => {
    try {
      const prefs = await preferencesService.getPreferences();
      setMyPromptsOnly(prefs.my_prompts_only);
    } catch (err) {
      logError('Error loading preferences', err);
    } finally {
      setIsLoading(false);
    }
  };

  const loadPrompts = async () => {
    const requestId = ++latestRequestRef.current;
    setIsLoading(true);
    try {
      const data = await promptsService.getPrompts(currentPage, pageSize, myPromptsOnly);
      if (requestId !== latestRequestRef.current) {
        return;
      }
      setPrompts(data.results);
      setTotalPrompts(data.total);
      setError('');
    } catch (err) {
      if (requestId !== latestRequestRef.current) {
        return;
      }
      const message = err instanceof Error ? err.message : t('prompts.errors.load');
      setError(message);
      toast.error(message);
    } finally {
      if (requestId === latestRequestRef.current) {
        setIsLoading(false);
      }
    }
  };

  const handleCreate = () => {
    setSelectedPrompt(null);
    setIsFormModalOpen(true);
  };

  const handleView = (prompt: Prompt) => {
    setPromptToView(prompt);
    setIsDetailModalOpen(true);
  };

  const handleEdit = (prompt: Prompt) => {
    setSelectedPrompt(prompt);
    setIsFormModalOpen(true);
  };

  const handleDelete = (prompt: Prompt) => {
    // Close detail modal first if it's open
    if (isDetailModalOpen) {
      setIsDetailModalOpen(false);
      setPromptToView(null);
    }
    setPromptToDelete(prompt);
    setIsDeleteModalOpen(true);
  };

  const handleFormSubmit = async (data: CreatePromptRequest) => {
    setIsSubmitting(true);
    try {
      let updatedPrompt: Prompt;
      if (selectedPrompt) {
        // Update existing prompt
        updatedPrompt = await promptsService.updatePrompt(selectedPrompt.id, data);
        toast.success(t('promptForm.messages.updated'));

        // If the detail modal is open, update the viewed prompt
        if (promptToView && promptToView.id === selectedPrompt.id) {
          setPromptToView(updatedPrompt);
        }
      } else {
        // Create new prompt
        await promptsService.createPrompt(data);
        toast.success(t('promptForm.messages.created'));
      }

      setIsFormModalOpen(false);
      setSelectedPrompt(null);

      // Force reload prompts with a small delay to ensure DB is updated
      setTimeout(async () => {
        await loadPrompts();
      }, 100);
    } catch (err) {
      const message = err instanceof Error ? err.message : t('prompts.errors.save');
      toast.error(message);
    } finally {
      setIsSubmitting(false);
    }
  };

  const confirmDelete = async () => {
    if (!promptToDelete) return;

    setIsSubmitting(true);
    try {
      await promptsService.deletePrompt(promptToDelete.id);
      toast.success(t('deleteConfirm.success'));
      setIsDeleteModalOpen(false);
      setPromptToDelete(null);
      await loadPrompts();
    } catch (err) {
      const message = err instanceof Error ? err.message : t('prompts.errors.delete');
      toast.error(message);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleCopyPrompt = async (prompt: Prompt | null) => {
    if (!prompt) {
      return;
    }
    try {
      logDebug('Copying prompt from Prompts page detail modal', { promptId: prompt.id });
      await promptsService.copyPrompt(prompt.id);
      toast.success(t('search.messages.copySuccess'));
      await loadPrompts();
    } catch (err) {
      logError('Error copying prompt from Prompts page', err);
      const message = err instanceof Error ? err.message : t('search.messages.copyError');
      toast.error(message);
    }
  };

  const totalPages = Math.ceil(totalPrompts / pageSize);

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('es-ES', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  const truncateText = (text: string, maxLength: number = 150) => {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
  };

  // Check if user can edit/delete a prompt
  const canModify = (prompt: Prompt): boolean => {
    if (isAdmin) return true; // Admin can modify everything
    if (prompt.created_by === null) return false; // Preloaded, only admin
    return prompt.created_by === user?.id; // Own prompt
  };

  const isPreloaded = (prompt: Prompt): boolean => {
    return prompt.created_by === null;
  };

  if (error && !prompts.length) {
    return (
      <div className="min-h-screen bg-slate-900">
        <Header />
        <div className="max-w-7xl mx-auto px-4 py-8">
          <div className="bg-red-500/10 border border-red-500 rounded-lg p-4">
            <p className="text-red-400">{error}</p>
            <button
              onClick={() => loadPrompts()}
              className="mt-2 text-red-400 hover:text-red-300 underline"
            >
              Reintentar
            </button>
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
        <div className="mb-8 flex items-center justify-between">
          <div>
            <h2 className="text-3xl font-bold text-white mb-2">{t('prompts.title')}</h2>
            <p className="text-gray-400">
              {totalPrompts} {t('prompts.totalPrompts')}
            </p>
          </div>

          <div className="flex items-center gap-3">
            {/* Export Buttons */}
            {prompts.length > 0 && (
              <div className="flex items-center gap-2">
                <button
                  onClick={() => {
                    exportToJSON(prompts, getExportFilename('json'));
                    toast.success(t('prompts.export.successJson'));
                  }}
                  className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg font-medium transition-colors flex items-center gap-2"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M9 19l3 3m0 0l3-3m-3 3V10"
                    />
                  </svg>
                  {t('prompts.export.json')}
                </button>
                <button
                  onClick={() => {
                    exportToCSV(prompts, getExportFilename('csv'));
                    toast.success(t('prompts.export.successCsv'));
                  }}
                  className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors flex items-center gap-2"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M9 19l3 3m0 0l3-3m-3 3V10"
                    />
                  </svg>
                  {t('prompts.export.csv')}
                </button>
              </div>
            )}

            {/* All authenticated users can create their own prompts */}
            <button
              onClick={handleCreate}
              className="px-4 py-2 bg-violet-600 hover:bg-violet-700 text-white rounded-lg font-medium transition-colors flex items-center gap-2"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 4v16m8-8H4"
                />
              </svg>
              {t('prompts.newPrompt')}
            </button>
          </div>
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
                📝 {t('common.filters.myPrompts')}
              </span>
            </label>
          </div>
        )}

        {/* Loading State */}
        {isLoading ? (
          <div className="flex items-center justify-center py-12">
            <Loading size="lg" text={t('prompts.loading')} />
          </div>
        ) : (
          <>
            {/* Prompts List */}
            <div className="space-y-4 mb-8">
              {prompts.map((prompt) => {
                const thumbnailUrl = buildMediaUrl(prompt.thumbnail_path);
                return (
                  <div
                    key={prompt.id}
                    className="bg-slate-800 rounded-lg p-6 border border-slate-700 hover:border-slate-600 transition-colors"
                  >
                    <div className="flex flex-col lg:flex-row gap-6 mb-4">
                      {thumbnailUrl && (
                        <div className="w-full lg:w-56">
                          <div className="bg-slate-900/40 border border-slate-700 rounded-lg overflow-hidden">
                            <img
                              src={thumbnailUrl}
                              alt={t('prompts.thumbnail.alt', { id: prompt.id })}
                              className="w-full h-48 object-cover"
                              loading="lazy"
                            />
                          </div>
                          <p className="text-xs text-gray-500 mt-2">{t('prompts.thumbnail.label')}</p>
                        </div>
                      )}
                      <div className="flex-1">
                        <div className="flex flex-wrap items-center gap-3 mb-2">
                          <h3 className="text-lg font-semibold text-white">Prompt #{prompt.id}</h3>
                          {isPreloaded(prompt) && (
                            <span className="px-2 py-1 bg-orange-600/20 text-orange-400 text-xs rounded-full">
                              Precargado
                            </span>
                          )}
                          {prompt.category && (
                            <span className="px-2 py-1 bg-blue-600/20 text-blue-400 text-xs rounded-full">
                              {prompt.category}
                            </span>
                          )}
                          {prompt.rating && (
                            <div className="flex items-center">
                              {[...Array(5)].map((_, i) => (
                                <svg
                                  key={i}
                                  className={`w-4 h-4 ${
                                    i < prompt.rating! ? 'text-yellow-400' : 'text-gray-600'
                                  }`}
                                  fill="currentColor"
                                  viewBox="0 0 20 20"
                                >
                                  <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                                </svg>
                              ))}
                            </div>
                          )}
                        </div>
                        <p className="text-gray-300 leading-relaxed">{truncateText(prompt.text)}</p>
                      </div>
                    </div>

                    {/* Tags */}
                    {prompt.tags && (
                      <div className="flex flex-wrap gap-2 mb-3">
                        {prompt.tags.split(',').map((tag, index) => (
                          <span
                            key={index}
                            className="px-2 py-1 bg-slate-700 text-gray-300 text-xs rounded"
                          >
                            {tag.trim()}
                          </span>
                        ))}
                      </div>
                    )}

                    {/* Footer */}
                    <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 pt-4 border-t border-slate-700">
                      <div className="flex flex-wrap items-center gap-4 text-sm text-gray-400">
                        {prompt.model && (
                          <span>
                            <strong>Model:</strong> {prompt.model}
                          </span>
                        )}
                        <span>{formatDate(prompt.created_at)}</span>
                      </div>

                      <div className="flex flex-wrap items-center gap-2">
                        <button
                          onClick={() => handleView(prompt)}
                          className="px-3 py-1 text-blue-400 hover:text-blue-300 hover:bg-blue-400/10 rounded transition-colors"
                        >
                          {t('prompts.actions.view')}
                        </button>
                        {canModify(prompt) && (
                          <>
                            <button
                              onClick={() => handleEdit(prompt)}
                              className="px-3 py-1 text-green-400 hover:text-green-300 hover:bg-green-400/10 rounded transition-colors"
                            >
                              {t('prompts.actions.edit')}
                            </button>
                            <button
                              onClick={() => handleDelete(prompt)}
                              className="px-3 py-1 text-red-400 hover:text-red-300 hover:bg-red-400/10 rounded transition-colors"
                            >
                              {t('prompts.actions.delete')}
                            </button>
                          </>
                        )}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="flex items-center justify-center gap-2">
                <button
                  onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
                  disabled={currentPage === 1}
                  className="px-4 py-2 bg-slate-800 hover:bg-slate-700 disabled:bg-slate-800 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-lg transition-colors"
                >
                  {t('prompts.pagination.previous')}
                </button>

                <div className="flex items-center gap-1">
                  {[...Array(Math.min(5, totalPages))].map((_, i) => {
                    let pageNum;
                    if (totalPages <= 5) {
                      pageNum = i + 1;
                    } else if (currentPage <= 3) {
                      pageNum = i + 1;
                    } else if (currentPage >= totalPages - 2) {
                      pageNum = totalPages - 4 + i;
                    } else {
                      pageNum = currentPage - 2 + i;
                    }

                    return (
                      <button
                        key={i}
                        onClick={() => setCurrentPage(pageNum)}
                        className={`px-4 py-2 rounded-lg transition-colors ${
                          currentPage === pageNum
                            ? 'bg-violet-600 text-white'
                            : 'bg-slate-800 hover:bg-slate-700 text-gray-300'
                        }`}
                      >
                        {pageNum}
                      </button>
                    );
                  })}
                </div>

                <button
                  onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
                  disabled={currentPage === totalPages}
                  className="px-4 py-2 bg-slate-800 hover:bg-slate-700 disabled:bg-slate-800 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-lg transition-colors"
                >
                  {t('prompts.pagination.next')}
                </button>
              </div>
            )}
          </>
        )}
      </main>

      {/* Detail Modal */}
      <PromptDetailModal
        isOpen={isDetailModalOpen}
        onClose={() => {
          setIsDetailModalOpen(false);
          setPromptToView(null);
        }}
        prompt={promptToView}
        onEdit={handleEdit}
        onDelete={handleDelete}
        canModify={promptToView ? canModify(promptToView) : false}
        canCopy={Boolean(user && promptToView && promptToView.created_by !== user.id)}
        onCopy={handleCopyPrompt}
      />

      {/* Form Modal */}
      <PromptFormModal
        isOpen={isFormModalOpen}
        onClose={() => {
          setIsFormModalOpen(false);
          setSelectedPrompt(null);
        }}
        onSubmit={handleFormSubmit}
        prompt={selectedPrompt}
        isLoading={isSubmitting}
      />

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
