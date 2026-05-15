"""Security unit tests."""

from __future__ import annotations

import pytest

from autoincome.core.security import (
    decode_access_token,
    generate_id,
    generate_secure_token,
    hash_password,
    safe_filename,
    sanitize_string,
    secure_compare,
    verify_password,
)


class TestPasswordHashing:
    def test_hash_and_verify(self):
        pwd = "SecurePass123!"
        h = hash_password(pwd)
        assert h != pwd
        assert verify_password(pwd, h)
        assert not verify_password("wrong", h)

    def test_different_hashes_for_same_password(self):
        pwd = "Test123!"
        h1 = hash_password(pwd)
        h2 = hash_password(pwd)
        assert h1 != h2  # bcrypt auto-salt


class TestJWT:
    def test_create_and_decode(self):
        from datetime import timedelta

        from autoincome.core.security import create_access_token

        token = create_access_token({"sub": "user123"}, "a" * 32, timedelta(minutes=5))
        payload = decode_access_token(token, "a" * 32)
        assert payload is not None
        assert payload["sub"] == "user123"

    def test_decode_invalid_token(self):
        assert decode_access_token("bad.token.here", "secret") is None

    def test_decode_wrong_secret(self):
        from datetime import timedelta

        from autoincome.core.security import create_access_token

        token = create_access_token({"sub": "x"}, "secret1" * 8, timedelta(minutes=5))
        assert decode_access_token(token, "secret2" * 8) is None


class TestSanitization:
    def test_valid_string(self):
        assert sanitize_string("hello world") == "hello world"

    def test_xss_rejection(self):
        with pytest.raises(ValueError):
            sanitize_string("<script>alert(1)</script>")

    def test_too_long(self):
        with pytest.raises(ValueError):
            sanitize_string("x" * 5000)

    def test_javascript_protocol(self):
        with pytest.raises(ValueError):
            sanitize_string("javascript:void(0)")


class TestSafeFilename:
    def test_valid(self):
        assert safe_filename("report.pdf") == "report.pdf"

    def test_path_traversal(self):
        with pytest.raises(ValueError):
            safe_filename("../../../etc/passwd")

    def test_empty(self):
        with pytest.raises(ValueError):
            safe_filename("")


class TestSecureRandom:
    def test_token_length(self):
        t = generate_secure_token(16)
        assert len(t) == 32  # hex

    def test_id_format(self):
        i = generate_id()
        assert len(i) == 16
        assert i.isalnum()


class TestSecureCompare:
    def test_equal(self):
        assert secure_compare("abc", "abc")

    def test_different(self):
        assert not secure_compare("abc", "def")
