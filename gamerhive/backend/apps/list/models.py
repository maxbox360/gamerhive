from django.db import models
from apps.videogames.models import VideoGame
from apps.user.models import Gamer

class List(models.Model):
    user = models.ForeignKey(Gamer, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=50) 
    games = models.ManyToManyField(VideoGame)

