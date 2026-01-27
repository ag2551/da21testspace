"""Credential management endpoints"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from typing import List
from datetime import datetime

from app.database import get_async_session
from app.models.credential import SocialCredential
from app.schemas.credential import (
    CredentialCreate,
    CredentialUpdate,
    CredentialPublic,
    CredentialValidation
)
from app.services.encryption import get_encryption_service, EncryptionService
from app.adapters.facebook import FacebookAdapter
from app.adapters.linkedin import LinkedInAdapter

router = APIRouter(prefix="/api/credentials", tags=["credentials"])


@router.post("/", response_model=CredentialPublic, status_code=201)
async def create_credential(
    *,
    session: AsyncSession = Depends(get_async_session),
    credential: CredentialCreate,
    encryption: EncryptionService = Depends(get_encryption_service)
):
    """Create new platform credential"""
    # Validate token before saving
    is_valid = await _validate_token(credential.platform, credential.access_token)
    if not is_valid:
        raise HTTPException(status_code=400, detail="Invalid access token")

    # Encrypt token
    encrypted_token = encryption.encrypt(credential.access_token)

    # Create credential
    db_credential = SocialCredential(
        platform=credential.platform,
        account_name=credential.account_name,
        encrypted_token=encrypted_token,
        token_expires_at=credential.token_expires_at
    )

    session.add(db_credential)
    await session.commit()
    await session.refresh(db_credential)

    return db_credential


@router.get("/", response_model=List[CredentialPublic])
async def list_credentials(
    *,
    session: AsyncSession = Depends(get_async_session)
):
    """List all credentials"""
    result = await session.execute(select(SocialCredential))
    credentials = result.scalars().all()
    return credentials


@router.get("/{credential_id}", response_model=CredentialPublic)
async def get_credential(
    *,
    session: AsyncSession = Depends(get_async_session),
    credential_id: int
):
    """Get specific credential"""
    result = await session.execute(
        select(SocialCredential).where(SocialCredential.id == credential_id)
    )
    credential = result.scalar_one_or_none()

    if not credential:
        raise HTTPException(status_code=404, detail="Credential not found")

    return credential


@router.put("/{credential_id}", response_model=CredentialPublic)
async def update_credential(
    *,
    session: AsyncSession = Depends(get_async_session),
    credential_id: int,
    credential_update: CredentialUpdate,
    encryption: EncryptionService = Depends(get_encryption_service)
):
    """Update credential"""
    result = await session.execute(
        select(SocialCredential).where(SocialCredential.id == credential_id)
    )
    credential = result.scalar_one_or_none()

    if not credential:
        raise HTTPException(status_code=404, detail="Credential not found")

    # Update fields
    if credential_update.account_name:
        credential.account_name = credential_update.account_name

    if credential_update.access_token:
        # Validate new token
        is_valid = await _validate_token(credential.platform, credential_update.access_token)
        if not is_valid:
            raise HTTPException(status_code=400, detail="Invalid access token")

        credential.encrypted_token = encryption.encrypt(credential_update.access_token)

    if credential_update.token_expires_at is not None:
        credential.token_expires_at = credential_update.token_expires_at

    if credential_update.is_active is not None:
        credential.is_active = credential_update.is_active

    credential.updated_at = datetime.utcnow()

    await session.commit()
    await session.refresh(credential)

    return credential


@router.delete("/{credential_id}", status_code=204)
async def delete_credential(
    *,
    session: AsyncSession = Depends(get_async_session),
    credential_id: int
):
    """Delete credential"""
    result = await session.execute(
        select(SocialCredential).where(SocialCredential.id == credential_id)
    )
    credential = result.scalar_one_or_none()

    if not credential:
        raise HTTPException(status_code=404, detail="Credential not found")

    await session.delete(credential)
    await session.commit()

    return None


@router.post("/{credential_id}/validate", response_model=CredentialValidation)
async def validate_credential(
    *,
    session: AsyncSession = Depends(get_async_session),
    credential_id: int,
    encryption: EncryptionService = Depends(get_encryption_service)
):
    """Validate credential with platform"""
    result = await session.execute(
        select(SocialCredential).where(SocialCredential.id == credential_id)
    )
    credential = result.scalar_one_or_none()

    if not credential:
        raise HTTPException(status_code=404, detail="Credential not found")

    # Decrypt token
    token = encryption.decrypt(credential.encrypted_token)

    # Validate
    is_valid = await _validate_token(credential.platform, token)

    return CredentialValidation(
        valid=is_valid,
        message="Credential is valid" if is_valid else "Credential validation failed",
        last_validated_at=datetime.utcnow()
    )


async def _validate_token(platform: str, token: str) -> bool:
    """Helper to validate token with platform adapter"""
    if platform == "facebook":
        adapter = FacebookAdapter()
    elif platform == "linkedin":
        adapter = LinkedInAdapter()
    else:
        return False

    return await adapter.validate_credentials(token)
