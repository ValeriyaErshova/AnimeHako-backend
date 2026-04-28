import pytest
from pydantic import ValidationError
from app.schemas import (
    UserRegister, UserLogin, UserResponse, Token,
    AnimeListItem, AnimeDetail, AnimeListResponse,
    UserAnimeCreate, UserAnimeUpdate, UserAnimeResponse,
    ReviewResponse, ProfileUpdate, GenreResponse, TagResponse
)
from decimal import Decimal

class TestUserSchemas:
    def test_user_register_valid(self):
        data = UserRegister(email="test@example.com", username="testuser", password="password123")
        assert data.email == "test@example.com"
        assert data.username == "testuser"

    def test_user_register_invalid_email(self):
        with pytest.raises(ValidationError):
            UserRegister(email="invalid-email", username="testuser", password="password123")

    def test_user_register_short_username(self):
        with pytest.raises(ValidationError):
            UserRegister(email="test@example.com", username="ab", password="password123")

    def test_user_register_short_password(self):
        with pytest.raises(ValidationError):
            UserRegister(email="test@example.com", username="testuser", password="12345")

    def test_user_login_valid(self):
        data = UserLogin(email="test@example.com", password="password123")
        assert data.email == "test@example.com"

    def test_user_login_invalid_email(self):
        with pytest.raises(ValidationError):
            UserLogin(email="not-an-email", password="password123")

class TestAnimeSchemas:
    def test_anime_list_item_valid(self):
        data = AnimeListItem(
            id=1,
            title="Test Anime",
            rating=Decimal("8.5"),
            year=2023,
            episodes=12,
            genres=["Action", "Adventure"]
        )
        assert data.title == "Test Anime"
        assert data.rating == Decimal("8.5")

    def test_anime_detail_valid(self):
        data = AnimeDetail(
            id=1,
            title="Test Anime",
            title_en="Test Anime EN",
            title_jp="テストアニメ",
            poster="http://example.com/poster.jpg",
            cover="http://example.com/cover.jpg",
            description="A great anime",
            rating=Decimal("8.5"),
            year=2023,
            season="spring",
            status="finished",
            episodes=12,
            duration=24,
            studio="Test Studio",
            genres=["Action"],
            tags=["mecha"]
        )
        assert data.studio == "Test Studio"
        assert data.duration == 24

    def test_anime_list_response_valid(self):
        anime = AnimeListItem(id=1, title="Test", genres=["Action"])
        data = AnimeListResponse(data=[anime], page=1, total_pages=1, total=1)
        assert len(data.data) == 1
        assert data.total == 1

class TestUserAnimeSchemas:
    def test_user_anime_create_valid_statuses(self):
        for status in ["watching", "completed", "dropped", "planned"]:
            data = UserAnimeCreate(anime_id=1, status=status)
            assert data.status == status

    def test_user_anime_create_invalid_status(self):
        with pytest.raises(ValidationError):
            UserAnimeCreate(anime_id=1, status="invalid")

    def test_user_anime_create_score_bounds(self):
        data = UserAnimeCreate(anime_id=1, status="watching", score=10)
        assert data.score == 10

    def test_user_anime_create_score_too_high(self):
        with pytest.raises(ValidationError):
            UserAnimeCreate(anime_id=1, status="watching", score=11)

    def test_user_anime_create_score_too_low(self):
        with pytest.raises(ValidationError):
            UserAnimeCreate(anime_id=1, status="watching", score=0)

    def test_user_anime_update_partial(self):
        data = UserAnimeUpdate(status="completed")
        assert data.status == "completed"
        assert data.score is None

class TestReviewSchemas:
    def test_review_response_valid(self):
        data = ReviewResponse(
            id=1,
            anime_id=1,
            author_name="TestUser",
            title="Great anime",
            content="Really enjoyed it",
            score=9
        )
        assert data.title == "Great anime"

class TestProfileUpdate:
    def test_profile_update_partial(self):
        data = ProfileUpdate(username="newname")
        assert data.username == "newname"
        assert data.avatar is None

    def test_profile_update_short_username(self):
        with pytest.raises(ValidationError):
            ProfileUpdate(username="ab")

class TestGenreTagSchemas:
    def test_genre_response(self):
        data = GenreResponse(id=1, name="Action", slug="action")
        assert data.slug == "action"

    def test_tag_response(self):
        data = TagResponse(id=1, name="Mecha", slug="mecha")
        assert data.slug == "mecha"
