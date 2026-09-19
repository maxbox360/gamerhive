from typing import Optional

from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.validators import validate_email
from django.db import IntegrityError
from ninja import Router, Schema
from ninja.errors import HttpError

User = get_user_model()

router = Router(tags=["Authentication"])


class RegisterUserInput(Schema):
    username: str
    email: str
    password: str
    first_name: Optional[str] = ""
    last_name: Optional[str] = ""


class LoginUserInput(Schema):
    username: str
    password: str


class LogoutResponse(Schema):
    success: bool


class UserPublicSchema(Schema):
    id: int
    username: str
    email: str
    first_name: Optional[str] = ""
    last_name: Optional[str] = ""


@router.post("/register", response={201: UserPublicSchema})
def register_user(request, payload: RegisterUserInput):
    username = payload.username.strip()
    email = payload.email.strip()
    first_name = (payload.first_name or "").strip()
    last_name = (payload.last_name or "").strip()

    if not username:
        raise HttpError(400, "username is required.")
    if not email:
        raise HttpError(400, "email is required.")

    try:
        validate_email(email)
    except DjangoValidationError as exc:
        raise HttpError(400, exc.messages[0])

    if not payload.password or not payload.password.strip():
        raise HttpError(400, "password is required.")

    if User.objects.filter(username__iexact=username).exists():
        raise HttpError(400, "A user with that username already exists.")
    if User.objects.filter(email__iexact=email).exists():
        raise HttpError(400, "A user with that email already exists.")

    user = User(username=username, email=email, first_name=first_name, last_name=last_name)
    try:
        validate_password(payload.password, user=user)
    except DjangoValidationError as exc:
        raise HttpError(400, "; ".join(exc.messages))

    try:
        user = User.objects.create_user(
            username=username,
            email=email,
            password=payload.password,
            first_name=first_name,
            last_name=last_name,
        )
    except IntegrityError:
        raise HttpError(400, "A user with that username or email already exists.")

    login(request, user)
    return user


@router.post("/login", response={200: UserPublicSchema, 400: dict, 401: dict})
def login_user(request, payload: LoginUserInput):
    username = (payload.username or "").strip()
    password = payload.password or ""

    if not username or not password:
        raise HttpError(400, "username and password are required.")

    user = authenticate(request, username=username, password=password)
    if user is None:
        raise HttpError(401, "Invalid credentials.")

    login(request, user)
    return user


@router.post("/logout", response={200: LogoutResponse})
def logout_user(request):
    logout(request)
    return {"success": True}
