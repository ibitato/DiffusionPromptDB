"""
Análisis de tipos de arte en la base de datos principal
"""

import sqlite3
from pathlib import Path

# Base de datos principal de la aplicación
DB_PATH = "src/api/database/prompts_catalog.db"

print("=" * 80)
print("ANÁLISIS DE TIPOS DE ARTE")
print("=" * 80)

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Ver estructura de la tabla art_styles
print("\n📋 Estructura de la tabla art_styles:")
cursor.execute("PRAGMA table_info(art_styles)")
columns = cursor.fetchall()
for col in columns:
    print(f"   - {col[1]} ({col[2]})")

# Contar total de registros
cursor.execute("SELECT COUNT(*) FROM art_styles")
total = cursor.fetchone()[0]
print(f"\n📊 Total registros en art_styles: {total:,}")

# Obtener distribución de primary_style
print("\n🎨 Distribución de primary_style:")
cursor.execute(
    """
    SELECT primary_style, COUNT(*) as count 
    FROM art_styles 
    GROUP BY primary_style 
    ORDER BY count DESC
"""
)
styles = cursor.fetchall()

unspecified_count = 0
for style, count in styles:
    is_unspecified = style and style.lower() == "unspecified"
    marker = "⚠️" if is_unspecified else "   "
    print(f"{marker} {style if style else '(NULL)'}: {count:,}")
    if is_unspecified:
        unspecified_count = count

print(f"\n⚠️ PROMPTS CON ARTE 'Unspecified': {unspecified_count:,}")

# Obtener tipos de arte válidos (excluyendo Unspecified y NULL)
print("\n✅ TIPOS DE ARTE VÁLIDOS (para usar en catalogación):")
cursor.execute(
    """
    SELECT DISTINCT primary_style, COUNT(*) as count 
    FROM art_styles 
    WHERE primary_style IS NOT NULL 
    AND LOWER(primary_style) != 'unspecified'
    GROUP BY primary_style
    ORDER BY count DESC
"""
)
valid_styles = cursor.fetchall()

for i, (style, count) in enumerate(valid_styles, 1):
    print(f"   {i:2}. {style}: {count:,} prompts")

print(f"\n📌 Total tipos de arte válidos: {len(valid_styles)}")

# Obtener sample de prompts con Unspecified
print("\n📝 SAMPLE de prompts con arte 'Unspecified' (primeros 5):")
cursor.execute(
    """
    SELECT p.id, SUBSTR(p.original_prompt, 1, 80) as prompt_preview
    FROM prompts p
    JOIN art_styles a ON p.id = a.prompt_id
    WHERE LOWER(a.primary_style) = 'unspecified'
    LIMIT 5
"""
)
samples = cursor.fetchall()
for prompt_id, preview in samples:
    print(f"   ID {prompt_id}: {preview}...")

conn.close()

print("\n" + "=" * 80)
print("RESUMEN")
print("=" * 80)
print(f"✅ Base de datos: {DB_PATH}")
print(f"📊 Total prompts: {total:,}")
print(f"⚠️ Prompts con 'Unspecified': {unspecified_count:,}")
print(f"🎨 Tipos de arte válidos: {len(valid_styles)}")
print("\n➡️ Necesitamos catalogar estos prompts 'Unspecified' usando Bedrock")
