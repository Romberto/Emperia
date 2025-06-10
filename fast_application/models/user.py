from sqlalchemy.orm import Mapped

from models.base import Base


class UserBase(Base):
    __tablename__ = "users"
    telegram_id: Mapped[int]