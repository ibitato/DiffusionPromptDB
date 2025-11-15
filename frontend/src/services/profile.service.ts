/**
 * Profile Service
 * Handles user profile CRUD, password updates, and account deletion.
 */

import api, { handleApiError } from './api';
import {
  DeleteAccountPayload,
  PasswordChangePayload,
  UserProfile,
  LandingPage,
} from '../types/api.types';

interface UpdateProfilePayload {
  full_name?: string;
  avatar_url?: string;
  location?: string;
  language?: string;
}

interface DefaultLandingPayload {
  default_landing_page: LandingPage;
}

export const profileService = {
  async getProfile(): Promise<UserProfile> {
    try {
      const response = await api.get<UserProfile>('/user/profile');
      return response.data;
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  },

  async updateProfile(payload: UpdateProfilePayload): Promise<UserProfile> {
    try {
      const response = await api.put<UserProfile>('/user/profile', payload);
      return response.data;
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  },

  async updatePassword(payload: PasswordChangePayload): Promise<void> {
    try {
      await api.put('/user/profile/password', payload);
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  },

  async updateDefaultLanding(page: LandingPage): Promise<UserProfile> {
    try {
      const response = await api.put<UserProfile>('/user/profile/default-page', {
        default_landing_page: page,
      } as DefaultLandingPayload);
      return response.data;
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  },

  async deleteAccount(payload: DeleteAccountPayload): Promise<void> {
    try {
      await api.delete('/user/account', { data: payload });
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  },
};
