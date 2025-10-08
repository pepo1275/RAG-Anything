# ⚠️ INSTRUCCIONES OBLIGATORIAS PARA CLAUDE CODE - RAG-ANYTHING PROJECT

## 🚨 LECTURA OBLIGATORIA EN CADA SESIÓN
Este archivo contiene las reglas críticas que DEBES seguir siempre al trabajar con el proyecto RAG-Anything.

---

## ⛔ REGLAS INQUEBRANTABLES

### 1. PRINCIPIO FUNDAMENTAL
**NUNCA pasar del plan a la acción sin aprobación explícita del usuario**

### 2. MEJORES PRÁCTICAS OBLIGATORIAS (POR DEFECTO)
- ✅ **Investigar PRIMERO**: SIEMPRE revisar código existente ANTES de crear nuevo
- ✅ **Reutilizar**: PREFERIR reutilización sobre reinvención de código
- ✅ **Usar herramientas existentes**: Procesadores de modalidad, parsers, utilidades ya desarrolladas
- ✅ **Tests sistemáticos**: PRE/POST tests para definir criterios de aceptación
- ✅ **Verificación obligatoria**: NO asumir problemas sin verificar con tests/usuario
- ✅ **Safety commits** ANTES de cualquier cambio crítico
- ✅ **TodoWrite** para TODA tarea con >3 pasos
- ✅ **Git**: Commits atómicos cada componente funcional
- ✅ **Testing**: Ejecutar tests ANTES y DESPUÉS de cambios
- ✅ **Backup**: De configuraciones y datos críticos
- ✅ **Un solo task**: Solo UNA tarea en in_progress a la vez
- ✅ **UTF-8 encoding**: SIEMPRE usar `export PYTHONIOENCODING=utf-8` antes de ejecutar scripts Python con emojis/caracteres especiales en Windows

### 3. CHECKPOINTS OBLIGATORIOS - DETENER Y ESPERAR APROBACIÓN
- [ ] **FASE 0**: Setup inicial → **🛑 STOP**
- [ ] **FASE 1**: Análisis completado → **🛑 STOP**
- [ ] **FASE 2**: Plan detallado → **🛑 STOP**
- [ ] **FASE 3**: Diseño técnico → **🛑 STOP**
- [ ] **FASE 4**: Backup realizado → **🛑 STOP**
- [ ] **FASE 6**: PR listo → **🛑 STOP**
- [ ] **FASE 7**: Pre-release → **🛑 STOP**

### 4. ANTES DE CUALQUIER CAMBIO
```bash
# SIEMPRE ejecutar safety commit
git add -A
git commit -m "safety: pre-[action] snapshot"
git push origin $(git branch --show-current)
```

### 5. CONDICIONES DE PARADA INMEDIATA
1. **Errores de API**: 401, 403, rate limits
2. **Tests fallando**: Cualquier test existente roto
3. **Import errors**: Dependencias faltantes
4. **Sin aprobación**: Usuario no ha confirmado proceder
5. **Regression detectada**: Funcionalidad existente afectada

---

## 🛠️ COMANDOS DE VALIDACIÓN

```bash
# ⚠️ IMPORTANTE: En Windows, SIEMPRE usar UTF-8 encoding para evitar errores con emojis/caracteres especiales
export PYTHONIOENCODING=utf-8

# Verificar cumplimiento de metodología
python project_status.py

# Validar antes de cambios
python test_environment/01_pretest_requirements.py

# Verificar tests
export PYTHONIOENCODING=utf-8 && python test_environment/03_post_validation_tests.py

# Verificar calidad de código
ruff check .
mypy raganything/
```

---

## 📊 METODOLOGÍA: RPVEA-A LIGHTWEIGHT

Este proyecto sigue la metodología **RPVEA-A Lightweight** - un enfoque de desarrollo estructurado, testing-first, y orientado a calidad.

### **Fases RPVEA:**
- **R**EVIEW: Analizar requisitos y estado actual
- **P**REPARE: Generar estrategia de testing (PRE/POST/Integration tests)
- **V**ALIDATE: Ejecutar PRE-tests, obtener aprobación del usuario
- **E**XECUTE: Implementar con confianza (baseline establecido)
- **A**SSESS: Ejecutar POST-tests, analizar resultados

### **Principios Clave:**
1. **PRE-tests DEBEN pasar** antes de cualquier cambio de código (establecer baseline)
2. **POST-tests definen el éxito** (criterios de aceptación claros)
3. **VALIDATE nunca se delega** (aprobación del usuario a través del orquestador)
4. **Usar Task tool** para delegar a agentes especializados cuando sea necesario

### **Clasificación por Tiers:**

**Tier 1: Cambios Rápidos (< 30 min)**
- Ejemplos: Typos, ajustes de config, updates de docs
- Proceso: RPVEA rápido (Claude solo)
- Testing: Mental check, sin tests formales
- Agentes: ❌ Ninguno (overhead > beneficio)

**Tier 2: Cambios Estándar (30 min - 4 horas)**
- Ejemplos: Nuevas funciones, actualizaciones de componentes, ejecución de benchmarks
- Proceso: RPVEA Lite + tests
- Testing: PRE/POST tests OBLIGATORIOS
- Agentes: ✅ Task tool para análisis cuando sea necesario
- TodoWrite: OBLIGATORIO

**Tier 3: Cambios Mayores (> 4 horas o arquitectónicos)**
- Ejemplos: Nueva integración de modelos, refactoring arquitectónico, nuevos módulos
- Proceso: RPVEA completo
- Testing: PRE/POST/Integration tests OBLIGATORIOS
- Agentes: ✅ Task tool para análisis comprehensivo
- TodoWrite: OBLIGATORIO
- Documentación: OBLIGATORIA

