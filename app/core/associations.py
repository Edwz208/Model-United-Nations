# app/core/associations.py

from sqlalchemy import Column, ForeignKey, Integer, Table

from app.core.database import Base


country_council = Table(
    "country_council",
    Base.metadata,
    Column(
        "country_id",
        Integer,
        ForeignKey("countries.country_id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "council_id",
        Integer,
        ForeignKey("councils.council_id", ondelete="CASCADE"),
        primary_key=True,
    ),
)