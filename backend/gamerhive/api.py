from ninja import NinjaAPI
from routers.games.router import router as games_router
from routers.users.router import router as users_router

api = NinjaAPI()
api.add_router("/games/", games_router)
api.add_router("/users/", users_router)
