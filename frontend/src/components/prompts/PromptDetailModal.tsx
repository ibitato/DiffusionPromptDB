/**
 * Prompt Detail Modal
 * Full view of a prompt with all its information
 */

import { Modal } from '../ui/Modal';
import { Prompt } from '../../types/api.types';
import { motion } from 'framer-motion';

interface PromptDetailModalProps {
  isOpen: boolean;
  onClose: () => void;
  prompt: Prompt | null;
  onEdit: (prompt: Prompt) => void;
  onDelete: (prompt: Prompt) => void;
  canModify?: boolean; // Whether user can edit/delete this prompt
}

export const PromptDetailModal = ({
  isOpen,
  onClose,
  prompt,
  onEdit,
  onDelete,
  canModify = false,
}: PromptDetailModalProps) => {
  if (!prompt) return null;

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString('es-ES', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const handleEdit = () => {
    onEdit(prompt);
    onClose();
  };

  const handleDelete = () => {
    onDelete(prompt);
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    // Could show a toast here
  };

  return (
    <>
      <Modal isOpen={isOpen} onClose={onClose} title={`Prompt #${prompt.id}`} size="xl">
        <div className="space-y-6">
          {/* Header with badges */}
          <div className="flex items-center gap-3 pb-4 border-b border-slate-700">
            {prompt.category && (
              <motion.span
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                className="px-3 py-1 bg-blue-600/20 text-blue-400 rounded-full text-sm font-medium"
              >
                {prompt.category}
              </motion.span>
            )}
            {prompt.model && (
              <motion.span
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.1 }}
                className="px-3 py-1 bg-purple-600/20 text-purple-400 rounded-full text-sm font-medium"
              >
                {prompt.model}
              </motion.span>
            )}
            {prompt.rating && (
              <motion.div
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.2 }}
                className="flex items-center gap-1"
              >
                {[...Array(5)].map((_, i) => (
                  <svg
                    key={i}
                    className={`w-5 h-5 ${
                      i < prompt.rating! ? 'text-yellow-400' : 'text-gray-600'
                    }`}
                    fill="currentColor"
                    viewBox="0 0 20 20"
                  >
                    <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                  </svg>
                ))}
              </motion.div>
            )}
          </div>

          {/* Prompt Text */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
          >
            <div className="flex items-center justify-between mb-2">
              <h4 className="text-sm font-semibold text-gray-300">Prompt Text</h4>
              <button
                onClick={() => copyToClipboard(prompt.text)}
                className="text-xs text-violet-400 hover:text-violet-300 flex items-center gap-1"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"
                  />
                </svg>
                Copiar
              </button>
            </div>
            <div className="p-4 bg-slate-700/50 rounded-lg">
              <p className="text-gray-200 leading-relaxed whitespace-pre-wrap">{prompt.text}</p>
            </div>
          </motion.div>

          {/* Negative Prompt */}
          {prompt.negative_prompt && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
            >
              <div className="flex items-center justify-between mb-2">
                <h4 className="text-sm font-semibold text-gray-300">Negative Prompt</h4>
                <button
                  onClick={() => copyToClipboard(prompt.negative_prompt!)}
                  className="text-xs text-violet-400 hover:text-violet-300 flex items-center gap-1"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"
                    />
                  </svg>
                  Copiar
                </button>
              </div>
              <div className="p-4 bg-slate-700/50 rounded-lg">
                <p className="text-gray-200 leading-relaxed whitespace-pre-wrap">
                  {prompt.negative_prompt}
                </p>
              </div>
            </motion.div>
          )}

          {/* Tags */}
          {prompt.tags && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
            >
              <h4 className="text-sm font-semibold text-gray-300 mb-2">Tags</h4>
              <div className="flex flex-wrap gap-2">
                {prompt.tags.split(',').map((tag, index) => (
                  <motion.span
                    key={index}
                    initial={{ opacity: 0, scale: 0.8 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: 0.3 + index * 0.05 }}
                    className="px-3 py-1 bg-slate-700 text-gray-300 text-sm rounded-full"
                  >
                    {tag.trim()}
                  </motion.span>
                ))}
              </div>
            </motion.div>
          )}

          {/* Parameters */}
          {prompt.parameters && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
            >
              <h4 className="text-sm font-semibold text-gray-300 mb-2">Parameters</h4>
              <div className="p-4 bg-slate-700/50 rounded-lg">
                <pre className="text-gray-200 text-sm whitespace-pre-wrap overflow-x-auto">
                  {prompt.parameters}
                </pre>
              </div>
            </motion.div>
          )}

          {/* Notes */}
          {prompt.notes && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5 }}
            >
              <h4 className="text-sm font-semibold text-gray-300 mb-2">Notes</h4>
              <div className="p-4 bg-slate-700/50 rounded-lg">
                <p className="text-gray-200 leading-relaxed whitespace-pre-wrap">{prompt.notes}</p>
              </div>
            </motion.div>
          )}

          {/* Metadata */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6 }}
            className="grid grid-cols-2 gap-4 p-4 bg-slate-700/30 rounded-lg"
          >
            <div>
              <p className="text-xs text-gray-400 mb-1">Created</p>
              <p className="text-sm text-gray-200">{formatDate(prompt.created_at)}</p>
            </div>
            <div>
              <p className="text-xs text-gray-400 mb-1">Updated</p>
              <p className="text-sm text-gray-200">{formatDate(prompt.updated_at)}</p>
            </div>
          </motion.div>

          {/* Actions */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.7 }}
            className="flex justify-between items-center pt-4 border-t border-slate-700"
          >
            <button
              onClick={onClose}
              className="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg transition-colors"
            >
              Cerrar
            </button>
            {canModify && (
              <div className="flex gap-3">
                <button
                  onClick={handleEdit}
                  className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors"
                >
                  Editar
                </button>
                <button
                  onClick={handleDelete}
                  className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors"
                >
                  Eliminar
                </button>
              </div>
            )}
          </motion.div>
        </div>
      </Modal>
    </>
  );
};
