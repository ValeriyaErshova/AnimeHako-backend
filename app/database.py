from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Table, DECIMAL, Index, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.sql import func
from app.config import settings

engine = create_engine(
    "postgresql://postgres:123456@localhost:5432/animehako",
    pool_pre_ping=True
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Связующие таблицы
anime_genres = Table(
    'anime_genres', Base.metadata,
    Column('anime_id', Integer, ForeignKey('anime.id', ondelete='CASCADE'), primary_key=True),
    Column('genre_id', Integer, ForeignKey('genres.id', ondelete='CASCADE'), primary_key=True)
)

anime_tags = Table(
    'anime_tags', Base.metadata,
    Column('anime_id', Integer, ForeignKey('anime.id', ondelete='CASCADE'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id', ondelete='CASCADE'), primary_key=True)
)

# Модели
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    avatar = Column(String(500))
    created_at = Column(DateTime, server_default=func.now())
    user_anime = relationship("UserAnime", back_populates="user", cascade="all, delete-orphan")

class Anime(Base):
    __tablename__ = "anime"
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    title_en = Column(String(255))
    title_jp = Column(String(255))
    poster = Column(String(500))
    cover = Column(String(500))
    description = Column(Text)
    rating = Column(DECIMAL(3, 1))
    year = Column(Integer)
    season = Column(String(20))
    status = Column(String(20))
    episodes = Column(Integer)
    duration = Column(Integer)
    studio = Column(String(255))
    external_id = Column(String(100), unique=True)
    created_at = Column(DateTime, server_default=func.now())

    __table_args__ = (
        Index('idx_anime_rating', 'rating'),
        Index('idx_anime_year', 'year'),
    )

    user_anime = relationship("UserAnime", back_populates="anime", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="anime", cascade="all, delete-orphan")
    screenshots = relationship("Screenshot", back_populates="anime", cascade="all, delete-orphan")
    genres = relationship("Genre", secondary=anime_genres, back_populates="anime")
    tags = relationship("Tag", secondary=anime_tags, back_populates="anime")

class UserAnime(Base):
    __tablename__ = "user_anime"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    anime_id = Column(Integer, ForeignKey("anime.id", ondelete="CASCADE"))
    status = Column(String(20))
    score = Column(Integer)
    episodes_watched = Column(Integer, default=0)
    is_favorite = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index('idx_user_anime_user_id', 'user_id'),
        Index('idx_user_anime_anime_id', 'anime_id'),
        Index('idx_user_anime_status', 'status'),
        UniqueConstraint('user_id', 'anime_id'),
    )

    user = relationship("User", back_populates="user_anime")
    anime = relationship("Anime", back_populates="user_anime")

class Review(Base):
    __tablename__ = "reviews"
    id = Column(Integer, primary_key=True)
    anime_id = Column(Integer, ForeignKey("anime.id", ondelete='CASCADE'))
    author_name = Column(String(255), nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    score = Column(Integer)
    external_id = Column(String(100))
    created_at = Column(DateTime, server_default=func.now())
    anime = relationship("Anime", back_populates="reviews")

class Screenshot(Base):
    __tablename__ = "screenshots"
    id = Column(Integer, primary_key=True)
    anime_id = Column(Integer, ForeignKey("anime.id", ondelete='CASCADE'))
    url = Column(String(500), nullable=False)
    anime = relationship("Anime", back_populates="screenshots")

class Genre(Base):
    __tablename__ = "genres"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    slug = Column(String(100), unique=True, nullable=False)
    anime = relationship("Anime", secondary=anime_genres, back_populates="genres")

class Tag(Base):
    __tablename__ = "tags"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    slug = Column(String(100), unique=True, nullable=False)
    anime = relationship("Anime", secondary=anime_tags, back_populates="tags")