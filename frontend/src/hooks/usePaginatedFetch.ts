import { useState, useEffect, useCallback } from "react";
import { PaginatedResponse, PaginationState } from "@/types/pagination";

interface UsePaginatedFetchOptions {
  pageSize?: number;
  initialPage?: number;
}

interface UsePaginatedFetchResult<T> {
  items: T[];
  loading: boolean;
  error: string | null;
  pagination: PaginationState;
  setPage: (page: number) => void;
  refetch: () => void;
}

/**
 * Generic hook for fetching paginated data
 * 
 * @param buildUrl - Function that builds the API URL with current page and filters
 * @param dependencies - Array of dependencies that should trigger a refetch (filters, etc.)
 * @param options - Optional configuration (pageSize, initialPage)
 * 
 * @example
 * const { items, loading, pagination, setPage } = usePaginatedFetch<Game>(
 *   (page, pageSize) => `${API_URL}/games/?page=${page}&page_size=${pageSize}&genre=${genre}`,
 *   [genre, platform],
 *   { pageSize: 24 }
 * );
 */
export function usePaginatedFetch<T>(
  buildUrl: (page: number, pageSize: number) => string,
  dependencies: any[] = [],
  options: UsePaginatedFetchOptions = {}
): UsePaginatedFetchResult<T> {
  const { pageSize = 24, initialPage = 1 } = options;

  const [items, setItems] = useState<T[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(initialPage);
  const [totalPages, setTotalPages] = useState(1);
  const [total, setTotal] = useState(0);

  // Reset to page 1 when dependencies change
  useEffect(() => {
    setPage(1);
  }, dependencies);

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const url = buildUrl(page, pageSize);
      const response = await fetch(url);

      if (!response.ok) {
        throw new Error(`Failed to fetch data: ${response.status}`);
      }

      const data: PaginatedResponse<T> = await response.json();
      setItems(data.items);
      setTotalPages(data.total_pages);
      setTotal(data.total);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
      setItems([]);
    } finally {
      setLoading(false);
    }
  }, [page, pageSize, buildUrl, ...dependencies]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return {
    items,
    loading,
    error,
    pagination: {
      page,
      totalPages,
      total,
      pageSize,
    },
    setPage,
    refetch: fetchData,
  };
}
