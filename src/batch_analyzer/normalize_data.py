#!/usr/bin/env python3
"""
Normalize Batch Data

Cleans and normalizes the converted batch output to ensure 100% compatibility with SQLite.
"""

import jsonlines
import sys
from pathlib import Path


def normalize_nsfw_level(level: str) -> str:
    """
    Normalize NSFW level to valid values.
    
    Args:
        level: Original NSFW level from Claude
        
    Returns:
        Normalized level ('safe', 'suggestive', or 'explicit')
    """
    if not level or level == 'unspecified' or level == 'unclear':
        # If unclear, assume safe (conservative approach)
        return 'safe'
    
    # Normalize case
    level = level.lower().strip()
    
    # Map variations
    if level in ['safe', 'sfw']:
        return 'safe'
    elif level in ['suggestive', 'mild', 'questionable']:
        return 'suggestive'
    elif level in ['explicit', 'nsfw', 'adult']:
        return 'explicit'
    else:
        # Default to safe for unknown values
        return 'safe'


def normalize_string_field(value) -> str:
    """
    Normalize a field that should be a string.
    
    Converts lists to first element, handles None, etc.
    
    Args:
        value: Original value (could be string, list, None, etc.)
        
    Returns:
        Normalized string
    """
    if value is None:
        return 'unspecified'
    
    if isinstance(value, list):
        # If it's a list, take the first element
        if len(value) > 0:
            return str(value[0])
        else:
            return 'unspecified'
    
    if isinstance(value, str):
        return value if value else 'unspecified'
    
    # For other types, convert to string
    return str(value)


def normalize_prompt_data(result: dict) -> dict:
    """
    Normalize a single prompt's data for SQLite compatibility.
    
    Args:
        result: Original prompt result
        
    Returns:
        Normalized prompt result
    """
    categories = result.get('categories', {})
    
    # Normalize NSFW level
    nsfw_content = categories.get('nsfw_content', {})
    nsfw_content['level'] = normalize_nsfw_level(nsfw_content.get('level'))
    
    # Normalize pose fields (common source of type errors)
    pose = categories.get('pose', {})
    pose['main_pose'] = normalize_string_field(pose.get('main_pose'))
    pose['body_position'] = normalize_string_field(pose.get('body_position'))
    pose['view_angle'] = normalize_string_field(pose.get('view_angle'))
    
    # Normalize other string fields that might be arrays
    clothing = categories.get('clothing', {})
    clothing['style'] = normalize_string_field(clothing.get('style'))
    clothing['coverage'] = normalize_string_field(clothing.get('coverage'))
    
    setting = categories.get('setting', {})
    setting['location_type'] = normalize_string_field(setting.get('location_type'))
    setting['indoor_outdoor'] = normalize_string_field(setting.get('indoor_outdoor'))
    setting['specific_place'] = normalize_string_field(setting.get('specific_place'))
    
    lighting = categories.get('lighting', {})
    lighting['type'] = normalize_string_field(lighting.get('type'))
    lighting['time_of_day'] = normalize_string_field(lighting.get('time_of_day'))
    
    art_style = categories.get('art_style', {})
    art_style['primary_style'] = normalize_string_field(art_style.get('primary_style'))
    
    mood = categories.get('mood_atmosphere', {})
    mood['overall_mood'] = normalize_string_field(mood.get('overall_mood'))
    
    sexual = categories.get('sexual_content', {})
    sexual['genital_visibility'] = normalize_string_field(sexual.get('genital_visibility'))
    
    relationships = categories.get('relationships', {})
    relationships['interaction_type'] = normalize_string_field(relationships.get('interaction_type'))
    relationships['relationship'] = normalize_string_field(relationships.get('relationship'))
    relationships['pov_perspective'] = normalize_string_field(relationships.get('pov_perspective'))
    
    camera = categories.get('camera_composition', {})
    camera['shot_type'] = normalize_string_field(camera.get('shot_type'))
    camera['camera_angle'] = normalize_string_field(camera.get('camera_angle'))
    camera['focus_area'] = normalize_string_field(camera.get('focus_area'))
    
    # Normalize character breast_size
    character = categories.get('character', {})
    character['breast_size'] = normalize_string_field(character.get('breast_size'))
    
    return result


def normalize_file(input_file: str, output_file: str):
    """
    Normalize entire file.
    
    Args:
        input_file: Original converted file
        output_file: Normalized output file
    """
    print(f"Normalizing: {input_file}")
    print(f"Output to: {output_file}")
    print()
    
    normalized = 0
    changes = 0
    
    with jsonlines.open(input_file) as reader, jsonlines.open(output_file, mode='w') as writer:
        for idx, result in enumerate(reader, start=1):
            original_nsfw = result.get('categories', {}).get('nsfw_content', {}).get('level')
            
            # Normalize
            normalized_result = normalize_prompt_data(result)
            
            new_nsfw = normalized_result.get('categories', {}).get('nsfw_content', {}).get('level')
            
            if original_nsfw != new_nsfw:
                changes += 1
            
            writer.write(normalized_result)
            normalized += 1
            
            if normalized % 1000 == 0:
                print(f"Normalized {normalized:,} prompts...", end='\r')
    
    print(f"\n✓ Normalization complete: {normalized:,} prompts processed")
    print(f"  Changes made: {changes} prompts modified")
    return normalized, changes


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Normalize batch data for import')
    parser.add_argument('input_file', nargs='?',
                       default='results/converted_batch_20251112.jsonl',
                       help='Converted JSONL file')
    parser.add_argument('--output', 
                       default='results/normalized_batch_20251112.jsonl',
                       help='Normalized output file')
    
    args = parser.parse_args()
    
    print("="*70)
    print("BATCH DATA NORMALIZER")
    print("="*70)
    print()
    
    if not Path(args.input_file).exists():
        print(f"❌ File not found: {args.input_file}")
        return 1
    
    # Normalize
    normalized, changes = normalize_file(args.input_file, args.output)
    
    print(f"\n✅ Normalized file ready: {args.output}")
    print(f"\n📋 Next steps:")
    print(f"   1. Import: python import_to_db.py {args.output} --db prompts_catalog.db --stats")
    print(f"   2. Test: python test_catalog_integration.py --db prompts_catalog.db")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
