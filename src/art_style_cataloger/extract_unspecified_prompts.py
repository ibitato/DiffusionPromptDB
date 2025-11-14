"""
Extrae prompts con art_style = 'Unspecified' de la BBDD principal
y los convierte a formato JSONL para Bedrock Batch API
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime

# Configuración
DB_PATH = "../api/database/prompts_catalog.db"
OUTPUT_DIR = Path("data")
OUTPUT_FILE = (
    OUTPUT_DIR / f"unspecified_prompts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"
)

# Crear directorio de salida
OUTPUT_DIR.mkdir(exist_ok=True)

print("=" * 80)
print("EXTRACTOR DE PROMPTS CON ART STYLE 'UNSPECIFIED'")
print("=" * 80)

# Conectar a la BBDD
conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Obtener prompts con art_style = 'Unspecified'
print(f"\n📊 Consultando BBDD: {DB_PATH}")
cursor.execute(
    """
    SELECT p.id, p.original_prompt
    FROM prompts p
    JOIN art_styles a ON p.id = a.prompt_id
    WHERE LOWER(a.primary_style) = 'unspecified'
    ORDER BY p.id
"""
)

prompts = cursor.fetchall()
print(f"✅ Encontrados {len(prompts):,} prompts con 'Unspecified'")

# Obtener lista de tipos de arte válidos
print(f"\n🎨 Obteniendo tipos de arte válidos...")
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
valid_styles = [row[0] for row in cursor.fetchall()]
print(f"✅ {len(valid_styles)} tipos de arte disponibles")

conn.close()

# Escribir a archivo JSONL
print(f"\n💾 Escribiendo a: {OUTPUT_FILE}")
count = 0
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    for row in prompts:
        record = {"id": row["id"], "prompt": row["original_prompt"]}
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
        count += 1
        if count % 500 == 0:
            print(f"   Procesados: {count:,} prompts")

print(f"✅ Completado: {count:,} prompts escritos")

# Guardar también la lista de tipos de arte válidos
art_styles_file = OUTPUT_DIR / "valid_art_styles.json"
with open(art_styles_file, "w", encoding="utf-8") as f:
    json.dump(
        {
            "total": len(valid_styles),
            "styles": valid_styles,
            "top_10": valid_styles[:10],
        },
        f,
        ensure_ascii=False,
        indent=2,
    )

print(f"✅ Lista de tipos de arte guardada en: {art_styles_file}")

print("\n" + "=" * 80)
print("RESUMEN")
print("=" * 80)
print(f"📁 Archivo de entrada para Bedrock: {OUTPUT_FILE}")
print(f"📊 Total prompts a catalogar: {count:,}")
print(f"🎨 Tipos de arte disponibles: {len(valid_styles)}")
print(f"💰 Costo estimado (Claude 3.5 Sonnet Batch): ~${count * 0.0008:.2f} USD")
print("\n➡️ Siguiente paso: python run_art_cataloger.py")
