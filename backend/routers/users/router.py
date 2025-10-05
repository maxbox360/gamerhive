# routers/users/router.py
from ninja import Router
from .models import User

router = Router(tags=["Users"])

@router.get("/", response=list[dict])
def list_users(request):
    return list(User.objects.values("id", "username", "email"))
