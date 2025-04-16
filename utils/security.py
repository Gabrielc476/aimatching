"""
Security utilities for LinkedIn Job Matcher.
"""

import os
import jwt
import bcrypt
import secrets
import string
import logging
import time
from typing import Optional, Dict, Any, Union
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


def generate_password_hash(password: str) -> str:
    """
    Generate a secure hash for a password.

    Args:
        password: Plain text password

    Returns:
        Hashed password suitable for storage
    """
    # Convert password to bytes if it's a string
    if isinstance(password, str):
        password = password.encode('utf-8')

    # Generate salt and hash password
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password, salt)

    # Return string representation
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against a hash.

    Args:
        plain_password: Plain text password
        hashed_password: Hashed password from database

    Returns:
        True if password matches, False otherwise
    """
    # Convert inputs to bytes if they're strings
    if isinstance(plain_password, str):
        plain_password = plain_password.encode('utf-8')

    if isinstance(hashed_password, str):
        hashed_password = hashed_password.encode('utf-8')

    try:
        return bcrypt.checkpw(plain_password, hashed_password)
    except Exception as e:
        logger.error(f"Error verifying password: {str(e)}")
        return False


def generate_token(payload: Dict[str, Any], secret_key: str, expires_in: int = 3600) -> str:
    """
    Generate a JWT token.

    Args:
        payload: Dictionary of data to encode in the token
        secret_key: Secret key for signing the token
        expires_in: Token expiration time in seconds

    Returns:
        JWT token string
    """
    # Add expiration time to payload
    expiration = datetime.utcnow() + timedelta(seconds=expires_in)
    payload.update({
        'exp': expiration,
        'iat': datetime.utcnow()  # Issued at
    })

    # Generate token
    token = jwt.encode(payload, secret_key, algorithm='HS256')

    # jwt.encode may return bytes in some versions of PyJWT
    if isinstance(token, bytes):
        return token.decode('utf-8')

    return token


def verify_token(token: str, secret_key: str) -> Optional[Dict[str, Any]]:
    """
    Verify and decode a JWT token.

    Args:
        token: JWT token to verify
        secret_key: Secret key used to sign the token

    Returns:
        Decoded payload if valid, None otherwise
    """
    try:
        # Verify and decode token
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("Token expired")
        return None
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid token: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Error verifying token: {str(e)}")
        return None


def generate_secure_token(length: int = 32) -> str:
    """
    Generate a cryptographically secure random token.

    Args:
        length: Length of the token in characters

    Returns:
        Secure random token
    """
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def hash_data(data: str, salt: Optional[str] = None) -> str:
    """
    Create a hash of data, optionally with a salt.

    Args:
        data: Data to hash
        salt: Optional salt to use

    Returns:
        Hashed data
    """
    import hashlib

    # Generate salt if not provided
    if salt is None:
        salt = secrets.token_hex(16)

    # Convert data to bytes if it's a string
    if isinstance(data, str):
        data = data.encode('utf-8')

    # Convert salt to bytes if it's a string
    if isinstance(salt, str):
        salt = salt.encode('utf-8')

    # Hash the data with the salt
    hasher = hashlib.sha256()
    hasher.update(salt)
    hasher.update(data)
    hashed = hasher.hexdigest()

    # Return the salt and hash
    salt_hex = salt.hex() if isinstance(salt, bytes) else salt
    return f"{salt_hex}${hashed}"


def verify_data_hash(data: str, hashed_data: str) -> bool:
    """
    Verify data against a hash.

    Args:
        data: Data to verify
        hashed_data: Previously hashed data with salt

    Returns:
        True if data matches the hash, False otherwise
    """
    try:
        # Split the salt and hash
        salt_hex, hash_value = hashed_data.split('$', 1)

        # Convert salt from hex to bytes
        salt = bytes.fromhex(salt_hex)

        # Hash the data with the salt
        import hashlib

        # Convert data to bytes if it's a string
        if isinstance(data, str):
            data = data.encode('utf-8')

        hasher = hashlib.sha256()
        hasher.update(salt)
        hasher.update(data)
        computed_hash = hasher.hexdigest()

        # Compare the computed hash with the stored hash
        return computed_hash == hash_value
    except Exception as e:
        logger.error(f"Error verifying data hash: {str(e)}")
        return False


def encrypt_data(data: str, key: str) -> str:
    """
    Encrypt data using AES.

    Args:
        data: Data to encrypt
        key: Encryption key

    Returns:
        Encrypted data as base64 string
    """
    try:
        from cryptography.fernet import Fernet
        import hashlib
        import base64

        # Derive a Fernet key from the provided key
        fernet_key = hashlib.sha256(key.encode()).digest()
        fernet_key = base64.urlsafe_b64encode(fernet_key[:32])

        # Create a Fernet instance
        f = Fernet(fernet_key)

        # Encrypt the data
        encrypted_data = f.encrypt(data.encode())

        # Return base64 encoded encrypted data
        return base64.b64encode(encrypted_data).decode()
    except Exception as e:
        logger.error(f"Error encrypting data: {str(e)}")
        raise


def decrypt_data(encrypted_data: str, key: str) -> str:
    """
    Decrypt data encrypted with encrypt_data.

    Args:
        encrypted_data: Encrypted data as base64 string
        key: Encryption key

    Returns:
        Decrypted data
    """
    try:
        from cryptography.fernet import Fernet
        import hashlib
        import base64

        # Derive a Fernet key from the provided key
        fernet_key = hashlib.sha256(key.encode()).digest()
        fernet_key = base64.urlsafe_b64encode(fernet_key[:32])

        # Create a Fernet instance
        f = Fernet(fernet_key)

        # Decode base64 encoded encrypted data
        encrypted_bytes = base64.b64decode(encrypted_data)

        # Decrypt the data
        decrypted_data = f.decrypt(encrypted_bytes)

        # Return decrypted data as string
        return decrypted_data.decode()
    except Exception as e:
        logger.error(f"Error decrypting data: {str(e)}")
        raise


def secure_compare(a: str, b: str) -> bool:
    """
    Compare two strings in constant time to prevent timing attacks.

    Args:
        a: First string
        b: Second string

    Returns:
        True if strings are equal, False otherwise
    """
    import hmac

    if isinstance(a, str):
        a = a.encode()

    if isinstance(b, str):
        b = b.encode()

    return hmac.compare_digest(a, b)


def generate_csrf_token() -> str:
    """
    Generate a CSRF token.

    Returns:
        CSRF token
    """
    return secrets.token_hex(32)