# Art Style Cataloger

Sistema para catalogar automáticamente los tipos de arte de prompts con valor "Unspecified" usando AWS Bedrock Batch API.

## Problema

Tenemos **4,953 prompts** (47.7% del total) con `art_style = "Unspecified"` en la base de datos.

## Solución

Usar AWS Bedrock Batch API con Claude 3.5 Sonnet para catalogar automáticamente estos prompts entre los 204 tipos de arte existentes.

## Tipos de Arte Disponibles

Los tipos más comunes:
- realistic (2,292 prompts)
- anime (1,509 prompts)  
- photorealistic (407 prompts)
- cartoon (151 prompts)
- illustration (54 prompts)
- ... y 199 más

## Prerequisitos

1. **AWS Credentials**: Configuradas en `~/.aws/credentials` o variables de entorno
2. **Bedrock Access**: Acceso habilitado a Claude 3.5 Sonnet en la región configurada
3. **S3 Bucket**: Bucket configurado para batch jobs (ver config del batch_analyzer)
4. **Python Dependencies**: `pip install -r ../batch_analyzer/requirements.txt`

## Setup Rápido

```bash
cd src/art_style_cataloger

# Opción 1: Usar configuración del batch_analyzer (recomendado)
# El sistema automáticamente usará ../batch_analyzer/config.yaml

# Opción 2: Crear configuración propia
cp ../batch_analyzer/config.yaml.example config.yaml
# Editar config.yaml con tus credenciales AWS y S3 bucket
```

## Flujo de Trabajo Completo

### Paso 1: Extraer prompts con "Unspecified"
```bash
python extract_unspecified_prompts.py
```
**Output:**
- `data/unspecified_prompts_YYYYMMDD_HHMMSS.jsonl` - Prompts a catalogar
- `data/valid_art_styles.json` - Lista de 204 tipos de arte disponibles

### Paso 2: Lanzar batch job en Bedrock
```bash
# Dry run primero (preparar sin enviar)
python run_art_cataloger.py --dry-run

# Enviar el job real
python run_art_cataloger.py
```
**Output:**
- `data/batch_input_YYYYMMDD_HHMMSS.jsonl` - Input preparado para Bedrock
- `data/job_XXXXX.json` - Información del job (ARN, status, etc.)

### Paso 3: Monitorear progreso
```bash
# Verificación única
python check_status.py

# Monitoreo continuo (actualiza cada 30s)
python check_status.py --watch
```
El job típicamente tarda 2-4 horas para ~5,000 prompts.

### Paso 4: Aplicar resultados
```bash
# Dry run primero (ver cambios sin aplicar)
python apply_results.py --dry-run

# Aplicar cambios reales (se crea backup automático)
python apply_results.py
```
**Seguridad:**
- Se crea backup automático de la BBDD antes de actualizar
- Validación de tipos de arte contra el catálogo existente
- Los resultados se guardan en `results/` para auditoría

## Comandos Adicionales

```bash
# Ver job específico
python check_status.py --job-arn arn:aws:bedrock:...

# Aplicar resultados de archivo específico
python apply_results.py --results-file results/batch_results_XXXXX.jsonl

# Ver ayuda
python extract_unspecified_prompts.py --help
python run_art_cataloger.py --help
python check_status.py --help
python apply_results.py --help
```

## Archivos

- `extract_unspecified_prompts.py` - Extrae prompts de la BBDD a JSONL
- `run_art_cataloger.py` - Lanza el batch job en Bedrock
- `check_status.py` - Monitorea el progreso del job
- `apply_results.py` - Aplica los resultados a la BBDD
- `config.yaml` - Configuración (AWS, S3, modelo, etc.)

## Base de Datos

**BBDD Principal**: `src/api/database/prompts_catalog.db`

**Tabla**: `art_styles`
- `prompt_id` (INTEGER)
- `primary_style` (TEXT)

## Costos Estimados

Para 4,953 prompts con Claude 3.5 Sonnet (Batch API con 50% descuento):
- Input tokens estimados: ~1.5M (300 tokens/prompt)
- Output tokens estimados: ~250K (50 tokens/prompt) 
- **Costo estimado: ~$4.13 USD**

## Seguridad

- Los resultados se guardan en `results/` (gitignored)
- La BBDD principal solo se actualiza después de revisión manual
- Siempre se hace backup antes de aplicar cambios
