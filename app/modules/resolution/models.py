# app/modules/resolution/models.py

from __future__ import annotations

from enum import Enum

from sqlalchemy import Integer, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ResolutionStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class Resolution(Base):
    __tablename__ = "resolutions"

    resolution_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    number: Mapped[int] = mapped_column(Integer, nullable=False)

    title: Mapped[str] = mapped_column(Text, nullable=False)

    clauses: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    council_id: Mapped[int] = mapped_column(
        ForeignKey("councils.council_id", ondelete="CASCADE"),
        nullable=False,
    )

    submitter: Mapped[int | None] = mapped_column(
        ForeignKey("countries.country_id", ondelete="SET NULL")
    )

    seconder: Mapped[int | None] = mapped_column(
        ForeignKey("countries.country_id", ondelete="SET NULL")
    )

    negator: Mapped[int | None] = mapped_column(
        ForeignKey("countries.country_id", ondelete="SET NULL")
    )

    url: Mapped[str | None] = mapped_column(Text)

    status: Mapped[ResolutionStatus] = mapped_column(
        SQLEnum(ResolutionStatus),
        default=ResolutionStatus.PENDING,
        nullable=False,
    )

    amendment_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)


    council: Mapped[Council] = relationship(
        back_populates="resolutions"
    )


    submitter_country: Mapped[Country] = relationship(
        foreign_keys=[submitter],
        back_populates="submitted_resolutions",
    )

    seconder_country: Mapped[Country] = relationship(
        foreign_keys=[seconder],
        back_populates="seconded_resolutions",
    )

    negator_country: Mapped[Country] = relationship(
        foreign_keys=[negator],
        back_populates="negated_resolutions",
    )


    amendments: Mapped[list[Amendment]] = relationship(
        back_populates="resolution",
        cascade="all, delete-orphan",
    )