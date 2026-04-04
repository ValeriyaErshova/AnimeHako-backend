from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

class UserRegister(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    username: str
    avatar: Optional[str] = None
    created_at: Optional[datetime] = None
    class Config: from_attributes = True

class Token(BaseModel):
    token: str
    user: UserResponse

class AnimeListItem(BaseModel):
    id: int
    title: str
    title_en: Optional[str] = None
    poster: Optional[str] = None
    rating: Optional[Decimal] = None
    year: Optional[int] = None
    episodes: Optional[int] = None
    genres: List[str] = []
    class Config: from_attributes = True

class AnimeDetail(BaseModel):
    id: int
    title: str
    title_en: Optional[str] = None
    title_jp: Optional[str] = None
    poster: Optional[str] = None
    cover: Optional[str] = None
    description: Optional[str] = None
    rating: Optional[Decimal] = None
    year: Optional[int] = None
    season: Optional[str] = None
    status: Optional[str] = None
    episodes: Optional[int] = None
    duration: Optional[int] = None
    studio: Optional[str] = None
    genres: List[str] = []
    tags: List[str] = []
    class Config: from_attributes = True

class AnimeListResponse(BaseModel):
    data: List[AnimeListItem]
    page: int
    total_pages: int
    total: int

class UserAnimeCreate(BaseModel):
    anime_id: int
    status: str = Field(..., pattern="^(watching|completed|dropped|planned)$")
    score: Optional[int] = Field(None, ge=1, le=10)
    episodes_watched: Optional[int] = Field(0, ge=0)

class UserAnimeUpdate(BaseModel):
    status: Optional[str] = Field(None, pattern="^(watching|completed|dropped|planned)$")
    score: Optional[int] = Field(None, ge=1, le=10)
    episodes_watched: Optional[int] = Field(None, ge=0)

class UserAnimeResponse(BaseModel):
    anime_id: int
    status: Optional[str] = None
    score: Optional[int] = None
    episodes_watched: int
    is_favorite: bool
    anime: Optional[AnimeListItem] = None
    class Config: from_attributes = True

class ReviewResponse(BaseModel):
    id: int
    anime_id: int
    author_name: str
    title: str
    content: str
    score: Optional[int] = None
    created_at: Optional[datetime] = None
    class Config: from_attributes = True

class ProfileUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    avatar: Optional[str] = None

class GenreResponse(BaseModel):
    id: int
    name: str
    slug: str

class TagResponse(BaseModel):
    id: int
    name: str
    slug: str