/**
 * Prompts Service
 * Handles all CRUD operations for prompts
 */

import api, { handleApiError } from './api';
import {
  Prompt,
  CreatePromptRequest,
  PaginatedResponse,
} from '../types/api.types';

export const promptsService = {
  /**
   * Get all prompts with pagination
   */
  getPrompts: async (
    page: number = 1,
    pageSize: number = 20,
    category?: string
  ): Promise<PaginatedResponse<Prompt>> => {
    try {
      const params = new URLSearchParams({
        page: page.toString(),
        page_size: pageSize.toString(),
      });

      if (category) {
        params.append('category', category);
      }

      const response = await api.get<PaginatedResponse<Prompt>>(
        `/prompts?${params.toString()}`
      );
      return response.data;
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  },

  /**
   * Get a single prompt by ID
   */
  getPromptById: async (id: number): Promise<Prompt> => {
    try {
      const response = await api.get<Prompt>(`/prompts/${id}`);
      return response.data;
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  },

  /**
   * Create a new prompt
   */
  createPrompt: async (prompt: CreatePromptRequest): Promise<Prompt> => {
    try {
      const response = await api.post<Prompt>('/prompts', prompt);
      return response.data;
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  },

  /**
   * Update an existing prompt
   */
  updatePrompt: async (id: number, prompt: CreatePromptRequest): Promise<Prompt> => {
    try {
      const response = await api.put<Prompt>(`/prompts/${id}`, prompt);
      return response.data;
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  },

  /**
   * Delete a prompt
   */
  deletePrompt: async (id: number): Promise<void> => {
    try {
      await api.delete(`/prompts/${id}`);
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  },

  /**
   * Search prompts
   */
  searchPrompts: async (
    text?: string,
    category?: string,
    model?: string,
    minRating?: number
  ): Promise<Prompt[]> => {
    try {
      const params = new URLSearchParams();

      if (text) params.append('text', text);
      if (category) params.append('category', category);
      if (model) params.append('model', model);
      if (minRating) params.append('min_rating', minRating.toString());

      const response = await api.get<Prompt[]>(`/prompts/search?${params.toString()}`);
      return response.data;
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  },
};
