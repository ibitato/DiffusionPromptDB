#!/usr/bin/env python3
"""
Clean BREAK Patterns from Prompts

Removes \n BREAK\n and \nBREAK\ patterns from prompts and replaces with comma.
"""

import sqlite3
import sys
from pathlib import Path


def clean_break_patterns(db_path: str = "database/prompts_catalog.db"):
    """
    Clean BREAK patterns from all prompts in database.
    
    Args:
        db_path: Path to database file
    """
    # Resolve path (try both API location and batch_analyzer location)
    if not Path(db_path).exists():
        db_path = "../api/database/prompts_catalog.db"
    if not Path(db_path).exists():
        db_path = "prompts_catalog.db"
    if not Path(db_path).exists():
        print(f"❌ Database not found: {db_path}")
        return False
    
    print("="*70)
    print("CLEAN BREAK PATTERNS")
    print("="*70)
    print(f"\nDatabase: {db_path}")
    print(f"Location: {Path(db_path).absolute()}\n")
    
    conn = sqlite3.connect(db_path, check_same_thread=False)
    cursor = conn.cursor()
    
    # Patterns to clean
    patterns = [
        '\n BREAK\n',  # Pattern with spaces
        '\nBREAK\\',   # Pattern with backslash
        '\nBREAK\n',   # Pattern without spaces
        ' BREAK ',     # Pattern with just spaces
    ]
    
    # Find prompts with BREAK patterns
    total_prompts = cursor.execute("SELECT COUNT(*) FROM prompts").fetchone()[0]
    print(f"Total prompts in database: {total_prompts:,}\n")
    
    print("Searching for BREAK patterns...")
    affected_prompts = []
    
    for prompt_row in cursor.execute("SELECT id, original_prompt FROM prompts"):
        prompt_id = prompt_row[0]
        original_text = prompt_row[1]
        
        # Check if any pattern exists
        found_pattern = False
        for pattern in patterns:
            if pattern in original_text:
                found_pattern = True
                break
        
        if found_pattern:
            affected_prompts.append((prompt_id, original_text))
    
    print(f"Found {len(affected_prompts)} prompts with BREAK patterns\n")
    
    if len(affected_prompts) == 0:
        print("✅ No prompts need cleaning!")
        conn.close()
        return True
    
    # Show some examples
    print("Examples of prompts to clean:")
    for i, (pid, text) in enumerate(affected_prompts[:3], 1):
        preview = text[:100] + "..." if len(text) > 100 else text
        print(f"  {i}. ID {pid}: {preview}")
    print()
    
    # Ask for confirmation
    print(f"⚠️  This will modify {len(affected_prompts)} prompts")
    print("   Patterns will be replaced with ', ' (comma + space)")
    response = input("\nProceed with cleaning? (y/n): ")
    
    if response.lower() != 'y':
        print("❌ Cleaning cancelled")
        conn.close()
        return False
    
    # Clean the prompts
    print("\nCleaning prompts...")
    cleaned = 0
    
    for prompt_id, original_text in affected_prompts:
        new_text = original_text
        
        # Replace all patterns
        for pattern in patterns:
            new_text = new_text.replace(pattern, ', ')
        
        # Clean up multiple consecutive commas
        while ',,' in new_text or ', ,' in new_text:
            new_text = new_text.replace(',,', ',').replace(', ,', ',')
        
        # Update database
        cursor.execute(
            "UPDATE prompts SET original_prompt = ? WHERE id = ?",
            (new_text, prompt_id)
        )
        cleaned += 1
        
        if cleaned % 100 == 0:
            print(f"  Cleaned {cleaned}/{len(affected_prompts)} prompts...", end='\r')
    
    conn.commit()
    conn.close()
    
    print(f"\n✅ Cleaning complete: {cleaned} prompts updated\n")
    
    # Summary
    print("="*70)
    print("SUMMARY")
    print("="*70)
    print(f"\n✅ Successfully cleaned {cleaned} prompts")
    print(f"   Patterns removed: \\n BREAK\\n, \\nBREAK\\, etc.")
    print(f"   Replaced with: ', ' (comma + space)")
    print(f"\n💡 Database updated and ready to use!")
    
    return True


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Clean BREAK patterns from prompts')
    parser.add_argument('--db', default='../api/database/prompts_catalog.db',
                       help='Database file path')
    parser.add_argument('--auto', action='store_true',
                       help='Run without confirmation')
    
    args = parser.parse_args()
    
    if args.auto:
        # Simulate 'y' response for automation
        import builtins
        original_input = builtins.input
        builtins.input = lambda _: 'y'
    
    success = clean_break_patterns(args.db)
    
    if args.auto:
        builtins.input = original_input
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
