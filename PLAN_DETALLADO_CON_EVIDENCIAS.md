# 📋 PLAN DETALLADO CON EVIDENCIAS - DESARROLLO RAG-ANYTHING

**Fecha:** 2025-09-09  
**Metodología:** CLAUDE.md - Investigar PRIMERO, Tests PRE/POST, Safety commits  
**Estado:** Problema confirmado con evidencias, solución identificada

---

## 🔍 INVESTIGACIÓN COMPLETADA

### ✅ **Evidencias del Estado Actual**

1. **Knowledge Graph EXISTE y está completo:**
   ```bash
   $ python -c "import json; f=open('test_environment/rag_storage/kv_store_full_docs.json', 'r', encoding='utf-8'); d=json.load(f); print(f'full_docs: {len(d)} docs'); print(list(d.keys())[:3])"
   full_docs: 1 docs
   ['ordenanza-prestaciones-001']
   ```

2. **Error confirmado en queries:**
   ```bash
   $ cd test_environment && python -c "import asyncio; from build_kg_from_docling import test_basic_query; asyncio.run(test_basic_query())"
   [ERROR] En consulta de prueba: No LightRAG instance available. Please process documents first or provide a pre-initialized LightRAG instance.
   ```

3. **Storage compartido confirmado:**
   ```bash
   $ dir test_environment\rag_storage\*.json
   build_stats.json              kv_store_llm_response_cache.json
   kv_store_doc_status.json      kv_store_text_chunks.json
   kv_store_full_docs.json       vdb_chunks.json
   kv_store_full_entities.json   vdb_entities.json
   kv_store_full_relations.json  vdb_relationships.json
   ```

4. **Tests POST existentes funcionando:**
   ```bash
   $ python test_environment/06_post_test_doc_storage.py
   [OK] POST-TEST EXITOSO - TODOS LOS CRITERIOS CUMPLIDOS
   ```

---

## 🎯 PROBLEMA ESPECÍFICO IDENTIFICADO

### **Análisis del código actual:**

**Líneas 307-321 (Instancia 1 - Ingesta) - ✅ CORRECTO:**
```python
config = RAGAnythingConfig(
    working_dir=str(rag_storage),
    parser="docling",
    enable_image_processing=True,
    enable_table_processing=True,
    enable_equation_processing=True,
    display_content_stats=True
)

rag = RAGAnything(
    config=config,
    llm_model_func=llm_model_func,
    vision_model_func=vision_model_func,  # ✅ INCLUIDO
    embedding_func=embedding_func
)
```

**Líneas 481-486 (Instancia 2 - Consultas) - ❌ PROBLEMÁTICO:**
```python
config = RAGAnythingConfig(working_dir=str(rag_storage))
rag = RAGAnything(
    config=config,
    llm_model_func=llm_model_func,
    # vision_model_func=vision_model_func,  # ❌ FALTA ESTA LÍNEA
    embedding_func=embedding_func
)
```

---

## 📊 TESTS CREADOS

### **Siguiendo metodología CLAUDE.md:**

1. **✅ 11_pre_test_vision_model_query.py**
   - Documenta el problema actual
   - Verifica que KG existe
   - Confirma que error es por vision_model_func faltante

2. **✅ 12_post_test_vision_model_query.py**
   - Validará que el fix funciona
   - Tests de queries básicas y multimodales
   - Criterios de aceptación claros

3. **✅ 13_integration_test_complete_pipeline.py**
   - Test end-to-end completo
   - Arquitectura dual
   - Performance y stress tests

---

## 🚀 PLAN DE EJECUCIÓN DETALLADO

### **FASE 1: EJECUTAR TESTS PRE (5 minutos)**
```bash
# 1. Ejecutar test PRE para documentar problema
cd test_environment
python 11_pre_test_vision_model_query.py

# Resultado esperado: Confirma el error específico
```

### **FASE 2: APLICAR FIX MÍNIMO (2 minutos)**
```bash
# 2. Safety commit
git add -A && git commit -m "safety: pre-fix snapshot con tests PRE/POST"

# 3. Aplicar fix (UNA LÍNEA)
# En test_environment/build_kg_from_docling.py línea 485, agregar:
# vision_model_func=vision_model_func,
```

