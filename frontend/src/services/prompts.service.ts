/**
 * Prompts Service
 *
 * @module services/prompts
 * @description Service for managing prompt CRUD operations.
 * Provides comprehensive API integration for creating, reading,
 * updating, and deleting prompts with proper error handling.
 *
 * Features:
 * - Paginated prompt listing with filtering
 * - Individual prompt retrieval with caching prevention
 * - Create new prompts with validation
 * - Update existing prompts
 * - Safe deletion operations
 * - Advanced search capabilities
 * - Automatic cache busting with timestamps
 */

import api, { handleApiError } from './api';
import { Prompt, CreatePromptRequest, PaginatedResponse } from '../types/api.types';

/**
 * Prompts service object containing all prompt-related API methods
 */
export const promptsService = {
  /**
   * Retrieves paginated list of prompts
   *
   * @param {number} [page=1] - Page number for pagination
   * @param {number} [pageSize=20] - Number of items per page
   * @param {string} [category] - Optional category filter
   * @returns {Promise<PaginatedResponse<Prompt>>} Paginated prompts response
   * @throws {Error} If API request fails
   *
   * @example
   * ```typescript
   * const prompts = await promptsService.getPrompts(1, 20, 'landscape');
   * // Process prompts.results
   * ```
   */
  getPrompts: async (
    page: number = 1,
    pageSize: number = 20,
    myPromptsOnly?: boolean
  ): Promise<PaginatedResponse<Prompt>> => {
    try {
      const params = new URLSearchParams({
        page: page.toString(),
        page_size: pageSize.toString(),
        _t: Date.now().toString(), // Add timestamp to prevent caching
      });

      if (myPromptsOnly) {
        params.append('my_prompts', 'true');
      }

      const response = await api.get<PaginatedResponse<Prompt>>(`/prompts?${params.toString()}`);
      return response.data;
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  },

  /**
   * Retrieves a single prompt by its ID
   *
   * @param {number} id - Prompt ID
   * @returns {Promise<Prompt>} The requested prompt
   * @throws {Error} If prompt not found or request fails
   *
   * @description
   * - Includes timestamp to prevent browser caching
   * - Returns full prompt details including metadata
   */
  getPromptById: async (id: number): Promise<Prompt> => {
    try {
      const response = await api.get<Prompt>(`/prompts/${id}?_t=${Date.now()}`);
      return response.data;
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  },

  /**
   * Creates a new prompt
   *
   * @param {CreatePromptRequest} prompt - Prompt data to create
   * @returns {Promise<Prompt>} The created prompt with generated ID
   * @throws {Error} If validation fails or request fails
   *
   * @example
   * ```typescript
   * const newPrompt = await promptsService.createPrompt({
   *   text: 'A beautiful landscape...',
   *   category: 'landscape',
   *   rating: 5
   * });
   * ```
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
   * Updates an existing prompt
   *
   * @param {number} id - ID of the prompt to update
   * @param {CreatePromptRequest} prompt - Updated prompt data
   * @returns {Promise<Prompt>} The updated prompt
   * @throws {Error} If prompt not found or update fails
   *
   * @description
   * - Replaces all prompt fields with provided data
   * - Returns updated prompt with new timestamp
   * - Requires authentication for write access
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
   * Deletes a prompt permanently
   *
   * @param {number} id - ID of the prompt to delete
   * @returns {Promise<void>}
   * @throws {Error} If prompt not found or deletion fails
   *
   * @description
   * - Permanently removes prompt from database
   * - Operation cannot be undone
   * - Requires authentication and proper permissions
   *
   * @example
   * ```typescript
   * await promptsService.deletePrompt(123);
   * // Prompt is now permanently deleted
   * ```
   */
  deletePrompt: async (id: number): Promise<void> => {
    try {
      await api.delete(`/prompts/${id}`);
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  },

  /**
   * Searches prompts with multiple filter criteria
   *
   * @param {string} [text] - Text to search in prompt content
   * @param {string} [category] - Category filter
   * @param {string} [model] - Model filter
   * @param {number} [minRating] - Minimum rating filter
   * @returns {Promise<Prompt[]>} Array of matching prompts
   * @throws {Error} If search fails
   *
   * @description
   * - Supports multiple simultaneous filters
   * - Returns all prompts if no filters provided
   * - Case-insensitive text search
   * - Results sorted by relevance
   *
   * @example
   * ```typescript
   * const results = await promptsService.searchPrompts(
   *   'landscape',
   *   'nature',
   *   'stable-diffusion-v1.5',
   *   4
   * );
   * ```
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
