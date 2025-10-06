# 🔍 INVESTIGACIÓN: ERROR "No LightRAG instance available"

**Fecha:** 2025-10-06
**Metodología:** RPVEA-A Lightweight (Tier 2)
**Estado:** ROOT CAUSE IDENTIFICADO

---

## 📋 RESUMEN EJECUTIVO

**Problema:** Queries fallan con error `"No LightRAG instance available. Please process documents first or provide a pre-initialized LightRAG instance."` incluso cuando:
- Knowledge Graph existe completamente (7 archivos verificados)
- `vision_model_func` está presente en el código
- Instancia RAGAnything fue creada correctamente

**Root Cause:** `aquery()` no inicializa automáticamente `self.lightrag` desde storage existente, a diferencia de `insert_content_list()`.

**Solución:** Agregar `await self._ensure_lightrag_initialized()` en `query.py:aquery()` antes del check de `self.lightrag is None`.

---

## 🔬 FASE R: REVIEW - HALLAZGOS DETALLADOS

### **1. Evidencias del Problema** (PRE-TEST Execution)

```bash
$ python test_environment/11_pre_test_vision_model_query.py

VERIFICACIÓN: KNOWLEDGE GRAPH EXISTENTE
[OK] Directorio existe: test_environment\rag_storage
  [OK] kv_store_full_docs.json: 40.9 KB
  [OK] kv_store_doc_status.json: 1.3 KB
  [OK] kv_store_full_entities.json: 2.8 KB
  [OK] kv_store_full_relations.json: 7.3 KB
  [OK] vdb_entities.json: 1218.8 KB
  [OK] vdb_relationships.json: 1272.3 KB
  [OK] graph_chunk_entity_relation.graphml: 77.7 KB

[INFO] Documentos en full_docs: 1
  - ordenanza-prestaciones-001: 40274 caracteres

TEST: QUERY SIN vision_model_func
[EXPECTED ERROR] No LightRAG instance available...

TEST: QUERY CON vision_model_func
[ERROR] Con vision_model_func: No LightRAG instance available...
```

**Hallazgo Crítico:** AMBAS instancias (con y sin `vision_model_func`) fallan → El problema NO es `vision_model_func` faltante.

---

### **2. Análisis de Código Fuente**

#### **A. Flujo de Inicialización (`raganything/raganything.py`)**

**Línea 53:** `self.lightrag` se declara como `Optional[LightRAG] = field(default=None)`

**Líneas 94-127:** `__post_init__()` solo configura config, logger, parser - **NO inicializa lightrag**

**Líneas 228-315:** `async def initialize_storages()` - Método que inicializa `self.lightrag`:

```python
async def initialize_storages(self):
    # Si lightrag ya está provisto...
    if self.lightrag is not None:
        await self.lightrag.initialize_storages()
        return

    # Si no, crear nueva instancia LightRAG
    lightrag_params = {
        "working_dir": self.working_dir,
        "llm_model_func": self.llm_model_func,
        "embedding_func": self.embedding_func,
    }

    self.lightrag = LightRAG(**lightrag_params)  # LÍNEA 298
    await self.lightrag.initialize_storages()
```

**CLAVE:** `initialize_storages()` debe ser llamado explícitamente para cargar instancia existente desde storage.

---

#### **B. Método `insert_content_list()` (processor.py)**

**Línea 1395:** ✅ **CORRECTO**

```python
async def insert_content_list(self, content_list, ...):
    await self._ensure_lightrag_initialized()  # ← INICIALIZA AUTOMÁTICAMENTE

    # ... resto del código
```

**Comportamiento:**
1. Usuario llama `await rag.insert_content_list(...)`
2. Internamente llama `_ensure_lightrag_initialized()`
3. Esto llama `initialize_storages()` si `self.lightrag is None`
4. LightRAG se carga desde storage existente o se crea nuevo
5. Inserción procede exitosamente

---

#### **C. Método `aquery()` (query.py)** ❌ **PROBLEMÁTICO**

**Líneas 115-118:** ❌ **FALLA INMEDIATA**

```python
async def aquery(self, query: str, mode: str = "mix", **kwargs) -> str:
    if self.lightrag is None:  # ← SOLO VERIFICA, NO INICIALIZA
        raise ValueError(
            "No LightRAG instance available..."
        )
    # ... resto del código
```

**Comportamiento:**
1. Usuario llama `await rag.aquery("query")`
2. `self.lightrag` es `None` (porque nunca se llamó `initialize_storages()`)
3. ❌ **FALLA INMEDIATAMENTE** con ValueError
4. **NUNCA** intenta cargar desde storage existente

---

### **3. Comparación de Flujos**

#### **INGESTA (Funciona) ✅**

```python
# test_environment/build_kg_from_docling.py línea 316-343

rag = RAGAnything(config=config, llm_model_func=..., embedding_func=...)
# self.lightrag es None aquí

await rag.insert_content_list(...)
    # ↓ Llama internamente
    await self._ensure_lightrag_initialized()
        # ↓ Llama internamente
        await self.initialize_storages()
            # ↓ Crea o carga LightRAG
            self.lightrag = LightRAG(...)
            await self.lightrag.initialize_storages()  # ← CARGA DESDE STORAGE

# ✅ ÉXITO: self.lightrag ya NO es None
```

---

#### **QUERY (Falla) ❌**

```python
# test_environment/build_kg_from_docling.py línea 508-520

rag = RAGAnything(config=config, llm_model_func=..., embedding_func=...)
# self.lightrag es None aquí

await rag.aquery("query")
    # ↓ Verifica inmediatamente
    if self.lightrag is None:  # ← TRUE!
        raise ValueError("No LightRAG instance available...")

# ❌ FALLA: Nunca intentó cargar desde storage
```

