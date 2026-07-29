export interface Genre {
  id: number;
  name: string;
  slug: string;
}

export interface Platform {
  id: number;
  name: string;
  slug: string;
  abbreviation?: string;
}

export interface Game {
  id: number;
  name: string;
  slug: string;
  summary?: string;
  cover_url?: string;
  genres: Genre[];
  platforms: Platform[];
}
