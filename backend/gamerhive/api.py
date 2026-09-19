from django.http import HttpRequest
from django.middleware.csrf import get_token
from ninja import NinjaAPI
from routers.games.router import router as games_router
from routers.users.router import router as users_router

api = NinjaAPI(
    title="GamerHive API",
    version="1.0.0",
    description="API for accessing games, genres, and platforms"
)

api.add_router("/games/", games_router)
api.add_router("/users/", users_router)


@api.get("/auth/csrf", tags=["Auth"])
def csrf(request: HttpRequest):
    return {"csrfToken": get_token(request)}
