from pathlib import Path

import environ
from pydantic import BaseModel, field_validator


class Settings(BaseModel):
    igdb_client_id: str
    igdb_access_token: str
    igdb_total_games: int = 200000
    igdb_batch_size: int = 500
    igdb_platform_families: tuple[str, ...] = (
        "PlayStation",
        "Xbox",
        "Nintendo",
        "Sega",
        "PC",
    )
    igdb_min_summary_chars: int = 40
    igdb_min_rating_count: int = 5

    @field_validator("igdb_total_games")
    @classmethod
    def validate_total_games(cls, value: int) -> int:
        if value < 1:
            raise ValueError("IGDB_TOTAL_GAMES must be >= 1")
        return value

    @field_validator("igdb_batch_size")
    @classmethod
    def validate_batch_size(cls, value: int) -> int:
        if value < 1 or value > 500:
            raise ValueError("IGDB_BATCH_SIZE must be between 1 and 500")
        return value

    @field_validator("igdb_min_summary_chars", "igdb_min_rating_count")
    @classmethod
    def validate_non_negative(cls, value: int) -> int:
        if value < 0:
            raise ValueError("IGDB thresholds must be >= 0")
        return value

    @classmethod
    def load(cls) -> "Settings":
        env = environ.Env()
        env_candidates = (
            Path("/app/.env"),
            Path(__file__).resolve().parents[2] / ".env",
            Path.cwd() / ".env",
        )
        for env_path in env_candidates:
            if env_path.exists():
                environ.Env.read_env(str(env_path))
                break

        families = tuple(
            f.strip()
            for f in env(
                "IGDB_PLATFORM_FAMILIES",
                default="PlayStation,Xbox,Nintendo,Sega,PC",
            ).split(",")
            if f.strip()
        )
        return cls(
            igdb_client_id=env("IGDB_CLIENT_ID"),
            igdb_access_token=env("IGDB_ACCESS_TOKEN"),
            igdb_total_games=env.int("IGDB_TOTAL_GAMES", default=200000),
            igdb_batch_size=env.int("IGDB_BATCH_SIZE", default=500),
            igdb_platform_families=families,
            igdb_min_summary_chars=env.int("IGDB_MIN_SUMMARY_CHARS", default=40),
            igdb_min_rating_count=env.int("IGDB_MIN_RATING_COUNT", default=5),
        )
