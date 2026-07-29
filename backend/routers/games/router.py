# routers/games/router.py
from django.shortcuts import get_object_or_404
from ninja import Router
from typing import List
from django.core.paginator import Paginator, EmptyPage
from django.views.decorators.cache import cache_page
from .schema import GameSchema, GenreSchema, PlatformSchema, PaginatedGameResponse
from .models import Game, Genre, Platform

router = Router()

# Game endpoints
@router.get("/games/", response=PaginatedGameResponse)
@cache_page(60)  # cache paginated list for 60s (tune as needed or use Redis in prod)
def list_games(request, genre: str = None, platform: str = None, page: int = 1, page_size: int = 24):
    """
    Get paginated games, optionally filtered by genre or platform name.
    Returns a paginated response with items and pagination metadata.
    """
    # Only select the fields we need for the listing to reduce DB io
    qs = Game.objects.all().only("id", "name", "slug", "summary", "cover_url", "created_at", "updated_at").prefetch_related("genres", "platforms").order_by("id")

    if genre:
        qs = qs.filter(genres__name__icontains=genre)

    if platform:
        qs = qs.filter(platforms__name__icontains=platform)

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
@cache_page(30)  # cache game detail for 30s; tune or remove if data must be real-time
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
