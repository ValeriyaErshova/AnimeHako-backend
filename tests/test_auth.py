import pytest
from app.auth import verify_password, get_password_hash, create_access_token, decode_token

class TestPasswordHashing:
    def test_password_hash_is_different_from_plain(self):
        password = "testpassword123"
        hashed = get_password_hash(password)
        assert hashed != password

    def test_verify_password_correct(self):
        password = "testpassword123"
        hashed = get_password_hash(password)
        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        password = "testpassword123"
        wrong_password = "wrongpassword"
        hashed = get_password_hash(password)
        assert verify_password(wrong_password, hashed) is False

    def test_hash_is_unique(self):
        password = "testpassword123"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        assert hash1 != hash2

class TestAccessToken:
    def test_create_access_token(self):
        token = create_access_token({"sub": "123"})
        assert isinstance(token, str)
        assert len(token) > 0

    def test_decode_valid_token(self):
        token = create_access_token({"sub": "123"})
        payload = decode_token(token)
        assert payload["sub"] == "123"
        assert "exp" in payload

    def test_decode_invalid_token(self):
        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc_info:
            decode_token("invalid.token.here")
        assert exc_info.value.status_code == 401
