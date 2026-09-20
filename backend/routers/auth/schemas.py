from typing import Optional

from ninja import Schema


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
