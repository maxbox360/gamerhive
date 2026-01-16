from routers.games.models import Game, Genre, Platform, Company
from routers.users.models import User
from django.contrib import admin
from django.utils.html import format_html

admin.site.register(User)

@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "cover_image", "created_at")  # fields shown in the list
    search_fields = ("name",)  # enables search by name
    filter_horizontal = ("genres", "platforms")  # better interface for many-to-many fields

    def cover_image(self, obj):
        if obj.cover_url:
            return format_html('<img src="{}" width="100" />', obj.cover_url)
        return "No Image"
    
    cover_image.short_description = "Cover Image"

@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name",)

@admin.register(Platform)
class PlatformAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name",)

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("name", )
    search_fields = ("name",)

