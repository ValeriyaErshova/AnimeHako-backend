--
-- PostgreSQL database dump
--

\restrict d550miqPPwKbpRpjh6p9yrCpU3T8RJ1oTqVZKjdICocyHfojYFTR7P44xtRB2gj

-- Dumped from database version 18.2
-- Dumped by pg_dump version 18.2

-- Started on 2026-04-03 14:48:20

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
-- TOC entry 5 (class 2615 OID 2200)
-- Name: public; Type: SCHEMA; Schema: -; Owner: pg_database_owner
--

CREATE SCHEMA public;


ALTER SCHEMA public OWNER TO pg_database_owner;

--
-- TOC entry 5069 (class 0 OID 0)
-- Dependencies: 5
-- Name: SCHEMA public; Type: COMMENT; Schema: -; Owner: pg_database_owner
--

COMMENT ON SCHEMA public IS 'standard public schema';


--
-- TOC entry 274 (class 1255 OID 17034)
-- Name: hash_password(text); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.hash_password(p_password text) RETURNS text
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN crypt(p_password, gen_salt('bf'));
END;
$$;


ALTER FUNCTION public.hash_password(p_password text) OWNER TO postgres;

--
-- TOC entry 273 (class 1255 OID 17032)
-- Name: update_updated_at_column(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.update_updated_at_column() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.update_updated_at_column() OWNER TO postgres;

--
-- TOC entry 275 (class 1255 OID 17035)
-- Name: verify_password(text, text); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.verify_password(p_password text, p_hash text) RETURNS boolean
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN p_hash = crypt(p_password, p_hash);
END;
$$;


ALTER FUNCTION public.verify_password(p_password text, p_hash text) OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 223 (class 1259 OID 16885)
-- Name: anime; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.anime (
    id integer NOT NULL,
    title character varying(255) NOT NULL,
    title_en character varying(255),
    title_jp character varying(255),
    poster character varying(500),
    cover character varying(500),
    description text,
    rating numeric(3,1),
    year integer,
    season character varying(20),
    status character varying(20),
    episodes integer,
    duration integer,
    studio character varying(255),
    external_id character varying(100),
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.anime OWNER TO postgres;

--
-- TOC entry 234 (class 1259 OID 16992)
-- Name: anime_genres; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.anime_genres (
    anime_id integer NOT NULL,
    genre_id integer NOT NULL
);


ALTER TABLE public.anime_genres OWNER TO postgres;

--
-- TOC entry 222 (class 1259 OID 16884)
-- Name: anime_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.anime_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.anime_id_seq OWNER TO postgres;

--
-- TOC entry 5070 (class 0 OID 0)
-- Dependencies: 222
-- Name: anime_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.anime_id_seq OWNED BY public.anime.id;


--
-- TOC entry 235 (class 1259 OID 17009)
-- Name: anime_tags; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.anime_tags (
    anime_id integer NOT NULL,
    tag_id integer NOT NULL
);


ALTER TABLE public.anime_tags OWNER TO postgres;

--
-- TOC entry 231 (class 1259 OID 16965)
-- Name: genres; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.genres (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    slug character varying(100) NOT NULL
);


ALTER TABLE public.genres OWNER TO postgres;

--
-- TOC entry 230 (class 1259 OID 16964)
-- Name: genres_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.genres_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.genres_id_seq OWNER TO postgres;

--
-- TOC entry 5071 (class 0 OID 0)
-- Dependencies: 230
-- Name: genres_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.genres_id_seq OWNED BY public.genres.id;


--
-- TOC entry 227 (class 1259 OID 16927)
-- Name: reviews; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.reviews (
    id integer NOT NULL,
    anime_id integer NOT NULL,
    author_name character varying(255) NOT NULL,
    title character varying(255) NOT NULL,
    content text NOT NULL,
    score integer,
    external_id character varying(100),
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT reviews_score_check CHECK (((score >= 1) AND (score <= 10)))
);


ALTER TABLE public.reviews OWNER TO postgres;

--
-- TOC entry 226 (class 1259 OID 16926)
-- Name: reviews_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.reviews_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.reviews_id_seq OWNER TO postgres;

--
-- TOC entry 5072 (class 0 OID 0)
-- Dependencies: 226
-- Name: reviews_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.reviews_id_seq OWNED BY public.reviews.id;


--
-- TOC entry 229 (class 1259 OID 16948)
-- Name: screenshots; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.screenshots (
    id integer NOT NULL,
    anime_id integer NOT NULL,
    url character varying(500) NOT NULL
);


ALTER TABLE public.screenshots OWNER TO postgres;

--
-- TOC entry 228 (class 1259 OID 16947)
-- Name: screenshots_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.screenshots_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.screenshots_id_seq OWNER TO postgres;

--
-- TOC entry 5073 (class 0 OID 0)
-- Dependencies: 228
-- Name: screenshots_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.screenshots_id_seq OWNED BY public.screenshots.id;


--
-- TOC entry 233 (class 1259 OID 16979)
-- Name: tags; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.tags (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    slug character varying(100) NOT NULL
);


ALTER TABLE public.tags OWNER TO postgres;

--
-- TOC entry 232 (class 1259 OID 16978)
-- Name: tags_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.tags_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.tags_id_seq OWNER TO postgres;

--
-- TOC entry 5074 (class 0 OID 0)
-- Dependencies: 232
-- Name: tags_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.tags_id_seq OWNED BY public.tags.id;


--
-- TOC entry 225 (class 1259 OID 16899)
-- Name: user_anime; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.user_anime (
    id integer NOT NULL,
    user_id integer NOT NULL,
    anime_id integer NOT NULL,
    status character varying(20),
    score integer,
    episodes_watched integer DEFAULT 0,
    is_favorite boolean DEFAULT false,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT user_anime_score_check CHECK (((score >= 1) AND (score <= 10))),
    CONSTRAINT user_anime_status_check CHECK (((status)::text = ANY ((ARRAY['watching'::character varying, 'completed'::character varying, 'dropped'::character varying, 'planned'::character varying])::text[])))
);


ALTER TABLE public.user_anime OWNER TO postgres;

--
-- TOC entry 224 (class 1259 OID 16898)
-- Name: user_anime_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.user_anime_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.user_anime_id_seq OWNER TO postgres;

--
-- TOC entry 5075 (class 0 OID 0)
-- Dependencies: 224
-- Name: user_anime_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.user_anime_id_seq OWNED BY public.user_anime.id;


--
-- TOC entry 221 (class 1259 OID 16867)
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    id integer NOT NULL,
    email character varying(255) NOT NULL,
    username character varying(50) NOT NULL,
    password_hash character varying(255) NOT NULL,
    avatar character varying(500),
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.users OWNER TO postgres;

--
-- TOC entry 220 (class 1259 OID 16866)
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_id_seq OWNER TO postgres;

--
-- TOC entry 5076 (class 0 OID 0)
-- Dependencies: 220
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- TOC entry 4836 (class 2604 OID 16888)
-- Name: anime id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.anime ALTER COLUMN id SET DEFAULT nextval('public.anime_id_seq'::regclass);


--
-- TOC entry 4846 (class 2604 OID 16968)
-- Name: genres id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.genres ALTER COLUMN id SET DEFAULT nextval('public.genres_id_seq'::regclass);


--
-- TOC entry 4843 (class 2604 OID 16930)
-- Name: reviews id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reviews ALTER COLUMN id SET DEFAULT nextval('public.reviews_id_seq'::regclass);


--
-- TOC entry 4845 (class 2604 OID 16951)
-- Name: screenshots id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.screenshots ALTER COLUMN id SET DEFAULT nextval('public.screenshots_id_seq'::regclass);


--
-- TOC entry 4847 (class 2604 OID 16982)
-- Name: tags id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tags ALTER COLUMN id SET DEFAULT nextval('public.tags_id_seq'::regclass);


--
-- TOC entry 4838 (class 2604 OID 16902)
-- Name: user_anime id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_anime ALTER COLUMN id SET DEFAULT nextval('public.user_anime_id_seq'::regclass);


--
-- TOC entry 4834 (class 2604 OID 16870)
-- Name: users id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- TOC entry 5051 (class 0 OID 16885)
-- Dependencies: 223
-- Data for Name: anime; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.anime (id, title, title_en, title_jp, poster, cover, description, rating, year, season, status, episodes, duration, studio, external_id, created_at) FROM stdin;
1	Атака Титанов	Attack on Titan	\N	\N	\N	История о том, как человечество борется с гигантскими титанами.	9.0	2013	\N	\N	25	\N	WIT Studio	\N	2026-04-02 17:46:01.72107
2	Клинок, рассекающий демонов	Demon Slayer	\N	\N	\N	Танджиро становится охотником на демонов, чтобы спасти свою сестру.	8.8	2019	\N	\N	26	\N	ufotable	\N	2026-04-02 17:46:01.72107
3	Ванпанчмен	One Punch Man	\N	\N	\N	Сайтама может победить любого противника одним ударом.	8.7	2015	\N	\N	12	\N	Madhouse	\N	2026-04-02 17:46:01.72107
4	Моя геройская академия	My Hero Academia	\N	\N	\N	В мире, где у большинства есть суперсилы, мальчик без силы мечтает стать героем.	8.5	2016	\N	\N	13	\N	Bones	\N	2026-04-02 17:46:01.72107
5	Реинкарнация безработного	Mushoku Tensei	\N	\N	\N	34-летний безработный перерождается в мире магии.	8.6	2021	\N	\N	11	\N	Studio Bind	\N	2026-04-02 17:46:01.72107
6	Магическая битва	Jujutsu Kaisen	\N	\N	\N	Итадори Юджи проглатывает палец проклятия и становится охотником на проклятия.	8.9	2020	\N	\N	24	\N	MAPPA	\N	2026-04-02 17:46:01.72107
7	Атака Титанов	Attack on Titan	\N	\N	\N	\N	9.0	2013	\N	\N	25	\N	\N	\N	2026-04-02 23:05:35.067713
8	Клинок, рассекающий демонов	Demon Slayer	\N	\N	\N	\N	8.8	2019	\N	\N	26	\N	\N	\N	2026-04-02 23:05:35.067713
9	Ванпанчмен	One Punch Man	\N	\N	\N	\N	8.7	2015	\N	\N	12	\N	\N	\N	2026-04-02 23:05:35.067713
10	Атака Титанов	Attack on Titan	\N	\N	\N	\N	9.0	2013	\N	\N	25	\N	\N	\N	2026-04-02 23:29:02.962682
11	Клинок, рассекающий демонов	Demon Slayer	\N	\N	\N	\N	8.8	2019	\N	\N	26	\N	\N	\N	2026-04-02 23:29:02.962682
12	Ванпанчмен	One Punch Man	\N	\N	\N	\N	8.7	2015	\N	\N	12	\N	\N	\N	2026-04-02 23:29:02.962682
\.


--
-- TOC entry 5062 (class 0 OID 16992)
-- Dependencies: 234
-- Data for Name: anime_genres; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.anime_genres (anime_id, genre_id) FROM stdin;
1	1
1	4
2	1
2	5
3	1
3	3
4	1
4	3
4	6
5	2
5	5
6	1
6	2
\.


--
-- TOC entry 5063 (class 0 OID 17009)
-- Dependencies: 235
-- Data for Name: anime_tags; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.anime_tags (anime_id, tag_id) FROM stdin;
\.


--
-- TOC entry 5059 (class 0 OID 16965)
-- Dependencies: 231
-- Data for Name: genres; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.genres (id, name, slug) FROM stdin;
1	Экшен	akshn
2	Фэнтези	fentezi
3	Комедия	komediya
4	Драма	drama
5	Приключения	priklyucheniya
6	Суперсилы	supersily
\.


--
-- TOC entry 5055 (class 0 OID 16927)
-- Dependencies: 227
-- Data for Name: reviews; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.reviews (id, anime_id, author_name, title, content, score, external_id, created_at) FROM stdin;
1	1	AnimeCritic	Шедевр современности	Атака Титанов перевернула моё представление об аниме...	10	\N	2026-04-02 17:46:01.72107
2	1	ShingekiFan	Лучшее аниме десятилетия	Невероятный сюжет и персонажи...	10	\N	2026-04-02 17:46:01.72107
3	2	DemonSlayerLover	Визуальный шедевр	Анимация от ufotable просто божественна...	9	\N	2026-04-02 17:46:01.72107
\.


--
-- TOC entry 5057 (class 0 OID 16948)
-- Dependencies: 229
-- Data for Name: screenshots; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.screenshots (id, anime_id, url) FROM stdin;
1	1	https://example.com/aot_screenshot1.jpg
2	1	https://example.com/aot_screenshot2.jpg
3	2	https://example.com/ds_screenshot1.jpg
\.


--
-- TOC entry 5061 (class 0 OID 16979)
-- Dependencies: 233
-- Data for Name: tags; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.tags (id, name, slug) FROM stdin;
\.


--
-- TOC entry 5053 (class 0 OID 16899)
-- Dependencies: 225
-- Data for Name: user_anime; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.user_anime (id, user_id, anime_id, status, score, episodes_watched, is_favorite, created_at, updated_at) FROM stdin;
\.


--
-- TOC entry 5049 (class 0 OID 16867)
-- Dependencies: 221
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.users (id, email, username, password_hash, avatar, created_at) FROM stdin;
1	test@mail.com	testuser	8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92	\N	2026-04-02 20:49:03.895795
\.


--
-- TOC entry 5077 (class 0 OID 0)
-- Dependencies: 222
-- Name: anime_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.anime_id_seq', 12, true);


--
-- TOC entry 5078 (class 0 OID 0)
-- Dependencies: 230
-- Name: genres_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.genres_id_seq', 6, true);


--
-- TOC entry 5079 (class 0 OID 0)
-- Dependencies: 226
-- Name: reviews_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.reviews_id_seq', 3, true);


--
-- TOC entry 5080 (class 0 OID 0)
-- Dependencies: 228
-- Name: screenshots_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.screenshots_id_seq', 3, true);


--
-- TOC entry 5081 (class 0 OID 0)
-- Dependencies: 232
-- Name: tags_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.tags_id_seq', 1, false);


--
-- TOC entry 5082 (class 0 OID 0)
-- Dependencies: 224
-- Name: user_anime_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.user_anime_id_seq', 1, false);


--
-- TOC entry 5083 (class 0 OID 0)
-- Dependencies: 220
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.users_id_seq', 1, true);


--
-- TOC entry 4858 (class 2606 OID 16897)
-- Name: anime anime_external_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.anime
    ADD CONSTRAINT anime_external_id_key UNIQUE (external_id);


--
-- TOC entry 4889 (class 2606 OID 16998)
-- Name: anime_genres anime_genres_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.anime_genres
    ADD CONSTRAINT anime_genres_pkey PRIMARY KEY (anime_id, genre_id);


--
-- TOC entry 4860 (class 2606 OID 16895)
-- Name: anime anime_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.anime
    ADD CONSTRAINT anime_pkey PRIMARY KEY (id);


--
-- TOC entry 4891 (class 2606 OID 17015)
-- Name: anime_tags anime_tags_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.anime_tags
    ADD CONSTRAINT anime_tags_pkey PRIMARY KEY (anime_id, tag_id);


--
-- TOC entry 4877 (class 2606 OID 16975)
-- Name: genres genres_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.genres
    ADD CONSTRAINT genres_name_key UNIQUE (name);


--
-- TOC entry 4879 (class 2606 OID 16973)
-- Name: genres genres_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.genres
    ADD CONSTRAINT genres_pkey PRIMARY KEY (id);


--
-- TOC entry 4881 (class 2606 OID 16977)
-- Name: genres genres_slug_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.genres
    ADD CONSTRAINT genres_slug_key UNIQUE (slug);


--
-- TOC entry 4873 (class 2606 OID 16941)
-- Name: reviews reviews_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reviews
    ADD CONSTRAINT reviews_pkey PRIMARY KEY (id);


--
-- TOC entry 4875 (class 2606 OID 16958)
-- Name: screenshots screenshots_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.screenshots
    ADD CONSTRAINT screenshots_pkey PRIMARY KEY (id);


--
-- TOC entry 4883 (class 2606 OID 16989)
-- Name: tags tags_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tags
    ADD CONSTRAINT tags_name_key UNIQUE (name);


--
-- TOC entry 4885 (class 2606 OID 16987)
-- Name: tags tags_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tags
    ADD CONSTRAINT tags_pkey PRIMARY KEY (id);


--
-- TOC entry 4887 (class 2606 OID 16991)
-- Name: tags tags_slug_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tags
    ADD CONSTRAINT tags_slug_key UNIQUE (slug);


--
-- TOC entry 4868 (class 2606 OID 16913)
-- Name: user_anime user_anime_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_anime
    ADD CONSTRAINT user_anime_pkey PRIMARY KEY (id);


--
-- TOC entry 4870 (class 2606 OID 16915)
-- Name: user_anime user_anime_user_id_anime_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_anime
    ADD CONSTRAINT user_anime_user_id_anime_id_key UNIQUE (user_id, anime_id);


--
-- TOC entry 4852 (class 2606 OID 16881)
-- Name: users users_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- TOC entry 4854 (class 2606 OID 16879)
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- TOC entry 4856 (class 2606 OID 16883)
-- Name: users users_username_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_username_key UNIQUE (username);


--
-- TOC entry 4861 (class 1259 OID 17031)
-- Name: idx_anime_external_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_anime_external_id ON public.anime USING btree (external_id);


--
-- TOC entry 4862 (class 1259 OID 17029)
-- Name: idx_anime_rating; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_anime_rating ON public.anime USING btree (rating DESC);


--
-- TOC entry 4863 (class 1259 OID 17030)
-- Name: idx_anime_year; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_anime_year ON public.anime USING btree (year);


--
-- TOC entry 4871 (class 1259 OID 17028)
-- Name: idx_reviews_anime_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_reviews_anime_id ON public.reviews USING btree (anime_id);


--
-- TOC entry 4864 (class 1259 OID 17027)
-- Name: idx_user_anime_anime_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_user_anime_anime_id ON public.user_anime USING btree (anime_id);


--
-- TOC entry 4865 (class 1259 OID 17036)
-- Name: idx_user_anime_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_user_anime_status ON public.user_anime USING btree (status);


--
-- TOC entry 4866 (class 1259 OID 17026)
-- Name: idx_user_anime_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_user_anime_user_id ON public.user_anime USING btree (user_id);


--
-- TOC entry 4900 (class 2620 OID 17033)
-- Name: user_anime update_user_anime_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_user_anime_updated_at BEFORE UPDATE ON public.user_anime FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- TOC entry 4896 (class 2606 OID 16999)
-- Name: anime_genres anime_genres_anime_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.anime_genres
    ADD CONSTRAINT anime_genres_anime_id_fkey FOREIGN KEY (anime_id) REFERENCES public.anime(id) ON DELETE CASCADE;


--
-- TOC entry 4897 (class 2606 OID 17004)
-- Name: anime_genres anime_genres_genre_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.anime_genres
    ADD CONSTRAINT anime_genres_genre_id_fkey FOREIGN KEY (genre_id) REFERENCES public.genres(id) ON DELETE CASCADE;


--
-- TOC entry 4898 (class 2606 OID 17016)
-- Name: anime_tags anime_tags_anime_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.anime_tags
    ADD CONSTRAINT anime_tags_anime_id_fkey FOREIGN KEY (anime_id) REFERENCES public.anime(id) ON DELETE CASCADE;


--
-- TOC entry 4899 (class 2606 OID 17021)
-- Name: anime_tags anime_tags_tag_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.anime_tags
    ADD CONSTRAINT anime_tags_tag_id_fkey FOREIGN KEY (tag_id) REFERENCES public.tags(id) ON DELETE CASCADE;


--
-- TOC entry 4894 (class 2606 OID 16942)
-- Name: reviews reviews_anime_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reviews
    ADD CONSTRAINT reviews_anime_id_fkey FOREIGN KEY (anime_id) REFERENCES public.anime(id) ON DELETE CASCADE;


--
-- TOC entry 4895 (class 2606 OID 16959)
-- Name: screenshots screenshots_anime_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.screenshots
    ADD CONSTRAINT screenshots_anime_id_fkey FOREIGN KEY (anime_id) REFERENCES public.anime(id) ON DELETE CASCADE;


--
-- TOC entry 4892 (class 2606 OID 16921)
-- Name: user_anime user_anime_anime_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_anime
    ADD CONSTRAINT user_anime_anime_id_fkey FOREIGN KEY (anime_id) REFERENCES public.anime(id) ON DELETE CASCADE;


--
-- TOC entry 4893 (class 2606 OID 16916)
-- Name: user_anime user_anime_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_anime
    ADD CONSTRAINT user_anime_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


-- Completed on 2026-04-03 14:48:20

--
-- PostgreSQL database dump complete
--

\unrestrict d550miqPPwKbpRpjh6p9yrCpU3T8RJ1oTqVZKjdICocyHfojYFTR7P44xtRB2gj

