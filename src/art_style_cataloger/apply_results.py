"""
Descarga los resultados del batch job y actualiza la BBDD
"""

import sys
import json
import sqlite3
import shutil
from pathlib import Path
from datetime import datetime

# Añadir el path del batch_analyzer
sys.path.insert(0, str(Path(__file__).parent.parent / "batch_analyzer"))

from core.bedrock_client import BedrockBatchClient
import yaml
import boto3


def load_config():
    """Carga la configuración"""
    config_file = Path("config.yaml")
    if not config_file.exists():
        batch_config = Path(__file__).parent.parent / "batch_analyzer" / "config.yaml"
        if batch_config.exists():
            with open(batch_config) as f:
                return yaml.safe_load(f)
    else:
        with open(config_file) as f:
            return yaml.safe_load(f)
    return None


def get_bedrock_client(config):
    """Crea cliente Bedrock desde config"""
    aws_config = config.get("aws", {})
    return BedrockBatchClient(
        profile_name=aws_config.get("profile"),
        region_name=aws_config.get("region", "us-east-1"),
    )


def find_latest_job():
    """Encuentra el archivo del job más reciente"""
    data_dir = Path("data")
    job_files = sorted(data_dir.glob("job_*.json"), reverse=True)
    if not job_files:
        return None
    return job_files[0]


def download_results(job_arn, config):
    """Descarga los resultados desde S3"""
    bedrock = get_bedrock_client(config)

    # Obtener información del job
    response = bedrock.bedrock_client.get_model_invocation_job(jobIdentifier=job_arn)

    if response["status"] != "Completed":
        print(f"❌ El job no ha completado aún. Estado: {response['status']}")
        return None

    # Obtener S3 output URI
    output_config = response.get("outputDataConfig", {})
    s3_output = output_config.get("s3OutputDataConfig", {})
    s3_uri = s3_output.get("s3Uri")

    if not s3_uri:
        print("❌ No se encontró URI de salida S3")
        return None

    print(f"📥 Descargando resultados desde: {s3_uri}")

    # Parsear S3 URI
    s3_parts = s3_uri.replace("s3://", "").split("/", 1)
    bucket = s3_parts[0]
    prefix = s3_parts[1] if len(s3_parts) > 1 else ""

    # Descargar desde S3
    s3_client = boto3.client(
        "s3",
        region_name=config["aws"]["region"],
        aws_access_key_id=config["aws"].get("access_key_id"),
        aws_secret_access_key=config["aws"].get("secret_access_key"),
    )

    # Listar archivos en el output
    response = s3_client.list_objects_v2(Bucket=bucket, Prefix=prefix)

    if "Contents" not in response:
        print("❌ No se encontraron archivos de resultados")
        return None

    # Descargar el archivo .jsonl.out
    results_dir = Path("results")
    results_dir.mkdir(exist_ok=True)

    output_file = (
        results_dir / f"batch_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"
    )

    for obj in response["Contents"]:
        key = obj["Key"]
        if key.endswith(".jsonl.out"):
            print(f"   Descargando: {key}")
            s3_client.download_file(bucket, key, str(output_file))
            print(f"✅ Descargado: {output_file}")
            return output_file

    print("❌ No se encontró archivo .jsonl.out")
    return None


