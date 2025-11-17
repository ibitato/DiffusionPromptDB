/**
 * PromptFormModal Component
 *
 * @description Modal dialog for creating and editing prompts.
 * Provides a comprehensive form with validation, internationalization,
 * and real-time feedback. Supports both create and edit modes.
 *
 * @component
 * @example
 * ```tsx
 * // Create mode
 * <PromptFormModal
 *   isOpen={isModalOpen}
 *   onClose={() => setIsModalOpen(false)}
 *   onSubmit={handleCreatePrompt}
 * />
 *
 * // Edit mode
 * <PromptFormModal
 *   isOpen={isModalOpen}
 *   onClose={() => setIsModalOpen(false)}
 *   onSubmit={handleUpdatePrompt}
 *   prompt={existingPrompt}
 *   isLoading={isSaving}
 * />
 * ```
 */

import { useEffect, useMemo, useState } from 'react';
import { useForm } from 'react-hook-form';
import { useTranslation } from 'react-i18next';
import { Modal } from '../ui/Modal';
import { Loading } from '../ui/Loading';
import { CreatePromptRequest, Prompt } from '../../types/api.types';
import { statsService } from '../../services/stats.service';
import { logDebug, logError } from '../../utils/logger';

/**
 * Props for the PromptFormModal component
 * @interface PromptFormModalProps
 */
interface PromptFormModalProps {
  /** Controls modal visibility */
  isOpen: boolean;

  /** Callback function triggered when modal closes */
  onClose: () => void;

  /** Async callback for form submission */
  onSubmit: (data: CreatePromptRequest) => Promise<void>;

  /** Optional prompt data for edit mode */
  prompt?: Prompt | null;

  /** Loading state to disable form interactions */
  isLoading?: boolean;
}

/**
 * PromptFormModal functional component
 *
 * @param {PromptFormModalProps} props - Component props
 * @returns {JSX.Element} Rendered modal with prompt form
 */
