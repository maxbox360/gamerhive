# routers/games/router.py
from django.shortcuts import get_object_or_404
from ninja import Router
from typing import List
from .schema import GameSchema, GenreSchema, PlatformSchema
from .models import Game, Genre, Platform

router = Router()

# Game endpoints
@router.get("/games", response=List[GameSchema])
def list_games(request):
    games = Game.objects.prefetch_related("genres", "platforms").all()
    return games

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
