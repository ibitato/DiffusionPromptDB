"""
Analiza las estadísticas de los resultados de catalogación
"""

import json
from pathlib import Path
from collections import Counter

results_file = Path("results/batch_results_20251114_145717.jsonl")

print("📊 ANALIZANDO RESULTADOS DE CATALOGACIÓN")
print("=" * 80)

results = {}
errors = 0

with open(results_file, "r", encoding="utf-8") as f:
    for line in f:
        if not line.strip():
            continue

        try:
            record = json.loads(line)
            record_id = record.get("recordId")

            if record.get("error"):
                errors += 1
                continue

            model_output = record.get("modelOutput", {})
            content = model_output.get("content", [])

            if content and len(content) > 0:
                text = content[0].get("text", "").strip()

                if text.startswith("{"):
                    try:
                        parsed = json.loads(text)
                        art_style_data = parsed.get("art_style", {})
                        primary_style = art_style_data.get(
                            "primary_style", "unspecified"
                        )
                        if primary_style and primary_style.lower() != "unspecified":
                            results[int(record_id)] = primary_style
                    except json.JSONDecodeError:
                        pass
        except Exception as e:
            print(f"Error: {e}")

# Estadísticas
styles = Counter(results.values())

print(f"\n✅ Total prompts catalogados: {len(results):,}")
print(f"📊 Tipos de arte únicos: {len(styles)}")
print(f"❌ Errores: {errors}")

print(f"\n🏆 TOP 20 ESTILOS DETECTADOS:")
print("-" * 80)
for i, (style, count) in enumerate(styles.most_common(20), 1):
    percentage = (count / len(results)) * 100
    print(f"  {i:2}. {style:35} {count:4,} prompts ({percentage:5.1f}%)")

print(f"\n💾 RESUMEN:")
print(f"   De los 4,953 prompts originales con 'Unspecified'")
print(
    f"   Se catalogaron exitosamente: {len(results):,} prompts ({(len(results)/4953)*100:.1f}%)"
)
print(f"   Restantes sin catalogar: {4953 - len(results):,} prompts")
