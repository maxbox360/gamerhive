from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
class User(AbstractUser):
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    email = models.EmailField(unique=True)
    bio = models.TextField(blank=True)
    location = models.CharField(max_length=100, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    website = models.URLField(blank=True)

    class Pronouns(models.TextChoices):
        HE_HIM = 'he/him', 'He/Him'
        SHE_HER = 'she/her', 'She/Her'
        THEY_THEM = 'they/them', 'They/Them'
        OTHER = 'other', 'Other'
        PREFER_NOT = 'prefer_not', 'Prefer not to say'

    pronouns = models.CharField(
        max_length=20,
        choices=Pronouns.choices,
        blank=True
    )

    avatar = models.ImageField(
        upload_to='avatars/', 
        null=True, 
        blank=True
    )

    def __str__(self):
        return self.username
    
    class Meta:
        app_label = "gamerhive"
