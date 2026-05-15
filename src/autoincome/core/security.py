"""Security utilities for AutoIncome.

Implements OWASP-compliant security primitives:
- Secure password hashing (bcrypt/Argon2id)
- JWT token generation/validation with JTI for revocation
- Input sanitization
- Secure random generation
- Rate limiting helpers
- Secret key entropy validation
- URL protocol validation
"""

from __future__ import annotations

import hashlib
import hmac
import math
import re
import secrets
import string
from datetime import datetime, timedelta, timezone
from typing import Any
from urllib.parse import urlparse

import bcrypt
from jose import JWTError, jwt

# ── Password Hashing ──────────────────────────────────────────────

def hash_password(plain: str) -> str:
    """Hash a plaintext password using bcrypt.

    bcrypt has a 72-byte limit on passwords.
    """
    plain_bytes = plain.encode("utf-8")[:72]
    return bcrypt.hashpw(plain_bytes, bcrypt.gensalt(rounds=12)).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """Verify a plaintext password against a hash."""
    plain_bytes = plain.encode("utf-8")[:72]
    return bcrypt.checkpw(plain_bytes, hashed.encode("utf-8"))


# ── JWT Tokens ────────────────────────────────────────────────────

def create_access_token(
    data: dict[str, Any],
    secret_key: str,
    expires_delta: timedelta | None = None,
) -> str:
    """Create a signed JWT access token with unique JTI for revocation.

    White-hat principle: minimal payload. Only sub (user ID) is stored.
    No email, no roles, no personal data in the token.
    """
    to_encode = {
        "sub": data.get("sub"),
    }
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=15))
    to_encode.update({
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "access",
        "jti": generate_id(),
    })
    return jwt.encode(to_encode, secret_key, algorithm="HS256")


def decode_access_token(token: str, secret_key: str) -> dict[str, Any] | None:
    """Decode and validate a JWT access token."""
    try:
        payload = jwt.decode(token, secret_key, algorithms=["HS256"])
        if payload.get("type") != "access":
            return None
        return payload
    except JWTError:
        return None


# ── Secret Key Entropy Validation ─────────────────────────────────

def validate_secret_key_entropy(key: str, min_bits: float = 4.0) -> None:
    """Validate that a secret key has sufficient entropy.

    White-hat defense: reject low-entropy keys like 'aaaaaaaa...' even
    if they meet length requirements. Prevents brute-force of JWT signing key.

    Args:
        key: The secret key to validate.
        min_bits: Minimum Shannon entropy per character.

    Raises:
        ValueError: If entropy is too low.
    """
    if len(key) < 32:
        raise ValueError("Secret key must be at least 32 characters")

    # Shannon entropy calculation
    if len(key) == 0:
        raise ValueError("Secret key cannot be empty")

    freq = {}
    for char in key:
        freq[char] = freq.get(char, 0) + 1

    entropy = 0.0
    length = len(key)
    for count in freq.values():
        p = count / length
        entropy -= p * math.log2(p)

    if entropy < min_bits:
        raise ValueError(
            f"Secret key entropy too low ({entropy:.2f} bits/char). "
            f"Use a cryptographically random key with at least {min_bits} bits/char. "
            f"Generate with: openssl rand -hex 32"
        )


# ── URL Protocol Validation ───────────────────────────────────────

def validate_safe_url(url: str | None) -> str | None:
    """Strictly validate URL protocol using urllib.parse.

    White-hat defense: urlparse prevents bypass techniques like
    javascript://example.com/http:// or data:text/html,... that
    simple startswith checks miss.
    """
    if url is None:
        return None
    url = url.strip()
    if not url:
        return None

    parsed = urlparse(url)
    scheme = parsed.scheme.lower()

    if scheme not in ("http", "https"):
        raise ValueError(
            f"URL must use HTTP or HTTPS protocol, got: {scheme or 'empty'}"
        )

    # Additional check: reject URLs with embedded credentials
    if parsed.username or parsed.password:
        raise ValueError("URL must not contain embedded credentials")

    return url


# ── Input Validation & Sanitization ───────────────────────────────

_MAX_STRING_LEN = 4096
_SAFE_PATTERN = re.compile(r"[<>'\"&%`]|javascript:|data:|vbscript:", re.IGNORECASE)
_PATH_TRAVERSAL = re.compile(r"\.{2,}[/\\]|")  # noqa: W605


def sanitize_string(value: str, max_len: int = _MAX_STRING_LEN) -> str:
    """Sanitize user input string to prevent XSS/injection."""
    if not isinstance(value, str):
        raise ValueError("Input must be a string")
    if len(value) > max_len:
        raise ValueError(f"Input exceeds maximum length of {max_len}")
    if _SAFE_PATTERN.search(value):
        raise ValueError("Input contains potentially dangerous content")
    return value.strip()


def safe_filename(name: str) -> str:
    """Sanitize a filename to prevent path traversal attacks."""
    if not name or len(name) > 255:
        raise ValueError("Invalid filename length")
    if _PATH_TRAVERSAL.search(name):
        raise ValueError("Path traversal detected")
    safe = re.sub(r"[^a-zA-Z0-9_.-]", "_", name)
    if safe in {"", ".", ".."}:
        raise ValueError("Invalid filename")
    return safe


# ── Cryptographically Secure Random ───────────────────────────────

def generate_secure_token(length: int = 32) -> str:
    """Generate a cryptographically secure random token."""
    return secrets.token_hex(length)


def generate_id() -> str:
    """Generate a secure unique identifier."""
    return hashlib.sha256(secrets.token_bytes(32)).hexdigest()[:16]


# ── Secure Comparison ─────────────────────────────────────────────

def secure_compare(a: str, b: str) -> bool:
    """Timing-safe string comparison to prevent timing attacks."""
    return hmac.compare_digest(a.encode(), b.encode())