**Documentación completa:** Ver `docs/workflows/rpvea-methodology-evaluation.md`

---

# CLAUDE.md - PROYECTO RAG-ANYTHING

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

RAG-Anything is a comprehensive All-in-One Multimodal Document Processing RAG system built on LightRAG. It provides seamless processing and querying across all content modalities (text, images, tables, equations, charts) within a single integrated framework.

Key features:
- End-to-End Multimodal Pipeline for document processing
- Universal Document Support (PDFs, Office documents, images, diverse formats)
- Specialized Content Analysis with dedicated processors
- Multimodal Knowledge Graph with entity extraction
- Adaptive Processing Modes (MinerU-based or direct content injection)
- Hybrid Intelligent Retrieval across textual and multimodal content

## Development Commands

### Main Development Commands (run from project root)

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
python test_environment/01_pretest_requirements.py
python test_environment/03_post_validation_tests.py

# Run main examples
python complete_example.py
python document_processing_example.py

# Format code
ruff check . --fix
ruff format .

# Type checking
mypy raganything/

# Check project status
python project_status.py
```

### Testing Commands

```bash
# Run pre-test requirements check
python test_environment/01_pretest_requirements.py

# Run post-validation tests
python test_environment/03_post_validation_tests.py

# Run safe processing script
python test_environment/04_safe_processing_script.py

# Test batch processing
python examples/batch_processing_example.py

# Test enhanced markdown
python examples/enhanced_markdown_example.py
```

## Code Architecture

### Core Library (`raganything/`)

- **Main Entry Point**: `raganything.py` - Contains the main `RAGAnything` class
- **Parser Module**: `parser.py` - Document parsing functionality
- **Processor Module**: `processor.py` - Document processing pipeline
- **Modal Processors**: `modalprocessors.py` - Specialized content processors
- **Query Module**: `query.py` - Query handling and retrieval
- **Batch Processing**: `batch.py`, `batch_parser.py` - Batch document processing
- **Enhanced Markdown**: `enhanced_markdown.py` - Advanced markdown processing
- **Configuration**: `config.py` - System configuration
- **Utilities**: `utils.py` - Helper functions

### Test Environment (`test_environment/`)

- **Pre-Test Requirements**: `01_pretest_requirements.py` - Validates environment setup
- **Acceptance Criteria**: `02_acceptance_criteria.md` - Test acceptance criteria
- **Post-Validation Tests**: `03_post_validation_tests.py` - Comprehensive test suite
- **Safe Processing**: `04_safe_processing_script.py` - Safe document processing

### Examples (`examples/`)

- **Batch Processing**: Example batch document processing
- **Enhanced Markdown**: Advanced markdown features
- **Gemini Integration**: Google Gemini LLM integration
- **Modal Processors**: Content processor examples
- **Office Documents**: Office document processing

## Configuration

### Environment Variables

Create a `.env` file from `env.example`:
- `OPENAI_API_KEY` - Required for OpenAI LLM and embeddings
- `GOOGLE_API_KEY` - Optional for Gemini integration
- Other provider-specific keys as needed

### Storage Setup

- **Documents**: Place input documents in `data/documents/`
- **Output**: Processed output goes to `data/output/` or `output/`
- **RAG Storage**: Vector storage in `rag_storage/`

## Development Guidelines

### Code Style

- Use Ruff for formatting and linting
- Line length: 120 characters
- Type hints are encouraged
- Follow PEP 8 conventions

### Testing Requirements

- Run pre-test requirements before changes
- Execute post-validation tests after changes
- Maintain test coverage for new features
- Document test cases in acceptance criteria

### Multimodal Processing Support

The system supports multiple processing modes:
1. **Auto Mode**: Automatic detection and processing
2. **Force Mode**: Force specific processing pipeline
3. **Vision Mode**: Enhanced visual content processing
4. **VLM Query**: Vision-Language Model enhanced queries

### Safety Protocols

Always create safety commits before:
- Modifying core processing pipelines
- Changing modal processors
- Updating configuration
- Installing new dependencies
- Modifying RAG storage structure

### Rollback Procedure

If anything fails:
```bash
git reset --hard HEAD~1  # Return to previous commit
git checkout -- .  # Discard all changes
```

## Critical Components

### Document Processing Pipeline

1. **Input**: Documents in various formats
2. **Parsing**: MinerU or direct content parsing
3. **Processing**: Modal processors for different content types
4. **Storage**: Vector embeddings in RAG storage
5. **Query**: Multimodal retrieval and response

### Modal Processors

- Image processor for visual content
- Table processor for structured data
- Equation processor for mathematical content
- Text processor for textual content

### Knowledge Graph Integration

- Entity extraction from multimodal content
- Relationship discovery across modalities
- Graph-based retrieval enhancement

## Best Practices

### When Adding New Features

1. Review existing code first
2. Check for reusable components
3. Write tests before implementation
4. Update documentation
5. Create atomic commits
6. Run validation tests

### When Fixing Bugs

1. Reproduce the issue with a test
2. Fix the bug
3. Verify fix with test
4. Check for regressions
5. Document the fix

### When Optimizing Performance

1. Profile current performance
2. Identify bottlenecks
3. Implement optimization
4. Measure improvement
5. Document changes

## Common Issues and Solutions

### Import Errors

Check dependencies:
```bash
pip install -r requirements.txt
```

### Processing Failures

Verify input documents are in supported formats and check logs in `test_environment/logs/`

### API Rate Limits

Implement retry logic with exponential backoff for API calls

### Memory Issues

Use batch processing for large document sets

## Next Steps

1. Enhance multimodal processing capabilities
2. Improve knowledge graph construction
3. Optimize query performance
4. Extend support for additional document formats
5. Implement advanced caching strategies