# backend/gamerhive/schemas.py
from ninja import Schema
from typing import List, Optional
from datetime import datetime

class GenreSchema(Schema):
    id: int
    name: str
    slug: str
    created_at: datetime
    updated_at: datetime

class PlatformSchema(Schema):
    id: int
    name: str
    slug: str
    abbreviation: Optional[str]
    category: Optional[int]
    platform_type: Optional[int]
    url: Optional[str]
    created_at: datetime
    updated_at: datetime

class GameSchema(Schema):
    id: int
    name: str
    slug: str
    summary: Optional[str]
    cover_id: Optional[int]
    genres: List[GenreSchema]
    platforms: List[PlatformSchema]
    created_at: datetime
    updated_at: datetime

