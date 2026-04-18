# routers/games/router.py
from django.shortcuts import get_object_or_404
from ninja import Router
from typing import List
from .schema import GameSchema, GenreSchema, PlatformSchema
from .models import Game, Genre, Platform

router = Router()

# Game endpoints
@router.get("/games/", response=list[GameSchema])
def list_games(request, genre: str = None, platform: str = None):
    """
    Get all games, optionally filtered by genre or platform name.
    """
    qs = Game.objects.all()

    if genre:
        qs = qs.filter(genres__name__icontains=genre)

    if platform:
        qs = qs.filter(platforms__name__icontains=platform)

    return qs

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
