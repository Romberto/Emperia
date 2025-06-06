from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class Users(Base):
    __tablename__ = "users"

    username:Mapped[str] = mapped_column(unique=True)