---

### **4. ¿Por qué el storage existe pero no se carga?**

**Respuesta:** `LightRAG.initialize_storages()` (de LightRAG core) automáticamente:
- Crea nuevos storages si no existen
- Carga storages existentes si existen

**PERO** solo si se llama. RAGAnything nunca llama `initialize_storages()` en el flujo de query.

---

## 📊 FASE P: PREPARE - ESTRATEGIA DE SOLUCIÓN

### **Solución Propuesta: Agregar `_ensure_lightrag_initialized()` en `aquery()`**

**Cambio mínimo y seguro:**

```python
# raganything/query.py - ANTES (líneas 115-118)
async def aquery(self, query: str, mode: str = "mix", **kwargs) -> str:
    if self.lightrag is None:
        raise ValueError(...)

    # ... resto
```

```python
# raganything/query.py - DESPUÉS (propuesto)
async def aquery(self, query: str, mode: str = "mix", **kwargs) -> str:
    await self._ensure_lightrag_initialized()  # ← AGREGAR ESTA LÍNEA

    # El check de None ya no es necesario porque _ensure_lightrag_initialized()
    # garantiza que self.lightrag no será None después de ejecutarse

    # ... resto
```

**Justificación:**
1. ✅ **Consistente** con `insert_content_list()` y otros métodos
2. ✅ **Mínimo cambio** - 1 línea agregada
3. ✅ **Backward compatible** - No rompe código existente
4. ✅ **Lazy initialization** - Solo inicializa cuando es necesario
5. ✅ **Carga automática** - Si storage existe, lo carga; si no, crea nuevo

---

### **Métodos que también deberían verificarse:**

Todos los métodos públicos de `QueryMixin` que usan `self.lightrag`:

```bash
$ grep -n "async def.*query" raganything/query.py

100:    async def aquery(self, query: str, mode: str = "mix", **kwargs) -> str:
151:    async def aquery_vlm_enhanced(
```

**Ambos necesitan el fix.**

---

### **Alternativa Descartada: Llamar `initialize_storages()` en `__post_init__`**

**Razón para descartar:**
- `__post_init__` es síncrono
- `initialize_storages()` es `async`
- No se puede llamar `await` desde método síncrono
- Requeriría refactoring mayor

**Lazy initialization es el patrón correcto.**

---

## ✅ TESTING STRATEGY

### **PRE-Tests (Ya Ejecutados)**

- ✅ `test_environment/11_pre_test_vision_model_query.py`
  - Confirma Knowledge Graph existe
  - Confirma error actual en queries

### **POST-Tests (Preparados)**

- ⏳ `test_environment/12_post_test_vision_model_query.py`
  - Verificará que queries funcionan después del fix
  - Validará múltiples queries consecutivas
  - Confirmará tiempo de respuesta < 5s

- ⏳ `test_environment/13_integration_test_complete_pipeline.py`
  - Pipeline end-to-end completo
  - Arquitectura dual (ingesta + query)
  - Performance y stress tests

---

## 📝 CRITERIOS DE ACEPTACIÓN (POST-FIX)

### **Must-Have (Críticos):**
- [ ] Query básica funciona sin errores
- [ ] Múltiples queries consecutivas exitosas
- [ ] Storage existente se carga correctamente
- [ ] No regression en insert_content_list()

### **Should-Have (Importantes):**
- [ ] Tiempo de respuesta < 5s por query
- [ ] Queries VLM-enhanced funcionan
- [ ] Todos los tests PRE/POST/Integration pasan

---

## 🎯 SIGUIENTE PASO

**FASE V: VALIDATE** - Presentar hallazgos y obtener aprobación para:

1. **Modificar:** `raganything/query.py`
   - Agregar `await self._ensure_lightrag_initialized()` en línea 115 (antes del check)
   - Agregar `await self._ensure_lightrag_initialized()` en `aquery_vlm_enhanced()` si necesario

2. **Ejecutar:** POST-tests para validar fix

3. **Commit:** Fix atómico con evidencias PRE/POST

---

## 📊 IMPACTO ESTIMADO

**Archivos modificados:** 1 (`raganything/query.py`)
**Líneas modificadas:** 2-3 (agregar llamadas a `_ensure_lightrag_initialized`)
**Riesgo:** Mínimo (patrón ya usado en processor.py)
**Tiempo estimado:** 5 minutos (cambio) + 10 minutos (testing) = 15 minutos total
**Beneficio:** Queries funcionarán con storage existente (problema resuelto)

---

## 🔄 METODOLOGÍA APLICADA

Este análisis siguió **RPVEA-A Lightweight (Tier 2)**:

- **R (Review):** ✅ Completado (este documento)
  - Analizado `query.py:116` (error source)
  - Entendido flujo de inicialización LightRAG
  - Comparado ingesta vs query

- **P (Prepare):** 🔄 En progreso
  - ✅ Root cause identificado
  - ✅ Solución propuesta
  - ✅ Tests PRE/POST preparados
  - ⏳ Esperando aprobación

- **V (Validate):** ⏳ Pendiente aprobación usuario

- **E (Execute):** ⏳ Pendiente

- **A (Assess):** ⏳ Pendiente

---

**Documentado por:** Claude Code (RPVEA-A methodology)
**Fecha:** 2025-10-06
**Próxima acción:** FASE V - Solicitar aprobación para aplicar fix
