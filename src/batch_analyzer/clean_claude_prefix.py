#!/usr/bin/env python3
"""
Clean Claude Analysis Prefix from Prompts

Removes the Claude analysis instruction text that appears at the start of prompts.
"""

import sqlite3
import sys
import re
from pathlib import Path


def clean_claude_prefix(db_path: str = "../api/database/prompts_catalog.db"):
    """
    Clean Claude analysis prefix from all prompts in database.
    
    The prefix looks like:
    "ng Stable Diffusion prompt and extract structured information according to the schema below.
    
    PROMPT TO ANALYZE:"
    
    Args:
        db_path: Path to database file
    """
    # Resolve path
    if not Path(db_path).exists():
        db_path = "database/prompts_catalog.db"
    if not Path(db_path).exists():
        db_path = "prompts_catalog.db"
    if not Path(db_path).exists():
        print(f"❌ Database not found: {db_path}")
        return False
    
    print("="*70)
    print("CLEAN CLAUDE ANALYSIS PREFIX")
    print("="*70)
    print(f"\nDatabase: {db_path}")
    print(f"Location: {Path(db_path).absolute()}\n")
    
    conn = sqlite3.connect(db_path, check_same_thread=False)
    cursor = conn.cursor()
    
    # Patterns to clean
    patterns = [
        r"ng Stable Diffusion prompt and extract structured information according to the schema below\.\s*PROMPT TO ANALYZE:\s*",
        r".*?PROMPT TO ANALYZE:\s*",  # Catch-all for variations
    ]
    
    # Find prompts with pattern
    total_prompts = cursor.execute("SELECT COUNT(*) FROM prompts").fetchone()[0]
    print(f"Total prompts in database: {total_prompts:,}\n")
    
    print("Searching for Claude analysis prefix...")
    affected_prompts = []
    
    for prompt_row in cursor.execute("SELECT id, original_prompt FROM prompts"):
        prompt_id = prompt_row[0]
        original_text = prompt_row[1]
        
        # Check if any pattern exists at the start
        for pattern in patterns:
            if re.match(pattern, original_text):
                affected_prompts.append((prompt_id, original_text))
                break
    
    print(f"Found {len(affected_prompts)} prompts with Claude prefix\n")
    
    if len(affected_prompts) == 0:
        print("✅ No prompts need cleaning!")
        conn.close()
        return True
    
    # Show some examples
    print("Examples of prompts to clean:")
    for i, (pid, text) in enumerate(affected_prompts[:3], 1):
        # Show first 100 chars
        preview = text[:100].replace('\n', ' ')
        print(f"  {i}. ID {pid}: {preview}...")
    print()
    
    # Ask for confirmation
    print(f"⚠️  This will modify {len(affected_prompts)} prompts")
    print("   The Claude analysis prefix will be removed")
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
        
        # Remove all patterns
        for pattern in patterns:
            new_text = re.sub(pattern, '', new_text, flags=re.DOTALL)
        
        # Strip leading/trailing whitespace
        new_text = new_text.strip()
        
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
    print(f"   Removed Claude analysis prefix text")
    print(f"\n💡 Database updated and ready to use!")
    
    return True


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Clean Claude analysis prefix from prompts')
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
    
    success = clean_claude_prefix(args.db)
    
    if args.auto:
        builtins.input = original_input
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
