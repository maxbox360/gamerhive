"use client";

import { useEffect, useState, useCallback } from "react";
import GameCard from "@/components/GameCard";
import { usePaginatedFetch } from "@/hooks/usePaginatedFetch";
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

interface Genre {
  id: number;
  name: string;
  slug: string;
}

interface Platform {
  id: number;
  name: string;
  slug: string;
  abbreviation?: string;
}

interface Game {
  id: number;
  name: string;
  slug: string;
  summary?: string;
  cover_url?: string;
  genres: Genre[];
  platforms: Platform[];
}

export default function GamesPage() {
  // Available filter options
  const [genres, setGenres] = useState<Genre[]>([]);
  const [platforms, setPlatforms] = useState<Platform[]>([]);

  // Filter states
  const [genreFilter, setGenreFilter] = useState("");
  const [platformFilter, setPlatformFilter] = useState("");
  const [searchQuery, setSearchQuery] = useState("");
  const [debouncedSearch, setDebouncedSearch] = useState("");

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  // Fetch genres and platforms for dropdowns
  useEffect(() => {
    const fetchFilters = async () => {
      try {
        const [genresRes, platformsRes] = await Promise.all([
          fetch(`${apiUrl}/api/games/genres`),
          fetch(`${apiUrl}/api/games/platforms`),
        ]);

        if (genresRes.ok) {
          const genresData = await genresRes.json();
          setGenres(genresData.sort((a: Genre, b: Genre) => a.name.localeCompare(b.name)));
        }

        if (platformsRes.ok) {
          const platformsData = await platformsRes.json();
          setPlatforms(platformsData.sort((a: Platform, b: Platform) => a.name.localeCompare(b.name)));
        }
      } catch (err) {
        console.error("Failed to fetch filter options:", err);
      }
    };

    fetchFilters();
  }, [apiUrl]);

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
      return `${apiUrl}/api/games/games/?${params}`;
    },
    [apiUrl, genreFilter, platformFilter, debouncedSearch]
  );

  const { items: games, loading, error, pagination, setPage, refetch } =
    usePaginatedFetch<Game>(buildUrl, [genreFilter, platformFilter, debouncedSearch], {
      pageSize: 24,
    });

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

        {/* Results info */}
        {!loading && (
          <EuiText color="subdued" size="s">
            <p>
              Showing page {pagination.page} of {pagination.totalPages} ({(pagination.total ?? 0).toLocaleString()} games)
            </p>
          </EuiText>
        )}

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
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fill, minmax(180px, 1fr))",
              gap: "16px",
            }}
          >
            {games.map((game) => (
              <GameCard key={game.id} game={game} />
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


