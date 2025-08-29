# 🛠️ COMANDOS DE VALIDACIÓN - RAG-ANYTHING PROJECT

## 📋 COMANDOS CRÍTICOS DE VALIDACIÓN

### SETUP Y ENVIRONMENT VALIDATION

```bash
# Verificar estado del repositorio
git status && git branch --show-current

# Verificar dependencias principales
python -c "import raganything; print('✅ RAG-Anything OK')"

# Verificar environment setup
python test_environment/01_pretest_requirements.py

# Check project status
python project_status.py
```

### TESTING VALIDATION

```bash
# Tests pre-requisitos (OBLIGATORIO antes de cambios)
python test_environment/01_pretest_requirements.py

# Tests post-validación (OBLIGATORIO después de cambios)
python test_environment/03_post_validation_tests.py

# Processing seguro documentos
python test_environment/04_safe_processing_script.py

# Ejemplo completo funcionando
python complete_example.py

# Document processing example
python document_processing_example.py
```

### CODE QUALITY VALIDATION

```bash
# Linting con Ruff
ruff check .

# Formatting con Ruff  
ruff format .

# Type checking (donde aplicable)
mypy raganything/

# Verificar imports y dependencias
python -c "
import raganything
from raganything import RAGAnything
from raganything.modalprocessors import ModalProcessor
print('✅ Core imports OK')
"
```

### MODAL PROCESSING VALIDATION

```bash
# Test modal processors
python examples/modalprocessors_example.py

# Test batch processing
python examples/batch_processing_example.py

# Test enhanced markdown
python examples/enhanced_markdown_example.py

# Test Gemini integration
python examples/gemini_example.py

# Test image formats
python examples/image_format_test.py

# Test office documents
python examples/office_document_test.py
```

### MULTIMODAL FUNCTIONALITY VALIDATION

```bash
# Test text processing
python examples/text_format_test.py

# Test RAG-Anything core example
python examples/raganything_example.py

# Test insert content list
python examples/insert_content_list_example.py

# Processing con documentos reales
python mi_primer_procesamiento.py
```

### KNOWLEDGE GRAPH VALIDATION

```bash
# Build knowledge graph from existing data
python test_environment/build_kg_from_existing.py

# Pre-tests knowledge graph
python test_environment/pre_tests_kg_build.py

# Post-tests knowledge graph
python test_environment/post_tests_kg_build.py
```

### DOCLING INTEGRATION VALIDATION

```bash
# Test Docling initialization
python test_environment/docling_init_test.py

# Simple Docling test
python test_environment/simple_docling_test.py

# Full Docling processing
python test_environment/docling_full_processing.py
```

---

## 🔄 PROTOCOLO DE SAFETY COMMITS

### ANTES DE CUALQUIER CAMBIO CRÍTICO

```bash
# Safety commit estándar
git add -A
git commit -m "safety: pre-[action] snapshot"
git push origin $(git branch --show-current)

# Backup RAG storage
cp -r rag_storage/ backup_rag_storage_$(date +%Y%m%d_%H%M%S)/

# Backup test environment logs
cp -r test_environment/logs/ backup_logs_$(date +%Y%m%d_%H%M%S)/

# Backup output data
cp -r data/output/ backup_output_$(date +%Y%m%d_%H%M%S)/
```

### VALIDACIÓN POST-CAMBIOS

```bash
# Verificar que los cambios no rompieron nada
python test_environment/01_pretest_requirements.py && \
python test_environment/03_post_validation_tests.py && \
python complete_example.py && \
echo "✅ All validations passed"
```

---

## 📊 MÉTRICAS DE CALIDAD REQUERIDAS

### OBJETIVOS MÍNIMOS
- **Tests passing:** 100% en test_environment/
- **Linting:** Sin errores ruff
- **Processing time:** <30s para documentos estándar
- **Modal coverage:** Text, images, tables funcionando
- **Knowledge graph:** Construction successful
- **API availability:** Verificación providers

### CRITERIOS DE ACEPTACIÓN
```bash
# Verificar métricas de calidad
python -c "
import json
import time
start = time.time()

# Test core functionality
from raganything import RAGAnything
rag = RAGAnything(config={'working_dir': './test'})

processing_time = time.time() - start
print(f'Processing time: {processing_time:.2f}s')
print('✅ Quality metrics OK' if processing_time < 30 else '❌ Performance issue')
"
```

