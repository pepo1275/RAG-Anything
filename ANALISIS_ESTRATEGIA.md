# 📊 ANÁLISIS Y ESTRATEGIA DE SOLUCIÓN

## 🔍 PROBLEMAS IDENTIFICADOS EN build_kg_from_docling.py

### 1. **Arquitectura Innecesariamente Compleja**
- Dos funciones separadas: `build_knowledge_graph_from_docling()` y `test_basic_query()`
- Duplicación de código de configuración
- Paths relativos problemáticos
- Funciones definidas en diferentes scopes

### 2. **Problema Principal: Scope de Variables**
```python
# En build_knowledge_graph_from_docling() - línea 265
def vision_model_func(...):  # Definida aquí

# En test_basic_query() - línea 485
vision_model_func=vision_model_func,  # ERROR: No está en scope
```

### 3. **Inconsistencias con Ejemplos Oficiales**
- `insert_content_list_example.py` tiene estructura más limpia
- Una sola función main() que hace todo
- Definiciones de funciones en el scope correcto
- Patrón oficial: inicializar UNA VEZ, usar para todo

## 🎯 ESTRATEGIA PROPUESTA

### **OPCIÓN A: Modificar Ejemplo Oficial** ⭐ **RECOMENDADA**
**Usar `examples/insert_content_list_example.py` como base**

**Ventajas:**
- ✅ Estructura oficial y probada
- ✅ Scope correcto de todas las variables
- ✅ Una sola instancia RAGAnything para todo
- ✅ Menos código, más mantenible
- ✅ Ya incluye `vision_model_func` correctamente

**Modificaciones necesarias:**
1. Cambiar `create_sample_content_list()` para cargar desde `content.json`
2. Agregar `force_reprocess=True` si necesario
3. Usar doc_id específico: "ordenanza-prestaciones-001"

### **OPCIÓN B: Arreglar build_kg_from_docling.py**
**Mantener archivo actual pero reestructurar**

**Desventajas:**
- ❌ Más trabajo de refactoring
- ❌ Mantiene arquitectura compleja
- ❌ Puede introducir nuevos bugs

## 🚀 IMPLEMENTACIÓN RECOMENDADA

### **PASO 1: Crear archivo basado en ejemplo oficial**
```python
# test_environment/build_kg_unified.py
# Basado en insert_content_list_example.py

async def main():
    # 1. Configurar logging y paths
    # 2. Cargar content.json (en lugar de sample)
    # 3. Configurar RAGAnything UNA VEZ
    # 4. Ejecutar insert_content_list() con force_reprocess
    # 5. Ejecutar queries de validación
    # 6. Todo en un solo flujo
```

### **PASO 2: Funciones en scope correcto**
```python
def llm_model_func(...):  # Definida ANTES de usar
def vision_model_func(...):  # Definida ANTES de usar  
embedding_func = EmbeddingFunc(...)  # Definida ANTES de usar

# Una sola instancia para todo
rag = RAGAnything(
    config=config,
    llm_model_func=llm_model_func,
    vision_model_func=vision_model_func,  # ✅ En scope
    embedding_func=embedding_func
)

# Usar la MISMA instancia para ingesta y queries
await rag.insert_content_list(...)  # Ingesta
result = await rag.aquery(...)      # Query
```

### **PASO 3: Loader personalizado**
```python
def load_content_from_docling():
    """Cargar content.json en formato de content_list"""
    content_file = Path("test_environment/output/content.json")
    with open(content_file, 'r', encoding='utf-8') as f:
        content_data = json.load(f)
    
    # Convertir a formato content_list si es necesario
    return content_data
```

## 📋 PLAN DE EJECUCIÓN

### **INMEDIATO (10 minutos):**
1. Copiar `examples/insert_content_list_example.py` → `test_environment/build_kg_unified.py`
2. Modificar función de carga de contenido
3. Cambiar doc_id y paths
4. Agregar `force_reprocess=True`

### **VALIDACIÓN (5 minutos):**
1. Ejecutar script unificado
2. Confirmar que ingesta + queries funcionan
3. Validar que no hay errores de scope

### **LIMPIEZA (5 minutos):**
1. Backup del archivo problemático
2. Reemplazar con versión funcional
3. Commit atómico del fix

## 🔧 CÓDIGO ESPECÍFICO

### **Diferencia clave en scope:**
```python
# ❌ PROBLEMÁTICO (build_kg_from_docling.py)
async def build_knowledge_graph_from_docling():
    def vision_model_func(...): pass  # Definida aquí
    # ... resto de la función

async def test_basic_query():
    # vision_model_func NO está disponible aquí ❌
    rag = RAGAnything(..., vision_model_func=vision_model_func)

# ✅ CORRECTO (insert_content_list_example.py)  
async def main():
    def vision_model_func(...): pass  # Definida en main
    def llm_model_func(...): pass     # Definida en main
    
    # Ambas funciones disponibles para todo ✅
    rag = RAGAnything(..., vision_model_func=vision_model_func)
    
    await rag.insert_content_list(...)  # Funciona
    result = await rag.aquery(...)      # Funciona
```

## ✅ VENTAJAS DE LA ESTRATEGIA

1. **Solución Rápida**: 20 minutos vs horas de debugging
2. **Código Oficial**: Base probada y mantenida
3. **Menos Bugs**: Evita problemas de scope y duplicación
4. **Más Mantenible**: Estructura más simple
5. **Extensible**: Fácil agregar más funcionalidades

## 🎯 PRÓXIMO PASO

**Implementar OPCIÓN A**: Crear `build_kg_unified.py` basado en ejemplo oficial.