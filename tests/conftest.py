import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.database import Base, get_db
from app.main import app
from app.models import User, Anime, Genre, UserAnime
from app.auth import get_password_hash

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

@pytest.fixture
def test_user(db):
    user = User(
        email="test@example.com",
        username="testuser",
        password_hash=get_password_hash("password123")
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture
def test_user_token(client, test_user):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "password123"}
    )
    return response.json()["token"]

@pytest.fixture
def auth_headers(test_user_token):
    return {"Authorization": f"Bearer {test_user_token}"}

@pytest.fixture
def test_anime(db):
    genre = Genre(id=1, name="Action", slug="action")
    db.add(genre)
    
    anime = Anime(
        id=1,
        title="Test Anime",
        title_en="Test Anime EN",
        poster="http://example.com/poster.jpg",
        cover="http://example.com/cover.jpg",
        rating=8.5,
        year=2023,
        episodes=12,
        status="finished",
        external_id="12345"
    )
    db.add(anime)
    db.commit()
    anime.genres.append(genre)
    db.commit()
    db.refresh(anime)
    return anime

@pytest.fixture
def test_user_anime(db, test_user, test_anime):
    user_anime = UserAnime(
        user_id=test_user.id,
        anime_id=test_anime.id,
        status="watching",
        score=8,
        episodes_watched=5
    )
    db.add(user_anime)
    db.commit()
    db.refresh(user_anime)
    return user_anime
