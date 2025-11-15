/**
 * Admin User Management Service
 */

import api, { handleApiError } from './api';
import { LandingPage } from '../types/api.types';

export interface AdminUser {
  id: number;
  username: string;
  email: string;
  role: 'admin' | 'user';
  is_active: boolean;
  created_at?: string;
  last_login?: string;
  default_landing_page: LandingPage;
}

export interface AdminUserCreatePayload {
  username: string;
  email: string;
  role: 'admin' | 'user';
  password: string;
  full_name?: string;
}

export interface AdminUserUpdatePayload {
  email?: string;
  role?: 'admin' | 'user';
  is_active?: boolean;
  full_name?: string;
  default_landing_page?: LandingPage;
}

export const adminUsersService = {
  async list(): Promise<AdminUser[]> {
    try {
      const response = await api.get<{ users: AdminUser[] }>('/admin/users');
      return response.data.users;
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  },

  async create(payload: AdminUserCreatePayload): Promise<AdminUser> {
    try {
      const response = await api.post<AdminUser>('/admin/users', payload);
      return response.data;
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  },

  async update(userId: number, payload: AdminUserUpdatePayload): Promise<AdminUser> {
    try {
      const response = await api.put<AdminUser>(`/admin/users/${userId}`, payload);
      return response.data;
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  },

  async resetPassword(userId: number, newPassword: string): Promise<void> {
    try {
      await api.put(`/admin/users/${userId}/password`, {
        new_password: newPassword,
      });
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  },

  async remove(userId: number): Promise<void> {
    try {
      await api.delete(`/admin/users/${userId}`);
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  },
};
