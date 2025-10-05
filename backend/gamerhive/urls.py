from django.contrib import admin
from django.urls import path
from gamerhive.api import api  # your NinjaAPI instance

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", api.urls), 
]
