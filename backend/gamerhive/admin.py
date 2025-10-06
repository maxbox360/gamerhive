from routers.games.models import Game, Genre, Platform
from routers.users.models import User
from django.contrib import admin

admin.site.register(User)

@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "created_at")  # fields shown in the list
    search_fields = ("name",)  # enables search by name
    filter_horizontal = ("genres", "platforms")  # better interface for many-to-many fields

@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name",)

@admin.register(Platform)
class PlatformAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name",)

