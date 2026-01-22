"""
SQLAlchemy ORM models for LINE bot database.
Uses SQLAlchemy 2.0 syntax with Mapped type annotations.
"""

from typing import Optional
from datetime import datetime
from sqlalchemy import String, Text, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column
from database import Base


class User(Base):
    """
    User model representing LINE users who interact with the bot.

    Attributes:
        line_user_id: LINE's unique user identifier (Primary Key)
        display_name: User's display name from LINE profile
        picture_url: URL to user's profile picture
        status_message: User's status message
        language: User's preferred language (default: zh-TW)
        created_at: Timestamp when user first interacted with bot
        updated_at: Timestamp of last interaction
    """
    __tablename__ = "users"

    # Primary key - LINE user ID
    line_user_id: Mapped[str] = mapped_column(
        String(255),
        primary_key=True,
        index=True,
        comment="LINE's unique user identifier"
    )

    # Profile information (nullable - may not be fetchable if user blocks bot)
    display_name: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="User's display name from LINE"
    )

    picture_url: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="URL to user's profile picture"
    )

    status_message: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="User's status message"
    )

    language: Mapped[str] = mapped_column(
        String(10),
        default='zh-TW',
        nullable=False,
        comment="User's preferred language"
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        comment="When user first interacted with bot"
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
        comment="Last interaction timestamp"
    )

    # Table configuration
    __table_args__ = (
        Index('idx_created_at', 'created_at'),
        Index('idx_updated_at', 'updated_at'),
    )

    def __repr__(self) -> str:
        """String representation of User object."""
        return f"User(line_user_id={self.line_user_id!r}, display_name={self.display_name!r})"

    def __str__(self) -> str:
        """Human-readable string representation."""
        return f"{self.display_name or 'Unknown'} ({self.line_user_id})"
