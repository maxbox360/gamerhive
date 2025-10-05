from routers.games.models import Game, Genre, Platform
from routers.users.models import User
from django.contrib import admin

admin.site.register(User)                 
admin.site.register(Game)
admin.site.register(Genre)
admin.site.register(Platform)   
