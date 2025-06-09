from pydantic import BaseModel
from pydantic.v1 import UUID4


class UserBase(BaseModel):
    id: UUID4


class UserRead(UserBase):
    id: UUID4
    telegram_id: int
    first_name: str
    last_name: str | None = None
    username: str | None = None
    photo_url: str | None = None


class TelegramAuthPayload(BaseModel):
    id: int
    first_name: str
    last_name: str | None = None
    username: str | None = None
    photo_url: str | None = None
    auth_date: int
    hash: str


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
