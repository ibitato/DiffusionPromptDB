/**
 * SearchBar Component
 * 
 * @description Quick search bar component for the header navigation.
 * Provides instant search functionality with internationalization support.
 * Can either trigger a custom onSearch callback or navigate to the search page.
 * 
 * @component
 * @example
 * ```tsx
 * // With custom search handler
 * <SearchBar onSearch={(query) => handleSearch(query)} />
 * 
 * // Without handler (navigates to search page)
 * <SearchBar />
 * ```
 */

import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';

/**
 * Props for the SearchBar component
 * @interface SearchBarProps
 * @property {function} [onSearch] - Optional callback function triggered when search is submitted
 */
interface SearchBarProps {
  /** Optional callback function triggered when search is submitted */
  onSearch?: (query: string) => void;
}

/**
 * SearchBar functional component
 * @param {SearchBarProps} props - Component props
 * @returns {JSX.Element} Rendered search bar
 */
export const SearchBar = ({ onSearch }: SearchBarProps) => {
  const [query, setQuery] = useState('');
  const navigate = useNavigate();
  const { t } = useTranslation();

  /**
   * Handles form submission for search
   * @param {React.FormEvent} e - Form event
   * @returns {Promise<void>}
   * 
   * @description
   * - Prevents default form submission
   * - Validates query is not empty
   * - Either calls custom onSearch callback or navigates to search page
   * - Encodes query parameter for URL safety
   */
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      if (onSearch) {
        // Use custom search handler if provided
        onSearch(query);
      } else {
        // Default: Navigate to search page with query parameter
        navigate(`/search?text=${encodeURIComponent(query)}`);
      }
    }
  };

  return (
    <form onSubmit={handleSubmit} className="relative">
      <div className="relative">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder={t('search.searchBarPlaceholder')}
          className="w-64 px-4 py-2 pl-10 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-violet-600 focus:border-transparent"
        />
        <svg
          className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
          />
        </svg>
      </div>
    </form>
  );
};
