import pytest
from app.models import User
from app.auth import get_password_hash

class TestAuthEndpoints:
    def test_register_success(self, client):
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "new@example.com",
                "username": "newuser",
                "password": "password123"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert data["user"]["email"] == "new@example.com"

    def test_register_duplicate_email(self, client, test_user):
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "username": "anotheruser",
                "password": "password123"
            }
        )
        assert response.status_code == 400

    def test_register_duplicate_username(self, client, test_user):
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "another@example.com",
                "username": "testuser",
                "password": "password123"
            }
        )
        assert response.status_code == 400

    def test_login_success(self, client, test_user):
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "test@example.com",
                "password": "password123"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "token" in data

    def test_login_invalid_email(self, client):
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "wrong@example.com",
                "password": "password123"
            }
        )
        assert response.status_code == 401

    def test_login_invalid_password(self, client, test_user):
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "test@example.com",
                "password": "wrongpassword"
            }
        )
        assert response.status_code == 401

class TestAnimeEndpoints:
    def test_get_anime_list(self, client, test_anime):
        response = client.get("/api/v1/anime")
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "page" in data
        assert len(data["data"]) > 0

    def test_get_anime_list_pagination(self, client, test_anime):
        response = client.get("/api/v1/anime?page=1&limit=10")
        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 1
        assert data["total_pages"] >= 1

    def test_get_anime_list_search(self, client, test_anime):
        response = client.get("/api/v1/anime?search=Test")
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) > 0

    def test_get_anime_detail(self, client, test_anime):
        response = client.get(f"/api/v1/anime/{test_anime.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Test Anime"

    def test_get_anime_detail_not_found(self, client):
        response = client.get("/api/v1/anime/99999")
        assert response.status_code == 404

    def test_get_screenshots(self, client, test_anime):
        response = client.get(f"/api/v1/anime/{test_anime.id}/screenshots")
        assert response.status_code == 200
        data = response.json()
        assert "screenshots" in data

    def test_get_anime_reviews(self, client, test_anime):
        response = client.get(f"/api/v1/anime/{test_anime.id}/reviews")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

class TestGenresTagsEndpoints:
    def test_get_genres(self, client, db):
        response = client.get("/api/v1/genres")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_get_tags(self, client, db):
        response = client.get("/api/v1/tags")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

class TestUserEndpoints:
    def test_get_profile(self, client, auth_headers, test_user):
        response = client.get("/api/v1/user/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "test@example.com"

    def test_get_profile_unauthorized(self, client):
        response = client.get("/api/v1/user/me")
        assert response.status_code == 403

    def test_update_profile(self, client, auth_headers, test_user):
        response = client.patch(
            "/api/v1/user/me",
            headers=auth_headers,
            json={"username": "updateduser"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "updateduser"

    def test_update_profile_duplicate_username(self, client, db, auth_headers, test_user):
        user2 = User(email="user2@example.com", username="user2", password_hash=get_password_hash("pass123"))
        db.add(user2)
        db.commit()
        
        response = client.patch(
            "/api/v1/user/me",
            headers=auth_headers,
            json={"username": "user2"}
        )
        assert response.status_code == 400

    def test_get_user_anime_list(self, client, auth_headers, test_user_anime):
        response = client.get("/api/v1/user/anime", headers=auth_headers)
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_get_user_anime_list_filter_status(self, client, auth_headers, test_user_anime):
        response = client.get("/api/v1/user/anime?status=watching", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert all(item["status"] == "watching" for item in data)

    def test_add_to_list(self, client, auth_headers, test_anime):
        response = client.post(
            "/api/v1/user/anime",
            headers=auth_headers,
            json={"anime_id": test_anime.id, "status": "completed", "score": 9}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
        assert data["score"] == 9

    def test_add_to_list_anime_not_found(self, client, auth_headers):
        response = client.post(
            "/api/v1/user/anime",
            headers=auth_headers,
            json={"anime_id": 99999, "status": "watching"}
        )
        assert response.status_code == 404

    def test_add_to_list_duplicate(self, client, auth_headers, test_user_anime):
        response = client.post(
            "/api/v1/user/anime",
            headers=auth_headers,
            json={"anime_id": test_user_anime.anime_id, "status": "completed"}
        )
        assert response.status_code == 400

    def test_update_list_entry(self, client, auth_headers, test_user_anime):
        response = client.patch(
            f"/api/v1/user/anime/{test_user_anime.anime_id}",
            headers=auth_headers,
            json={"status": "completed", "score": 10}
        )
        assert response.status_code == 200

    def test_update_list_entry_not_found(self, client, auth_headers):
        response = client.patch(
            "/api/v1/user/anime/99999",
            headers=auth_headers,
            json={"status": "completed"}
        )
        assert response.status_code == 404

    def test_remove_from_list(self, client, auth_headers, test_user_anime):
        response = client.delete(
            f"/api/v1/user/anime/{test_user_anime.anime_id}",
            headers=auth_headers
        )
        assert response.status_code == 200

    def test_remove_from_list_not_found(self, client, auth_headers):
        response = client.delete(
            "/api/v1/user/anime/99999",
            headers=auth_headers
        )
        assert response.status_code == 404

    def test_add_to_favorites(self, client, auth_headers, test_user_anime):
        response = client.post(
            f"/api/v1/user/favorites/{test_user_anime.anime_id}",
            headers=auth_headers
        )
        assert response.status_code == 200

    def test_remove_from_favorites(self, client, auth_headers, test_user_anime):
        response = client.delete(
            f"/api/v1/user/favorites/{test_user_anime.anime_id}",
            headers=auth_headers
        )
        assert response.status_code == 200
