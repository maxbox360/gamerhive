from django.db import models

class VideoGame(models.Model):
    title = models.CharField(max_length=255)
    release_date = models.DateField()
    star_rating = models.DecimalField(max_digits=3, decimal_places=1, default=0.0)
    box_art = models.ImageField(upload_to='game_covers/', blank=True, null=True)
    platform = models.CharField(max_length=100)
    publisher = models.CharField(max_length=255)
    developer = models.CharField(max_length=255)
    genre = models.CharField(max_length=100)

    def __str__(self):
        return self.title

