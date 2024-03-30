from django.db import models
from apps.videogames.models import VideoGame
from apps.user.models import Gamer

class Wishlist(models.Model):
    user = models.ForeignKey(Gamer, on_delete=models.CASCADE)
    game = models.ForeignKey(VideoGame, on_delete=models.CASCADE)
    added_date = models.DateTimeField(auto_now_add=True)
