# app/modules/amendments/models.py

from __future__ import annotations

from enum import Enum

from sqlalchemy import Integer, SmallInteger, Text, ForeignKey, DateTime, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.database import Base


class AmendmentStatus(str, Enum):
    PENDING = "pending review"
    APPROVED = "approved"
    REJECTED = "rejected"


class Amendment(Base):
    __tablename__ = "amendments"

    amendment_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    resolution_id: Mapped[int] = mapped_column(
        ForeignKey("resolutions.resolution_id", ondelete="CASCADE"),
        nullable=False,
    )

    amendment_number: Mapped[int] = mapped_column(Integer, nullable=False)

    clause_number: Mapped[int] = mapped_column(SmallInteger, nullable=False)

    content: Mapped[str | None] = mapped_column(Text)

    submitter: Mapped[int] = mapped_column(
        ForeignKey("countries.country_id", ondelete="RESTRICT"),
        nullable=False,
    )

    status: Mapped[AmendmentStatus] = mapped_column(
        SQLEnum(AmendmentStatus),
        default=AmendmentStatus.PENDING,
        nullable=False,
    )

    modified_at: Mapped[DateTime] = mapped_column(
        DateTime,
        server_default=func.current_timestamp(),
        nullable=False,
    )


    resolution: Mapped[Resolution] = relationship(
        back_populates="amendments"
    )

    submitter_country: Mapped[Country] = relationship()