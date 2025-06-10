from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class UserBase(Base):
    __tablename__ = "users"
    telegram_id: Mapped[int] = mapped_column(unique=True, index=True, nullable=False)
    first_name:Mapped[str | None] = mapped_column(default=None)
    last_name:Mapped[str | None] = mapped_column(default=None)
    username:Mapped[str | None] = mapped_column(default=None)
    photo_ur:Mapped[str | None] = mapped_column(default=None)