import api, { handleApiError } from './api';
import { BatchImageIngestionResponse } from '../types/api.types';

export interface IngestionPayload {
  files: File[];
  tags?: string;
  category?: string;
  artStyle?: string;
  rating?: number;
  notes?: string;
}

export const ingestionService = {
  ingestImages: async ({
    files,
    tags,
    category,
    artStyle,
    rating,
    notes,
  }: IngestionPayload): Promise<BatchImageIngestionResponse> => {
    try {
      const formData = new FormData();
      files.forEach((file) => formData.append('files', file));
      if (tags) formData.append('tags', tags);
      if (category) formData.append('category', category);
      if (artStyle) formData.append('art_style', artStyle);
      if (typeof rating === 'number') formData.append('rating', rating.toString());
      if (notes) formData.append('notes', notes);

      const response = await api.post<BatchImageIngestionResponse>(
        `/prompts/ingest`,
        formData,
        {
          headers: { 'Content-Type': 'multipart/form-data' },
        }
      );
      return response.data;
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  },
};
