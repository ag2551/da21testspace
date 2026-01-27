"""Tests for encryption service"""
import pytest
import os
from cryptography.fernet import Fernet


def test_encrypt_decrypt():
    """Test encryption and decryption"""
    # Generate test key
    test_key = Fernet.generate_key().decode()
    os.environ["ENCRYPTION_KEY"] = test_key

    # Import after setting env var
    from app.services.encryption import EncryptionService

    service = EncryptionService()
    original = "test_token_12345"

    encrypted = service.encrypt(original)
    assert encrypted != original
    assert isinstance(encrypted, str)

    decrypted = service.decrypt(encrypted)
    assert decrypted == original


def test_different_plaintexts_produce_different_ciphertexts():
    """Test that different inputs produce different outputs"""
    test_key = Fernet.generate_key().decode()
    os.environ["ENCRYPTION_KEY"] = test_key

    from app.services.encryption import EncryptionService

    service = EncryptionService()

    encrypted1 = service.encrypt("token1")
    encrypted2 = service.encrypt("token2")

    assert encrypted1 != encrypted2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
