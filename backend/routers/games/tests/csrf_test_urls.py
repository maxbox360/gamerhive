from django.http import HttpRequest
from django.middleware.csrf import get_token
from django.urls import path
from ninja import NinjaAPI

test_api = NinjaAPI(csrf=True, urls_namespace="csrf-test")


@test_api.get("/auth/csrf", tags=["Tests"])
def csrf(request: HttpRequest):
    return {"csrfToken": get_token(request)}


@test_api.post("/csrf-probe", tags=["Tests"])
def csrf_probe(request):
    return {"authenticated": request.user.is_authenticated}


urlpatterns = [
    path("api/", test_api.urls),
]
