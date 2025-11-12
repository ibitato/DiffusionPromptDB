/**
 * Search Service
 * Handles advanced search operations
 */

import api, { handleApiError } from './api';
import { ComplexSearchParams, CatalogPrompt } from '../types/api.types';

export const searchService = {
  /**
   * Complex search with multiple filters
   */
  complexSearch: async (params: ComplexSearchParams): Promise<{ total: number; results: CatalogPrompt[] }> => {
    try {
      const searchParams = new URLSearchParams();

      if (params.text) searchParams.append('text', params.text);
      if (params.nsfw_level) searchParams.append('nsfw_level', params.nsfw_level);
      if (params.number_of_people !== undefined) {
        searchParams.append('number_of_people', params.number_of_people.toString());
      }
      if (params.art_style) searchParams.append('art_style', params.art_style);
      if (params.limit) searchParams.append('limit', params.limit.toString());
      if (params.offset) searchParams.append('offset', params.offset.toString());

      const response = await api.get<{ total: number; results: CatalogPrompt[] }>(
        `/search/complex?${searchParams.toString()}`
      );

      return response.data; // Return full response with total and results
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  },

  /**
   * Search by NSFW level
   */
  searchByNSFW: async (level: string, limit: number = 20): Promise<CatalogPrompt[]> => {
    try {
      const response = await api.get<{ total: number; results: CatalogPrompt[] }>(
        `/catalog/search/nsfw/${level}?limit=${limit}`
      );
      return response.data.results;
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  },

  /**
   * Search by art style
   */
  searchByStyle: async (style: string, limit: number = 20): Promise<CatalogPrompt[]> => {
    try {
      const response = await api.get<{ total: number; results: CatalogPrompt[] }>(
        `/catalog/search/style/${style}?limit=${limit}`
      );
      return response.data.results;
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  },

  /**
   * Search by tag with pagination
   */
  searchByTag: async (tag: string, limit: number = 20, offset: number = 0): Promise<{ total: number; results: CatalogPrompt[] }> => {
    try {
      const response = await api.get<{ total: number; results: CatalogPrompt[] }>(
        `/search/tags/${tag}?limit=${limit}&offset=${offset}`
      );
      return response.data; // Return full response with total and results
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  },
};
