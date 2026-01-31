"""SocialCredential model"""
from datetime import datetime
from sqlmodel import SQLModel, Field
from typing import Optional


class SocialCredential(SQLModel, table=True):
    """Stores encrypted social media platform credentials"""

    __tablename__ = "social_credentials"

    id: Optional[int] = Field(default=None, primary_key=True)
    platform: str = Field(index=True)  # "facebook" or "linkedin"
    account_name: str
    encrypted_token: str
    page_id_or_urn: Optional[str] = None  # Facebook Page ID or LinkedIn Person/Org URN
    token_expires_at: Optional[datetime] = None
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