---

## 🚨 CONDICIONES DE STOP INMEDIATO

### ERRORES CRÍTICOS QUE REQUIEREN PARADA
```bash
# Si alguno de estos comandos falla, STOP inmediato:

# 1. Dependencias básicas
python -c "import raganything, docling, openai"

# 2. Environment setup
python test_environment/01_pretest_requirements.py

# 3. Basic functionality
python -c "from raganything import RAGAnything; rag = RAGAnything()"

# 4. Test environment
python test_environment/03_post_validation_tests.py
```

### API Y CONFIGURACIÓN
```bash
# Verificar API keys (si configuradas)
python -c "
import os
print('✅ OPENAI_API_KEY configured' if os.getenv('OPENAI_API_KEY') else '⚠️  OPENAI_API_KEY not set')
print('✅ GOOGLE_API_KEY configured' if os.getenv('GOOGLE_API_KEY') else '⚠️  GOOGLE_API_KEY not set')
"

# Verificar archivos críticos existen
ls -la CLAUDE.md DEVELOPMENT_METHODOLOGY.md CHECKPOINTS.md
```

---

## 🔧 RECOVERY Y ROLLBACK

### ROLLBACK PROCEDURES

```bash
# Level 1: Configuration rollback
git checkout HEAD~1 -- raganything/
git checkout HEAD~1 -- requirements.txt

# Level 2: Full commit rollback
git reset --hard HEAD~1
git push origin feature/branch-name --force

# Level 3: Storage rollback
rm -rf rag_storage/
cp -r backup_rag_storage_YYYYMMDD_HHMMSS/ rag_storage/

# Level 4: Complete environment reset
git checkout main
git pull origin main
pip install -r requirements.txt
python test_environment/01_pretest_requirements.py
```

### VALIDATION DESPUÉS DE ROLLBACK

```bash
# Verificar que rollback fue exitoso
python test_environment/01_pretest_requirements.py && \
python complete_example.py && \
echo "✅ Rollback successful, system functional"
```

---

## 🎯 COMANDOS ESPECÍFICOS MODALIDADES

### TEXT PROCESSING

```bash
# Validar procesamiento de texto
python examples/text_format_test.py

# Test enhanced markdown
python examples/enhanced_markdown_example.py
```

### IMAGE PROCESSING

```bash
# Test image formats
python examples/image_format_test.py

# Modal processors
python examples/modalprocessors_example.py
```

### OFFICE DOCUMENTS

```bash
# Test office document processing
python examples/office_document_test.py
```

### BATCH PROCESSING

```bash
# Batch processing validation
python examples/batch_processing_example.py
```

---

## 📈 MONITORING Y LOGGING

### LOG ANALYSIS

```bash
# Check recent processing logs
ls -la test_environment/logs/

# Analyze latest log
tail -f test_environment/logs/processing_*.log

# Check post validation reports
cat test_environment/logs/post_validation_report.json
```

### STORAGE ANALYSIS

```bash
# Check RAG storage status
ls -la rag_storage/

# Analyze storage contents
python -c "
import os
import json
if os.path.exists('rag_storage/kv_store_parse_cache.json'):
    with open('rag_storage/kv_store_parse_cache.json', 'r') as f:
        data = json.load(f)
        print(f'Storage entries: {len(data)}')
else:
    print('Storage not initialized')
"
```

---

## 🏆 SUCCESS CRITERIA

### DEPLOYMENT READY CHECKLIST

```bash
# Full validation pipeline (must pass 100%)
python test_environment/01_pretest_requirements.py && \
python test_environment/03_post_validation_tests.py && \
python complete_example.py && \
python document_processing_example.py && \
ruff check . && \
echo "✅ DEPLOYMENT READY"
```

### FEATURE COMPLETE VALIDATION

```bash
# Comprehensive feature validation
python examples/raganything_example.py && \
python examples/modalprocessors_example.py && \
python examples/batch_processing_example.py && \
python examples/enhanced_markdown_example.py && \
echo "✅ ALL FEATURES VALIDATED"
```

---

*Comandos de validación para desarrollo seguro y sistemático - Proyecto RAG-Anything*
*Última actualización: 2025-08-29*
*Versión: 1.0-RAG-Anything*