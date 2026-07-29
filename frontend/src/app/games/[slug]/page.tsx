import Link from "next/link";
import { notFound } from "next/navigation";
import type { Game } from "@/types";

export default async function GameDetailPage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  const apiCandidates = [
    process.env.INTERNAL_API_URL,
    process.env.API_URL,
    process.env.NEXT_PUBLIC_API_URL,
    "http://django:8000",
    "http://localhost:8000",
  ].filter(Boolean) as string[];

  let res: Response | null = null;
  let lastError: unknown = null;
  for (const apiUrl of apiCandidates) {
    const base = apiUrl.replace(/\/$/, "");
    const url = `${base}/api/games/games/${encodeURIComponent(slug)}`;
    try {
      const candidateRes = await fetch(url, { cache: "no-store" });
      res = candidateRes;
      if (candidateRes.ok || candidateRes.status === 404) {
        break;
      }
    } catch (err) {
      lastError = err;
    }
  }

  if (!res) {
    throw new Error(`Failed to fetch game API: ${String(lastError)}`);
  }

  if (res.status === 404) {
    return notFound();
  }
  if (!res.ok) {
    throw new Error(`Failed to fetch game: ${res.status} ${res.statusText}`);
  }

  const game: Game = await res.json();
  const platforms = game.platforms?.map((p) => p.abbreviation || p.name).join(" • ") || "Unknown platform";

  return (
    <div style={{ minHeight: "100vh", backgroundColor: "#262626", color: "#fff", padding: "24px 16px" }}>
      <div style={{ maxWidth: 1100, margin: "0 auto" }}>
        <Link href="/games" style={{ color: "#FFD700", textDecoration: "none", fontWeight: 600 }}>
          ← Back to games
        </Link>

        <div style={{ display: "grid", gridTemplateColumns: "280px 1fr", gap: 24, marginTop: 16 }}>
          <div style={{ borderRadius: 12, overflow: "hidden", background: "#1d1d1d" }}>
            {game.cover_url ? (
              <div style={{ position: "relative", width: "100%", aspectRatio: "3 / 4" }}>
                <img
                  src={game.cover_url}
                  alt={game.name}
                  style={{ width: "100%", height: "100%", objectFit: "cover", position: "absolute", inset: 0 }}
                  loading="lazy"
                />
              </div>
            ) : (
              <div style={{ aspectRatio: "3 / 4", display: "grid", placeItems: "center", color: "#999" }}>
                No cover
              </div>
            )}
          </div>

          <div>
            <h1 style={{ color: "#FFD700", margin: 0 }}>{game.name}</h1>
            <p style={{ color: "#bbb", marginTop: 8 }}>{platforms}</p>

            {game.genres?.length > 0 && (
              <div style={{ display: "flex", gap: 8, flexWrap: "wrap", marginTop: 12 }}>
                {game.genres.map((genre) => (
                  <span
                    key={genre.id}
                    style={{
                      fontSize: 12,
                      border: "1px solid #444",
                      borderRadius: 999,
                      padding: "4px 10px",
                      color: "#ddd",
                    }}
                  >
                    {genre.name}
                  </span>
                ))}
              </div>
            )}

            <h2 style={{ marginTop: 24, marginBottom: 8, fontSize: 20 }}>Summary</h2>
            <p style={{ color: "#ddd", lineHeight: 1.6 }}>
              {game.summary || "No summary available yet."}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
