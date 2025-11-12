#!/usr/bin/env python3
"""
Import Analyzed Prompts to SQLite Database

Creates a searchable SQLite database from analyzed prompt results.
"""

import sqlite3
import jsonlines
import sys
from pathlib import Path
from datetime import datetime


class PromptDatabase:
    """SQLite database for cataloged prompts."""
    
    def __init__(self, db_path: str = "catalog.db"):
        """Initialize database connection."""
        self.db_path = db_path
        self.conn = None
    
    def __enter__(self):
        """Context manager entry."""
        self.conn = sqlite3.connect(self.db_path)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if self.conn:
            self.conn.close()
    
    def create_schema(self):
        """Create database schema from SQL file."""
        schema_file = Path("db_schema.sql")
        if not schema_file.exists():
            raise FileNotFoundError("db_schema.sql not found")
        
        with open(schema_file) as f:
            schema_sql = f.read()
        
        self.conn.executescript(schema_sql)
        self.conn.commit()
        print("✓ Database schema created")
    
    def import_prompt(self, result: dict):
        """
        Import a single analyzed prompt into the database.
        
        Args:
            result: Analyzed prompt result dictionary
        """
        prompt_id = result['id']
        categories = result['categories']
        metadata = result['metadata']
        
        # Insert main prompt
        self.conn.execute("""
            INSERT OR REPLACE INTO prompts (id, original_prompt, processed_at, model_used, input_tokens, output_tokens)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            prompt_id,
            result['original_prompt'],
            metadata.get('processed_at'),
            metadata.get('model_used'),
            metadata.get('tokens_used', {}).get('input', 0),
            metadata.get('tokens_used', {}).get('output', 0)
        ))
        
        # Character data
        char = categories.get('character', {})
        self.conn.execute("""
            INSERT OR REPLACE INTO characters (prompt_id, number_of_people, breast_size)
            VALUES (?, ?, ?)
        """, (prompt_id, char.get('number_of_people', 0), char.get('breast_size', 'unspecified')))
        
        for gender in char.get('genders', []):
            self.conn.execute("INSERT INTO character_genders VALUES (?, ?)", (prompt_id, gender))
        
        for age in char.get('age_ranges', []):
            self.conn.execute("INSERT INTO character_ages VALUES (?, ?)", (prompt_id, age))
        
        for body_type in char.get('body_types', []):
            self.conn.execute("INSERT INTO character_body_types VALUES (?, ?)", (prompt_id, body_type))
        
        # Hair
        hair = char.get('hair', {})
        for color in hair.get('colors', []):
            self.conn.execute("INSERT INTO character_hair (prompt_id, color) VALUES (?, ?)", (prompt_id, color))
        for style in hair.get('styles', []):
            self.conn.execute("INSERT INTO character_hair (prompt_id, style) VALUES (?, ?)", (prompt_id, style))
        for length in hair.get('lengths', []):
            self.conn.execute("INSERT INTO character_hair (prompt_id, length) VALUES (?, ?)", (prompt_id, length))
        
        # Eyes
        eyes = char.get('eyes', {})
        for color in eyes.get('colors', []):
            self.conn.execute("INSERT INTO character_eyes (prompt_id, color) VALUES (?, ?)", (prompt_id, color))
        for shape in eyes.get('shapes', []):
            self.conn.execute("INSERT INTO character_eyes (prompt_id, shape) VALUES (?, ?)", (prompt_id, shape))
        
        # Character attributes
        for skin_tone in char.get('skin_tones', []):
            self.conn.execute("INSERT INTO character_attributes VALUES (?, ?, ?)", (prompt_id, 'skin_tone', skin_tone))
        for feature in char.get('facial_features', []):
            self.conn.execute("INSERT INTO character_attributes VALUES (?, ?, ?)", (prompt_id, 'facial_feature', feature))
        for ethnicity in char.get('ethnicities', []):
            self.conn.execute("INSERT INTO character_attributes VALUES (?, ?, ?)", (prompt_id, 'ethnicity', ethnicity))
        for species in char.get('species', []):
            self.conn.execute("INSERT INTO character_attributes VALUES (?, ?, ?)", (prompt_id, 'species', species))
        for attr in char.get('physical_attributes', []):
            self.conn.execute("INSERT INTO character_attributes VALUES (?, ?, ?)", (prompt_id, 'physical', attr))
        
        # Pose
        pose = categories.get('pose', {})
        self.conn.execute("""
            INSERT OR REPLACE INTO poses (prompt_id, main_pose, body_position, view_angle)
            VALUES (?, ?, ?, ?)
        """, (prompt_id, pose.get('main_pose'), pose.get('body_position'), pose.get('view_angle')))
        
        for action in pose.get('actions', []):
            self.conn.execute("INSERT INTO pose_actions VALUES (?, ?)", (prompt_id, action))
        
        # Clothing
        clothing = categories.get('clothing', {})
        self.conn.execute("""
            INSERT OR REPLACE INTO clothing (prompt_id, style, coverage)
            VALUES (?, ?, ?)
        """, (prompt_id, clothing.get('style'), clothing.get('coverage')))
        
        for item in clothing.get('items', []):
            self.conn.execute("INSERT INTO clothing_items VALUES (?, ?)", (prompt_id, item))
        for accessory in clothing.get('accessories', []):
            self.conn.execute("INSERT INTO clothing_accessories VALUES (?, ?)", (prompt_id, accessory))
        
        # Setting
        setting = categories.get('setting', {})
        self.conn.execute("""
            INSERT OR REPLACE INTO settings (prompt_id, location_type, indoor_outdoor, specific_place)
            VALUES (?, ?, ?, ?)
        """, (prompt_id, setting.get('location_type'), setting.get('indoor_outdoor'), setting.get('specific_place')))
        
        for detail in setting.get('environment_details', []):
            self.conn.execute("INSERT INTO environment_details VALUES (?, ?)", (prompt_id, detail))
        
        # Lighting
        lighting = categories.get('lighting', {})
        self.conn.execute("""
            INSERT OR REPLACE INTO lighting (prompt_id, type, time_of_day)
            VALUES (?, ?, ?)
        """, (prompt_id, lighting.get('type'), lighting.get('time_of_day')))
        
        for quality in lighting.get('quality', []):
            self.conn.execute("INSERT INTO lighting_quality VALUES (?, ?)", (prompt_id, quality))
        
        # Art style
        art_style = categories.get('art_style', {})
        self.conn.execute("""
            INSERT OR REPLACE INTO art_styles (prompt_id, primary_style)
            VALUES (?, ?)
        """, (prompt_id, art_style.get('primary_style')))
        
        for tag in art_style.get('quality_tags', []):
            self.conn.execute("INSERT INTO art_style_tags VALUES (?, ?, ?)", (prompt_id, 'quality', tag))
        for technique in art_style.get('technique', []):
            self.conn.execute("INSERT INTO art_style_tags VALUES (?, ?, ?)", (prompt_id, 'technique', technique))
        for score in art_style.get('score_indicators', []):
            self.conn.execute("INSERT INTO art_style_tags VALUES (?, ?, ?)", (prompt_id, 'score', score))
        
        # Technical
        self.conn.execute("INSERT OR REPLACE INTO technical (prompt_id) VALUES (?)", (prompt_id,))
        
        technical = categories.get('technical', {})
        for res in technical.get('resolution', []):
            self.conn.execute("INSERT INTO technical_details VALUES (?, ?, ?)", (prompt_id, 'resolution', res))
        for setting in technical.get('camera_settings', []):
            self.conn.execute("INSERT INTO technical_details VALUES (?, ?, ?)", (prompt_id, 'camera_setting', setting))
        for detail in technical.get('detail_level', []):
            self.conn.execute("INSERT INTO technical_details VALUES (?, ?, ?)", (prompt_id, 'detail_level', detail))
        
        # NSFW content
        nsfw = categories.get('nsfw_content', {})
        self.conn.execute("""
            INSERT OR REPLACE INTO nsfw_content (prompt_id, level)
            VALUES (?, ?)
        """, (prompt_id, nsfw.get('level', 'safe')))
        
        for element in nsfw.get('elements', []):
            self.conn.execute("INSERT INTO nsfw_elements VALUES (?, ?)", (prompt_id, element))
        
        # Sexual content
        sexual = categories.get('sexual_content', {})
        self.conn.execute("""
            INSERT OR REPLACE INTO sexual_content (prompt_id, genital_visibility)
            VALUES (?, ?)
        """, (prompt_id, sexual.get('genital_visibility')))
        
        for act in sexual.get('sexual_acts', []):
            self.conn.execute("INSERT INTO sexual_details VALUES (?, ?, ?)", (prompt_id, 'act', act))
        for position in sexual.get('sexual_positions', []):
            self.conn.execute("INSERT INTO sexual_details VALUES (?, ?, ?)", (prompt_id, 'position', position))
        for fluid in sexual.get('body_fluids', []):
            self.conn.execute("INSERT INTO sexual_details VALUES (?, ?, ?)", (prompt_id, 'body_fluid', fluid))
        for fetish in sexual.get('fetishes', []):
            self.conn.execute("INSERT INTO sexual_details VALUES (?, ?, ?)", (prompt_id, 'fetish', fetish))
        
        # Relationships
        rel = categories.get('relationships', {})
        self.conn.execute("""
            INSERT OR REPLACE INTO relationships (prompt_id, interaction_type, relationship, pov_perspective)
            VALUES (?, ?, ?, ?)
        """, (prompt_id, rel.get('interaction_type'), rel.get('relationship'), rel.get('pov_perspective')))
        
        # References
        refs = categories.get('references', {})
        for char_name in refs.get('character_names', []):
            self.conn.execute("INSERT INTO prompt_references VALUES (?, ?, ?)", (prompt_id, 'character', char_name))
        for series in refs.get('series_franchise', []):
            self.conn.execute("INSERT INTO prompt_references VALUES (?, ?, ?)", (prompt_id, 'series', series))
        for artist in refs.get('artist_references', []):
            self.conn.execute("INSERT INTO prompt_references VALUES (?, ?, ?)", (prompt_id, 'artist', artist))
        
        # Camera composition
        camera = categories.get('camera_composition', {})
        self.conn.execute("""
            INSERT OR REPLACE INTO camera_composition (prompt_id, shot_type, camera_angle, focus_area)
            VALUES (?, ?, ?, ?)
        """, (prompt_id, camera.get('shot_type'), camera.get('camera_angle'), camera.get('focus_area')))
        
        for note in camera.get('composition_notes', []):
            self.conn.execute("INSERT INTO composition_notes VALUES (?, ?)", (prompt_id, note))
        
        # Mood/atmosphere
        mood = categories.get('mood_atmosphere', {})
        self.conn.execute("""
            INSERT OR REPLACE INTO mood_atmosphere (prompt_id, overall_mood)
            VALUES (?, ?)
        """, (prompt_id, mood.get('overall_mood')))
        
        for emotion in mood.get('emotions', []):
            self.conn.execute("INSERT INTO emotions VALUES (?, ?)", (prompt_id, emotion))
        
        # Main tags
        for idx, tag in enumerate(categories.get('main_tags', [])):
            self.conn.execute("INSERT INTO main_tags VALUES (?, ?, ?)", (prompt_id, tag, idx))
    
    def import_from_jsonl(self, jsonl_file: str):
        """
        Import all prompts from JSONL file.
        
        Args:
            jsonl_file: Path to JSONL results file
        """
        imported = 0
        failed = 0
        
        print(f"Importing from: {jsonl_file}")
        
        with jsonlines.open(jsonl_file) as reader:
            for result in reader:
                try:
                    self.import_prompt(result)
                    imported += 1
                    if imported % 10 == 0:
                        print(f"  Imported {imported} prompts...", end='\r')
                except Exception as e:
                    failed += 1
                    print(f"\n  Error importing prompt {result.get('id')}: {e}")
        
        self.conn.commit()
        print(f"\n✓ Import complete: {imported} successful, {failed} failed")
        return imported, failed
    
    def get_stats(self):
        """Get database statistics."""
        cursor = self.conn.cursor()
        
        stats = {
            'total_prompts': cursor.execute("SELECT COUNT(*) FROM prompts").fetchone()[0],
            'nsfw_distribution': {},
            'top_tags': [],
            'top_art_styles': [],
            'character_counts': {}
        }
        
        # NSFW distribution
        for row in cursor.execute("SELECT level, COUNT(*) FROM nsfw_content GROUP BY level"):
            stats['nsfw_distribution'][row[0]] = row[1]
        
        # Top tags
        stats['top_tags'] = cursor.execute("""
            SELECT tag, COUNT(*) as count 
            FROM main_tags 
            GROUP BY tag 
            ORDER BY count DESC 
            LIMIT 20
        """).fetchall()
        
        # Top art styles
        stats['top_art_styles'] = cursor.execute("""
            SELECT primary_style, COUNT(*) as count 
            FROM art_styles 
            WHERE primary_style IS NOT NULL
            GROUP BY primary_style 
            ORDER BY count DESC 
            LIMIT 10
        """).fetchall()
        
        # Character counts
        stats['character_counts'] = cursor.execute("""
            SELECT number_of_people, COUNT(*) as count 
            FROM characters 
            GROUP BY number_of_people 
            ORDER BY number_of_people
        """).fetchall()
        
        return stats


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Import analyzed prompts to SQLite database')
    parser.add_argument('jsonl_file', help='Path to JSONL results file')
    parser.add_argument('--db', default='catalog.db', help='Database file path')
    parser.add_argument('--stats', action='store_true', help='Show statistics after import')
    
    args = parser.parse_args()
    
    print("="*70)
    print("Prompt Catalog Database Importer")
    print("="*70)
    print()
    
    # Check if file exists
    if not Path(args.jsonl_file).exists():
        print(f"❌ File not found: {args.jsonl_file}")
        return 1
    
    # Create database
    print(f"Creating database: {args.db}")
    
    with PromptDatabase(args.db) as db:
        # Create schema
        db.create_schema()
        
        # Import data
        imported, failed = db.import_from_jsonl(args.jsonl_file)
        
        # Show statistics
        if args.stats and imported > 0:
            print("\n" + "="*70)
            print("DATABASE STATISTICS")
            print("="*70)
            
            stats = db.get_stats()
            
            print(f"\nTotal prompts: {stats['total_prompts']:,}")
            print(f"\nNSFW Distribution:")
            for level, count in stats['nsfw_distribution'].items():
                print(f"  {level}: {count}")
            
            print(f"\nTop 10 Tags:")
            for tag, count in stats['top_tags'][:10]:
                print(f"  {tag}: {count}")
            
            print(f"\nTop Art Styles:")
            for style, count in stats['top_art_styles']:
                print(f"  {style}: {count}")
            
            print(f"\nCharacter Counts:")
            for num, count in stats['character_counts']:
                print(f"  {num} people: {count} prompts")
    
    print(f"\n✅ Database created: {args.db}")
    print(f"   Location: {Path(args.db).absolute()}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
