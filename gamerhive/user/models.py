from django.db import models
from django.contrib.auth.models import AbstractUser

# User Model
class Gamer(AbstractUser):
    bio = models.TextField(blank=True)
    location = models.CharField(max_length=100, blank=True)
    website = models.URLField(blank=True)
    ALLOWED_REPLIES_CHOICES = [
        ('anyone', 'Anyone'),
        ('friends', 'Friends'),
        ('you', 'You')
    ]
    replies = models.CharField(max_length=10, choices=ALLOWED_REPLIES_CHOICES, default='anyone')


    # Potential Relationships
    # wishlist = models.ManyToManyField(Game, through='Wishlist')
    # backlog = models.ManyToManyField(Game, through='Backlog')
    # favorites = models.ManyToManyField(Game, through='Favorites')


    # Methods
    def __str__(self):
        return self.username

