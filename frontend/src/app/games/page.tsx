"use client";

import { useEffect, useState, useCallback, useLayoutEffect, useRef } from "react";
import GameCard from "@/components/GameCard";
import { usePaginatedFetch } from "@/hooks/usePaginatedFetch";
import type { Game, Genre, Platform } from "@/types";
import {
  EuiFlexGroup,
  EuiFlexItem,
  EuiPagination,
  EuiLoadingSpinner,
  EuiCallOut,
  EuiButton,
  EuiSpacer,
  EuiText,
  EuiTitle,
  EuiPanel,
} from "@elastic/eui";

// Target item count the grid aims for per page; the actual page size is
// this rounded to a multiple of however many columns the browser's own
// auto-fill grid places (measured from real rendered cards below), so the
// last row is never partial.
const DEFAULT_PAGE_SIZE = 24;

export default function GamesPage() {
  const FILTER_CACHE_KEY = "games-filters-v1";
  // Available filter options
  const [genres, setGenres] = useState<Genre[]>([]);
  const [platforms, setPlatforms] = useState<Platform[]>([]);

  // Filter states
  const [genreFilter, setGenreFilter] = useState("");
  const [platformFilter, setPlatformFilter] = useState("");
  const [searchQuery, setSearchQuery] = useState("");
  const [debouncedSearch, setDebouncedSearch] = useState("");

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
  const apiBaseUrl = apiUrl.replace(/\/$/, "");

  // Read the column count the existing auto-fill grid actually rendered
  // (rather than re-deriving its width math ourselves, which drifted from
  // the browser's real layout) by grouping the rendered cards that share
  // the first card's offsetTop. Align pageSize to a multiple of that count.
  const gridRef = useRef<HTMLDivElement>(null);
  const [pageSize, setPageSize] = useState(DEFAULT_PAGE_SIZE);

  const alignPageSize = useCallback(() => {
    const grid = gridRef.current;
    if (!grid || grid.children.length === 0) return;

    const cards = Array.from(grid.children) as HTMLElement[];
    const firstRowTop = cards[0].offsetTop;
    const columns = cards.filter((card) => card.offsetTop === firstRowTop).length;
    const rows = Math.max(1, Math.round(DEFAULT_PAGE_SIZE / columns));
    const aligned = columns * rows;

    setPageSize((prev) => (prev === aligned ? prev : aligned));
  }, []);

  // Fetch genres and platforms for dropdowns
  useEffect(() => {
    const fetchFilters = async () => {
      const cached = window.sessionStorage.getItem(FILTER_CACHE_KEY);
      if (cached) {
        try {
          const parsed = JSON.parse(cached) as { genres: Genre[]; platforms: Platform[] };
          setGenres(parsed.genres);
          setPlatforms(parsed.platforms);
          return;
        } catch {
          window.sessionStorage.removeItem(FILTER_CACHE_KEY);
        }
      }

      try {
        const [genresRes, platformsRes] = await Promise.all([
          fetch(`${apiBaseUrl}/api/games/genres`, { credentials: "include" }),
          fetch(`${apiBaseUrl}/api/games/platforms`, { credentials: "include" }),
        ]);

        let sortedGenres: Genre[] = [];
        if (genresRes.ok) {
          const genresData = await genresRes.json();
          sortedGenres = genresData.sort((a: Genre, b: Genre) => a.name.localeCompare(b.name));
          setGenres(sortedGenres);
        }

        let sortedPlatforms: Platform[] = [];
        if (platformsRes.ok) {
          const platformsData = await platformsRes.json();
          sortedPlatforms = platformsData.sort((a: Platform, b: Platform) => a.name.localeCompare(b.name));
          setPlatforms(sortedPlatforms);
        }

        if (genresRes.ok && platformsRes.ok) {
          window.sessionStorage.setItem(
            FILTER_CACHE_KEY,
            JSON.stringify({
              genres: sortedGenres,
              platforms: sortedPlatforms,
            })
          );
        }
      } catch (err) {
        console.error("Failed to fetch filter options:", err);
      }
    };

    fetchFilters();
  }, [apiBaseUrl]);

  // Debounce search input
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearch(searchQuery);
    }, 300);
    return () => clearTimeout(timer);
  }, [searchQuery]);

  const buildUrl = useCallback(
    (page: number, pageSize: number) => {
      const params = new URLSearchParams();
      params.append("page", page.toString());
      params.append("page_size", pageSize.toString());
      if (genreFilter) params.append("genre", genreFilter);
      if (platformFilter) params.append("platform", platformFilter);
      if (debouncedSearch) params.append("search", debouncedSearch);
      return `${apiBaseUrl}/api/games/games/?${params}`;
    },
    [apiBaseUrl, genreFilter, platformFilter, debouncedSearch]
  );

  const { items: games, loading, error, pagination, setPage, refetch } =
    usePaginatedFetch<Game>(buildUrl, [genreFilter, platformFilter, debouncedSearch], {
      pageSize,
    });

  // Re-check column alignment once cards actually render, and again on any
  // viewport resize (grid may be unmounted during loading, in which case
  // alignPageSize no-ops and the next data load re-triggers this).
  useLayoutEffect(() => {
    alignPageSize();
  }, [games, alignPageSize]);

  useEffect(() => {
    window.addEventListener("resize", alignPageSize);
    return () => window.removeEventListener("resize", alignPageSize);
  }, [alignPageSize]);

  const clearFilters = () => {
    setGenreFilter("");
    setPlatformFilter("");
    setSearchQuery("");
  };

  const hasActiveFilters = genreFilter || platformFilter || searchQuery;

  // Build options for EuiSelect
  const genreOptions = [
    { value: "", text: "All Genres" },
    ...genres.map((g) => ({ value: g.name, text: g.name })),
  ];

  const platformOptions = [
    { value: "", text: "All Platforms" },
    ...platforms.map((p) => ({ value: p.name, text: p.name })),
  ];

  return (
    <div style={{ minHeight: "100vh", backgroundColor: "#262626" }}>
      {/* Page Header */}
      <EuiPanel paddingSize="l" borderRadius="none" style={{ backgroundColor: "#262626" }}>
        <div style={{ maxWidth: "1400px", margin: "0 auto" }}>
          <EuiTitle size="l">
            <h1 style={{ color: "#FFD700" }}>Games</h1>
          </EuiTitle>
          <EuiSpacer size="s" />
          <EuiText style={{ color: "#ccc" }}>
            <p>Discover and explore our collection of {(pagination.total ?? 0).toLocaleString()} games</p>
          </EuiText>
        </div>
      </EuiPanel>

      <EuiSpacer size="l" />

      {/* Filters */}
      <div style={{ maxWidth: "1400px", margin: "0 auto", padding: "0 16px" }}>
        <EuiFlexGroup gutterSize="m" wrap responsive>
          {/* Search */}
          <EuiFlexItem grow={2} style={{ minWidth: "200px" }}>
            {/* Use a native input search to avoid React 19 element.ref deprecation warnings
                caused by some third-party components accessing the React element.ref getter. */}
            <input
              type="search"
              placeholder="Search games..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              style={{ width: "100%", padding: "8px 12px", borderRadius: 4, border: "1px solid #333", background: "#262626", color: "#fff" }}
            />
          </EuiFlexItem>

          {/* Genre Dropdown (native to avoid React 19 .ref access in EUI) */}
          <EuiFlexItem grow={1} style={{ minWidth: "150px" }}>
            <select
              value={genreFilter}
              onChange={(e) => setGenreFilter(e.target.value)}
              style={{ width: "100%", padding: "8px 12px", borderRadius: 4, border: "1px solid #333", background: "#262626", color: "#fff" }}
            >
              {genreOptions.map((opt) => (
                <option key={opt.value || "all"} value={opt.value}>
                  {opt.text}
                </option>
              ))}
            </select>
          </EuiFlexItem>

          {/* Platform Dropdown (native to avoid React 19 .ref access in EUI) */}
          <EuiFlexItem grow={1} style={{ minWidth: "150px" }}>
            <select
              value={platformFilter}
              onChange={(e) => setPlatformFilter(e.target.value)}
              style={{ width: "100%", padding: "8px 12px", borderRadius: 4, border: "1px solid #333", background: "#262626", color: "#fff" }}
            >
              {platformOptions.map((opt) => (
                <option key={opt.value || "all"} value={opt.value}>
                  {opt.text}
                </option>
              ))}
            </select>
          </EuiFlexItem>

          {/* Clear Filters */}
          {hasActiveFilters && (
            <EuiFlexItem grow={false}>
              <EuiButton color="danger" onClick={clearFilters} size="m">
                Clear Filters
              </EuiButton>
            </EuiFlexItem>
          )}
        </EuiFlexGroup>

        <EuiSpacer size="m" />

        <EuiSpacer size="l" />

        {/* Loading State */}
        {loading && (
          <EuiFlexGroup justifyContent="center" alignItems="center" style={{ padding: "80px 0" }}>
            <EuiFlexItem grow={false}>
              <EuiLoadingSpinner size="xl" />
            </EuiFlexItem>
          </EuiFlexGroup>
        )}

        {/* Error State */}
        {error && (
          <>
            <EuiCallOut title="Error loading games" color="danger" iconType="error">
              <p>{error}</p>
              <EuiButton color="danger" onClick={refetch} size="s">
                Try again
              </EuiButton>
            </EuiCallOut>
            <EuiSpacer size="l" />
          </>
        )}

        {/* Games Grid */}
        {!loading && !error && (
          <div
            ref={gridRef}
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fill, minmax(180px, 1fr))",
              gap: "16px",
            }}
          >
            {games.map((game) => (
              <GameCard key={game.id} game={game} variant="default" />
            ))}
          </div>
        )}

        {/* Empty State */}
        {!loading && !error && games.length === 0 && (
          <EuiCallOut title="No games found" color="warning" iconType="search">
            <p>Try adjusting your search or filters</p>
          </EuiCallOut>
        )}

        <EuiSpacer size="xl" />

        {/* Pagination */}
        {!loading && !error && pagination.totalPages > 1 && (
          <EuiFlexGroup justifyContent="center">
            <EuiFlexItem grow={false}>
              <EuiPagination
                pageCount={pagination.totalPages}
                activePage={pagination.page - 1}
                onPageClick={(pageIndex) => setPage(pageIndex + 1)}
              />
            </EuiFlexItem>
          </EuiFlexGroup>
        )}

        <EuiSpacer size="xl" />
      </div>
    </div>
  );
}
