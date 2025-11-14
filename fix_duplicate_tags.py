import sqlite3

# Connect to database
conn = sqlite3.connect('src/api/database/prompts_catalog.db')
cursor = conn.cursor()

print("=== ANTES DE LA CORRECCIÓN ===")
cursor.execute("SELECT * FROM main_tags WHERE prompt_id = 10384 ORDER BY tag")
tags = cursor.fetchall()
print(f"Total de tags: {len(tags)}")
for tag in tags:
    print(f"  - {tag}")

# Remove duplicate 'll' tags
print("\n=== ELIMINANDO DUPLICADOS ===")
cursor.execute("DELETE FROM main_tags WHERE prompt_id = 10384 AND tag = 'll'")
print(f"Tags 'll' eliminados: {cursor.rowcount}")

# Re-insert one 'll' tag
cursor.execute("INSERT INTO main_tags (prompt_id, tag) VALUES (10384, 'll')")
print("Re-insertado un tag 'll'")

conn.commit()

print("\n=== DESPUÉS DE LA CORRECCIÓN ===")
cursor.execute("SELECT * FROM main_tags WHERE prompt_id = 10384 ORDER BY tag")
tags = cursor.fetchall()
print(f"Total de tags: {len(tags)}")
for tag in tags:
    print(f"  - {tag}")

# Create the proper tags string for the API
tags_list = [tag[1] for tag in tags]
tags_string = ','.join(tags_list)
print(f"\nString de tags para la API: {tags_string}")

conn.close()

print("\n✅ Duplicados eliminados correctamente")