export const PromptFormModal = ({
  isOpen,
  onClose,
  onSubmit,
  prompt,
  isLoading = false,
}: PromptFormModalProps) => {
  const { t } = useTranslation();
  const [artStyles, setArtStyles] = useState<Array<{ style: string; count: number }>>([]);
  const [isLoadingStyles, setIsLoadingStyles] = useState(true);

  /**
   * React Hook Form configuration
   * Provides form state management, validation, and submission handling
   */
  const {
    register,
    handleSubmit,
    reset,
    watch,
    formState: { errors },
  } = useForm<CreatePromptRequest>({
    defaultValues: prompt
      ? {
          text: prompt.text || '',
          negative_prompt: prompt.negative_prompt || '',
          model: prompt.model || '',
          category: prompt.category || '',
          art_style: prompt.art_style || '',
          tags: prompt.tags || '',
          rating: prompt.rating || 5,
          notes: prompt.notes || '',
          parameters: prompt.parameters || '',
        }
      : {
          text: '',
          negative_prompt: '',
          model: '',
          category: '',
          art_style: '',
          tags: '',
          rating: 5,
          notes: '',
          parameters: '',
        },
  });

  // Watch the rating value to show selected star
  const currentRating = watch('rating');
  const styleLocaleCompare = (a: string, b: string) =>
    a.localeCompare(b, undefined, { sensitivity: 'base' });

  const normalizedArtStyles = useMemo(() => {
    const unique = new Map<string, number>();
    artStyles.forEach((item) => {
      if (item.style) {
        unique.set(item.style, item.count);
      }
    });
    if (prompt?.art_style && prompt.art_style.trim() && !unique.has(prompt.art_style)) {
      unique.set(prompt.art_style, 0);
    }
    return Array.from(unique.entries())
      .map(([style, count]) => ({ style, count }))
      .sort((a, b) => styleLocaleCompare(a.style, b.style));
  }, [artStyles, prompt?.art_style]);

  const validateArtStyle = (value: string) => {
    if (!value) {
      return t('promptForm.validation.artStyleRequired');
    }
    const exists = normalizedArtStyles.some((item) => item.style === value);
    if (!exists) {
      return t('promptForm.validation.artStyleInvalid');
    }
    return true;
  };

  /**
   * Load art styles for dropdown
   */
  useEffect(() => {
    const loadArtStyles = async () => {
      try {
        const filters = await statsService.getFilters();
        setArtStyles(filters.art_styles);
      } catch (err) {
        logError('Failed to load art styles', err);
      } finally {
        setIsLoadingStyles(false);
      }
    };

    if (isOpen) {
      loadArtStyles();
    }
  }, [isOpen]);

  /**
   * Effect to reset form when prompt prop changes
   * Ensures form is populated with correct data in edit mode
   * or cleared in create mode
   */
  useEffect(() => {
    if (prompt && isOpen) {
      logDebug('PromptFormModal: populating form for editing', { promptId: prompt.id });

      const formData = {
        text: prompt.text || '',
        negative_prompt: prompt.negative_prompt || '',
        model: prompt.model || '',
        category: prompt.category || '',
        art_style: prompt.art_style || '',
        tags: prompt.tags || '',
        rating: prompt.rating || 5,
        notes: prompt.notes || '',
        parameters: prompt.parameters || '',
      };

      reset(formData);
    } else if (!prompt && isOpen) {
      logDebug('PromptFormModal: resetting form for create mode');
      reset({
        text: '',
        negative_prompt: '',
        model: '',
        category: '',
        art_style: '',
        tags: '',
        rating: 5,
        notes: '',
        parameters: '',
      });
    }
  }, [prompt, reset, isOpen]);

  /**
   * Handles form submission
   * @param {CreatePromptRequest} data - Form data
   * @returns {Promise<void>}
   *
   * @description
   * - Submits form data to parent component
   * - Resets form after successful submission
   * - Parent handles success/error states
   */
  const handleFormSubmit = async (data: CreatePromptRequest) => {
    await onSubmit(data);
    reset();
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={prompt ? t('promptForm.editTitle') : t('promptForm.createTitle')}
      size="lg"
    >
      <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-4">
        {/* Prompt Text */}
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            {t('promptForm.fields.text')} <span className="text-red-400">*</span>
          </label>
          <textarea
            {...register('text', { required: t('promptForm.fields.textRequired') })}
            rows={4}
            className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-violet-600 focus:border-transparent resize-none"
            placeholder={t('promptForm.fields.textPlaceholder')}
            disabled={isLoading}
          />
          {errors.text && <p className="mt-1 text-sm text-red-400">{errors.text.message}</p>}
        </div>

        {/* Negative Prompt */}
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            {t('promptForm.fields.negativePrompt')}
          </label>
          <textarea
            {...register('negative_prompt')}
            rows={3}
            className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-violet-600 focus:border-transparent resize-none"
            placeholder={t('promptForm.fields.negativePromptPlaceholder')}
            disabled={isLoading}
          />
        </div>

        {/* Category - single full width field now */}
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            <span className="flex items-center gap-1">
              <span>📁</span>
              <span>{t('promptForm.fields.category')}</span>
            </span>
          </label>
          <input
            {...register('category')}
            type="text"
            className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-violet-600 focus:border-transparent"
            placeholder={t('promptForm.fields.categoryPlaceholder')}
            disabled={isLoading}
          />
        </div>

        {/* Art Style - Dropdown */}
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            <span className="flex items-center gap-1">
              <span>🎨</span>
              <span>{t('promptForm.fields.artStyle')}</span>
            </span>
          </label>
          <select
            {...register('art_style', {
              validate: validateArtStyle,
            })}
            className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-violet-600 focus:border-transparent"
            disabled={isLoading || isLoadingStyles}
          >
            <option value="">{t('promptForm.fields.artStylePlaceholder')}</option>
            {normalizedArtStyles.map((item) => (
              <option key={item.style} value={item.style}>
                {item.style.charAt(0).toUpperCase() + item.style.slice(1)} ({item.count})
              </option>
            ))}
          </select>
          {errors.art_style && (
            <p className="mt-1 text-sm text-red-400">{errors.art_style.message}</p>
          )}
        </div>

        {/* Tags */}
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            <span className="flex items-center gap-1">
              <span>🏷️</span>
              <span>{t('promptForm.fields.tags')}</span>
            </span>
          </label>
          <input
            {...register('tags')}
            type="text"
            className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-violet-600 focus:border-transparent"
            placeholder={t('promptForm.fields.tagsPlaceholder')}
            disabled={isLoading}
          />
        </div>

        {/* Rating */}
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            <span className="flex items-center gap-1">
              <span>⭐</span>
              <span>{t('promptForm.fields.rating')}</span>
            </span>
          </label>
          <div className="flex items-center gap-2">
            {[1, 2, 3, 4, 5].map((value) => (
              <label key={value} className="cursor-pointer">
                <input
                  {...register('rating')}
                  type="radio"
                  value={value}
                  className="sr-only"
                  disabled={isLoading}
                />
                <svg
                  className={`w-8 h-8 hover:scale-110 transition-transform ${
                    Number(currentRating) >= value ? 'text-yellow-400' : 'text-gray-600'
                  }`}
                  fill="currentColor"
                  viewBox="0 0 20 20"
                >
                  <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                </svg>
              </label>
            ))}
          </div>
        </div>

        {/* Parameters */}
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            <span className="flex items-center gap-1">
              <span>⚙️</span>
              <span>{t('promptForm.fields.parameters')}</span>
            </span>
          </label>
          <textarea
            {...register('parameters')}
            rows={2}
            className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-violet-600 focus:border-transparent resize-none font-mono text-sm"
            placeholder={t('promptForm.fields.parametersPlaceholder')}
            disabled={isLoading}
          />
        </div>

        {/* Notes */}
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            <span className="flex items-center gap-1">
              <span>📝</span>
              <span>{t('promptForm.fields.notes')}</span>
            </span>
          </label>
          <textarea
            {...register('notes')}
            rows={2}
            className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-violet-600 focus:border-transparent resize-none"
            placeholder={t('promptForm.fields.notesPlaceholder')}
            disabled={isLoading}
          />
        </div>

        {/* Actions */}
        <div className="flex justify-end gap-3 pt-4 border-t border-slate-700">
          <button
            type="button"
            onClick={onClose}
            disabled={isLoading}
            className="px-4 py-2 bg-slate-700 hover:bg-slate-600 disabled:opacity-50 text-white rounded-lg transition-colors"
          >
            {t('promptForm.actions.cancel')}
          </button>
          <button
            type="submit"
            disabled={isLoading}
            className="px-4 py-2 bg-violet-600 hover:bg-violet-700 disabled:opacity-50 text-white rounded-lg transition-colors flex items-center gap-2"
          >
            {isLoading && <Loading size="sm" />}
            {prompt ? t('promptForm.actions.update') : t('promptForm.actions.create')}
          </button>
        </div>
      </form>
    </Modal>
  );
};
