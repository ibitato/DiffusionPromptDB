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

import { useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { useTranslation } from 'react-i18next';
import { Modal } from '../ui/Modal';
import { Loading } from '../ui/Loading';
import { CreatePromptRequest, Prompt } from '../../types/api.types';

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
  
  // Debug log to see what we receive
  console.log('PromptFormModal rendered with prompt:', prompt);
  
  /**
   * React Hook Form configuration
   * Provides form state management, validation, and submission handling
   */
  const {
    register,
    handleSubmit,
    reset,
    setValue,
    watch,
    formState: { errors },
  } = useForm<CreatePromptRequest>({
    defaultValues: prompt ? {
      text: prompt.text || '',
      negative_prompt: prompt.negative_prompt || '',
      model: prompt.model || '',
      category: prompt.category || '',
      art_style: prompt.art_style || '',
      tags: prompt.tags || '',
      rating: prompt.rating || 5,
      notes: prompt.notes || '',
      parameters: prompt.parameters || '',
    } : {
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

  // Watch the text field to see if it's being populated
  const watchText = watch('text');
  console.log('Current text value in form:', watchText);

  /**
   * Effect to reset form when prompt prop changes
   * Ensures form is populated with correct data in edit mode
   * or cleared in create mode
   */
  useEffect(() => {
    if (prompt && isOpen) {
      // Edit mode: populate form with existing prompt data
      console.log('useEffect - Setting values for prompt:', prompt);
      
      // Reset the entire form with new values
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
      
      console.log('Form data to set:', formData);
      reset(formData);
    } else if (!prompt && isOpen) {
      // Create mode: clear form with default values
      console.log('useEffect - Clearing form for create mode');
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
          <label className="block text-sm font-medium text-gray-300 mb-2">{t('promptForm.fields.negativePrompt')}</label>
          <textarea
            {...register('negative_prompt')}
            rows={3}
            className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-violet-600 focus:border-transparent resize-none"
            placeholder={t('promptForm.fields.negativePromptPlaceholder')}
            disabled={isLoading}
          />
        </div>

        {/* Model and Category */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              <span className="flex items-center gap-1">
                <span>🤖</span>
                <span>{t('promptForm.fields.model')}</span>
              </span>
            </label>
            <input
              {...register('model')}
              type="text"
              className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-violet-600 focus:border-transparent"
              placeholder={t('promptForm.fields.modelPlaceholder')}
              disabled={isLoading}
            />
          </div>

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
        </div>

        {/* Art Style */}
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            <span className="flex items-center gap-1">
              <span>🎨</span>
              <span>{t('promptForm.fields.artStyle')}</span>
            </span>
          </label>
          <input
            {...register('art_style')}
            type="text"
            className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-violet-600 focus:border-transparent"
            placeholder={t('promptForm.fields.artStylePlaceholder')}
            disabled={isLoading}
          />
          <p className="mt-1 text-xs text-gray-400">{t('promptForm.fields.artStyle')}</p>
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
          <p className="mt-1 text-xs text-gray-400">{t('promptForm.fields.tagsHelp')}</p>
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
                  className="w-8 h-8 text-yellow-400 hover:scale-110 transition-transform"
                  fill="currentColor"
                  viewBox="0 0 20 20"
                >
                  <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                </svg>
              </label>
            ))}
          </div>
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