def parse_results(results_file):
    """Parsea los resultados del batch job"""
    print(f"\n📋 Parseando resultados: {results_file}")

    results = {}
    errors = []
    json_responses = 0
    simple_responses = 0

    with open(results_file, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            if not line.strip():
                continue

            try:
                record = json.loads(line)
                record_id = record.get("recordId")

                if record.get("error"):
                    errors.append({"id": record_id, "error": record["error"]})
                    continue

                # Extraer el art_style de la respuesta
                model_output = record.get("modelOutput", {})
                content = model_output.get("content", [])

                if content and len(content) > 0:
                    text = content[0].get("text", "").strip()

                    # Claude devolvió JSON completo en vez de solo el estilo
                    if text.startswith("{"):
                        try:
                            parsed = json.loads(text)
                            # Extraer art_style del JSON
                            art_style_data = parsed.get("art_style", {})
                            primary_style = art_style_data.get(
                                "primary_style", "unspecified"
                            )
                            if primary_style and primary_style.lower() != "unspecified":
                                results[int(record_id)] = primary_style
                                json_responses += 1
                        except json.JSONDecodeError:
                            pass
                    else:
                        # Respuesta simple con solo el nombre del estilo
                        if text and text.lower() != "unspecified":
                            results[int(record_id)] = text
                            simple_responses += 1

            except Exception as e:
                print(f"⚠️ Error en línea {line_num}: {e}")

    print(f"✅ Parseados: {len(results):,} resultados válidos")
    print(f"   📊 Respuestas JSON: {json_responses:,}")
    print(f"   📊 Respuestas simples: {simple_responses:,}")
    if errors:
        print(f"⚠️ Errores: {len(errors)}")

    return results, errors


def backup_database(db_path):
    """Crea backup de la base de datos"""
    backup_path = Path(
        str(db_path) + f".backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    )
    print(f"\n💾 Creando backup: {backup_path}")
    shutil.copy2(db_path, backup_path)
    print(f"✅ Backup creado")
    return backup_path


def update_database(
    results, db_path="../api/database/prompts_catalog.db", dry_run=False
):
    """Actualiza la base de datos con los resultados"""
    db_path = Path(db_path)

    if not db_path.exists():
        print(f"❌ Base de datos no encontrada: {db_path}")
        return False

    if dry_run:
        print(f"\n🔍 DRY RUN - Mostrando cambios sin aplicar:")
    else:
        print(f"\n💾 Actualizando base de datos: {db_path}")
        # Crear backup
        backup_database(db_path)

    # Conectar a la BBDD
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Estadísticas
    updated = 0
    invalid = 0
    unchanged = 0

    # Obtener lista de estilos válidos
    cursor.execute(
        """
        SELECT DISTINCT primary_style 
        FROM art_styles 
        WHERE primary_style IS NOT NULL 
        AND LOWER(primary_style) != 'unspecified'
    """
    )
    valid_styles = {row[0].lower(): row[0] for row in cursor.fetchall()}

    print(f"\n📊 Procesando {len(results):,} resultados...")

    for prompt_id, art_style in results.items():
        # Verificar que el estilo es válido
        art_style_lower = art_style.lower().strip()

        if art_style_lower in valid_styles:
            # Usar el estilo con el casing correcto de la BBDD
            correct_style = valid_styles[art_style_lower]

            if dry_run:
                if updated < 10:  # Mostrar solo los primeros 10 en dry run
                    print(f"   ID {prompt_id}: 'Unspecified' → '{correct_style}'")
            else:
                cursor.execute(
                    """
                    UPDATE art_styles 
                    SET primary_style = ? 
                    WHERE prompt_id = ? 
                    AND LOWER(primary_style) = 'unspecified'
                """,
                    (correct_style, prompt_id),
                )

                if cursor.rowcount > 0:
                    updated += 1
                else:
                    unchanged += 1
        else:
            invalid += 1
            if invalid <= 10:  # Mostrar primeros 10 inválidos
                print(f"   ⚠️ ID {prompt_id}: Estilo inválido '{art_style}'")

        if (updated + invalid + unchanged) % 500 == 0:
            print(f"   Procesados: {updated + invalid + unchanged:,}")

    if not dry_run:
        conn.commit()

    conn.close()

    # Resumen
    print("\n" + "=" * 80)
    print("RESUMEN DE ACTUALIZACIÓN")
    print("=" * 80)
    print(f"✅ Actualizados: {updated:,} prompts")
    print(f"⚠️ Inválidos: {invalid:,} prompts")
    print(f"⏭️  Sin cambios: {unchanged:,} prompts")

    if not dry_run:
        print(f"\n✅ Base de datos actualizada exitosamente")

    return True


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Aplicar resultados del batch job")
    parser.add_argument("--job-arn", help="ARN del job (opcional, usa el más reciente)")
    parser.add_argument(
        "--results-file", help="Archivo de resultados (si ya fue descargado)"
    )
    parser.add_argument(
        "--db",
        default="../api/database/prompts_catalog.db",
        help="Ruta a la base de datos",
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Mostrar cambios sin aplicar"
    )

    args = parser.parse_args()

    config = load_config()
    if not config:
        print("❌ No se pudo cargar la configuración")
        return

    # Si no se proporciona archivo de resultados, descargar
    if not args.results_file:
        # Buscar job más reciente si no se proporciona ARN
        if not args.job_arn:
            job_file = find_latest_job()
            if not job_file:
                print("❌ No se encontró ningún job")
                return

            with open(job_file) as f:
                job_data = json.load(f)
                args.job_arn = job_data["job_arn"]

            print(f"📁 Usando job más reciente: {job_file.name}")

        # Descargar resultados
        results_file = download_results(args.job_arn, config)
        if not results_file:
            return
    else:
        results_file = Path(args.results_file)
        if not results_file.exists():
            print(f"❌ Archivo de resultados no encontrado: {results_file}")
            return

    # Parsear resultados
    results, errors = parse_results(results_file)

    if errors:
        print(f"\n⚠️ Se encontraron {len(errors)} errores en los resultados")
        errors_file = (
            Path("results") / f"errors_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        with open(errors_file, "w") as f:
            json.dump(errors, f, indent=2)
        print(f"   Guardados en: {errors_file}")

    if not results:
        print("❌ No hay resultados para aplicar")
        return

    # Actualizar base de datos
    update_database(results, args.db, args.dry_run)


if __name__ == "__main__":
    main()
