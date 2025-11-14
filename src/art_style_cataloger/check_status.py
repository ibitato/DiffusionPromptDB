"""
Monitorea el progreso del batch job de catalogación
"""
import sys
import json
from pathlib import Path
from datetime import datetime
import time

# Añadir el path del batch_analyzer
sys.path.insert(0, str(Path(__file__).parent.parent / "batch_analyzer"))

from core.bedrock_client import BedrockBatchClient
import yaml

def load_config():
    """Carga la configuración"""
    config_file = Path("config.yaml")
    if not config_file.exists():
        # Usar config del batch_analyzer
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
    aws_config = config.get('aws', {})
    return BedrockBatchClient(
        profile_name=aws_config.get('profile'),
        region_name=aws_config.get('region', 'us-east-1')
    )

def find_latest_job():
    """Encuentra el archivo del job más reciente"""
    data_dir = Path("data")
    job_files = sorted(data_dir.glob("job_*.json"), reverse=True)
    if not job_files:
        return None
    return job_files[0]

def format_duration(seconds):
    """Formatea duración en formato legible"""
    if seconds < 60:
        return f"{seconds:.0f}s"
    elif seconds < 3600:
        return f"{seconds/60:.1f}m"
    else:
        return f"{seconds/3600:.1f}h"

def check_status(job_arn=None, watch=False):
    """Verifica el estado del batch job"""
    config = load_config()
    if not config:
        print("❌ No se pudo cargar la configuración")
        return
    
    bedrock = get_bedrock_client(config)
    
    # Si no se proporciona ARN, buscar el job más reciente
    if not job_arn:
        job_file = find_latest_job()
        if not job_file:
            print("❌ No se encontró ningún job. Ejecuta primero: python run_art_cataloger.py")
            return
        
        with open(job_file) as f:
            job_data = json.load(f)
            job_arn = job_data["job_arn"]
        
        print(f"📁 Usando job más reciente: {job_file.name}")
    
    print("=" * 80)
    print("ESTADO DEL BATCH JOB")
    print("=" * 80)
    
    while True:
        try:
            # Obtener estado del job
            response = bedrock.bedrock_client.get_model_invocation_job(jobIdentifier=job_arn)
            
            status = response['status']
            job_name = response.get('jobName', 'N/A')
            submit_time = response.get('submitTime')
            end_time = response.get('endTime')
            
            # Calcular estadísticas
            if submit_time:
                elapsed = (datetime.now(submit_time.tzinfo) - submit_time).total_seconds()
            else:
                elapsed = 0
            
            # Mostrar información
            print(f"\n🔍 Job ARN: {job_arn}")
            print(f"📝 Job Name: {job_name}")
            print(f"📊 Estado: {status}")
            print(f"⏱️  Tiempo transcurrido: {format_duration(elapsed)}")
            
            # Métricas si están disponibles
            if 'invocationMetrics' in response:
                metrics = response['invocationMetrics']
                total = metrics.get('totalRecordCount', 0)
                processed = metrics.get('completeRecordCount', 0)
                failed = metrics.get('errorRecordCount', 0)
                
                if total > 0:
                    progress = (processed / total) * 100
                    print(f"\n📈 Progreso:")
                    print(f"   Total: {total:,} prompts")
                    print(f"   ✅ Procesados: {processed:,} ({progress:.1f}%)")
                    print(f"   ❌ Fallidos: {failed:,}")
                    
                    if processed > 0 and status == 'InProgress':
                        rate = processed / elapsed if elapsed > 0 else 0
                        remaining = total - processed
                        eta = remaining / rate if rate > 0 else 0
                        print(f"   ⚡ Velocidad: {rate:.1f} prompts/s")
                        print(f"   ⏳ Tiempo estimado: {format_duration(eta)}")
            
            # Output location si está disponible
            if 'outputDataConfig' in response:
                output = response['outputDataConfig'].get('s3OutputDataConfig', {})
                output_uri = output.get('s3Uri', 'N/A')
                print(f"\n📤 Output S3: {output_uri}")
            
            # Estados finales
            if status == 'Completed':
                print(f"\n✅ ¡Job completado exitosamente!")
                print(f"⏱️  Duración total: {format_duration(elapsed)}")
                print(f"\n➡️ Siguiente paso: python apply_results.py")
                break
            
            elif status == 'Failed':
                print(f"\n❌ Job falló")
                if 'failureMessage' in response:
                    print(f"   Error: {response['failureMessage']}")
                break
            
            elif status == 'Stopping' or status == 'Stopped':
                print(f"\n⚠️ Job detenido")
                break
            
            # Si no estamos en modo watch, salir
            if not watch:
                break
            
            # Esperar antes de la siguiente verificación
            print(f"\n⏳ Verificando de nuevo en 30 segundos... (Ctrl+C para salir)")
            time.sleep(30)
            print("\033[2J\033[H")  # Limpiar pantalla
            
        except KeyboardInterrupt:
            print(f"\n\n⏸️  Monitoreo interrumpido (el job sigue ejecutándose)")
            break
        except Exception as e:
            print(f"\n❌ Error al verificar estado: {e}")
            break

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Verificar estado del batch job")
    parser.add_argument("--job-arn", help="ARN del job (opcional, usa el más reciente)")
    parser.add_argument("--watch", action="store_true",
                       help="Monitorear continuamente hasta que complete")
    
    args = parser.parse_args()
    check_status(args.job_arn, args.watch)

if __name__ == "__main__":
    main()
