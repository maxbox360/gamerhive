# routers/games/router.py
from django.shortcuts import get_object_or_404
from ninja import Router, Query
from typing import List, Optional
from .schema import GameSchema, GenreSchema, PlatformSchema, PaginatedGamesSchema
from .models import Game, Genre, Platform
import math

router = Router()

# Game endpoints
@router.get("/games/", response=PaginatedGamesSchema)
def list_games(
    request,
    genre: Optional[str] = None,
    platform: Optional[str] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(24, ge=1, le=100),
):
    """
    Get paginated games, optionally filtered by genre, platform, or search query.
    """
    qs = Game.objects.prefetch_related("genres", "platforms").order_by("-id")

    if genre:
        qs = qs.filter(genres__name__icontains=genre)

    if platform:
        qs = qs.filter(platforms__name__icontains=platform)

    if search:
        qs = qs.filter(name__icontains=search)

    # Get total count before pagination
    total = qs.count()
    total_pages = math.ceil(total / page_size) if total > 0 else 1

    # Apply pagination
    offset = (page - 1) * page_size
    items = list(qs[offset : offset + page_size])

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }

@router.get("/games/{slug}", response=GameSchema)
def get_game(request, slug: str):
    game = get_object_or_404(Game.objects.prefetch_related("genres", "platforms"), slug=slug)
    return game

# Genre endpoints
@router.get("/genres", response=List[GenreSchema])
def list_genres(request):
    return Genre.objects.all()

# Platform endpoints
@router.get("/platforms", response=List[PlatformSchema])
def list_platforms(request):
    return Platform.objects.all()
