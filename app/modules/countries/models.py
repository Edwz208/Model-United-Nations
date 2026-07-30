# app/modules/countries/models.py

from __future__ import annotations

from enum import Enum

from sqlalchemy import Integer, Text, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.associations import country_council


class CountryRole(str, Enum):
    MEMBER = "member"
    ADMIN = "admin"


class Country(Base):
    __tablename__ = "countries"

    country_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    name: Mapped[str] = mapped_column(Text, unique=True, nullable=False)

    delegate1: Mapped[str | None] = mapped_column(Text)
    delegate2: Mapped[str | None] = mapped_column(Text)
    delegate3: Mapped[str | None] = mapped_column(Text)
    delegate4: Mapped[str | None] = mapped_column(Text)

    role: Mapped[CountryRole] = mapped_column(SQLEnum(CountryRole), default=CountryRole.MEMBER, nullable=False)

    login: Mapped[str] = mapped_column(Text, default="", nullable=False)

    speaker_points: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    amendments_submitted: Mapped[int] = mapped_column(Integer, default=0, nullable=False)


    councils: Mapped[list[Council]] = relationship(
        secondary=country_council,
        back_populates="countries",
    )


    submitted_resolutions: Mapped[list[Resolution]] = relationship(
        foreign_keys="Resolution.submitter",
        back_populates="submitter_country",
    )

    seconded_resolutions: Mapped[list[Resolution]] = relationship(
        foreign_keys="Resolution.seconder",
        back_populates="seconder_country",
    )

    negated_resolutions: Mapped[list[Resolution]] = relationship(
        foreign_keys="Resolution.negator",
        back_populates="negator_country",
    )