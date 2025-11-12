-- SQLite Database Schema for Cataloged Prompts
-- Optimized for filtering and mixed searches across categories

-- Main prompts table
CREATE TABLE IF NOT EXISTS prompts (
    id INTEGER PRIMARY KEY,
    original_prompt TEXT NOT NULL,
    processed_at TIMESTAMP,
    model_used TEXT,
    input_tokens INTEGER,
    output_tokens INTEGER
);

-- Character information
CREATE TABLE IF NOT EXISTS characters (
    prompt_id INTEGER PRIMARY KEY,
    number_of_people INTEGER,
    breast_size TEXT,
    FOREIGN KEY (prompt_id) REFERENCES prompts(id)
);

CREATE TABLE IF NOT EXISTS character_genders (
    prompt_id INTEGER,
    gender TEXT,
    FOREIGN KEY (prompt_id) REFERENCES prompts(id)
);

CREATE TABLE IF NOT EXISTS character_ages (
    prompt_id INTEGER,
    age_range TEXT,
    FOREIGN KEY (prompt_id) REFERENCES prompts(id)
);

CREATE TABLE IF NOT EXISTS character_body_types (
    prompt_id INTEGER,
    body_type TEXT,
    FOREIGN KEY (prompt_id) REFERENCES prompts(id)
);

CREATE TABLE IF NOT EXISTS character_hair (
    prompt_id INTEGER,
    color TEXT,
    style TEXT,
    length TEXT,
    FOREIGN KEY (prompt_id) REFERENCES prompts(id)
);

CREATE TABLE IF NOT EXISTS character_eyes (
    prompt_id INTEGER,
    color TEXT,
    shape TEXT,
    FOREIGN KEY (prompt_id) REFERENCES prompts(id)
);

CREATE TABLE IF NOT EXISTS character_attributes (
    prompt_id INTEGER,
    attribute_type TEXT, -- 'skin_tone', 'facial_feature', 'ethnicity', 'species', 'physical'
    attribute_value TEXT,
    FOREIGN KEY (prompt_id) REFERENCES prompts(id)
);

-- Pose and positioning
CREATE TABLE IF NOT EXISTS poses (
    prompt_id INTEGER PRIMARY KEY,
    main_pose TEXT,
    body_position TEXT,
    view_angle TEXT,
    FOREIGN KEY (prompt_id) REFERENCES prompts(id)
);

CREATE TABLE IF NOT EXISTS pose_actions (
    prompt_id INTEGER,
    action TEXT,
    FOREIGN KEY (prompt_id) REFERENCES prompts(id)
);

-- Clothing
CREATE TABLE IF NOT EXISTS clothing (
    prompt_id INTEGER PRIMARY KEY,
    style TEXT,
    coverage TEXT,
    FOREIGN KEY (prompt_id) REFERENCES prompts(id)
);

CREATE TABLE IF NOT EXISTS clothing_items (
    prompt_id INTEGER,
    item TEXT,
    FOREIGN KEY (prompt_id) REFERENCES prompts(id)
);

CREATE TABLE IF NOT EXISTS clothing_accessories (
    prompt_id INTEGER,
    accessory TEXT,
    FOREIGN KEY (prompt_id) REFERENCES prompts(id)
);

-- Setting and environment
CREATE TABLE IF NOT EXISTS settings (
    prompt_id INTEGER PRIMARY KEY,
    location_type TEXT,
    indoor_outdoor TEXT,
    specific_place TEXT,
    FOREIGN KEY (prompt_id) REFERENCES prompts(id)
);

CREATE TABLE IF NOT EXISTS environment_details (
    prompt_id INTEGER,
    detail TEXT,
    FOREIGN KEY (prompt_id) REFERENCES prompts(id)
);

-- Lighting
CREATE TABLE IF NOT EXISTS lighting (
    prompt_id INTEGER PRIMARY KEY,
    type TEXT,
    time_of_day TEXT,
    FOREIGN KEY (prompt_id) REFERENCES prompts(id)
);

CREATE TABLE IF NOT EXISTS lighting_quality (
    prompt_id INTEGER,
    quality TEXT,
    FOREIGN KEY (prompt_id) REFERENCES prompts(id)
);

-- Art style
CREATE TABLE IF NOT EXISTS art_styles (
    prompt_id INTEGER PRIMARY KEY,
    primary_style TEXT,
    FOREIGN KEY (prompt_id) REFERENCES prompts(id)
);

