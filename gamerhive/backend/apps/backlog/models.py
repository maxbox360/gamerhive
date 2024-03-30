from django.db import models
from apps.user.models import Gamer
from apps.videogames.models import VideoGame

class Backlog(models.Model):
    user = models.ForeignKey(Gamer, on_delete=models.CASCADE)
    game = models.ForeignKey(VideoGames, on_delete=models.CASCADE)
    added_date = models.DateTimeField(auto_now_add=True)
