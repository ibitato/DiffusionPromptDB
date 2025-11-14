"""
Script para analizar qué bases de datos usa la aplicación
"""
import sqlite3
import os
from pathlib import Path

# Bases de datos encontradas
databases = [
    "data/prompts.db",
    "src/api/catalog.db",
    "src/api/database/prompts_catalog.db",
    "src/api/src/api/database/prompts_catalog.db",
    "src/batch_analyzer/prompts_catalog.db",
    "src/data/users.db"
]

print("=" * 80)
print("ANÁLISIS DE BASES DE DATOS")
print("=" * 80)

for db_path in databases:
    full_path = Path(db_path)
    if not full_path.exists():
        print(f"\n❌ {db_path} - NO EXISTE")
        continue
    
    print(f"\n✅ {db_path}")
    print(f"   Tamaño: {full_path.stat().st_size / (1024*1024):.2f} MB")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Obtener lista de tablas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"   Tablas ({len(tables)}): {', '.join([t[0] for t in tables])}")
        
        # Si tiene tabla prompts, contar registros
        if any('prompts' in t[0] for t in tables):
            cursor.execute("SELECT COUNT(*) FROM prompts")
            count = cursor.fetchone()[0]
            print(f"   📊 Prompts: {count:,}")
            
            # Ver columnas de la tabla prompts
            cursor.execute("PRAGMA table_info(prompts)")
            columns = cursor.fetchall()
            col_names = [col[1] for col in columns]
            print(f"   Columnas: {', '.join(col_names[:10])}{'...' if len(col_names) > 10 else ''}")
            
            # Revisar art_style si existe
            if 'art_style' in col_names:
                cursor.execute("SELECT art_style, COUNT(*) FROM prompts GROUP BY art_style ORDER BY COUNT(*) DESC LIMIT 10")
                art_styles = cursor.fetchall()
                print(f"   🎨 Tipos de arte:")
                for style, count in art_styles:
                    print(f"      - {style if style else '(NULL)'}: {count:,}")
        
        conn.close()
        
    except Exception as e:
        print(f"   ⚠️ Error: {e}")

print("\n" + "=" * 80)
print("CONFIGURACIÓN DE LA API (config.py)")
print("=" * 80)
print("prompts_db_path: 'database/prompts_catalog.db'")
print("catalog_db_path: 'database/prompts_catalog.db'")
print("\n➡️ La app usa: src/api/database/prompts_catalog.db")
