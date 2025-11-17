/**
 * Stats Service
 * Handles statistics and admin endpoints
 */

import api, { handleApiError } from './api';
import { Stats } from '../types/api.types';

export const statsService = {
  /**
   * Get overall statistics
   * Requires authentication (non-admin users allowed); personal stats still use the same token.
   */
  getStats: async (myPromptsOnly: boolean = false): Promise<Stats> => {
    try {
      const response = await api.get<Stats>('/admin/stats', {
        params: myPromptsOnly ? { my_prompts_only: true } : undefined,
      });
      return response.data;
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  },

  /**
   * Health check
   * Public endpoint - no auth required
   */
  healthCheck: async (): Promise<{ status: string; timestamp: string }> => {
    try {
      const response = await api.get('/admin/health');
      return response.data;
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  },

  /**
   * Get available filters
   * Requires authentication even though data is non-sensitive, so we keep everything behind the dashboard session.
   */
  getFilters: async (): Promise<{
    nsfw_levels: string[];
    art_styles: Array<{ style: string; count: number }>;
  }> => {
    try {
      const response = await api.get('/admin/filters');
      return response.data;
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  },
};
