/**
 * API Types
 * TypeScript definitions for API responses and requests
 */

// Base API Response
export interface ApiResponse<T> {
  data: T;
  message?: string;
  status: number;
}

// Pagination
export interface PaginatedResponse<T> {
  total: number;
  page: number;
  page_size: number;
  results: T[];
}

// Error Response
export interface ApiError {
  detail: string;
  status?: number;
}

export type NSFWLevel = 'safe' | 'suggestive' | 'explicit';

// Auth Types
export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface RegistrationRequest {
  username: string;
  email: string;
  password: string;
}

export interface RegistrationResponse {
  detail: string;
  verification_token?: string | null;
  warning?: string;
  expires_at?: string;
}

export type LandingPage = 'dashboard' | 'search';

export interface User {
  id: number;
  username: string;
  email?: string;
  role: 'admin' | 'user';
  full_name?: string | null;
  avatar_url?: string | null;
  location?: string | null;
  language?: string;
  default_landing_page?: LandingPage;
  must_change_password?: boolean;
  password_last_changed?: string | null;
  created_at?: string | null;
  last_login?: string | null;
  is_active?: boolean;
}

export interface UserProfile extends User {}

export interface PasswordChangePayload {
  current_password: string;
  new_password: string;
}

export interface DeleteAccountPayload {
  password: string;
  confirm: boolean;
  reason?: string;
}

// Prompt Types
export interface Prompt {
  id: number;
  text: string;
  negative_prompt?: string;
  model?: string;
  parameters?: string;
  tags?: string;
  category?: string;
  art_style?: string; // Art style from catalog
  rating?: number;
  notes?: string;
  nsfw_level?: NSFWLevel;
  created_at: string;
  updated_at: string;
  created_by?: number | null; // NULL = preloaded, number = user_id
  image_path?: string | null;
  thumbnail_path?: string | null;
}

export interface CreatePromptRequest {
  text: string;
  negative_prompt?: string;
  model?: string;
  parameters?: string;
  tags?: string;
  category?: string;
  art_style?: string;
  rating?: number;
  notes?: string;
  nsfw_level?: NSFWLevel;
}

export interface UpdatePromptRequest extends CreatePromptRequest {
  id: number;
}

export interface PromptModelListResponse {
  models: string[];
}

// Search Types
export interface SearchFilters {
  text?: string;
  category?: string;
  model?: string;
  min_rating?: number;
  nsfw_level?: 'explicit' | 'suggestive' | 'safe';
  art_style?: string;
  number_of_people?: number;
  tags?: string[];
}

export interface ComplexSearchParams {
  text?: string;
  tags?: string; // Comma-separated tags
  nsfw_level?: string;
  number_of_people?: number;
  art_style?: string;
  model?: string;
  my_prompts?: boolean; // Filter to only show user's own prompts
  limit?: number;
  offset?: number;
}

// Stats Types
export interface Stats {
  total_prompts: number;
  total_art_styles?: number;
  total_tags?: number;
  nsfw_distribution: Record<string, number>;
  top_tags: Array<{ tag: string; count: number }>;
  top_art_styles: Array<{ style: string; count: number }>;
  categories_distribution?: Record<string, number>;
}

// Catalog Types
export interface CatalogPrompt {
  id: number;
  original_prompt: string;
  created_by?: number | null;
  nsfw_level?: string;
  art_style?: string;
  number_of_people?: number;
  tags?: string[];
  thumbnail_path?: string | null;
}

export interface ImageIngestionResult {
  filename: string;
  status: 'created' | 'failed' | 'skipped';
  detail: string;
  prompt_id?: number | null;
}

export interface BatchImageIngestionResponse {
  created: number;
  failed: number;
  results: ImageIngestionResult[];
}
