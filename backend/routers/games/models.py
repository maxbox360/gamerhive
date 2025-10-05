from django.db import models

class Genre(models.Model):
    igdb_genre_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=150, unique=True)
    url = models.URLField(blank=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    def __str__(self):
        return self.name


class Platform(models.Model):
    igdb_platform_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=150, unique=True)
    abbreviation = models.CharField(max_length=50, blank=True)
    category = models.IntegerField(null=True, blank=True)
    platform_type = models.IntegerField(null=True, blank=True)
    url = models.URLField(blank=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    def __str__(self):
        return self.name


class Game(models.Model):
    igdb_game_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    summary = models.TextField(blank=True)
    url = models.URLField(blank=True)
    cover_id = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    genres = models.ManyToManyField(Genre, related_name="games", blank=True)
    platforms = models.ManyToManyField(Platform, related_name="games", blank=True)

    def __str__(self):
        return self.name

