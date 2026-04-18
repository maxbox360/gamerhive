import GameDetailClient from "./GameDetailClient";
import { notFound } from "next/navigation";

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

export default async function GameDetailPage({ params }: { params: { slug: string } }) {
  // In Next 15 params may be a promise; await it before accessing properties per the runtime warning.
  const { slug } = (await params) as { slug: string };
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  const primaryUrl = `${apiUrl}/api/games/games/${encodeURIComponent(slug)}`;
  let lastFetchedUrl: string | null = null;
  let lastStatus: number | null = null;

  try {
    let res = await fetch(primaryUrl);
    lastFetchedUrl = res.url;
    lastStatus = res.status;

    if (res.status === 404) {
      const altUrl = `${primaryUrl}/`;
      const alt = await fetch(altUrl);
      lastFetchedUrl = alt.url;
      lastStatus = alt.status;
      if (alt.ok) {
        res = alt;
      } else if (alt.status === 404) {
        return notFound();
      } else {
        throw new Error(`API error: ${alt.status} ${alt.statusText}`);
      }
    }

    if (!res.ok) {
      throw new Error(`API error: ${res.status} ${res.statusText}`);
    }

    const data: Game = await res.json();
    return <GameDetailClient initialGame={data} lastFetchedUrl={lastFetchedUrl} lastStatus={lastStatus} />;
  } catch (err: any) {
    // Network or other fetch failure — render client component with an error message so UI can show a friendly retry/diagnostic.
    console.error("GameDetail fetch error:", err);
    const message = err?.message ?? String(err);
    return <GameDetailClient initialGame={null} lastFetchedUrl={lastFetchedUrl} lastStatus={lastStatus} errorMessage={message} />;
  }
}








