/**
 * Prompt Form Modal
 * Modal for creating/editing prompts
 */

import { useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { Modal } from '../ui/Modal';
import { Loading } from '../ui/Loading';
import { CreatePromptRequest, Prompt } from '../../types/api.types';

interface PromptFormModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: CreatePromptRequest) => Promise<void>;
  prompt?: Prompt | null;
  isLoading?: boolean;
}

export const PromptFormModal = ({
  isOpen,
  onClose,
  onSubmit,
  prompt,
  isLoading = false,
}: PromptFormModalProps) => {
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<CreatePromptRequest>({
    defaultValues: prompt || {
      text: '',
      negative_prompt: '',
      model: '',
      category: '',
      tags: '',
      rating: 5,
      notes: '',
    },
  });

  // Reset form when prompt changes
  useEffect(() => {
    if (prompt) {
      reset(prompt);
    } else {
      reset({
        text: '',
        negative_prompt: '',
        model: '',
        category: '',
        tags: '',
        rating: 5,
        notes: '',
      });
    }
  }, [prompt, reset]);

  const handleFormSubmit = async (data: CreatePromptRequest) => {
    await onSubmit(data);
    reset();
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={prompt ? 'Editar Prompt' : 'Crear Nuevo Prompt'}
      size="lg"
    >
      <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-4">
        {/* Prompt Text */}
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Prompt Text <span className="text-red-400">*</span>
          </label>
          <textarea
            {...register('text', { required: 'El texto del prompt es requerido' })}
            rows={4}
            className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-violet-600 focus:border-transparent resize-none"
            placeholder="Ingresa el prompt..."
            disabled={isLoading}
          />
          {errors.text && (
            <p className="mt-1 text-sm text-red-400">{errors.text.message}</p>
          )}
        </div>

        {/* Negative Prompt */}
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Negative Prompt
          </label>
          <textarea
            {...register('negative_prompt')}
            rows={3}
            className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-violet-600 focus:border-transparent resize-none"
            placeholder="Prompt negativo (opcional)..."
            disabled={isLoading}
          />
        </div>

        {/* Model and Category */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Model
            </label>
            <input
              {...register('model')}
              type="text"
              className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-violet-600 focus:border-transparent"
              placeholder="stable-diffusion-v1.5"
              disabled={isLoading}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Category
            </label>
            <input
              {...register('category')}
              type="text"
              className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-violet-600 focus:border-transparent"
              placeholder="landscape, portrait, etc."
              disabled={isLoading}
            />
          </div>
        </div>

        {/* Tags */}
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Tags
          </label>
          <input
            {...register('tags')}
            type="text"
            className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-violet-600 focus:border-transparent"
            placeholder="tag1, tag2, tag3"
            disabled={isLoading}
          />
          <p className="mt-1 text-xs text-gray-400">
            Separar tags con comas
          </p>
        </div>

        {/* Rating */}
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Rating
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
            Notes
          </label>
          <textarea
            {...register('notes')}
            rows={2}
            className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-violet-600 focus:border-transparent resize-none"
            placeholder="Notas adicionales (opcional)..."
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
            Cancelar
          </button>
          <button
            type="submit"
            disabled={isLoading}
            className="px-4 py-2 bg-violet-600 hover:bg-violet-700 disabled:opacity-50 text-white rounded-lg transition-colors flex items-center gap-2"
          >
            {isLoading && <Loading size="sm" />}
            {prompt ? 'Actualizar' : 'Crear'}
          </button>
        </div>
      </form>
    </Modal>
  );
};
