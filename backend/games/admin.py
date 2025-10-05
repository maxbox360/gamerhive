from django.contrib import admin
from .models import Game

@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('name', 'igdb_id', 'release_date') 
    search_fields = ('name',)                             
    list_filter = ('release_date',)                       
    ordering = ('name',)                                  

