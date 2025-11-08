# RPVEA VLM + Image Dedup Validation - CLI vs Python API Solutions

**Fecha:** 2025-10-16
**Contexto:** Validación RPVEA-A de VLM Descriptions + Image Deduplication
**Problema:** Error al ejecutar `process_document_complete()` - CLI de Docling/MinerU no encontrado

---

## Problema Detectado

### Error Actual
```
FileNotFoundError: [WinError 2] El sistema no puede encontrar el archivo especificado
RuntimeError: docling command not found. Please ensure Docling is properly installed.
```

### Causa Raíz
El método `process_document_complete()` de RAGAnything llama internamente a:
```
process_document_complete()
  → parse_document()
  → doc_parser.parse_pdf()
  → _run_docling_command()
  → subprocess.run(["docling", ...])  # ❌ CLI no instalado
```

**Estado actual del entorno:**
- ✅ Docling Python library instalada: `pip install docling`
- ❌ Docling CLI **NO** instalado (comando `docling` no disponible en PATH)
- ✅ MinerU Python library instalada: `pip install magic-pdf`
- ❌ MinerU CLI **NO** instalado (comando `mineru` no disponible)

### Archivos Involucrados
- `raganything/parser.py:1333-1346` - DoclingParser._run_docling_command()
- `raganything/parser.py:1240-1256` - MineruParser._run_mineru_command()
- Ambos intentan ejecutar comandos CLI via `subprocess.run()`

---

## OPCIÓN A: Usar Docling Python API Directamente (RECOMENDADO)

### Descripción
Modificar el script de procesamiento para usar la API de Python de Docling directamente, evitando las llamadas CLI en `parser.py`.

### Patrón Exitoso (Ya Validado Ayer)
El script `test_environment/docling_full_processing.py` procesó exitosamente documentos usando:

```python
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.datamodel.base_models import InputFormat

# Configurar pipeline
pipeline_options = PdfPipelineOptions()
pipeline_options.do_ocr = True
pipeline_options.do_table_structure = True

# Crear converter
converter = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
    }
)

# Parsear PDF (Python API, NO CLI)
result = converter.convert(str(pdf_path))

# Extraer content_list
content_list = extract_content_from_docling(result)

# Pasar a RAGAnything para procesamiento VLM
await rag.insert_content_list(content_list)
```

### Implementación

**Modificar:** `test_environment/rpvea_vlm_image_dedup_validation.py`
**Método:** `_create_processing_script()` (líneas 395-564)

**Cambios necesarios:**

1. **Imports adicionales:**
```python
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.datamodel.base_models import InputFormat
```

2. **Parsing con Python API:**
```python
# Configurar Docling pipeline
pipeline_options = PdfPipelineOptions()
pipeline_options.do_ocr = True
pipeline_options.do_table_structure = True

converter = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
    }
)

# Parsear documento
result = converter.convert(str(pdf_path))

# Extraer content_list (similar a docling_full_processing.py)
content_list = []
for element in result.document.iterate_items():
    # Extraer texto, imágenes, tablas, ecuaciones
    # ... (lógica de extracción)
    pass
```

3. **Llamar a RAGAnything:**
```python
# ❌ NO usar esto (llama a parser.py → CLI)
# await rag.process_document_complete(file_path=str(pdf_path), output_dir=str(output_dir))

# ✅ Usar esto (bypass parser.py)
await rag.insert_content_list(content_list)
```

### Ventajas
- ✅ **No requiere instalación adicional** - solo usamos lo que ya tenemos
- ✅ **Ya validado** - `docling_full_processing.py` funcionó ayer
- ✅ **Más control** - acceso directo a opciones de Docling
- ✅ **Compatibilidad Windows** - evita problemas de PATH y subprocess
- ✅ **Rápido** - solo modificar 1 archivo Python

### Desventajas
- ⚠️ **Código más largo** - necesitamos reimplementar lógica de extracción
- ⚠️ **Duplicación** - lógica similar a `parser.py` pero separada
- ⚠️ **Mantenimiento** - si Docling API cambia, necesitamos actualizar

### Esfuerzo Estimado
- **Tiempo:** 15-20 minutos
- **Complejidad:** Baja (copiar código de `docling_full_processing.py`)
- **Riesgo:** Bajo (patrón ya probado)

---

## OPCIÓN B: Instalar CLI de Docling y MinerU

### Descripción
Instalar los comandos CLI de Docling y MinerU para que `parser.py` pueda ejecutarlos via subprocess.

### Implementación

#### 1. Instalar Docling CLI

**Según documentación oficial de Docling:**
```bash
# Opción 1: Via pip (si está disponible)
pip install docling-cli

# Opción 2: Via pipx (recomendado para CLIs)
pipx install docling

# Opción 3: Desde repositorio
git clone https://github.com/DS4SD/docling.git
cd docling
pip install -e .[cli]
```

**Verificar instalación:**
```bash
docling --version
docling --help
```

#### 2. Instalar MinerU CLI

**Según documentación de MinerU 2.0:**
```bash
# Instalar con extras CLI
pip install magic-pdf[cli]

# O instalar paquete completo
pip install "magic-pdf[full]"

# Configurar CLI
mineru --version
mineru config
```

