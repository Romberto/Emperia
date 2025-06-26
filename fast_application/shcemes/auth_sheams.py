from pydantic import BaseModel


class TelegramAuthPayload(BaseModel):
    id: int
    first_name: str
    last_name: str | None = None
    username: str | None = None
    photo_url: str | None = None
    auth_date: int
    hash: str

class UserRead(BaseModel):
    id: int
    telegram_id: int
    first_name: str
    last_name: str | None = None
    username: str | None = None
    photo_url: str | None = None

class TokenPair(BaseModel):
    access_token: str
    refresh_token: str | None = None
    token_type: str = "Bearer"

class SosRequest(BaseModel):
    type: str  # "dtp" или "conflict"
    latitude: float
    longitude: float