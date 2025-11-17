/**
 * Prompts Hooks with React Query
 * Custom hooks for prompts with caching
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { promptsService } from '../services/prompts.service';
import { CreatePromptRequest } from '../types/api.types';
import { useToast } from './useToast';

// Query keys
export const promptKeys = {
  all: ['prompts'] as const,
  lists: () => [...promptKeys.all, 'list'] as const,
  list: (page: number, pageSize: number, category?: string) =>
    [...promptKeys.lists(), { page, pageSize, category }] as const,
  detail: (id: number) => [...promptKeys.all, 'detail', id] as const,
};

// Hook to get paginated prompts
export const usePrompts = (page: number = 1, pageSize: number = 20, category?: string) => {
  return useQuery({
    queryKey: promptKeys.list(page, pageSize, category),
    queryFn: () => promptsService.getPrompts(page, pageSize, category),
    staleTime: 1000 * 60 * 5, // 5 minutes
  });
};

// Hook to get single prompt
export const usePrompt = (id: number) => {
  return useQuery({
    queryKey: promptKeys.detail(id),
    queryFn: () => promptsService.getPromptById(id),
    enabled: !!id,
  });
};

// Hook to create prompt
export const useCreatePrompt = () => {
  const queryClient = useQueryClient();
  const toast = useToast();

  return useMutation({
    mutationFn: (data: CreatePromptRequest) => promptsService.createPrompt(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: promptKeys.lists() });
      toast.success('Prompt creado exitosamente');
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Error al crear prompt');
    },
  });
};

// Hook to update prompt
export const useUpdatePrompt = () => {
  const queryClient = useQueryClient();
  const toast = useToast();

  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: CreatePromptRequest }) =>
      promptsService.updatePrompt(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: promptKeys.lists() });
      queryClient.invalidateQueries({ queryKey: promptKeys.detail(variables.id) });
      toast.success('Prompt actualizado exitosamente');
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Error al actualizar prompt');
    },
  });
};

// Hook to delete prompt
export const useDeletePrompt = () => {
  const queryClient = useQueryClient();
  const toast = useToast();

  return useMutation({
    mutationFn: (id: number) => promptsService.deletePrompt(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: promptKeys.lists() });
      toast.success('Prompt eliminado exitosamente');
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Error al eliminar prompt');
    },
  });
};
