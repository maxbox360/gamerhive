import Link from "next/link";

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

interface GameCardProps {
  game: Game;
}

export default function GameCard({ game }: GameCardProps) {
  return (
    <Link href={`/games/${game.slug}`} className="group">
      <div className="bg-neutral-800 rounded-lg overflow-hidden transition-transform duration-200 group-hover:scale-105 group-hover:shadow-lg group-hover:shadow-amber-400/20">
        {/* Cover Image */}
        <div className="aspect-[3/4] relative overflow-hidden bg-neutral-700">
          {game.cover_url ? (
            <img
              src={game.cover_url}
              alt={game.name}
              className="w-full h-full object-cover"
              loading="lazy"
            />
          ) : (
            <div className="w-full h-full flex items-center justify-center">
              <span className="text-4xl"></span>
            </div>
          )}
          {/* Hover Overlay */}
          <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-200">
            <div className="absolute bottom-0 left-0 right-0 p-3">
              {game.genres && game.genres.length > 0 && (
                <div className="flex flex-wrap gap-1">
                  {game.genres.slice(0, 2).map((genre) => (
                    <span
                      key={genre.id}
                      className="text-xs bg-amber-400/20 text-amber-400 px-2 py-0.5 rounded"
                    >
                      {genre.name}
                    </span>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Game Title */}
        <div className="p-3">
          <h3 className="font-medium text-sm text-white truncate group-hover:text-amber-400 transition-colors">
            {game.name}
          </h3>
          {game.platforms && game.platforms.length > 0 && (
            <p className="text-xs text-neutral-500 truncate mt-1">
              {game.platforms
                .slice(0, 3)
                .map((p) => p.abbreviation || p.name)
                .join(" • ")}
            </p>
          )}
        </div>
      </div>
    </Link>
  );
}
