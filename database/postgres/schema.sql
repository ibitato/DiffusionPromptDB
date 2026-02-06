--
-- PostgreSQL database dump
--


-- Dumped from database version 16.10 (Ubuntu 16.10-0ubuntu0.24.04.1)
-- Dumped by pg_dump version 16.10 (Ubuntu 16.10-0ubuntu0.24.04.1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: account_deletion_audit; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.account_deletion_audit (
    id bigint NOT NULL,
    user_id bigint,
    username text,
    email text,
    deleted_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    dump_path text,
    reason text
);


--
-- Name: account_deletion_audit_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.account_deletion_audit_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: account_deletion_audit_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.account_deletion_audit_id_seq OWNED BY public.account_deletion_audit.id;


--
-- Name: art_style_tags; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.art_style_tags (
    prompt_id bigint,
    tag_type text,
    tag_value text
);


--
-- Name: art_styles; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.art_styles (
    prompt_id bigint NOT NULL,
    primary_style text
);


--
-- Name: camera_composition; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.camera_composition (
    prompt_id bigint NOT NULL,
    shot_type text,
    camera_angle text,
    focus_area text
);


--
-- Name: character_ages; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.character_ages (
    prompt_id bigint,
    age_range text
);


--
-- Name: character_attributes; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.character_attributes (
    prompt_id bigint,
    attribute_type text,
    attribute_value text
);


--
-- Name: character_body_types; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.character_body_types (
    prompt_id bigint,
    body_type text
);


--
-- Name: character_eyes; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.character_eyes (
    prompt_id bigint,
    color text,
    shape text
);


--
-- Name: character_genders; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.character_genders (
    prompt_id bigint,
    gender text
);


--
-- Name: character_hair; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.character_hair (
    prompt_id bigint,
    color text,
    style text,
    length text
);


--
-- Name: characters; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.characters (
    prompt_id bigint NOT NULL,
    number_of_people bigint,
    breast_size text
);


--
-- Name: clothing; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.clothing (
    prompt_id bigint NOT NULL,
    style text,
    coverage text
);


--
-- Name: clothing_accessories; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.clothing_accessories (
    prompt_id bigint,
    accessory text
);


--
-- Name: clothing_items; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.clothing_items (
    prompt_id bigint,
    item text
);


--
-- Name: composition_notes; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.composition_notes (
    prompt_id bigint,
    note text
);


--
-- Name: emotions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.emotions (
    prompt_id bigint,
    emotion text
);


--
-- Name: environment_details; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.environment_details (
    prompt_id bigint,
    detail text
);


--
-- Name: lighting; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.lighting (
    prompt_id bigint NOT NULL,
    type text,
    time_of_day text
);


--
-- Name: lighting_quality; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.lighting_quality (
    prompt_id bigint,
    quality text
);


--
-- Name: main_tags; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.main_tags (
    prompt_id bigint,
    tag text,
    tag_order bigint
);


--
-- Name: mood_atmosphere; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.mood_atmosphere (
    prompt_id bigint NOT NULL,
    overall_mood text
);


--
-- Name: nsfw_content; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.nsfw_content (
    prompt_id bigint NOT NULL,
    level text
);


--
-- Name: nsfw_elements; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.nsfw_elements (
    prompt_id bigint,
    element text
);


--
-- Name: pose_actions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.pose_actions (
    prompt_id bigint,
    action text
);


--
-- Name: poses; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.poses (
    prompt_id bigint NOT NULL,
    main_pose text,
    body_position text,
    view_angle text
);


--
-- Name: prompt_references; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.prompt_references (
    prompt_id bigint,
    reference_type text,
    reference_name text
);


--
-- Name: prompts; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.prompts (
    id bigint NOT NULL,
    original_prompt text,
    processed_at timestamp without time zone,
    model_used text,
    input_tokens bigint,
    output_tokens bigint,
    created_by bigint,
    negative_prompt text,
    parameters text,
    rating bigint,
    notes text,
    image_path text,
    thumbnail_path text
);


--
-- Name: prompts_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.prompts ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.prompts_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: relationships; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.relationships (
    prompt_id bigint NOT NULL,
    interaction_type text,
    relationship text,
    pov_perspective text
);


--
-- Name: settings; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.settings (
    prompt_id bigint NOT NULL,
    location_type text,
    indoor_outdoor text,
    specific_place text
);


--
-- Name: sexual_content; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.sexual_content (
    prompt_id bigint NOT NULL,
    genital_visibility text
);


--
-- Name: sexual_details; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.sexual_details (
    prompt_id bigint,
    detail_type text,
    detail_value text
);


--
-- Name: sqlite_stat1; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.sqlite_stat1 (
    tbl text,
    idx text,
    stat text
);


--
-- Name: technical; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.technical (
    prompt_id bigint NOT NULL
);


--
-- Name: technical_details; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.technical_details (
    prompt_id bigint,
    detail_type text,
    detail_value text
);


--
-- Name: user_password_history; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.user_password_history (
    id bigint NOT NULL,
    user_id bigint,
    password_hash text,
    changed_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: user_password_history_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.user_password_history_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: user_password_history_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.user_password_history_id_seq OWNED BY public.user_password_history.id;


--
-- Name: user_preferences; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.user_preferences (
    user_id bigint NOT NULL,
    show_unspecified boolean DEFAULT true,
    my_prompts_only boolean DEFAULT false,
    excluded_tags text DEFAULT '["high quality", "masterpiece", "best quality"]'::text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: user_verification_tokens; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.user_verification_tokens (
    id bigint NOT NULL,
    user_id bigint,
    token_hash text,
    expires_at timestamp without time zone,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: user_verification_tokens_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.user_verification_tokens_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: user_verification_tokens_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.user_verification_tokens_id_seq OWNED BY public.user_verification_tokens.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.users (
    id bigint NOT NULL,
    username text,
    email text,
    password_hash text,
    role text DEFAULT 'user'::text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    last_login timestamp without time zone,
    is_active boolean DEFAULT true,
    full_name text,
    avatar_url text,
    location text,
    language text DEFAULT 'en'::text,
    default_landing_page text DEFAULT 'dashboard'::text,
    must_change_password boolean DEFAULT false,
    password_last_changed timestamp without time zone
);


--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.users_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: account_deletion_audit id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.account_deletion_audit ALTER COLUMN id SET DEFAULT nextval('public.account_deletion_audit_id_seq'::regclass);


--
-- Name: user_password_history id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_password_history ALTER COLUMN id SET DEFAULT nextval('public.user_password_history_id_seq'::regclass);


--
-- Name: user_verification_tokens id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_verification_tokens ALTER COLUMN id SET DEFAULT nextval('public.user_verification_tokens_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Name: prompts idx_16841_prompts_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.prompts
    ADD CONSTRAINT idx_16841_prompts_pkey PRIMARY KEY (id);


--
-- Name: characters idx_16846_characters_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.characters
    ADD CONSTRAINT idx_16846_characters_pkey PRIMARY KEY (prompt_id);


--
-- Name: poses idx_16881_poses_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.poses
    ADD CONSTRAINT idx_16881_poses_pkey PRIMARY KEY (prompt_id);


--
-- Name: clothing idx_16891_clothing_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.clothing
    ADD CONSTRAINT idx_16891_clothing_pkey PRIMARY KEY (prompt_id);


--
-- Name: settings idx_16906_settings_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.settings
    ADD CONSTRAINT idx_16906_settings_pkey PRIMARY KEY (prompt_id);


--
-- Name: lighting idx_16916_lighting_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.lighting
    ADD CONSTRAINT idx_16916_lighting_pkey PRIMARY KEY (prompt_id);


--
-- Name: art_styles idx_16926_art_styles_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.art_styles
    ADD CONSTRAINT idx_16926_art_styles_pkey PRIMARY KEY (prompt_id);


--
-- Name: technical idx_16936_technical_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.technical
    ADD CONSTRAINT idx_16936_technical_pkey PRIMARY KEY (prompt_id);


--
-- Name: nsfw_content idx_16944_nsfw_content_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.nsfw_content
    ADD CONSTRAINT idx_16944_nsfw_content_pkey PRIMARY KEY (prompt_id);


--
-- Name: sexual_content idx_16954_sexual_content_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sexual_content
    ADD CONSTRAINT idx_16954_sexual_content_pkey PRIMARY KEY (prompt_id);


--
-- Name: relationships idx_16964_relationships_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.relationships
    ADD CONSTRAINT idx_16964_relationships_pkey PRIMARY KEY (prompt_id);


--
-- Name: camera_composition idx_16974_camera_composition_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.camera_composition
    ADD CONSTRAINT idx_16974_camera_composition_pkey PRIMARY KEY (prompt_id);


--
-- Name: mood_atmosphere idx_16984_mood_atmosphere_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.mood_atmosphere
    ADD CONSTRAINT idx_16984_mood_atmosphere_pkey PRIMARY KEY (prompt_id);


--
-- Name: users idx_17214_users_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT idx_17214_users_pkey PRIMARY KEY (id);


--
-- Name: user_preferences idx_17226_user_preferences_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_preferences
    ADD CONSTRAINT idx_17226_user_preferences_pkey PRIMARY KEY (user_id);


--
-- Name: user_password_history idx_17237_user_password_history_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_password_history
    ADD CONSTRAINT idx_17237_user_password_history_pkey PRIMARY KEY (id);


--
-- Name: account_deletion_audit idx_17245_account_deletion_audit_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.account_deletion_audit
    ADD CONSTRAINT idx_17245_account_deletion_audit_pkey PRIMARY KEY (id);


--
-- Name: user_verification_tokens idx_17253_user_verification_tokens_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_verification_tokens
    ADD CONSTRAINT idx_17253_user_verification_tokens_pkey PRIMARY KEY (id);


--
-- Name: idx_16846_idx_characters_people_count; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_16846_idx_characters_people_count ON public.characters USING btree (number_of_people);


--
-- Name: idx_16851_idx_character_gender; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_16851_idx_character_gender ON public.character_genders USING btree (gender);


--
-- Name: idx_16856_idx_character_age; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_16856_idx_character_age ON public.character_ages USING btree (age_range);


--
-- Name: idx_16906_idx_setting_indoor_outdoor; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_16906_idx_setting_indoor_outdoor ON public.settings USING btree (indoor_outdoor);


--
-- Name: idx_16906_idx_setting_type; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_16906_idx_setting_type ON public.settings USING btree (location_type);


--
-- Name: idx_16926_idx_art_style; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_16926_idx_art_style ON public.art_styles USING btree (primary_style);


--
-- Name: idx_16944_idx_nsfw_level; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_16944_idx_nsfw_level ON public.nsfw_content USING btree (level);


--
-- Name: idx_16954_idx_sexual_visibility; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_16954_idx_sexual_visibility ON public.sexual_content USING btree (genital_visibility);


--
-- Name: idx_16969_idx_references; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_16969_idx_references ON public.prompt_references USING btree (reference_type, reference_name);


--
-- Name: idx_16994_idx_main_tags; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_16994_idx_main_tags ON public.main_tags USING btree (tag);


--
-- Name: idx_17214_sqlite_autoindex_users_1; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX idx_17214_sqlite_autoindex_users_1 ON public.users USING btree (username);


--
-- Name: idx_17214_sqlite_autoindex_users_2; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX idx_17214_sqlite_autoindex_users_2 ON public.users USING btree (email);


--
-- Name: idx_17253_sqlite_autoindex_user_verification_tokens_1; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX idx_17253_sqlite_autoindex_user_verification_tokens_1 ON public.user_verification_tokens USING btree (token_hash);


--
-- Name: art_style_tags art_style_tags_prompt_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.art_style_tags
    ADD CONSTRAINT art_style_tags_prompt_id_fkey FOREIGN KEY (prompt_id) REFERENCES public.prompts(id);


--
-- Name: art_styles art_styles_prompt_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.art_styles
    ADD CONSTRAINT art_styles_prompt_id_fkey FOREIGN KEY (prompt_id) REFERENCES public.prompts(id);


--
-- Name: camera_composition camera_composition_prompt_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.camera_composition
    ADD CONSTRAINT camera_composition_prompt_id_fkey FOREIGN KEY (prompt_id) REFERENCES public.prompts(id);


--
-- Name: character_ages character_ages_prompt_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.character_ages
    ADD CONSTRAINT character_ages_prompt_id_fkey FOREIGN KEY (prompt_id) REFERENCES public.prompts(id);


--
-- Name: character_attributes character_attributes_prompt_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.character_attributes
    ADD CONSTRAINT character_attributes_prompt_id_fkey FOREIGN KEY (prompt_id) REFERENCES public.prompts(id);


--
-- Name: character_body_types character_body_types_prompt_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.character_body_types
    ADD CONSTRAINT character_body_types_prompt_id_fkey FOREIGN KEY (prompt_id) REFERENCES public.prompts(id);


--
-- Name: character_eyes character_eyes_prompt_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.character_eyes
    ADD CONSTRAINT character_eyes_prompt_id_fkey FOREIGN KEY (prompt_id) REFERENCES public.prompts(id);


--
-- Name: character_genders character_genders_prompt_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.character_genders
    ADD CONSTRAINT character_genders_prompt_id_fkey FOREIGN KEY (prompt_id) REFERENCES public.prompts(id);


--
-- Name: character_hair character_hair_prompt_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.character_hair
    ADD CONSTRAINT character_hair_prompt_id_fkey FOREIGN KEY (prompt_id) REFERENCES public.prompts(id);


--
-- Name: characters characters_prompt_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.characters
    ADD CONSTRAINT characters_prompt_id_fkey FOREIGN KEY (prompt_id) REFERENCES public.prompts(id);


--
-- Name: clothing_accessories clothing_accessories_prompt_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.clothing_accessories
    ADD CONSTRAINT clothing_accessories_prompt_id_fkey FOREIGN KEY (prompt_id) REFERENCES public.prompts(id);


--
-- Name: clothing_items clothing_items_prompt_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.clothing_items
    ADD CONSTRAINT clothing_items_prompt_id_fkey FOREIGN KEY (prompt_id) REFERENCES public.prompts(id);


--
-- Name: clothing clothing_prompt_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.clothing
    ADD CONSTRAINT clothing_prompt_id_fkey FOREIGN KEY (prompt_id) REFERENCES public.prompts(id);


--
-- Name: composition_notes composition_notes_prompt_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.composition_notes
    ADD CONSTRAINT composition_notes_prompt_id_fkey FOREIGN KEY (prompt_id) REFERENCES public.prompts(id);


--
-- Name: emotions emotions_prompt_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.emotions
    ADD CONSTRAINT emotions_prompt_id_fkey FOREIGN KEY (prompt_id) REFERENCES public.prompts(id);


--
-- Name: environment_details environment_details_prompt_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.environment_details
    ADD CONSTRAINT environment_details_prompt_id_fkey FOREIGN KEY (prompt_id) REFERENCES public.prompts(id);


--
-- Name: lighting lighting_prompt_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.lighting
    ADD CONSTRAINT lighting_prompt_id_fkey FOREIGN KEY (prompt_id) REFERENCES public.prompts(id);


--
-- Name: lighting_quality lighting_quality_prompt_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.lighting_quality
    ADD CONSTRAINT lighting_quality_prompt_id_fkey FOREIGN KEY (prompt_id) REFERENCES public.prompts(id);


--
-- Name: main_tags main_tags_prompt_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.main_tags
    ADD CONSTRAINT main_tags_prompt_id_fkey FOREIGN KEY (prompt_id) REFERENCES public.prompts(id);


--
-- Name: mood_atmosphere mood_atmosphere_prompt_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.mood_atmosphere
    ADD CONSTRAINT mood_atmosphere_prompt_id_fkey FOREIGN KEY (prompt_id) REFERENCES public.prompts(id);


--
-- Name: nsfw_content nsfw_content_prompt_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.nsfw_content
    ADD CONSTRAINT nsfw_content_prompt_id_fkey FOREIGN KEY (prompt_id) REFERENCES public.prompts(id);


--
-- Name: nsfw_elements nsfw_elements_prompt_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.nsfw_elements
    ADD CONSTRAINT nsfw_elements_prompt_id_fkey FOREIGN KEY (prompt_id) REFERENCES public.prompts(id);


--
-- Name: pose_actions pose_actions_prompt_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.pose_actions
    ADD CONSTRAINT pose_actions_prompt_id_fkey FOREIGN KEY (prompt_id) REFERENCES public.prompts(id);


--
-- Name: poses poses_prompt_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.poses
    ADD CONSTRAINT poses_prompt_id_fkey FOREIGN KEY (prompt_id) REFERENCES public.prompts(id);


--
-- Name: prompt_references prompt_references_prompt_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.prompt_references
    ADD CONSTRAINT prompt_references_prompt_id_fkey FOREIGN KEY (prompt_id) REFERENCES public.prompts(id);


--
-- Name: relationships relationships_prompt_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.relationships
    ADD CONSTRAINT relationships_prompt_id_fkey FOREIGN KEY (prompt_id) REFERENCES public.prompts(id);


--
-- Name: settings settings_prompt_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.settings
    ADD CONSTRAINT settings_prompt_id_fkey FOREIGN KEY (prompt_id) REFERENCES public.prompts(id);


--
-- Name: sexual_content sexual_content_prompt_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sexual_content
    ADD CONSTRAINT sexual_content_prompt_id_fkey FOREIGN KEY (prompt_id) REFERENCES public.prompts(id);


--
-- Name: sexual_details sexual_details_prompt_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sexual_details
    ADD CONSTRAINT sexual_details_prompt_id_fkey FOREIGN KEY (prompt_id) REFERENCES public.prompts(id);


--
-- Name: technical_details technical_details_prompt_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.technical_details
    ADD CONSTRAINT technical_details_prompt_id_fkey FOREIGN KEY (prompt_id) REFERENCES public.prompts(id);


--
-- Name: technical technical_prompt_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.technical
    ADD CONSTRAINT technical_prompt_id_fkey FOREIGN KEY (prompt_id) REFERENCES public.prompts(id);


--
-- Name: user_password_history user_password_history_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_password_history
    ADD CONSTRAINT user_password_history_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: user_preferences user_preferences_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_preferences
    ADD CONSTRAINT user_preferences_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: user_verification_tokens user_verification_tokens_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_verification_tokens
    ADD CONSTRAINT user_verification_tokens_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- SQLite compatibility helpers
--

CREATE OR REPLACE FUNCTION public.group_concat_accum(state text, value text)
 RETURNS text
 LANGUAGE sql
 IMMUTABLE
AS $function$
    SELECT CASE
        WHEN value IS NULL THEN state
        WHEN state IS NULL OR state = '' THEN value
        ELSE state || ',' || value
    END;
$function$;

DROP AGGREGATE IF EXISTS public.group_concat(text);

CREATE AGGREGATE public.group_concat(text) (
    SFUNC = public.group_concat_accum,
    STYPE = text
);


--
-- PostgreSQL database dump complete
--
