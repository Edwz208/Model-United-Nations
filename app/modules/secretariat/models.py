# app/modules/secretariat/models.py

from __future__ import annotations

from sqlalchemy import Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base

class Secretariat(Base):
    __tablename__ = "secretariat"

    secretariat_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    name: Mapped[str] = mapped_column(Text, default="", unique=True, nullable=False)

    position: Mapped[str] = mapped_column(Text, default="", nullable=False)