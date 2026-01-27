"""Pydantic schemas for credentials"""
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional


class CredentialBase(BaseModel):
    """Base credential schema"""
    platform: str = Field(..., pattern="^(facebook|linkedin)$")
    account_name: str


class CredentialCreate(CredentialBase):
    """Schema for creating a credential"""
    access_token: str
    token_expires_at: Optional[datetime] = None


class CredentialUpdate(BaseModel):
    """Schema for updating a credential"""
    account_name: Optional[str] = None
    access_token: Optional[str] = None
    token_expires_at: Optional[datetime] = None
    is_active: Optional[bool] = None


class CredentialPublic(CredentialBase):
    """Public credential schema (no sensitive data)"""
    id: int
    token_expires_at: Optional[datetime]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CredentialValidation(BaseModel):
    """Schema for credential validation response"""
    valid: bool
    message: str
    last_validated_at: datetime
