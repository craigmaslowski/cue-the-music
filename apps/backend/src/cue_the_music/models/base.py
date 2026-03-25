"""Shared SQLAlchemy base class and mixins."""

from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class TimestampMixin:
    """Mixin providing created_at and updated_at columns for all models."""

    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        onupdate=func.now(),
    )


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models in this project."""
