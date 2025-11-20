import api, { handleApiError } from './api';
import {
  BatchImageIngestionResponse,
  ImageIngestionResult,
} from '../types/api.types';

export interface IngestionFilePayload {
  clientId: string;
  file: File;
  tags?: string;
  category?: string;
  artStyle?: string;
  rating?: number;
  notes?: string;
}

export interface AggregatedIngestionResponse
  extends BatchImageIngestionResponse {
  results: Array<ImageIngestionResult & { clientId: string }>;
}

export const ingestionService = {
  ingestImages: async (
    items: IngestionFilePayload[]
  ): Promise<AggregatedIngestionResponse> => {
    const aggregate: AggregatedIngestionResponse = {
      created: 0,
      failed: 0,
      results: [],
    };

    for (const item of items) {
      const formData = new FormData();
      formData.append('files', item.file);
      if (item.tags) formData.append('tags', item.tags);
      if (item.category) formData.append('category', item.category);
      if (item.artStyle) formData.append('art_style', item.artStyle);
      if (typeof item.rating === 'number') {
        formData.append('rating', item.rating.toString());
      }
      if (item.notes) formData.append('notes', item.notes);

      try {
        const response = await api.post<BatchImageIngestionResponse>(
          `/prompts/ingest`,
          formData,
          {
            headers: { 'Content-Type': 'multipart/form-data' },
          }
        );

        aggregate.created += response.data.created;
        aggregate.failed += response.data.failed;
        const fileResult: ImageIngestionResult =
          response.data.results[0] ?? {
            filename: item.file.name,
            status: 'failed',
            detail: 'Unknown result',
          };

        aggregate.results.push({
          ...fileResult,
          filename: fileResult.filename || item.file.name,
          clientId: item.clientId,
        });
      } catch (error) {
        aggregate.failed += 1;
        aggregate.results.push({
          filename: item.file.name,
          status: 'failed',
          detail: handleApiError(error),
          clientId: item.clientId,
        });
      }
    }

    return aggregate;
  },
};
