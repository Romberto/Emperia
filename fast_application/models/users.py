from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Users(Base):
    __tablename__ = "users"
    telegram_id: Mapped[int]
    first_name:Mapped[str | None] = mapped_column(default=None)
    last_name:Mapped[str | None] = mapped_column(default=None)
    username:Mapped[str | None] = mapped_column(default=None)
    photo_ur:Mapped[str | None] = mapped_column(default=None)
