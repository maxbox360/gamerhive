// Generic paginated response type - works for any entity
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

// Pagination state used by components
export interface PaginationState {
  page: number;
  totalPages: number;
  total: number;
  pageSize: number;
}

// Props for pagination controls
export interface PaginationProps {
  page: number;
  totalPages: number;
  onPageChange: (page: number) => void;
  disabled?: boolean;
}
