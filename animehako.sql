--
-- PostgreSQL database dump
--

-- Dumped from database version 18.2
-- Dumped by pg_dump version 18.2

-- Started on 2026-04-11 20:13:40

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- TOC entry 4 (class 2615 OID 2200)
-- Name: public; Type: SCHEMA; Schema: -; Owner: pg_database_owner
--

CREATE SCHEMA public;


ALTER SCHEMA public OWNER TO pg_database_owner;

--
-- TOC entry 4902 (class 0 OID 0)
-- Dependencies: 4
-- Name: SCHEMA public; Type: COMMENT; Schema: -; Owner: pg_database_owner
--

COMMENT ON SCHEMA public IS 'standard public schema';

--
-- TOC entry 1 (class 1255 OID 16384)
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    avatar VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


--
-- TOC entry 2 (class 1255 OID 16385)
-- Name: anime; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.anime (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    title_en VARCHAR(255),
    title_jp VARCHAR(255),
    poster VARCHAR(500),
    cover VARCHAR(500),
    description TEXT,
    rating DECIMAL(3,1),
    year INTEGER,
    season VARCHAR(20),
    status VARCHAR(20),
    episodes INTEGER,
    duration INTEGER,
    studio VARCHAR(255),
    external_id VARCHAR(100) UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_anime_rating ON public.anime (rating);
CREATE INDEX idx_anime_year ON public.anime (year);


--
-- TOC entry 3 (class 1255 OID 16386)
-- Name: user_anime; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.user_anime (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES public.users(id) ON DELETE CASCADE,
    anime_id INTEGER REFERENCES public.anime(id) ON DELETE CASCADE,
    status VARCHAR(20),
    score INTEGER,
    episodes_watched INTEGER DEFAULT 0,
    is_favorite BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (user_id, anime_id)
);

CREATE INDEX idx_user_anime_user_id ON public.user_anime (user_id);
CREATE INDEX idx_user_anime_anime_id ON public.user_anime (anime_id);
CREATE INDEX idx_user_anime_status ON public.user_anime (status);


--
-- TOC entry 4 (class 1255 OID 16387)
-- Name: reviews; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.reviews (
    id SERIAL PRIMARY KEY,
    anime_id INTEGER REFERENCES public.anime(id) ON DELETE CASCADE,
    author_name VARCHAR(255) NOT NULL,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    score INTEGER,
    external_id VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


--
-- TOC entry 5 (class 1255 OID 16388)
-- Name: screenshots; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.screenshots (
    id SERIAL PRIMARY KEY,
    anime_id INTEGER REFERENCES public.anime(id) ON DELETE CASCADE,
    url VARCHAR(500) NOT NULL
);


--
-- TOC entry 6 (class 1255 OID 16389)
-- Name: genres; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.genres (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL
);


--
-- TOC entry 7 (class 1255 OID 16390)
-- Name: tags; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.tags (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL
);


--
-- TOC entry 8 (class 1255 OID 16391)
-- Name: anime_genres; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.anime_genres (
    anime_id INTEGER REFERENCES public.anime(id) ON DELETE CASCADE,
    genre_id INTEGER REFERENCES public.genres(id) ON DELETE CASCADE,
    PRIMARY KEY (anime_id, genre_id)
);


--
-- TOC entry 9 (class 1255 OID 16392)
-- Name: anime_tags; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.anime_tags (
    anime_id INTEGER REFERENCES public.anime(id) ON DELETE CASCADE,
    tag_id INTEGER REFERENCES public.tags(id) ON DELETE CASCADE,
    PRIMARY KEY (anime_id, tag_id)
);

--
-- PostgreSQL database dump complete
--
