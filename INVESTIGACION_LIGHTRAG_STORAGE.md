# 🔍 INVESTIGACIÓN: LIGHTRAG STORAGE Y KNOWLEDGE GRAPH

**Fecha:** 29 de Agosto, 2025  
**Objetivo:** Entender arquitectura de almacenamiento de LightRAG para construcción correcta del KG

---

## 📊 RESULTADOS DE INVESTIGACIÓN

### ✅ TESTS PRE - PREREQUISITOS VALIDADOS
- **content.json**: 281.1 KB ✓
- **metadata.json**: 0.7 KB ✓
- **RAGAnything**: Importable ✓
- **Conclusión**: Todos los prerequisitos OK para proceder

### 🏗️ ARQUITECTURA DE ALMACENAMIENTO LIGHTRAG

**Versión detectada:** LightRAG 1.4.6

#### Tipos de Storage por Defecto:
- **KV Storage**: `JsonKVStorage` → Archivos JSON para metadatos
- **Vector Storage**: `NanoVectorDBStorage` → Base de datos vectorial ligera (archivos .db)
- **Graph Storage**: `NetworkXStorage` → Grafo en memoria serializado (.pkl)
- **Doc Status Storage**: `JsonDocStatusStorage` → Estado de documentos (doc_status.json)

#### Almacenamientos Alternativos Disponibles:
```
Neo4JStorage, MilvusVectorDBStorage, MongoKVStorage, MongoGraphStorage, 
RedisKVStorage, ChromaVectorDBStorage, PGKVStorage, PGVectorStorage, 
FaissVectorDBStorage, QdrantVectorDBStorage, MemgraphStorage
```

### 📁 ESTRUCTURA DE ARCHIVOS ESPERADA

**Directorio base:** `C:\Users\Gamer\Dev\RAG-Anything\test_environment\rag_storage\`

**Archivos que se crearán:**
```
rag_storage/
├── *.json          → Metadatos y configuración (JsonKVStorage)
├── *.db            → Base de datos vectorial (NanoVectorDB)  
├── *.pkl           → Grafo NetworkX serializado
├── doc_status.json → Estado de procesamiento de documentos
└── workspace/      → Archivos de trabajo temporales
```

### 🔧 CONFIGURACIÓN IDENTIFICADA

```python
# Configuración por defecto en RAGAnything
RAGAnythingConfig(
    working_dir="test_environment/rag_storage",  # Directorio principal
    parser="docling",                            # Parser a usar
    skip_parsing=True,                           # No reprocesar (usar existente)
    enable_knowledge_graph=True                  # Habilitar KG
)

# LightRAG se inicializa con:
LightRAG(
    working_dir='./rag_storage',
    kv_storage='JsonKVStorage',         # Archivos JSON
    vector_storage='NanoVectorDBStorage', # DB vectorial ligera
    graph_storage='NetworkXStorage',      # Grafo NetworkX
    doc_status_storage='JsonDocStatusStorage'
)
```

### 🎯 MÉTODO DE CONSTRUCCIÓN DEL KG

**Proceso identificado:**
1. **Input**: `content.json` (281.1 KB ya procesado por Docling)
2. **Conversión**: Transformar a formato de documentos RAGAnything
3. **Indexación**: `rag.index_documents()` o `rag.add_documents()`
4. **Storage**: LightRAG almacena automáticamente en los archivos correspondientes
5. **Output**: KG operativo en `rag_storage/`

### 🔍 MÉTODOS DISPONIBLES PARA INDEXAR

Según la investigación del código:
- `rag.index_documents(documents)` - Método preferido
- `rag.add_documents(documents)` - Método alternativo
- Auto-detección de método disponible en runtime

### ⚠️ CONSIDERACIONES TÉCNICAS

**Ventajas del sistema por defecto:**
- ✅ Sin dependencias externas de BD
- ✅ Archivos locales fáciles de debuggear
- ✅ Rápido para desarrollo
- ✅ Portable

**Limitaciones:**
- ⚠️ No escalable para producción masiva
- ⚠️ Grafo en memoria (limitado por RAM)
- ⚠️ No concurrencia multi-usuario

---

## 🎯 PLAN DE EJECUCIÓN CONFIRMADO

**Estrategia:** Usar configuración por defecto de LightRAG para construcción rápida del KG

**Directorio destino confirmado:** `test_environment/rag_storage/`

**Archivos de entrada validados:**
- `test_environment/output/content.json` (281.1 KB) ✓
- `test_environment/output/metadata.json` (0.7 KB) ✓

**Tiempo estimado:** 2-5 minutos

**Criterios de éxito:**
- Archivos de KG creados en `rag_storage/`
- Sistema responde a consultas de prueba
- Tests POST pasan correctamente

---

**Estado:** ✅ INVESTIGACIÓN COMPLETADA - READY TO BUILD

*Investigación realizada el 29 de Agosto, 2025*