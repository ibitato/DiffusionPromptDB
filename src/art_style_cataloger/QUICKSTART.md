# Quick Start Guide - Art Style Cataloger

## Resumen del Sistema

Has creado un sistema completo para catalogar automáticamente los 4,953 prompts con tipo de arte "Unspecified" usando AWS Bedrock Batch API.

## 🎯 Estado Actual

- ✅ **Base de datos identificada**: `src/api/database/prompts_catalog.db`
- ✅ **Prompts a catalogar**: 4,953 (47.7% del total)
- ✅ **Tipos de arte disponibles**: 204 estilos diferentes
- ✅ **Infraestructura**: Reutiliza batch_analyzer existente
- ✅ **Costo estimado**: ~$4.13 USD con Claude 3.5 Sonnet Batch API

## 📁 Archivos Creados

```
src/art_style_cataloger/
├── README.md                       # Documentación completa
├── QUICKSTART.md                   # Esta guía
├── .gitignore                      # Ignora datos y resultados
├── extract_unspecified_prompts.py  # Paso 1: Extraer de BBDD
├── run_art_cataloger.py           # Paso 2: Lanzar batch job
├── check_status.py                # Paso 3: Monitorear
└── apply_results.py               # Paso 4: Actualizar BBDD
```

## 🚀 Uso Inmediato

### Opción A: Ejecución Completa (Recomendada)

```bash
cd src/art_style_cataloger

# 1. Extraer prompts
python extract_unspecified_prompts.py

# 2. Lanzar batch job (usa config de batch_analyzer automáticamente)
python run_art_cataloger.py

# 3. Monitorear (espera 2-4 horas)
python check_status.py --watch

# 4. Aplicar resultados
python apply_results.py --dry-run  # Primero ver cambios
python apply_results.py            # Luego aplicar
```

### Opción B: Test Rápido (Sin AWS)

```bash
cd src/art_style_cataloger

# Solo extraer y ver los datos
python extract_unspecified_prompts.py

# Preparar batch input sin enviarlo
python run_art_cataloger.py --dry-run
```

## ⚙️ Configuración

El sistema usa automáticamente la configuración de `../batch_analyzer/config.yaml`. 

**Asegúrate que tienes configurado:**
1. AWS credentials (en `~/.aws/credentials` o variables de entorno)
2. Acceso a Bedrock en la región configurada
3. S3 bucket para batch jobs

Si necesitas configuración separada:
```bash
cp ../batch_analyzer/config.yaml.example config.yaml
# Editar config.yaml
```

## 📊 Análisis de Datos

Para ver estadísticas antes de ejecutar:

```bash
# Ver distribución de tipos de arte actual
python ../../scripts/analyze_art_styles.py

# Ver todas las bases de datos
python ../../scripts/check_databases.py
```

## 🔒 Seguridad

- ✅ Los datos extraídos se guardan en `data/` (gitignored)
- ✅ Los resultados se guardan en `results/` (gitignored)
- ✅ Se crea backup automático antes de actualizar BBDD
- ✅ Validación de tipos de arte contra catálogo existente
- ✅ Opción `--dry-run` en todos los scripts críticos

## 💡 Características Clave

1. **Reutiliza infraestructura**: No duplica código del batch_analyzer
2. **Sin enmarronar desarrollo**: Directorio separado, datos gitignored
3. **Monitoreo en tiempo real**: Ve progreso del batch job
4. **Seguro**: Backups automáticos, validación de datos
5. **Flexible**: Dry-run mode, opciones de línea de comandos

## 📖 Documentación

- **README.md**: Documentación completa del sistema
- **src/batch_analyzer/README.md**: Documentación de la infraestructura Bedrock
- **Scripts de análisis**: En `scripts/` para estadísticas

## 🆘 Troubleshooting

**Error: "Config file not found"**
- El sistema usará automáticamente `../batch_analyzer/config.yaml`
- O crea tu propio `config.yaml`

**Error: "AWS connection failed"**
- Verifica credenciales: `aws sts get-caller-identity`
- Verifica acceso a Bedrock en AWS Console

**Error: "Base de datos no encontrada"**
- Verifica ruta: `src/api/database/prompts_catalog.db`
- El script usa rutas relativas desde art_style_cataloger/

## 📈 Próximos Pasos

1. **Ejecutar extracción**: `python extract_unspecified_prompts.py`
2. **Revisar datos**: Verificar `data/unspecified_prompts_*.jsonl`
3. **Lanzar job**: `python run_art_cataloger.py` (o --dry-run primero)
4. **Monitorear**: `python check_status.py --watch`
5. **Aplicar**: `python apply_results.py --dry-run` luego sin --dry-run

## 💰 Costos

- **Claude 3.5 Sonnet Batch API**: 50% descuento vs standard
- **Input**: ~300 tokens/prompt × 4,953 = ~1.5M tokens
- **Output**: ~50 tokens/prompt × 4,953 = ~250K tokens
- **Total estimado**: ~$4.13 USD

---

**Listo para usar!** 🎉

Ejecuta `python extract_unspecified_prompts.py` para comenzar.
