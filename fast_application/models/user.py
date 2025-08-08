from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import BigInteger, String

from shcemes.auth_sheams import Role
from .base import Base


class UserBase(Base):
    __tablename__ = "users"
    telegram_id: Mapped[int] = mapped_column(
        BigInteger, unique=True, index=True, nullable=False
    )
    first_name: Mapped[str | None] = mapped_column(default=None)
    last_name: Mapped[str | None] = mapped_column(default=None)
    username: Mapped[str | None] = mapped_column(default=None)
    photo_url: Mapped[str | None] = mapped_column(default=None)
    role: Mapped[str] = mapped_column(String, default=Role.user)
