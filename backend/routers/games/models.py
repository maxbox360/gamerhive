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
    
    class Meta:
        app_label = 'gamerhive'


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
    
    class Meta:
        app_label = 'gamerhive'

class Company(models.Model):
    igdb_company_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name
    
    class Meta:
        app_label = 'gamerhive'


class Game(models.Model):
    igdb_game_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    summary = models.TextField(blank=True)
    story_line = models.TextField(blank=True, null=True)
    release_date = models.DateTimeField(blank=True, null=True)
    url = models.URLField(blank=True)
    cover_url = models.URLField(max_length=500, blank=True, null=True)
    screenshots = models.JSONField(blank=True, null=True)
    websites = models.JSONField(blank=True, null=True)
    publishers = models.ManyToManyField(Company, related_name="published_games", blank=True)
    developers = models.ManyToManyField(Company, related_name="developed_games", blank=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    genres = models.ManyToManyField(Genre, related_name="games", blank=True)
    platforms = models.ManyToManyField(Platform, related_name="games", blank=True)

    def __str__(self):
        return self.name
    
    class Meta:
        app_label = 'gamerhive'
