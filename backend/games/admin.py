from django.contrib import admin
from .models import Game, Genre, Platform

@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'igdb_genre_id')
    search_fields = ('name',)

@admin.register(Platform)
class PlatformAdmin(admin.ModelAdmin):
    list_display = ('name', 'abbreviation', 'igdb_platform_id')
    search_fields = ('name', 'abbreviation')

@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'igdb_game_id')
    search_fields = ('name',)
    list_filter = ('genres', 'platforms')  # filters on right sidebar
    filter_horizontal = ('genres', 'platforms')  # nice multi-select widget for many-to-many
                                

