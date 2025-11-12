#!/usr/bin/env python3
"""
Example SQL Queries for Prompt Catalog

Demonstrates advanced search capabilities.
"""

import sqlite3

# Connect to database
conn = sqlite3.connect('prompts_catalog.db')

print("="*80)
print("EXAMPLE QUERIES - Prompt Catalog Database")
print("="*80)

# Query 1: Anime prompts with 1 girl, explicit
print("\n📊 QUERY 1: Anime prompts with 1 female character, explicit content")
print("-"*80)
results = conn.execute("""
    SELECT p.id, substr(p.original_prompt, 1, 100) as prompt
    FROM prompts p
    JOIN nsfw_content n ON p.id = n.prompt_id
    JOIN characters c ON p.id = c.prompt_id
    JOIN art_styles a ON p.id = a.prompt_id
    JOIN character_genders g ON p.id = g.prompt_id
    WHERE n.level = 'explicit'
      AND c.number_of_people = 1
      AND a.primary_style LIKE '%anime%'
      AND g.gender = 'female'
    LIMIT 5
""").fetchall()

for i, (pid, prompt) in enumerate(results, 1):
    print(f"{i}. [ID {pid}] {prompt}...")

print(f"\nTotal found: {len(results)}")

# Query 2: Prompts with blonde hair
print("\n📊 QUERY 2: Prompts featuring blonde hair")
print("-"*80)
results = conn.execute("""
    SELECT DISTINCT p.id, substr(p.original_prompt, 1, 100) as prompt
    FROM prompts p
    JOIN character_hair h ON p.id = h.prompt_id
    WHERE h.color LIKE '%blonde%' OR h.color LIKE '%blond%'
    LIMIT 5
""").fetchall()

for i, (pid, prompt) in enumerate(results, 1):
    print(f"{i}. [ID {pid}] {prompt}...")

print(f"\nTotal found: {len(results)}")

# Query 3: Indoor scenes with realistic style
print("\n📊 QUERY 3: Indoor scenes with realistic/photorealistic style")
print("-"*80)
results = conn.execute("""
    SELECT p.id, substr(p.original_prompt, 1, 100) as prompt, 
           s.specific_place, a.primary_style
    FROM prompts p
    JOIN settings s ON p.id = s.prompt_id
    JOIN art_styles a ON p.id = a.prompt_id
    WHERE s.indoor_outdoor = 'indoor'
      AND (a.primary_style LIKE '%realistic%' OR a.primary_style LIKE '%photorealistic%')
    LIMIT 5
""").fetchall()

for i, (pid, prompt, place, style) in enumerate(results, 1):
    print(f"{i}. [ID {pid}] {style} @ {place or 'indoor'}")
    print(f"   {prompt}...")

print(f"\nTotal found: {len(results)}")

# Query 4: Prompts with multiple people
print("\n📊 QUERY 4: Prompts with 2+ people")
print("-"*80)
results = conn.execute("""
    SELECT p.id, c.number_of_people, substr(p.original_prompt, 1, 80) as prompt
    FROM prompts p
    JOIN characters c ON p.id = c.prompt_id
    WHERE c.number_of_people >= 2
    ORDER BY c.number_of_people DESC
    LIMIT 5
""").fetchall()

for i, (pid, count, prompt) in enumerate(results, 1):
    print(f"{i}. [ID {pid}] {count} people: {prompt}...")

print(f"\nTotal found: {len(results)}")

# Query 5: Most common tags
print("\n📊 QUERY 5: Top 15 most common tags")
print("-"*80)
results = conn.execute("""
    SELECT tag, COUNT(*) as frequency
    FROM main_tags
    GROUP BY tag
    ORDER BY frequency DESC
    LIMIT 15
""").fetchall()

for i, (tag, count) in enumerate(results, 1):
    bar = "█" * min(count, 20)
    print(f"{i:2d}. {tag:20s} {bar} {count}")

# Query 6: Complex search - Explicit, 2 people, photorealistic
print("\n📊 QUERY 6: Complex - Explicit + 2 people + Photorealistic")
print("-"*80)
results = conn.execute("""
    SELECT DISTINCT p.id, substr(p.original_prompt, 1, 100) as prompt
    FROM prompts p
    JOIN nsfw_content n ON p.id = n.prompt_id
    JOIN characters c ON p.id = c.prompt_id
    JOIN art_styles a ON p.id = a.prompt_id
    WHERE n.level = 'explicit'
      AND c.number_of_people = 2
      AND a.primary_style LIKE '%photorealistic%'
    LIMIT 5
""").fetchall()

for i, (pid, prompt) in enumerate(results, 1):
    print(f"{i}. [ID {pid}] {prompt}...")

print(f"\nTotal found: {len(results)}")

# Query 7: Distribution by art style
print("\n📊 QUERY 7: Distribution by art style")
print("-"*80)
results = conn.execute("""
    SELECT primary_style, COUNT(*) as count
    FROM art_styles
    WHERE primary_style IS NOT NULL
    GROUP BY primary_style
    ORDER BY count DESC
""").fetchall()

for style, count in results:
    pct = (count / 30) * 100
    print(f"  {style:20s} {count:2d} prompts ({pct:5.1f}%)")

print("\n" + "="*80)
print("✅ All example queries completed successfully!")
print("="*80)
print("\nDatabase contains 30 prompts with full categorization.")
print("You can run complex searches combining any categories.")

conn.close()
