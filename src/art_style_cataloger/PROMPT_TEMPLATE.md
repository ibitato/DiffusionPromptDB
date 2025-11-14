# Prompt Template para Catalogación de Arte

## 📋 Prompt Actual

El prompt que se envía a Claude 3.5 Sonnet para cada imagen es:

```
Analyze the following Stable Diffusion prompt and determine its art style.

Available art styles (choose ONE that best matches):
realistic, anime, photorealistic, cartoon, DISNEY_ANIMATION, semi realistic, 
ultra-realistic, illustration, 2d, impressionism, semi-realistic, 
Flat vector illustration, realism, fantasy, digital art, hyper-realistic, 
official art, realistic anime, watercolor

... and 184 more styles including: drawn animation, hentai, comic book, 
ultra realistic, g0thicPXL, cell shading, cinematic, concept art, drawn style, 
hyperrealistic, painting, 3d, pixel art, retro, stylized, Disney, gbf_style, 
semi-realism, urushihara satoshi style, comicbookpage style

Rules:
1. Choose ONLY ONE art style from the available list
2. If the prompt explicitly mentions an art style (e.g., "anime", "realistic"), use that
3. If multiple styles could apply, choose the most dominant one
4. Consider visual characteristics described in the prompt
5. Return ONLY the exact style name from the list (case-sensitive)
6. If truly ambiguous, choose the most generic applicable style

Prompt to analyze:
[EL PROMPT DE STABLE DIFFUSION AQUÍ]

Respond with ONLY the art style name, nothing else.
```

## 🎯 Ejemplo Real

**Input:**
```
score_9, 1girl, breasts, purple hair, nipples, uncensored, photorealistic lighting
```

**Output esperado:**
```
realistic
```

## 💡 Prompt Mejorado (Opcional)

Si quieres resultados más precisos, puedes usar este prompt mejorado:

```
You are an expert in Stable Diffusion prompts and art style classification.

Analyze the following Stable Diffusion prompt and classify it into ONE art style from the provided list.

AVAILABLE STYLES (204 total):
Top 20 most common:
- realistic (2,292 examples)
- anime (1,509 examples)
- photorealistic (407 examples)
- cartoon (151 examples)
- DISNEY_ANIMATION (105 examples)
- semi realistic (75 examples)
- ultra-realistic (58 examples)
- illustration (54 examples)
- 2d (43 examples)
- impressionism (35 examples)
[... rest of styles ...]

CLASSIFICATION RULES:
1. If the prompt explicitly mentions an art style keyword, prioritize that
2. Analyze visual characteristics:
   - "realistic", "photorealistic", "ultra-realistic" → choose the exact match
   - "anime", "manga", "japanese" indicators → anime
   - "cartoon", "toon", "cel shaded" → cartoon
   - "painting", "watercolor", "oil painting" → painting/watercolor
3. If ambiguous, choose the most generic applicable style
4. Return ONLY the exact style name (case-sensitive)

PROMPT TO ANALYZE:
```
[STABLE DIFFUSION PROMPT]
```

RESPONSE FORMAT:
Return only the style name, no explanation.
```

## 🔧 Dónde Cambiar el Prompt

El prompt se genera en el método `create_prompt_template()` del archivo:
`src/art_style_cataloger/run_art_cataloger.py`

Para modificarlo, edita las líneas 54-70 aproximadamente.

## 📊 Métricas del Prompt

**Tokens estimados por prompt:**
- Template base: ~250 tokens
- Prompt de usuario: ~50 tokens (promedio)
- **Total input**: ~300 tokens/prompt

**Output esperado:**
- 1-3 palabras (nombre del estilo)
- **Total output**: ~10-50 tokens/prompt

**Max tokens configurado**: 100 (suficiente)

## ⚙️ Configuración Actual

```python
"modelInput": {
    "anthropic_version": "bedrock-2023-05-31",
    "max_tokens": 100,
    "messages": [
        {
            "role": "user",
            "content": "[PROMPT TEMPLATE]"
        }
    ]
}
```

## 🎨 Ejemplos de Casos

### Caso 1: Estilo Explícito
**Input:** `"score_9, anime style, 1girl, colorful"`
**Expected:** `anime`

### Caso 2: Indicadores Visuales
**Input:** `"masterpiece, oil painting, landscape, sunset"`
**Expected:** `oil painting`

### Caso 3: Realismo
**Input:** `"photorealistic, 8k, detailed portrait, studio lighting"`
**Expected:** `photorealistic`

### Caso 4: Ambiguo
**Input:** `"score_9, 1girl, detailed"`
**Expected:** `realistic` (genérico)

## 🔄 Iteración y Mejora

Después de la primera ejecución, puedes:

1. Analizar resultados con `apply_results.py --dry-run`
2. Ver cuántos prompts fueron clasificados como "inválidos"
3. Ajustar el prompt si la precisión es baja
4. Re-ejecutar solo los prompts problemáticos

## 📝 Notas

- El prompt es case-sensitive (respeta mayúsculas/minúsculas)
- Lista completa de 204 estilos cargada desde `data/valid_art_styles.json`
- Top 20 estilos mostrados explícitamente en el prompt
- Otros 20 estilos mencionados como referencia
- Total: 40 estilos explícitos + "and 164 more"
