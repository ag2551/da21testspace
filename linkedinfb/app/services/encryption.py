"""Token encryption service using Fernet"""
from cryptography.fernet import Fernet
from app.config import get_settings

settings = get_settings()


class EncryptionService:
    """Handles encryption and decryption of sensitive tokens"""

    def __init__(self):
        self.cipher = Fernet(settings.encryption_key.encode())

    def encrypt(self, plaintext: str) -> str:
        """Encrypt a plaintext string"""
        return self.cipher.encrypt(plaintext.encode()).decode()

    def decrypt(self, ciphertext: str) -> str:
        """Decrypt a ciphertext string"""
        return self.cipher.decrypt(ciphertext.encode()).decode()


def get_encryption_service() -> EncryptionService:
    """Dependency for encryption service"""
    return EncryptionService()