### **FASE 3: VALIDAR CON TESTS POST (10 minutos)**
```bash
# 4. Ejecutar test POST
python 12_post_test_vision_model_query.py

# 5. Ejecutar test de integración
python 13_integration_test_complete_pipeline.py

# Resultado esperado: Todos los criterios PASS
```

### **FASE 4: COMMIT ATÓMICO (2 minutos)**
```bash
# 6. Commit del fix
git add test_environment/build_kg_from_docling.py
git commit -m "fix: add vision_model_func to query instance for multimodal support

Resolves: 'No LightRAG instance available' error in queries
- Add missing vision_model_func parameter in line 485
- Enables multimodal query capabilities  
- Maintains consistency with ingestion instance
- Validated with comprehensive PRE/POST tests

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## 📋 CRITERIOS DE ACEPTACIÓN

### **PRE-TEST debe mostrar:**
- [ ] Knowledge Graph existe con 1 documento
- [ ] Error "No LightRAG instance available" reproducible
- [ ] Instancia CON vision_model_func funciona
- [ ] Instancia SIN vision_model_func falla

### **POST-TEST debe mostrar:**
- [ ] Query básica funciona sin errores
- [ ] Múltiples queries consecutivas exitosas
- [ ] Pipeline completo operativo
- [ ] Tiempo de respuesta <5s por query

### **INTEGRATION-TEST debe mostrar:**
- [ ] Arquitectura dual funcionando
- [ ] Storage compartido consistente
- [ ] Performance aceptable (>0.5 queries/s)
- [ ] Todos los archivos KG válidos

---

## 🔧 COMANDOS DE EJECUCIÓN

```bash
# COMANDO COMPLETO DE EJECUCIÓN:
cd C:\Users\Gamer\Dev\RAG-Anything

# 1. PRE-TEST
cd test_environment && python 11_pre_test_vision_model_query.py

# 2. SAFETY COMMIT  
git add -A && git commit -m "safety: pre-fix snapshot con tests PRE/POST"

# 3. EDITAR ARCHIVO (una línea)
# test_environment/build_kg_from_docling.py línea 485:
# Agregar: vision_model_func=vision_model_func,

# 4. POST-TEST
python 12_post_test_vision_model_query.py

# 5. INTEGRATION TEST
python 13_integration_test_complete_pipeline.py

# 6. COMMIT FIX
git add test_environment/build_kg_from_docling.py
git commit -m "fix: add vision_model_func to query instance"
```

---

## ⚠️ CONTINGENCIAS

### **Si PRE-TEST falla:**
1. Verificar KG existe: `ls test_environment/rag_storage/`
2. Si no existe, ejecutar: `python build_kg_from_docling.py`
3. Revisar imports en test PRE

### **Si POST-TEST falla después del fix:**
1. Rollback: `git reset --hard HEAD~1`
2. Verificar que la línea se agregó correctamente
3. Revisar logs de error para diagnóstico

### **Si INTEGRATION-TEST falla:**
1. Ejecutar tests individuales para aislar problema
2. Verificar API_KEY y rate limits
3. Revisar memoria disponible

---

## 📊 MÉTRICAS DE ÉXITO

### **Tiempo total estimado:** 20 minutos
### **Archivos modificados:** 1 línea en 1 archivo
### **Tests ejecutados:** 3 suites completas
### **Criterios obligatorios:** 12 checks deben pasar

---

## 🎯 RESUMEN EJECUTIVO

**PROBLEMA:** Instancia de consultas no tiene `vision_model_func`  
**SOLUCIÓN:** Agregar una línea de código  
**VALIDACIÓN:** 3 suites de tests comprehensivos  
**TIEMPO:** 20 minutos total  
**RIESGO:** Mínimo (cambio de 1 línea con rollback disponible)

**RESULTADO ESPERADO:** Pipeline multimodal completamente funcional end-to-end

---

## 🔄 SIGUIENTE PASO

**EJECUTAR PRE-TEST para confirmar el problema actual antes del fix:**
```bash
cd test_environment && python 11_pre_test_vision_model_query.py
```

Una vez confirmado el problema, procederemos con el fix siguiendo la metodología CLAUDE.md estrictamente.