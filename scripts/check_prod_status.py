"""
Verifica el estado actual de la BBDD de producción
"""

import sqlite3

DB_PATH = "src/api/database/prompts_catalog.db"

print("=" * 70)
print("📊 ESTADO ACTUAL BBDD DE PRODUCCIÓN")
print("=" * 70)

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Total de registros
cursor.execute("SELECT COUNT(*) FROM art_styles")
total = cursor.fetchone()[0]

# Unspecified
cursor.execute(
    "SELECT COUNT(*) FROM art_styles WHERE LOWER(primary_style) = 'unspecified'"
)
unspecified = cursor.fetchone()[0]

# Catalogados
catalogados = total - unspecified

print(f"\n📍 Base de datos: {DB_PATH}")
print(f"\n📈 ESTADÍSTICAS:")
print(f"   Total registros: {total:,}")
print(f"   ✅ Catalogados: {catalogados:,} ({(catalogados/total*100):.1f}%)")
print(f"   ⚠️  Unspecified: {unspecified:,} ({(unspecified/total*100):.1f}%)")

print(f"\n🎯 PROGRESO DEL BATCH JOB:")
print(f"   Antes: 4,953 unspecified (47.7%)")
print(f"   Ahora: {unspecified:,} unspecified ({(unspecified/total*100):.1f}%)")
print(f"   🎉 Catalogados: {4953-unspecified:,} prompts")
print(f"   📊 Tasa de éxito: {((4953-unspecified)/4953*100):.1f}%")

print("\n" + "=" * 70)
conn.close()
