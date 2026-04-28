import pytest
from app.config import Settings

class TestSettings:
    def test_default_values(self, monkeypatch):
        monkeypatch.delenv("DATABASE_URL", raising=False)
        monkeypatch.delenv("SECRET_KEY", raising=False)
        monkeypatch.delenv("ALGORITHM", raising=False)
        monkeypatch.delenv("ACCESS_TOKEN_EXPIRE_MINUTES", raising=False)
        
        settings = Settings()
        
        assert settings.DATABASE_URL is not None
        assert settings.SECRET_KEY is not None
        assert settings.ALGORITHM == "HS256"
        assert settings.ACCESS_TOKEN_EXPIRE_MINUTES == 30

    def test_algorithm_default(self, monkeypatch):
        monkeypatch.delenv("ALGORITHM", raising=False)
        settings = Settings()
        assert settings.ALGORITHM == "HS256"

    def test_token_expiry_default(self, monkeypatch):
        monkeypatch.delenv("ACCESS_TOKEN_EXPIRE_MINUTES", raising=False)
        settings = Settings()
        assert settings.ACCESS_TOKEN_EXPIRE_MINUTES == 30

    def test_env_file_loading(self, tmp_path, monkeypatch):
        env_file = tmp_path / ".env"
        env_file.write_text("SECRET_KEY=testsecret123\nACCESS_TOKEN_EXPIRE_MINUTES=60\n")
        
        monkeypatch.chdir(tmp_path)
        settings = Settings()
        
        assert settings.SECRET_KEY == "testsecret123"
        assert settings.ACCESS_TOKEN_EXPIRE_MINUTES == 60
