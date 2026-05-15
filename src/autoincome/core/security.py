"""Security utilities for AutoIncome.

Implements OWASP-compliant security primitives:
- Secure password hashing (bcrypt/Argon2id)
- JWT token generation/validation
- Input sanitization
- Secure random generation
- Rate limiting helpers
"""

from __future__ import annotations

import hashlib
import hmac
import re
import secrets
import string
from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

# ── Password Hashing ──────────────────────────────────────────────
# Use bcrypt with auto-upgrading (fallback to Argon2id if available)
_pwd_context = CryptContext(
    schemes=["bcrypt", "argon2id"],
    deprecated="auto",
    bcrypt__rounds=12,  # OWASP recommended minimum
)


def hash_password(plain: str) -> str:
    """Hash a plaintext password using bcrypt.

    Args:
        plain: Raw password string.

    Returns:
        Bcrypt hash string.
    """
    return _pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    """Verify a plaintext password against a hash.

    Args:
        plain: Raw password to verify.
        hashed: Stored bcrypt hash.

    Returns:
        True if password matches.
    """
    return _pwd_context.verify(plain, hashed)


# ── JWT Tokens ────────────────────────────────────────────────────

def create_access_token(
    data: dict[str, Any],
    secret_key: str,
    expires_delta: timedelta | None = None,
) -> str:
    """Create a signed JWT access token.

    Args:
        data: Payload dictionary (must not contain sensitive data).
        secret_key: HS256 secret key.
        expires_delta: Token lifetime. Defaults to 15 minutes.

    Returns:
        Encoded JWT string.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc), "type": "access"})
    return jwt.encode(to_encode, secret_key, algorithm="HS256")


def decode_access_token(token: str, secret_key: str) -> dict[str, Any] | None:
    """Decode and validate a JWT access token.

    Args:
        token: JWT string.
        secret_key: HS256 secret key.

    Returns:
        Decoded payload dict, or None if invalid/expired.
    """
    try:
        payload = jwt.decode(token, secret_key, algorithms=["HS256"])
        if payload.get("type") != "access":
            return None
        return payload
    except JWTError:
        return None


# ── Input Validation & Sanitization ───────────────────────────────

_MAX_STRING_LEN = 4096
_SAFE_PATTERN = re.compile(r"[<>'\"&%`]|javascript:|data:|vbscript:", re.IGNORECASE)
_PATH_TRAVERSAL = re.compile(r"\.{2,}[/\\]|")  # noqa: W605


def sanitize_string(value: str, max_len: int = _MAX_STRING_LEN) -> str:
    """Sanitize user input string to prevent XSS/injection.

    Args:
        value: Raw user input.
        max_len: Maximum allowed length.

    Returns:
        Sanitized string.

    Raises:
        ValueError: If input contains dangerous patterns or exceeds length.
    """
    if not isinstance(value, str):
        raise ValueError("Input must be a string")
    if len(value) > max_len:
        raise ValueError(f"Input exceeds maximum length of {max_len}")
    if _SAFE_PATTERN.search(value):
        raise ValueError("Input contains potentially dangerous content")
    return value.strip()


def safe_filename(name: str) -> str:
    """Sanitize a filename to prevent path traversal attacks.

    Args:
        name: Proposed filename.

    Returns:
        Safe filename.

    Raises:
        ValueError: If filename is unsafe.
    """
    if not name or len(name) > 255:
        raise ValueError("Invalid filename length")
    if _PATH_TRAVERSAL.search(name):
        raise ValueError("Path traversal detected")
    # Allow only safe characters
    safe = re.sub(r"[^a-zA-Z0-9_.-]", "_", name)
    if safe in {"", ".", ".."}:
        raise ValueError("Invalid filename")
    return safe


# ── Cryptographically Secure Random ───────────────────────────────

def generate_secure_token(length: int = 32) -> str:
    """Generate a cryptographically secure random token.

    Args:
        length: Token length in bytes (result hex string is 2x).

    Returns:
        Hex-encoded secure random string.
    """
    return secrets.token_hex(length)


def generate_id() -> str:
    """Generate a secure unique identifier."""
    return hashlib.sha256(secrets.token_bytes(32)).hexdigest()[:16]


# ── Secure Comparison ─────────────────────────────────────────────

def secure_compare(a: str, b: str) -> bool:
    """Timing-safe string comparison to prevent timing attacks.

    Args:
        a: First string.
        b: Second string.

    Returns:
        True if strings are equal.
    """
    return hmac.compare_digest(a.encode(), b.encode())
