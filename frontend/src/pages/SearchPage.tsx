/**
 * Advanced Search Page
 * Search prompts with multiple filters
 */

import { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { Header } from '../components/layout/Header';
import { Loading } from '../components/ui/Loading';
import { useToast } from '../components/ui/Toast';
import { PromptDetailModal } from '../components/prompts/PromptDetailModal';
import { searchService } from '../services/search.service';
import { CatalogPrompt, Prompt } from '../types/api.types';

export const SearchPage = () => {
  const [searchParams] = useSearchParams();
  const [results, setResults] = useState<CatalogPrompt[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalResults, setTotalResults] = useState(0);
  const [allResultsCount, setAllResultsCount] = useState(0);
  const pageSize = 20;

  // Filters state
  const [nsfwLevel, setNsfwLevel] = useState('');
  const [artStyle, setArtStyle] = useState('');
  const [numberOfPeople, setNumberOfPeople] = useState('');
  const [searchText, setSearchText] = useState('');
  const [searchTag, setSearchTag] = useState('');
  
  // Detail modal
  const [selectedPrompt, setSelectedPrompt] = useState<Prompt | null>(null);
  const [isDetailModalOpen, setIsDetailModalOpen] = useState(false);

  const toast = useToast();

  // Available options
  const nsfwLevels = ['explicit', 'suggestive', 'safe'];
  const artStyles = ['anime', 'photorealistic', 'cartoon', 'digital art', '3d', 'pixel art'];

  useEffect(() => {
    // Check for text search from SearchBar
    const textParam = searchParams.get('text');
    if (textParam) {
      setSearchText(textParam);
    }
    
    // Check for tag search (legacy)
    const tag = searchParams.get('tag');
    if (tag && !textParam) {
      performTagSearch(tag);
    }
  }, [searchParams]);
  
  // Auto-search when searchText changes from URL parameter
  useEffect(() => {
    if (searchText && !hasSearched) {
      performSearch(1);
    }
  }, [searchText]);
  
  const performTagSearch = async (tag: string) => {
    setIsLoading(true);
    setHasSearched(true);
    
    try {
      const response = await searchService.searchByTag(tag, 20, 0);
      setResults(response.results);
      setAllResultsCount(response.total);
      
      if (response.results.length === 0) {
        toast.info(`No se encontraron prompts con el tag "${tag}"`);
      } else {
        toast.success(`Encontrados ${response.total} prompts con el tag "${tag}"`);
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Error en la búsqueda';
      toast.error(message);
      setResults([]);
    } finally {
      setIsLoading(false);
    }
  };

  const performSearch = async (page: number = 1) => {
    setIsLoading(true);
    setHasSearched(true);
    setCurrentPage(page);

    try {
      // If searching by tag only, use tag search endpoint
      if (searchTag && !searchText && !nsfwLevel && !artStyle && !numberOfPeople) {
        const response = await searchService.searchByTag(
          searchTag, 
          pageSize, 
          (page - 1) * pageSize
        );
        
        setResults(response.results);
        setTotalResults(response.results.length);
        setAllResultsCount(response.total);
        
        if (response.total === 0) {
          toast.info(`No se encontraron prompts con el tag "${searchTag}"`);
        } else {
          toast.success(`Encontrados ${response.total} prompts totales`);
        }
      } else {
        // Complex search with filters
        const params: any = {};

        // Text search in prompt content
        if (searchText) params.text = searchText;
        
        // Other filters
        if (nsfwLevel) params.nsfw_level = nsfwLevel;
        if (artStyle) params.art_style = artStyle;
        if (numberOfPeople) params.number_of_people = parseInt(numberOfPeople);
        
        // Pagination
        params.limit = pageSize;
        params.offset = (page - 1) * pageSize;

        const response = await searchService.complexSearch(params);
        setResults(response.results);
        setTotalResults(response.results.length);
        setAllResultsCount(response.total);

        if (response.results.length === 0) {
          toast.info('No se encontraron resultados');
        } else {
          toast.success(`Encontrados ${response.total} resultados totales`);
        }
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Error en la búsqueda';
      toast.error(message);
      setResults([]);
      setAllResultsCount(0);
    } finally {
      setIsLoading(false);
    }
  };

  const clearFilters = () => {
    setNsfwLevel('');
    setArtStyle('');
    setNumberOfPeople('');
    setSearchText('');
    setSearchTag('');
    setResults([]);
    setHasSearched(false);
    setCurrentPage(1);
  };

  const activeFiltersCount = [nsfwLevel, artStyle, numberOfPeople, searchText, searchTag].filter(Boolean).length;

  return (
    <div className="min-h-screen bg-slate-900">
      <Header />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Page Header */}
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-white mb-2">Búsqueda Avanzada</h2>
          <p className="text-gray-400">Filtra prompts por múltiples criterios</p>
        </div>

        {/* Filters Section */}
        <div className="bg-slate-800 rounded-lg p-6 border border-slate-700 mb-8">
          {/* Main Filters */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
            {/* NSFW Level Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">NSFW Level</label>
              <select
                value={nsfwLevel}
                onChange={(e) => setNsfwLevel(e.target.value)}
                className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-violet-600"
              >
                <option value="">Todos</option>
                {nsfwLevels.map((level) => (
                  <option key={level} value={level}>
                    {level.charAt(0).toUpperCase() + level.slice(1)}
                  </option>
                ))}
              </select>
            </div>

            {/* Art Style Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">Art Style</label>
              <select
                value={artStyle}
                onChange={(e) => setArtStyle(e.target.value)}
                className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-violet-600"
              >
                <option value="">Todos</option>
                {artStyles.map((style) => (
                  <option key={style} value={style}>
                    {style.charAt(0).toUpperCase() + style.slice(1)}
                  </option>
                ))}
              </select>
            </div>

            {/* Number of People Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Número de Personas
              </label>
              <input
                type="number"
                min="0"
                max="10"
                value={numberOfPeople}
                onChange={(e) => setNumberOfPeople(e.target.value)}
                placeholder="Ej: 1, 2, 3..."
                className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-violet-600"
              />
            </div>
          </div>
          
          {/* Text Search */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Buscar en Texto del Prompt
            </label>
            <input
              type="text"
              value={searchText}
              onChange={(e) => setSearchText(e.target.value)}
              placeholder="Buscar palabras en el prompt..."
              className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-violet-600"
            />
            <p className="text-xs text-gray-500 mt-1">
              Busca por cualquier palabra o frase en el texto del prompt
            </p>
          </div>
          
          {/* Tag Search */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Buscar por Tag
            </label>
            <input
              type="text"
              value={searchTag}
              onChange={(e) => setSearchTag(e.target.value)}
              placeholder="Buscar por tag (ej: 1girl, anime, etc)..."
              className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-violet-600"
            />
            <p className="text-xs text-gray-500 mt-1">
              Busca prompts que contengan un tag específico
            </p>
          </div>

          {/* Action Buttons */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <button
                onClick={() => performSearch(1)}
                disabled={isLoading || activeFiltersCount === 0}
                className="px-6 py-2 bg-violet-600 hover:bg-violet-700 disabled:bg-slate-600 disabled:cursor-not-allowed text-white rounded-lg font-medium transition-colors flex items-center gap-2"
              >
                {isLoading && <Loading size="sm" />}
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                  />
                </svg>
                Buscar
              </button>

              {activeFiltersCount > 0 && (
                <button
                  onClick={clearFilters}
                  className="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg font-medium transition-colors"
                >
                  Limpiar Filtros
                </button>
              )}
            </div>

            {activeFiltersCount > 0 && (
              <span className="text-sm text-gray-400">
                {activeFiltersCount} filtro{activeFiltersCount !== 1 ? 's' : ''} activo
                {activeFiltersCount !== 1 ? 's' : ''}
              </span>
            )}
          </div>

          {/* Active Filters Chips */}
          {activeFiltersCount > 0 && (
            <div className="flex flex-wrap gap-2 mt-4 pt-4 border-t border-slate-700">
              {nsfwLevel && (
                <span className="px-3 py-1 bg-orange-600/20 text-orange-400 rounded-full text-sm flex items-center gap-2">
                  NSFW: {nsfwLevel}
                  <button onClick={() => setNsfwLevel('')} className="hover:text-orange-300">
                    ×
                  </button>
                </span>
              )}
              {artStyle && (
                <span className="px-3 py-1 bg-blue-600/20 text-blue-400 rounded-full text-sm flex items-center gap-2">
                  Style: {artStyle}
                  <button onClick={() => setArtStyle('')} className="hover:text-blue-300">
                    ×
                  </button>
                </span>
              )}
              {numberOfPeople && (
                <span className="px-3 py-1 bg-green-600/20 text-green-400 rounded-full text-sm flex items-center gap-2">
                  People: {numberOfPeople}
                  <button onClick={() => setNumberOfPeople('')} className="hover:text-green-300">
                    ×
                  </button>
                </span>
              )}
              {searchText && (
                <span className="px-3 py-1 bg-violet-600/20 text-violet-400 rounded-full text-sm flex items-center gap-2">
                  Texto: "{searchText}"
                  <button onClick={() => setSearchText('')} className="hover:text-violet-300">
                    ×
                  </button>
                </span>
              )}
              {searchTag && (
                <span className="px-3 py-1 bg-indigo-600/20 text-indigo-400 rounded-full text-sm flex items-center gap-2">
                  Tag: "{searchTag}"
                  <button onClick={() => setSearchTag('')} className="hover:text-indigo-300">
                    ×
                  </button>
                </span>
              )}
            </div>
          )}
        </div>

        {/* Results Section */}
        {isLoading ? (
          <div className="flex items-center justify-center py-12">
            <Loading size="lg" text="Buscando..." />
          </div>
        ) : hasSearched ? (
          <>
            {/* Results Header */}
            <div className="mb-4 flex items-center justify-between">
              <h3 className="text-xl font-semibold text-white">
                {results.length > 0 ? (
                  <>
                    {allResultsCount > 0 && <span className="text-violet-400">{allResultsCount} resultados totales</span>}
                    {allResultsCount > 0 && ' - '}
                    Página {currentPage}
                  </>
                ) : 'Sin Resultados'}
              </h3>
              {results.length > 0 && (
                <span className="text-sm text-gray-400">
                  Mostrando {((currentPage - 1) * pageSize) + 1} - {Math.min(currentPage * pageSize, ((currentPage - 1) * pageSize) + results.length)} de {allResultsCount}
                </span>
              )}
            </div>

            {/* Results Grid */}
            {results.length > 0 ? (
              <>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                {results.map((result, index) => (
                  <div
                    key={result.id || index}
                    onClick={() => {
                      const promptForModal: Prompt = {
                        id: result.id,
                        text: result.original_prompt,
                        created_at: new Date().toISOString(),
                        updated_at: new Date().toISOString(),
                      } as Prompt;
                      setSelectedPrompt(promptForModal);
                      setIsDetailModalOpen(true);
                    }}
                    className="bg-slate-800 rounded-lg p-6 border border-slate-700 hover:border-violet-600 hover:shadow-lg transition-all cursor-pointer transform hover:scale-[1.02]"
                  >
                    <div className="mb-4">
                      <div className="flex items-center gap-2 mb-2">
                        <h4 className="text-lg font-semibold text-white">Prompt #{result.id}</h4>
                        {result.nsfw_level && (
                          <span className="px-2 py-1 bg-orange-600/20 text-orange-400 text-xs rounded-full">
                            {result.nsfw_level}
                          </span>
                        )}
                        {result.art_style && (
                          <span className="px-2 py-1 bg-blue-600/20 text-blue-400 text-xs rounded-full">
                            {result.art_style}
                          </span>
                        )}
                      </div>
                      <p className="text-gray-300 text-sm leading-relaxed">
                        {result.original_prompt.substring(0, 200)}
                        {result.original_prompt.length > 200 && '...'}
                      </p>
                    </div>

                    {result.tags && result.tags.length > 0 && (
                      <div className="flex flex-wrap gap-2">
                        {result.tags.slice(0, 5).map((tag, i) => (
                          <span
                            key={i}
                            className="px-2 py-1 bg-slate-700 text-gray-300 text-xs rounded"
                          >
                            {tag}
                          </span>
                        ))}
                        {result.tags.length > 5 && (
                          <span className="px-2 py-1 bg-slate-700 text-gray-400 text-xs rounded">
                            +{result.tags.length - 5} más
                          </span>
                        )}
                      </div>
                    )}
                  </div>
                ))}
              </div>
              
              {/* Pagination */}
              {results.length === pageSize && (
                <div className="flex items-center justify-center gap-2">
                  <button
                    onClick={() => performSearch(currentPage - 1)}
                    disabled={currentPage === 1 || isLoading}
                    className="px-4 py-2 bg-slate-800 hover:bg-slate-700 disabled:bg-slate-800 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-lg transition-colors"
                  >
                    Anterior
                  </button>
                  
                  <span className="text-gray-400 px-4">Página {currentPage}</span>
                  
                  <button
                    onClick={() => performSearch(currentPage + 1)}
                    disabled={results.length < pageSize || isLoading}
                    className="px-4 py-2 bg-slate-800 hover:bg-slate-700 disabled:bg-slate-800 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-lg transition-colors"
                  >
                    Siguiente
                  </button>
                </div>
              )}
              </>
            ) : (
              <div className="text-center py-12">
                <svg
                  className="w-16 h-16 text-gray-600 mx-auto mb-4"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
                <p className="text-gray-400 text-lg">
                  No se encontraron resultados con los filtros seleccionados
                </p>
                <p className="text-gray-500 text-sm mt-2">
                  Intenta con diferentes criterios de búsqueda
                </p>
              </div>
            )}
          </>
        ) : (
          <div className="text-center py-12">
            <svg
              className="w-16 h-16 text-gray-600 mx-auto mb-4"
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
            <p className="text-gray-400 text-lg">Selecciona filtros y haz click en Buscar</p>
          </div>
        )}
      </main>
      
      {/* Detail Modal */}
      {selectedPrompt && (
        <PromptDetailModal
          isOpen={isDetailModalOpen}
          onClose={() => {
            setIsDetailModalOpen(false);
            setSelectedPrompt(null);
          }}
          prompt={selectedPrompt}
          onEdit={() => {}}
          onDelete={() => {}}
        />
      )}
    </div>
  );
};
