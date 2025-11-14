"""
Script principal para catalogar tipos de arte usando AWS Bedrock Batch API
Reutiliza la infraestructura de src/batch_analyzer
"""

import sys
import json
from pathlib import Path
from datetime import datetime
import os

# Añadir el path del batch_analyzer para reutilizar el código
sys.path.insert(0, str(Path(__file__).parent.parent / "batch_analyzer"))

from core.bedrock_client import BedrockBatchClient
import yaml


class ArtStyleCataloger:
    """Catalogador de tipos de arte usando Bedrock"""

    def __init__(self, config_path="config.yaml"):
        """Inicializa el catalogador"""
        self.config = self._load_config(config_path)

        # Inicializar cliente Bedrock
        aws_config = self.config.get("aws", {})
        self.bedrock = BedrockBatchClient(
            profile_name=aws_config.get("profile"),
            region_name=aws_config.get("region", "us-east-1"),
        )

        self.valid_styles = self._load_valid_styles()

    def _load_config(self, config_path):
        """Carga la configuración"""
        config_file = Path(config_path)
        if not config_file.exists():
            print(f"⚠️ Config file not found: {config_path}")
            print("📋 Using default configuration from batch_analyzer")
            # Usar config del batch_analyzer
            batch_config = (
                Path(__file__).parent.parent / "batch_analyzer" / "config.yaml"
            )
            if batch_config.exists():
                with open(batch_config) as f:
                    return yaml.safe_load(f)
            else:
                raise FileNotFoundError(
                    "No se encontró ningún archivo de configuración"
                )

        with open(config_file) as f:
            return yaml.safe_load(f)

    def _load_valid_styles(self):
        """Carga la lista de tipos de arte válidos"""
        styles_file = Path("data/valid_art_styles.json")
        if not styles_file.exists():
            print("⚠️ Archivo de tipos de arte no encontrado")
            print("➡️ Ejecuta primero: python extract_unspecified_prompts.py")
            sys.exit(1)

        with open(styles_file) as f:
            data = json.load(f)
            return data["styles"]

    def create_prompt_template(self):
        """Crea el prompt template para catalogación de arte"""
        # Top 20 estilos más comunes para referencia
        top_styles = self.valid_styles[:20]

        template = f"""Analyze the following Stable Diffusion prompt and determine its art style.

Available art styles (choose ONE that best matches):
{', '.join(top_styles)}

... and {len(self.valid_styles) - 20} more styles including: {', '.join(self.valid_styles[20:40])}

Rules:
1. Choose ONLY ONE art style from the available list
2. If the prompt explicitly mentions an art style (e.g., "anime", "realistic"), use that
3. If multiple styles could apply, choose the most dominant one
4. Consider visual characteristics described in the prompt
5. Return ONLY the exact style name from the list (case-sensitive)
6. If truly ambiguous, choose the most generic applicable style

Prompt to analyze:
{{{{PROMPT}}}}

Respond with ONLY the art style name, nothing else."""

        return template

    def prepare_batch_input(self, input_file):
        """Prepara el archivo de entrada para Bedrock Batch API"""
        print(f"\n📋 Preparando batch input desde: {input_file}")

        template = self.create_prompt_template()
        output_file = (
            Path("data")
            / f"batch_input_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"
        )

        count = 0
        with open(input_file, "r", encoding="utf-8") as fin, open(
            output_file, "w", encoding="utf-8"
        ) as fout:

            for line in fin:
                if not line.strip():
                    continue

                record = json.loads(line)
                prompt_id = record["id"]
                prompt_text = record["prompt"]

                # Formato para Bedrock Batch API
                batch_record = {
                    "recordId": str(prompt_id),
                    "modelInput": {
                        "anthropic_version": "bedrock-2023-05-31",
                        "max_tokens": 100,
                        "messages": [
                            {
                                "role": "user",
                                "content": template.replace("{{PROMPT}}", prompt_text),
                            }
                        ],
                    },
                }

                fout.write(json.dumps(batch_record) + "\n")
                count += 1

        print(f"✅ {count:,} registros preparados en: {output_file}")
        return output_file

    def run(self, input_file, dry_run=False):
        """Ejecuta el proceso de catalogación"""
        print("=" * 80)
        print("ART STYLE CATALOGER - AWS BEDROCK BATCH API")
        print("=" * 80)

        # Preparar input
        batch_input = self.prepare_batch_input(input_file)

        if dry_run:
            print("\n🔍 DRY RUN - No se enviará el job a Bedrock")
            print(f"📁 Archivo preparado: {batch_input}")
            print(f"\n✅ Preparación completa. Usa sin --dry-run para lanzar el job.")
            return

        # Configuración S3 y Bedrock
        model_id = self.config["bedrock"]["model_id"]
        batch_config = self.config["batch"]
        input_s3_uri = batch_config["input_s3_uri"]
        output_s3_uri = batch_config["output_s3_uri"]

        print(f"\n🚀 Lanzando batch job en Bedrock...")
        print(f"   Modelo: {model_id}")
        print(f"   Input file: {batch_input}")
        print(f"   S3 Input: {input_s3_uri}")
        print(f"   S3 Output: {output_s3_uri}")

        try:
            # Leer registros del archivo
            with open(batch_input, "r") as f:
                requests = [json.loads(line) for line in f if line.strip()]

            # Preparar nombres con timestamp único
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            job_name = f"art-cataloger-{timestamp}"
            s3_input_file = (
                f"{input_s3_uri.rstrip('/')}/art-cataloger-{timestamp}.jsonl"
            )

            # Subir a S3
            print(f"\n📤 Subiendo {len(requests)} registros a S3...")
            print(f"   Destino: {s3_input_file}")
            success, msg = self.bedrock.upload_batch_input(requests, s3_input_file)

            if not success:
                print(f"❌ Error subiendo a S3: {msg}")
                return

            print(f"✅ {msg}")

            print(f"\n🚀 Creando batch job: {job_name}")

            success, job_arn, msg = self.bedrock.create_batch_job(
                job_name=job_name,
                model_id=model_id,
                input_s3_uri=s3_input_file,
                output_s3_uri=output_s3_uri,
            )

            if not success:
                print(f"❌ Error creando batch job: {msg}")
                return

            # Guardar información del job
            job_file = Path("data") / f"job_{job_arn.split('/')[-1]}.json"
            with open(job_file, "w") as f:
                json.dump(
                    {
                        "job_arn": job_arn,
                        "job_name": job_name,
                        "model_id": model_id,
                        "submitted_at": datetime.now().isoformat(),
                        "input_file": str(batch_input),
                        "total_records": len(requests),
                    },
                    f,
                    indent=2,
                )

            print(f"\n✅ Batch job creado exitosamente!")
            print(f"   Job ARN: {job_arn}")
            print(f"   Total prompts: {len(requests):,}")
            print(f"   Info guardada en: {job_file}")
            print(f"\n➡️ Monitorear progreso: python check_status.py --watch")

        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback

            traceback.print_exc()
            raise


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Catalogar tipos de arte con Bedrock")
    parser.add_argument(
        "--input",
        default="data/unspecified_prompts_*.jsonl",
        help="Archivo JSONL con los prompts a catalogar",
    )
    parser.add_argument(
        "--config", default="config.yaml", help="Archivo de configuración"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Preparar input sin enviar a Bedrock"
    )

    args = parser.parse_args()

    # Buscar el archivo más reciente si se usa wildcard
    if "*" in args.input:
        data_dir = Path("data")
        files = sorted(data_dir.glob("unspecified_prompts_*.jsonl"), reverse=True)
        if not files:
            print("❌ No se encontró ningún archivo de prompts")
            print("➡️ Ejecuta primero: python extract_unspecified_prompts.py")
            sys.exit(1)
        args.input = files[0]
        print(f"📁 Usando archivo más reciente: {args.input}")

    cataloger = ArtStyleCataloger(args.config)
    cataloger.run(args.input, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
