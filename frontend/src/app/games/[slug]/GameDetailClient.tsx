"use client";

import { useState } from "react";
import Link from "next/link";
import {
  EuiFlexGroup,
  EuiFlexItem,
  EuiPanel,
  EuiTitle,
  EuiText,
  EuiButton,
  EuiSpacer,
  EuiButtonIcon,
  EuiBadge,
  EuiCallOut,
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

export default function GameDetailClient({
  initialGame,
  lastFetchedUrl,
  lastStatus,
  errorMessage,
}: {
  initialGame?: Game | null;
  lastFetchedUrl?: string | null;
  lastStatus?: number | null;
  errorMessage?: string | null;
}) {
  const [game] = useState<Game | null>(initialGame ?? null);
  const [serverError] = useState<string | null>(errorMessage ?? null);
  const [showDebugBanner, setShowDebugBanner] = useState(true);

  // User action state (UI-only for now)
  const [liked, setLiked] = useState(false);
  const [wouldPlay, setWouldPlay] = useState(false);
  const [finished, setFinished] = useState(false);
  const [userRating, setUserRating] = useState<number | null>(null);

  // Rating distribution (0.5..5.0) — prefer backend-provided field, otherwise a placeholder
  const ratingDistribution: Record<string, number> = (game as any)?.rating_distribution || {
    "5.0": 40,
    "4.5": 10,
    "4.0": 25,
    "3.5": 8,
    "3.0": 6,
    "2.5": 4,
    "2.0": 3,
    "1.5": 2,
    "1.0": 1,
    "0.5": 1,
  };

  const totalRatings = Object.values(ratingDistribution).reduce((a, b) => a + b, 0) || 1;

  const formatPlatformList = (platforms: Platform[] | undefined) => {
    if (!platforms || platforms.length === 0) return "—";
    return platforms.map((p) => p.abbreviation || p.name).join(" • ");
  };

  // Star rating UI component (supports half-star precision)
  function StarRating({ value, onChange }: { value: number | null; onChange: (v: number) => void }) {
    const [hoverValue, setHoverValue] = useState<number | null>(null);

    const activeValue = hoverValue ?? value ?? 0;

    const handleMove = (e: React.MouseEvent, starIndex: number) => {
      const el = e.currentTarget as HTMLElement;
      const rect = el.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const pct = x / rect.width;
      const newVal = pct <= 0.5 ? starIndex - 0.5 : starIndex;
      setHoverValue(newVal);
    };

    const handleLeave = () => setHoverValue(null);

    const handleClick = (v: number) => onChange(v);

    const starPath = "M12 .587l3.668 7.431 8.2 1.192-5.934 5.787 1.402 8.171L12 18.896 4.664 23.168l1.402-8.171L.132 9.21l8.2-1.192z";

    return (
      <div style={{ display: "flex", gap: 6, alignItems: "center" }} onMouseLeave={handleLeave}>
        {[1, 2, 3, 4, 5].map((i) => {
          const fill = Math.max(0, Math.min(1, (activeValue - (i - 1))));
          const pct = Math.round(fill * 100);
          const clipId = `clip-star-${(initialGame as Game).id}-${i}`;
          return (
            <div
              key={i}
              onMouseMove={(e) => handleMove(e, i)}
              onClick={() => handleClick(hoverValue ?? i)}
              style={{ width: 28, height: 28, cursor: "pointer", display: "inline-block" }}
              aria-label={`Rate ${i} star`}
              role="button"
              tabIndex={0}
            >
              <svg viewBox="0 0 24 24" width={28} height={28}>
                <defs>
                  <clipPath id={clipId}>
                    <rect x="0" y="0" width={`${pct}%`} height="100%" />
                  </clipPath>
                </defs>
                {/* background star */}
                <path d={starPath} fill="#333" />
                {/* filled portion */}
                <g clipPath={`url(#${clipId})`}>
                  <path d={starPath} fill="#FFD700" />
                </g>
              </svg>
            </div>
          );
        })}
      </div>
    );
  }

  if (!game) {
    return (
      <>
        {serverError ? (
          <EuiPanel paddingSize="l">
            <EuiCallOut title="Unable to load game" color="warning" iconType="alert">
              <p>{serverError}</p>
              <div style={{ marginTop: 8 }}>
                <EuiButton onClick={() => location.reload()}>Try again</EuiButton>
              </div>
            </EuiCallOut>
          </EuiPanel>
        ) : (
          <EuiPanel paddingSize="l">
            <EuiText>No game data provided.</EuiText>
          </EuiPanel>
        )}
      </>
    );
  }
  return (
    <div style={{ minHeight: "100vh", backgroundColor: "#111" }}>
      <div style={{ maxWidth: "1200px", margin: "0 auto", padding: "16px" }}>
        {/* Top header */}
        <EuiPanel paddingSize="l" style={{ backgroundColor: "#1b1b1b" }}>
          <EuiFlexGroup alignItems="center" gutterSize="m">
            <EuiFlexItem grow={false} style={{ minWidth: 0 }}>
              <Link href="/games">
                <EuiButton color="primary">← Back to games</EuiButton>
              </Link>
            </EuiFlexItem>
            <EuiFlexItem>
              <EuiTitle size="m">
                <h2 style={{ color: "#FFD700", margin: 0 }}>{game.name}</h2>
              </EuiTitle>
              <EuiText color="subdued">
                <p style={{ margin: 0 }}>{formatPlatformList(game.platforms)}</p>
              </EuiText>
            </EuiFlexItem>
          </EuiFlexGroup>
        </EuiPanel>

        <EuiSpacer size="l" />

        {/* Three-column layout */}
        <div style={{ display: "grid", gridTemplateColumns: "300px 1fr 260px", gap: 16 }}>
          {/* Left column */}
          <div>
            <div>
              <EuiPanel paddingSize="s" style={{ backgroundColor: "#161616" }}>
                <div style={{ borderRadius: 6, overflow: "hidden", background: "#0f0f0f" }}>
                  {game.cover_url ? (
                    // eslint-disable-next-line @next/next/no-img-element
                    <img src={game.cover_url} alt={game.name} style={{ width: "100%", height: "auto", display: "block" }} />
                  ) : (
                    <div style={{ width: "100%", height: 420, display: "flex", alignItems: "center", justifyContent: "center", background: "#0b0b0b" }}>
                      <EuiText color="subdued">No cover available</EuiText>
                    </div>
                  )}
                </div>
              </EuiPanel>

              {/* Icon row directly under poster: same visual width as poster panel */}
              {/* moved further down so it doesn't overlap the poster */}
              <div style={{ display: "flex", justifyContent: "center", marginTop: 24 }}>
                <div
                  style={{
                    width: 300,
                    background: "#161616",
                    padding: "8px 12px",
                    borderRadius: 12,
                    boxShadow: "0 6px 20px rgba(0,0,0,0.6)",
                    display: "flex",
                    gap: 16,
                    alignItems: "center",
                    justifyContent: "space-around",
                    boxSizing: "border-box",
                  }}
                >
                  <div style={{ display: "flex", flexDirection: "column", alignItems: "center" }} title="Players">
                    <EuiButtonIcon iconType="users" color="text" onClick={() => {}} aria-label="Players" />
                    <div style={{ color: "#ddd", fontSize: 12, marginTop: 4 }}>{(game as any)?.user_stats?.players ?? "—"}</div>
                  </div>

                  <div style={{ display: "flex", flexDirection: "column", alignItems: "center" }} title="Lists">
                    <EuiButtonIcon iconType="list" color="text" onClick={() => {}} aria-label="Lists" />
                    <div style={{ color: "#ddd", fontSize: 12, marginTop: 4 }}>{(game as any)?.user_stats?.lists ?? "—"}</div>
                  </div>

                  <div style={{ display: "flex", flexDirection: "column", alignItems: "center" }} title="Likes">
                    <EuiButtonIcon iconType="heart" color="text" onClick={() => {}} aria-label="Likes" />
                    <div style={{ color: "#ddd", fontSize: 12, marginTop: 4 }}>{(game as any)?.user_stats?.likes ?? "—"}</div>
                  </div>
                </div>
              </div>
            </div>

            <EuiSpacer />

            <EuiPanel paddingSize="s">
              <EuiTitle size="xs">
                <h4 style={{ margin: 0 }}>Where to play / Media</h4>
              </EuiTitle>
              <EuiSpacer size="s" />
              <EuiText size="s" color="subdued">
                <p style={{ margin: 0 }}>{formatPlatformList(game.platforms)}</p>
              </EuiText>
              <EuiSpacer />
              {(game as any)?.trailer_url && (
                <EuiButton href={(game as any).trailer_url} target="_blank" iconType="playFilled">
                  Watch trailer
                </EuiButton>
              )}
            </EuiPanel>
          </div>

          {/* Middle column */}
          <div>
            <EuiPanel paddingSize="m">
              <EuiTitle size="l">
                <h1 style={{ margin: 0 }}>{game.name}</h1>
              </EuiTitle>
              <EuiText color="subdued">
                <p style={{ marginTop: 8 }}>
                  {(game as any).release_year ? `${(game as any).release_year}` : "Unknown year"}
                  {" • "}
                  {(game as any).director ? `Directed by ${(game as any).director}` : "Director unknown"}
                </p>
              </EuiText>

              <EuiSpacer />

              <EuiText style={{ whiteSpace: "pre-wrap", color: "#ddd" }}>
                <p>{game.summary ?? "No description available."}</p>
              </EuiText>

              <EuiSpacer />

              {game.genres && game.genres.length > 0 && (
                <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
                  {game.genres.map((g) => (
                    <EuiBadge key={g.id} color="hollow">
                      {g.name}
                    </EuiBadge>
                  ))}
                </div>
              )}
            </EuiPanel>
          </div>

          {/* Right column */}
          <div>
            <EuiPanel paddingSize="s">
              <EuiTitle size="xs">
                <h4 style={{ margin: 0 }}>Actions</h4>
              </EuiTitle>
              <EuiSpacer size="s" />
              <div style={{ display: "flex", gap: 8, alignItems: "center", width: "100%" }}>
                {/* Make the three action icons larger and span most of the actions panel */}
                <div style={{ width: "33%", display: "flex", justifyContent: "center" }} title={wouldPlay ? "Remove 'Would play'" : "Mark as 'Would play'"}>
                  <EuiButtonIcon
                    onClick={() => setWouldPlay((s) => !s)}
                    iconType="playFilled"
                    color={wouldPlay ? "primary" : "text"}
                    aria-label={wouldPlay ? "Remove Would play" : "Would play"}
                    style={{ width: 56, height: 56, transform: "scale(2)", transformOrigin: "center" }}
                  />
                </div>

                <div style={{ width: "33%", display: "flex", justifyContent: "center" }} title={liked ? "Unlike" : "Like"}>
                  <EuiButtonIcon
                    onClick={() => setLiked((s) => !s)}
                    iconType="heart"
                    color={liked ? "danger" : "text"}
                    aria-label={liked ? "Unlike" : "Like"}
                    style={{ width: 56, height: 56, transform: "scale(2)", transformOrigin: "center" }}
                  />
                </div>

                <div style={{ width: "33%", display: "flex", justifyContent: "center" }} title={finished ? "Mark as not finished" : "Mark as finished"}>
                  <EuiButtonIcon
                    onClick={() => setFinished((s) => !s)}
                    iconType="checkInCircleFilled"
                    color={finished ? "success" : "text"}
                    aria-label={finished ? "Unmark finished" : "Mark finished"}
                    style={{ width: 56, height: 56, transform: "scale(2)", transformOrigin: "center" }}
                  />
                </div>
              </div>

              <EuiSpacer />

              <EuiText size="s">
                <p style={{ margin: 0, textAlign: "center" }}>Your rating:</p>
              </EuiText>
              <div style={{ display: "flex", justifyContent: "center", marginTop: 8 }}>
                <div>
                  <StarRating value={userRating} onChange={(v) => setUserRating(v)} />
                </div>
              </div>

              <EuiSpacer />

              {/* Action buttons under rating - stacked vertically */}
              <div style={{ display: "flex", flexDirection: "column", gap: 8, marginTop: 8 }}>
                <EuiButton fullWidth onClick={() => console.log("Show your activity")}>Show your activity</EuiButton>
                <EuiButton fullWidth onClick={() => console.log("Review or log")}>Review or log...</EuiButton>
                <EuiButton fullWidth onClick={() => console.log("Add to lists")}>Add to lists</EuiButton>
                <EuiButton fullWidth onClick={() => console.log("Share")}>Share</EuiButton>
              </div>
            </EuiPanel>

            <EuiSpacer />

            <EuiPanel paddingSize="s">
              <EuiTitle size="xs">
                <h4 style={{ margin: 0 }}>Ratings breakdown</h4>
              </EuiTitle>
              <EuiSpacer size="s" />
              <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
                {/* Horizontal stacked bar showing distribution from low (left) to high (right) */}
                <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                  <div style={{ width: 24, textAlign: "center", color: "#ddd" }}>★</div>
                  <div style={{ flex: 1 }}>
                    <div style={{ display: "flex", height: 20, borderRadius: 8, overflow: "hidden", background: "#222" }}>
                      {Object.keys(ratingDistribution)
                        .sort((a, b) => Number.parseFloat(a) - Number.parseFloat(b))
                        .map((k, idx) => {
                          const count = ratingDistribution[k] || 0;
                          const frac = count / totalRatings;
                          const bg = "#FFD700";
                          const isFirst = idx === 0;
                          return (
                            <div
                              key={k}
                              title={`${k} stars — ${count} (${Math.round(frac * 100)}%)`}
                              style={{
                                width: `${frac * 100}%`,
                                background: bg,
                                height: "100%",
                                borderLeft: isFirst ? "none" : "2px solid rgba(0,0,0,0.25)",
                              }}
                            />
                          );
                        })}
                    </div>
                  </div>
                  <div style={{ width: 60, textAlign: "center", color: "#ddd" }}>★★★★★</div>
                </div>

                <div style={{ textAlign: "right", color: "#aaa", fontSize: 12 }}>{totalRatings} ratings</div>
              </div>
            </EuiPanel>
          </div>
        </div>

        {/* Visible debug banner (can be hidden) */}
        {lastFetchedUrl && showDebugBanner && (
          <div style={{ marginTop: 12 }}>
            <EuiCallOut
              title={`Last API request: ${lastStatus ?? "-"}`}
              color={lastStatus && lastStatus >= 200 && lastStatus < 300 ? "success" : "warning"}
              iconType="inspect"
            >
              <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                <div style={{ overflow: "hidden", textOverflow: "ellipsis" }}>
                  <code style={{ fontSize: 12 }}>{lastFetchedUrl}</code>
                </div>
                <div style={{ marginLeft: 12 }}>
                  <EuiButton size="s" onClick={() => setShowDebugBanner(false)}>
                    Hide
                  </EuiButton>
                </div>
              </div>
            </EuiCallOut>
          </div>
        )}
      </div>
    </div>
  );
}


