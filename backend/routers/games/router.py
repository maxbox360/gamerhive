# routers/games/router.py
from django.shortcuts import get_object_or_404
from ninja import Router
from typing import List
from django.core.paginator import Paginator, EmptyPage
from .schema import (
    GameSchema,
    GenreListSchema,
    PlatformListSchema,
    PaginatedGameCardResponse,
)
from .models import Game, Genre, Platform

router = Router()

# Game endpoints
@router.get("/games/", response=PaginatedGameCardResponse)
def list_games(
    request,
    genre: str = None,
    platform: str = None,
    search: str = None,
    page: int = 1,
    page_size: int = 24,
):
    """
    Get paginated games, optionally filtered by genre or platform name.
    Returns a paginated response with items and pagination metadata.
    """
    page_size = max(1, min(int(page_size), 48))
    qs = (
        Game.objects.all()
        .only("id", "name", "slug", "cover_url")
        .prefetch_related("genres", "platforms")
        .order_by("id")
    )

    if genre:
        qs = qs.filter(genres__name__icontains=genre)

    if platform:
        qs = qs.filter(platforms__name__icontains=platform)

    if search:
        qs = qs.filter(name__icontains=search)

    qs = qs.distinct()

    paginator = Paginator(qs, page_size)
    try:
        page_obj = paginator.page(page)
    except EmptyPage:
        page_obj = []

    items = list(page_obj) if hasattr(page_obj, "object_list") else []

    return {
        "items": items,
        "total": paginator.count,
        "page": int(page),
        "page_size": int(page_size),
        "total_pages": paginator.num_pages,
    }

@router.get("/games/{slug}", response=GameSchema)
def get_game(request, slug: str):
    game = get_object_or_404(Game.objects.prefetch_related("genres", "platforms"), slug=slug)
    return game

# Genre endpoints
@router.get("/genres", response=List[GenreListSchema])
def list_genres(request):
    return Genre.objects.only("id", "name", "slug").order_by("name")

# Platform endpoints
@router.get("/platforms", response=List[PlatformListSchema])
def list_platforms(request):
    return Platform.objects.only("id", "name", "slug", "abbreviation").order_by("name")
