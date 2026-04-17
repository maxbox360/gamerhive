"use client";

import { PaginationProps } from "@/types/pagination";

export default function Pagination({
  page,
  totalPages,
  onPageChange,
  disabled = false,
}: PaginationProps) {
  if (totalPages <= 1) return null;

  return (
    <div className="flex justify-center items-center gap-2 sm:gap-4 mt-8 pb-8 flex-wrap">
      {/* First Page */}
      <button
        onClick={() => onPageChange(1)}
        disabled={page === 1 || disabled}
        className="px-3 py-2 bg-neutral-800 border border-neutral-700 rounded-lg text-white disabled:opacity-50 disabled:cursor-not-allowed hover:border-amber-400 transition-colors text-sm sm:text-base"
        aria-label="Go to first page"
      >
        First
      </button>

      {/* Previous Page */}
      <button
        onClick={() => onPageChange(Math.max(1, page - 1))}
        disabled={page === 1 || disabled}
        className="px-3 sm:px-4 py-2 bg-neutral-800 border border-neutral-700 rounded-lg text-white disabled:opacity-50 disabled:cursor-not-allowed hover:border-amber-400 transition-colors text-sm sm:text-base"
        aria-label="Go to previous page"
      >
        ← Prev
      </button>

      {/* Page Input */}
      <div className="flex items-center gap-2">
        <input
          type="number"
          min={1}
          max={totalPages}
          value={page}
          onChange={(e) => {
            const val = parseInt(e.target.value);
            if (val >= 1 && val <= totalPages) {
              onPageChange(val);
            }
          }}
          disabled={disabled}
          className="w-14 sm:w-16 px-2 py-2 bg-neutral-800 border border-neutral-700 rounded-lg text-white text-center focus:outline-none focus:border-amber-400 disabled:opacity-50 text-sm sm:text-base"
          aria-label="Current page"
        />
        <span className="text-neutral-400 text-sm sm:text-base">
          of {totalPages.toLocaleString()}
        </span>
      </div>

      {/* Next Page */}
      <button
        onClick={() => onPageChange(Math.min(totalPages, page + 1))}
        disabled={page === totalPages || disabled}
        className="px-3 sm:px-4 py-2 bg-neutral-800 border border-neutral-700 rounded-lg text-white disabled:opacity-50 disabled:cursor-not-allowed hover:border-amber-400 transition-colors text-sm sm:text-base"
        aria-label="Go to next page"
      >
        Next →
      </button>

      {/* Last Page */}
      <button
        onClick={() => onPageChange(totalPages)}
        disabled={page === totalPages || disabled}
        className="px-3 py-2 bg-neutral-800 border border-neutral-700 rounded-lg text-white disabled:opacity-50 disabled:cursor-not-allowed hover:border-amber-400 transition-colors text-sm sm:text-base"
        aria-label="Go to last page"
      >
        Last
      </button>
    </div>
  );
}

