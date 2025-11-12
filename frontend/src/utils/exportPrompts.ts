/**
 * Export Prompts Utilities
 * Functions to export prompts to CSV and JSON
 */

import { Prompt } from '../types/api.types';

/**
 * Export prompts to JSON file
 */
export const exportToJSON = (prompts: Prompt[], filename: string = 'prompts.json') => {
  const dataStr = JSON.stringify(prompts, null, 2);
  const dataBlob = new Blob([dataStr], { type: 'application/json' });
  downloadFile(dataBlob, filename);
};

/**
 * Export prompts to CSV file
 */
export const exportToCSV = (prompts: Prompt[], filename: string = 'prompts.csv') => {
  // Define CSV headers
  const headers = [
    'ID',
    'Text',
    'Negative Prompt',
    'Model',
    'Category',
    'Tags',
    'Rating',
    'Notes',
    'Created At',
    'Updated At',
  ];

  // Convert prompts to CSV rows
  const rows = prompts.map((prompt) => [
    prompt.id,
    escapeCSVField(prompt.text),
    escapeCSVField(prompt.negative_prompt || ''),
    escapeCSVField(prompt.model || ''),
    escapeCSVField(prompt.category || ''),
    escapeCSVField(prompt.tags || ''),
    prompt.rating || '',
    escapeCSVField(prompt.notes || ''),
    prompt.created_at,
    prompt.updated_at,
  ]);

  // Combine headers and rows
  const csvContent = [headers.join(','), ...rows.map((row) => row.join(','))].join('\n');

  const dataBlob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  downloadFile(dataBlob, filename);
};

/**
 * Escape CSV field (handle commas, quotes, newlines)
 */
const escapeCSVField = (field: string): string => {
  if (!field) return '';

  // If field contains comma, quote, or newline, wrap in quotes and escape quotes
  if (field.includes(',') || field.includes('"') || field.includes('\n')) {
    return `"${field.replace(/"/g, '""')}"`;
  }

  return field;
};

/**
 * Download file helper
 */
const downloadFile = (blob: Blob, filename: string) => {
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(url);
};

/**
 * Get formatted filename with timestamp
 */
export const getExportFilename = (format: 'json' | 'csv'): string => {
  const now = new Date();
  const timestamp = now.toISOString().split('T')[0]; // YYYY-MM-DD
  return `prompts_export_${timestamp}.${format}`;
};
