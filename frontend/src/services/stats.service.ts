/**
 * Stats Service
 * Handles statistics and admin endpoints
 */

import api, { handleApiError } from './api';
import { Stats } from '../types/api.types';

export const statsService = {
  /**
   * Get overall statistics
   * Public endpoint - no auth required
   */
  getStats: async (): Promise<Stats> => {
    try {
      const response = await api.get<Stats>('/admin/stats');
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
   * Public endpoint - no auth required
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
