from django.db import models

class Game(models.Model):
    igdb_id = models.IntegerField(unique=True)  # External API ID
    name = models.CharField(max_length=255)
    release_date = models.DateField(null=True, blank=True)
    summary = models.TextField(blank=True)
    cover_url = models.URLField(blank=True)
    genres = models.JSONField(blank=True, null=True)

    def __str__(self):
        return self.name
