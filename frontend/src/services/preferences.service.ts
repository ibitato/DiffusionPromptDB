/**
 * User Preferences Service
 * Handles user preferences endpoints
 */

import api, { handleApiError } from './api';

export interface UserPreferences {
  user_id: number;
  show_unspecified: boolean;
  my_prompts_only: boolean;
  excluded_tags: string[];
}

export interface UpdatePreferences {
  show_unspecified?: boolean;
  my_prompts_only?: boolean;
  excluded_tags?: string[];
}

export const preferencesService = {
  /**
   * Get user preferences
   * Requires: JWT Token
   */
  getPreferences: async (): Promise<UserPreferences> => {
    try {
      const response = await api.get<UserPreferences>('/user/preferences');
      return response.data;
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  },

  /**
   * Update user preferences
   * Requires: JWT Token
   */
  updatePreferences: async (preferences: UpdatePreferences): Promise<UserPreferences> => {
    try {
      const response = await api.put<UserPreferences>('/user/preferences', preferences);
      return response.data;
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  },
};
