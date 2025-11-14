import sqlite3
import json

# Connect to database
conn = sqlite3.connect('src/api/database/prompts_catalog.db')
cursor = conn.cursor()

print("=== ESTRUCTURA DE LA BASE DE DATOS ===\n")

# Get all tables related to tags
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%tag%'")
tag_tables = cursor.fetchall()

print("Tablas relacionadas con tags:")
for table in tag_tables:
    print(f"  - {table[0]}")
    
    # Get table structure
    cursor.execute(f"PRAGMA table_info({table[0]})")
    columns = cursor.fetchall()
    print("    Columnas:")
    for col in columns:
        print(f"      - {col[1]} ({col[2]})")
    
    # Get sample data
    cursor.execute(f"SELECT * FROM {table[0]} LIMIT 5")
    rows = cursor.fetchall()
    if rows:
        print(f"    Primeros registros:")
        for row in rows:
            print(f"      {row}")
    print()

# Check if there's a valid_tags table or similar
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND (name LIKE '%valid%' OR name LIKE '%allowed%' OR name LIKE '%catalog%')")
validation_tables = cursor.fetchall()

if validation_tables:
    print("\nTablas de validación/catálogo:")
    for table in validation_tables:
        print(f"  - {table[0]}")

# Check main_tags for prompt 10384
print("\n=== TAGS DEL PROMPT #10384 ===")
cursor.execute("SELECT * FROM main_tags WHERE prompt_id = 10384")
tags = cursor.fetchall()
print(f"Total de tags: {len(tags)}")
for tag in tags:
    print(f"  - {tag}")

# Check if there's a tags catalog/reference table
cursor.execute("SELECT DISTINCT tag FROM main_tags ORDER BY tag LIMIT 20")
unique_tags = cursor.fetchall()
print("\n=== ALGUNOS TAGS ÚNICOS EN LA BD ===")
for tag in unique_tags:
    print(f"  - {tag[0]}")

# Check if 'll' exists anywhere
cursor.execute("SELECT COUNT(*) FROM main_tags WHERE tag = 'll'")
ll_count = cursor.fetchone()[0]
print(f"\n=== TAG 'll' ===")
print(f"Aparece {ll_count} veces en la base de datos")

conn.close()