**Nota:** MinerU requiere configuración adicional (modelos, paths)

#### 3. Configurar PATH (Windows)

Si los comandos no se reconocen después de instalar:

```powershell
# Agregar Scripts de Python a PATH
$pythonScripts = (python -c "import sys; print(sys.prefix + '\\Scripts')")
$env:Path += ";$pythonScripts"

# Verificar
docling --version
mineru --version
```

#### 4. Actualizar parser.py (Opcional)

Si los CLIs están en ubicaciones no estándar:

```python
# En raganything/parser.py, modificar comandos
DOCLING_CMD = "docling"  # O ruta completa: r"C:\path\to\docling.exe"
MINERU_CMD = "mineru"    # O ruta completa: r"C:\path\to\mineru.exe"
```

#### 5. Ejecutar Validación

Una vez instalados los CLIs, el script actual debería funcionar:

```bash
export PYTHONIOENCODING=utf-8
python test_environment/rpvea_vlm_image_dedup_validation.py
```

El orquestador llamará:
```
process_document_complete() → parser.py → subprocess.run(["docling", ...])  # ✅ Ahora funciona
```

### Ventajas
- ✅ **Código sin cambios** - el orquestador actual funciona tal cual
- ✅ **Usa arquitectura existente** - `parser.py` funciona como fue diseñado
- ✅ **Consistencia** - mismo flujo que producción
- ✅ **Sin duplicación** - reutiliza `parser.py` completamente

### Desventajas
- ⚠️ **Instalación adicional** - requiere paquetes extra
- ⚠️ **Posibles problemas de PATH** - especialmente en Windows
- ⚠️ **Configuración compleja** - MinerU requiere setup adicional
- ⚠️ **Dependencias extra** - más componentes que mantener
- ⚠️ **Overhead** - subprocess más lento que API directa

### Esfuerzo Estimado
- **Tiempo:** 30-60 minutos (instalación + troubleshooting)
- **Complejidad:** Media (configuración de CLIs en Windows)
- **Riesgo:** Medio (posibles problemas de PATH, permisos, modelos)

---

## COMPARACIÓN DIRECTA

| Criterio | Opción A: Python API | Opción B: CLI |
|----------|---------------------|---------------|
| **Instalación** | ✅ Ya tenemos todo | ⚠️ Requiere paquetes extra |
| **Tiempo setup** | 15-20 min | 30-60 min |
| **Riesgo** | Bajo (ya validado) | Medio (config CLI) |
| **Cambios código** | Modificar 1 archivo | Sin cambios |
| **Performance** | ✅ Más rápido (API directa) | ⚠️ Más lento (subprocess) |
| **Windows compat** | ✅ Sin problemas | ⚠️ Posibles issues PATH |
| **Mantenimiento** | ⚠️ Duplicación lógica | ✅ Usa parser.py |
| **Consistencia** | ⚠️ Bypass de parser.py | ✅ Flujo estándar |

---

## RECOMENDACIÓN

### Para Esta Validación: OPCIÓN A (Python API)

**Razones:**
1. **Urgencia:** Necesitamos validar VLM + dedup hoy
2. **Patrón probado:** `docling_full_processing.py` ya funcionó ayer
3. **Bajo riesgo:** Solo adaptamos código existente
4. **Windows:** Evitamos problemas de subprocess en Windows

### Para Producción Futura: OPCIÓN B (CLI)

**Razones:**
1. **Consistencia:** Usar la arquitectura diseñada en `parser.py`
2. **Mantenimiento:** No duplicar lógica de parsing
3. **Features completas:** Aprovechar todas las capacidades de los CLIs

---

## PLAN DE ACCIÓN RECOMENDADO

### Fase 1: Validación (HOY) - Opción A
```bash
1. Modificar rpvea_vlm_image_dedup_validation.py
2. Usar Docling Python API directamente
3. Completar validación RPVEA-A
4. Documentar resultados
```

### Fase 2: Mejora (FUTURO) - Opción B
```bash
1. Instalar Docling CLI
2. Instalar MinerU CLI
3. Configurar PATHs
4. Validar que parser.py funciona con CLIs
5. Documentar setup en README
```

---

## REFERENCIAS

### Archivos Clave
- `test_environment/docling_full_processing.py` - Patrón Python API exitoso
- `raganything/parser.py:1333-1346` - DoclingParser._run_docling_command()
- `docs/REFERENCE_Docling_MinerU_VLM_Setup.md` - Setup original

### Documentación Externa
- [Docling Python API](https://github.com/DS4SD/docling)
- [MinerU Documentation](https://github.com/opendatalab/MinerU)
- [Subprocess Best Practices Windows](https://docs.python.org/3/library/subprocess.html)

---

## DECISIÓN FINAL

**Usuario debe decidir:**
- [ ] **Opción A:** Modificar script para usar Python API (15-20 min, bajo riesgo)
- [ ] **Opción B:** Instalar CLIs de Docling/MinerU (30-60 min, medio riesgo)

**Pregunta clave:** ¿Quieres completar la validación rápido (A) o configurar el entorno completo (B)?
