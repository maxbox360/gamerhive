# routers/users/router.py
from ninja import Router
from ninja.errors import HttpError
from .models import User

router = Router(tags=["Users"])


@router.get("/", response=list[dict])
def list_users(request):
    if not request.user.is_authenticated:
        raise HttpError(401, "Authentication credentials were not provided.")

    return list(User.objects.values("id", "username", "email"))
