from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc
from typing import Optional, List
from app.database import get_db
from app.database import anime_genres, anime_tags
from app.models import User, Anime, UserAnime, Review, Screenshot, Genre, Tag
from app.schemas import (
    UserRegister, UserLogin, Token, UserResponse, ProfileUpdate,
    AnimeListResponse, AnimeDetail, AnimeListItem,
    UserAnimeCreate, UserAnimeUpdate, UserAnimeResponse,
    ReviewResponse, GenreResponse, TagResponse
)
from app.auth import get_current_user, verify_password, get_password_hash, create_access_token

router = APIRouter()

# ===== Аутентификация =====
@router.post("/api/v1/auth/register", response_model=Token)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(400, "Email already registered")
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(400, "Username already taken")
    
    user = User(email=user_data.email, username=user_data.username, password_hash=get_password_hash(user_data.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_access_token({"sub": user.id})
    return Token(token=token, user=UserResponse.model_validate(user))

@router.post("/api/v1/auth/login", response_model=Token)
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_data.email).first()
    if not user or not verify_password(user_data.password, user.password_hash):
        raise HTTPException(401, "Invalid credentials")
    token = create_access_token({"sub": user.id})
    return Token(token=token, user=UserResponse.model_validate(user))

# ===== Аниме =====
@router.get("/api/v1/anime", response_model=AnimeListResponse)
def get_anime_list(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    genres: Optional[str] = None,
    year: Optional[int] = None,
    sort: Optional[str] = Query(None, pattern="^(rating|year|created)$"),
    db: Session = Depends(get_db)
):
    query = db.query(Anime)
    if search:
        query = query.filter(or_(Anime.title.ilike(f"%{search}%"), Anime.title_en.ilike(f"%{search}%")))
    if genres:
        genre_names = genres.split(",")
        query = query.filter(Anime.genres.any(Genre.name.in_(genre_names)))
    if year:
        query = query.filter(Anime.year == year)
    if sort == "rating":
        query = query.order_by(desc(Anime.rating))
    elif sort == "year":
        query = query.order_by(desc(Anime.year))
    else:
        query = query.order_by(desc(Anime.created_at))
    
    total = query.count()
    total_pages = (total + limit - 1) // limit
    anime_list = query.offset((page - 1) * limit).limit(limit).all()
    
    return AnimeListResponse(
        data=[AnimeListItem(id=a.id, title=a.title, title_en=a.title_en, poster=a.poster,
              rating=a.rating, year=a.year, episodes=a.episodes, genres=[g.name for g in a.genres]) for a in anime_list],
        page=page, total_pages=total_pages, total=total
    )

@router.get("/api/v1/anime/{anime_id}", response_model=AnimeDetail)
def get_anime_detail(anime_id: int, db: Session = Depends(get_db)):
    anime = db.query(Anime).filter(Anime.id == anime_id).first()
    if not anime:
        raise HTTPException(404, "Anime not found")
    return AnimeDetail(id=anime.id, title=anime.title, title_en=anime.title_en, title_jp=anime.title_jp,
        poster=anime.poster, cover=anime.cover, description=anime.description, rating=anime.rating,
        year=anime.year, season=anime.season, status=anime.status, episodes=anime.episodes,
        duration=anime.duration, studio=anime.studio, genres=[g.name for g in anime.genres],
        tags=[t.name for t in anime.tags])

@router.get("/api/v1/anime/{anime_id}/screenshots")
def get_screenshots(anime_id: int, db: Session = Depends(get_db)):
    if not db.query(Anime).filter(Anime.id == anime_id).first():
        raise HTTPException(404, "Anime not found")
    screenshots = db.query(Screenshot).filter(Screenshot.anime_id == anime_id).all()
    return {"screenshots": [s.url for s in screenshots]}

@router.get("/api/v1/anime/{anime_id}/reviews", response_model=List[ReviewResponse])
def get_anime_reviews(anime_id: int, limit: int = Query(20, ge=1), offset: int = Query(0, ge=0), db: Session = Depends(get_db)):
    if not db.query(Anime).filter(Anime.id == anime_id).first():
        raise HTTPException(404, "Anime not found")
    return db.query(Review).filter(Review.anime_id == anime_id).offset(offset).limit(limit).all()

@router.get("/api/v1/genres", response_model=List[GenreResponse])
def get_genres(db: Session = Depends(get_db)):
    return [GenreResponse(id=g.id, name=g.name, slug=g.slug) for g in db.query(Genre).all()]

@router.get("/api/v1/tags", response_model=List[TagResponse])
def get_tags(db: Session = Depends(get_db)):
    return [TagResponse(id=t.id, name=t.name, slug=t.slug) for t in db.query(Tag).all()]

# ===== Обзоры =====
@router.get("/api/v1/reviews/{review_id}", response_model=ReviewResponse)
def get_review(review_id: int, db: Session = Depends(get_db)):
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(404, "Review not found")
    return review

# ===== Пользователь =====
@router.get("/api/v1/user/me", response_model=UserResponse)
def get_profile(current_user: User = Depends(get_current_user)):
    return current_user

@router.patch("/api/v1/user/me", response_model=UserResponse)
def update_profile(profile_data: ProfileUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if profile_data.username:
        if db.query(User).filter(User.username == profile_data.username, User.id != current_user.id).first():
            raise HTTPException(400, "Username already taken")
        current_user.username = profile_data.username
    if profile_data.avatar:
        current_user.avatar = profile_data.avatar
    db.commit()
    db.refresh(current_user)
    return current_user

@router.get("/api/v1/user/anime", response_model=List[UserAnimeResponse])
def get_user_anime(status: Optional[str] = Query(None, pattern="^(watching|completed|dropped|planned)$"), 
                   current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    query = db.query(UserAnime).filter(UserAnime.user_id == current_user.id)
    if status:
        query = query.filter(UserAnime.status == status)
    
    result = []
    for ua in query.all():
        anime = db.query(Anime).filter(Anime.id == ua.anime_id).first()
        result.append(UserAnimeResponse(
            anime_id=ua.anime_id, status=ua.status, score=ua.score,
            episodes_watched=ua.episodes_watched or 0, is_favorite=ua.is_favorite or False,
            anime=AnimeListItem(id=anime.id, title=anime.title, title_en=anime.title_en,
                  poster=anime.poster, rating=anime.rating, year=anime.year,
                  episodes=anime.episodes, genres=[g.name for g in anime.genres]) if anime else None
        ))
    return result

@router.post("/api/v1/user/anime", response_model=UserAnimeResponse)
def add_to_list(data: UserAnimeCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not db.query(Anime).filter(Anime.id == data.anime_id).first():
        raise HTTPException(404, "Anime not found")
    if db.query(UserAnime).filter(UserAnime.user_id == current_user.id, UserAnime.anime_id == data.anime_id).first():
        raise HTTPException(400, "Anime already in your list")
    
    user_anime = UserAnime(user_id=current_user.id, anime_id=data.anime_id, status=data.status,
                           score=data.score, episodes_watched=data.episodes_watched or 0)
    db.add(user_anime)
    db.commit()
    db.refresh(user_anime)
    return UserAnimeResponse(anime_id=user_anime.anime_id, status=user_anime.status,
        score=user_anime.score, episodes_watched=user_anime.episodes_watched,
        is_favorite=user_anime.is_favorite or False)

@router.patch("/api/v1/user/anime/{anime_id}")
def update_list_entry(anime_id: int, data: UserAnimeUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user_anime = db.query(UserAnime).filter(UserAnime.user_id == current_user.id, UserAnime.anime_id == anime_id).first()
    if not user_anime:
        raise HTTPException(404, "Anime not found in your list")
    if data.status is not None:
        user_anime.status = data.status
    if data.score is not None:
        user_anime.score = data.score
    if data.episodes_watched is not None:
        user_anime.episodes_watched = data.episodes_watched
    db.commit()
    return {"message": "Updated successfully"}

@router.delete("/api/v1/user/anime/{anime_id}")
def remove_from_list(anime_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user_anime = db.query(UserAnime).filter(UserAnime.user_id == current_user.id, UserAnime.anime_id == anime_id).first()
    if not user_anime:
        raise HTTPException(404, "Anime not found in your list")
    db.delete(user_anime)
    db.commit()
    return {"message": "Removed from list"}

@router.post("/api/v1/user/favorites/{anime_id}")
def add_to_favorites(anime_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user_anime = db.query(UserAnime).filter(UserAnime.user_id == current_user.id, UserAnime.anime_id == anime_id).first()
    if not user_anime:
        raise HTTPException(404, "Anime not found in your list")
    user_anime.is_favorite = True
    db.commit()
    return {"message": "Added to favorites"}

@router.delete("/api/v1/user/favorites/{anime_id}")
def remove_from_favorites(anime_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user_anime = db.query(UserAnime).filter(UserAnime.user_id == current_user.id, UserAnime.anime_id == anime_id).first()
    if not user_anime:
        raise HTTPException(404, "Anime not found in your list")
    user_anime.is_favorite = False
    db.commit()
    return {"message": "Removed from favorites"}