CREATE TABLE IF NOT EXISTS art_style_tags (
    prompt_id INTEGER,
    tag_type TEXT, -- 'quality', 'technique', 'score'
    tag_value TEXT,
    FOREIGN KEY (prompt_id) REFERENCES prompts(id)
);

-- Technical aspects
CREATE TABLE IF NOT EXISTS technical (
    prompt_id INTEGER PRIMARY KEY,
    FOREIGN KEY (prompt_id) REFERENCES prompts(id)
);

CREATE TABLE IF NOT EXISTS technical_details (
    prompt_id INTEGER,
    detail_type TEXT, -- 'resolution', 'camera_setting', 'detail_level'
    detail_value TEXT,
    FOREIGN KEY (prompt_id) REFERENCES prompts(id)
);

-- NSFW content
CREATE TABLE IF NOT EXISTS nsfw_content (
    prompt_id INTEGER PRIMARY KEY,
    level TEXT CHECK(level IN ('safe', 'suggestive', 'explicit')),
    FOREIGN KEY (prompt_id) REFERENCES prompts(id)
);

CREATE TABLE IF NOT EXISTS nsfw_elements (
    prompt_id INTEGER,
    element TEXT,
    FOREIGN KEY (prompt_id) REFERENCES prompts(id)
);

-- Sexual content
CREATE TABLE IF NOT EXISTS sexual_content (
    prompt_id INTEGER PRIMARY KEY,
    genital_visibility TEXT,
    FOREIGN KEY (prompt_id) REFERENCES prompts(id)
);

CREATE TABLE IF NOT EXISTS sexual_details (
    prompt_id INTEGER,
    detail_type TEXT, -- 'act', 'position', 'body_fluid', 'fetish'
    detail_value TEXT,
    FOREIGN KEY (prompt_id) REFERENCES prompts(id)
);

-- Relationships
CREATE TABLE IF NOT EXISTS relationships (
    prompt_id INTEGER PRIMARY KEY,
    interaction_type TEXT,
    relationship TEXT,
    pov_perspective TEXT,
    FOREIGN KEY (prompt_id) REFERENCES prompts(id)
);

-- References (characters, series, artists)
CREATE TABLE IF NOT EXISTS prompt_references (
    prompt_id INTEGER,
    reference_type TEXT, -- 'character', 'series', 'artist'
    reference_name TEXT,
    FOREIGN KEY (prompt_id) REFERENCES prompts(id)
);

-- Camera composition
CREATE TABLE IF NOT EXISTS camera_composition (
    prompt_id INTEGER PRIMARY KEY,
    shot_type TEXT,
    camera_angle TEXT,
    focus_area TEXT,
    FOREIGN KEY (prompt_id) REFERENCES prompts(id)
);

CREATE TABLE IF NOT EXISTS composition_notes (
    prompt_id INTEGER,
    note TEXT,
    FOREIGN KEY (prompt_id) REFERENCES prompts(id)
);

-- Mood and atmosphere
CREATE TABLE IF NOT EXISTS mood_atmosphere (
    prompt_id INTEGER PRIMARY KEY,
    overall_mood TEXT,
    FOREIGN KEY (prompt_id) REFERENCES prompts(id)
);

CREATE TABLE IF NOT EXISTS emotions (
    prompt_id INTEGER,
    emotion TEXT,
    FOREIGN KEY (prompt_id) REFERENCES prompts(id)
);

-- Main tags
CREATE TABLE IF NOT EXISTS main_tags (
    prompt_id INTEGER,
    tag TEXT,
    tag_order INTEGER,
    FOREIGN KEY (prompt_id) REFERENCES prompts(id)
);

-- Indexes for fast searching
CREATE INDEX IF NOT EXISTS idx_nsfw_level ON nsfw_content(level);
CREATE INDEX IF NOT EXISTS idx_art_style ON art_styles(primary_style);
CREATE INDEX IF NOT EXISTS idx_character_gender ON character_genders(gender);
CREATE INDEX IF NOT EXISTS idx_character_age ON character_ages(age_range);
CREATE INDEX IF NOT EXISTS idx_setting_type ON settings(location_type);
CREATE INDEX IF NOT EXISTS idx_setting_indoor_outdoor ON settings(indoor_outdoor);
CREATE INDEX IF NOT EXISTS idx_main_tags ON main_tags(tag);
CREATE INDEX IF NOT EXISTS idx_references ON prompt_references(reference_type, reference_name);
CREATE INDEX IF NOT EXISTS idx_sexual_visibility ON sexual_content(genital_visibility);
CREATE INDEX IF NOT EXISTS idx_characters_people_count ON characters(number_of_people);
