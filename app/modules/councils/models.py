# app/modules/councils/models.py

from __future__ import annotations

from sqlalchemy import Integer, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.associations import country_council


class Council(Base):
    __tablename__ = "councils"

    council_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    name: Mapped[str] = mapped_column(Text, unique=True, nullable=False)

    resolution_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    is_main: Mapped[bool] = mapped_column(Boolean, default=False)


    countries: Mapped[list[Country]] = relationship(
        secondary=country_council,
        back_populates="councils",
    )


    resolutions: Mapped[list[Resolution]] = relationship(
        back_populates="council",
        cascade="all, delete-orphan",
    )