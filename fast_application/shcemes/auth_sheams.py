from enum import Enum

from pydantic import BaseModel


class TelegramAuthPayload(BaseModel):
    id: int
    first_name: str | None = None
    last_name: str | None = None
    username: str | None = None
    photo_url: str | None = None
    auth_date: int
    hash: str


class UserCreate(BaseModel):
    id: int
    first_name: str | None = None
    last_name: str | None = None
    username: str | None = None
    photo_url: str | None = None


class UserRead(BaseModel):
    id: int
    telegram_id: int
    first_name: str | None = None
    last_name: str | None = None
    username: str | None = None
    photo_url: str | None = None


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str | None = None
    token_type: str = "Bearer"


class SosType(str, Enum):
    dtp = "dtp"
    conflict = "conflict"
    distroy = "distroy"


class SosRequest(BaseModel):
    type: SosType
    latitude: float
    longitude: float
