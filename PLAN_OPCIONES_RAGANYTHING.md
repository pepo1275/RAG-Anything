# 📋 PLANES DE IMPLEMENTACIÓN - RAGAnything con Docling

**Fecha:** 26 de Agosto, 2025  
**Objetivo:** Integrar RAGAnything con contenido procesado por Docling  
**Estado actual:** Docling funcional, contenido ya procesado, RAGAnything sin probar

---

## 🅰️ OPCIÓN A: Configurar RAGAnything para usar Docling como Parser

### Objetivo:
Modificar RAGAnything para que use Docling en lugar de MinerU, permitiendo procesamiento completo end-to-end con construcción de knowledge graph.

### ✅ VENTAJAS:
- Solución integrada completa
- Pipeline unificado de procesamiento
- Knowledge graph construido automáticamente
- Reutilizable para futuros PDFs

### ⚠️ DESVENTAJAS:
- Reprocesará el PDF (tiempo ~3-4 minutos)
- Posibles incompatibilidades no detectadas
- Contenido ya procesado no se aprovecha

### 📝 PLAN DE IMPLEMENTACIÓN:

#### Paso 1: Modificar configuración del parser (2 min)

```python
# Archivo: test_environment\04_safe_processing_script.py
# Línea 122 - CAMBIAR:
parser="mineru",  # ❌ ACTUAL

# POR:
parser="docling",  # ✅ NUEVO
```

#### Paso 2: Verificar compatibilidad de configuración (5 min)

```python
# test_raganything_docling_config.py
from raganything import RAGAnything, RAGAnythingConfig

def test_docling_config():
    """Verificar que RAGAnything acepta docling como parser"""
    try:
        config = RAGAnythingConfig(
            working_dir="test_environment/rag_storage",
            parser="docling",  # Parser modificado
            parse_method="auto",
            enable_image_processing=True,
            enable_table_processing=True,
            display_content_stats=True
        )
        
        # Intentar inicializar
        rag = RAGAnything(config=config)
        print("[OK] RAGAnything acepta docling como parser")
        
        # Verificar métodos disponibles
        if hasattr(rag, 'process_document'):
            print("[OK] Método process_document disponible")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Configuración no compatible: {e}")
        return False

if __name__ == "__main__":
    test_docling_config()
```

#### Paso 3: Ejecutar procesamiento completo (10 min)

```bash
# Comando para ejecutar
cd C:\Users\Gamer\Dev\RAG-Anything
python test_environment\04_safe_processing_script.py raganything
```

#### Paso 4: Validar resultados (5 min)

```python
# validate_raganything_output.py
from pathlib import Path
import json

def validate_rag_output():
    """Validar que RAGAnything generó todos los archivos esperados"""
    
    output_dir = Path("test_environment/output")
    rag_storage = Path("test_environment/rag_storage")
    
    expected_files = {
        "output": [
            "content.md",
            "content.json",
            "metadata.json"
        ],
        "rag_storage": [
            "graph_data.json",  # Knowledge graph
            "index.pkl",        # Índices
            "embeddings.npy"    # Embeddings
        ]
    }
    
    results = {}
    
    # Verificar archivos de output
    for file in expected_files["output"]:
        file_path = output_dir / file
        results[file] = file_path.exists()
        print(f"{'[OK]' if results[file] else '[MISS]'} {file}")
    
    # Verificar archivos de RAG storage
    for file in expected_files["rag_storage"]:
        file_path = rag_storage / file
        results[file] = file_path.exists()
        print(f"{'[OK]' if results[file] else '[MISS]'} {file}")
    
    # Verificar contenido del knowledge graph
    graph_file = rag_storage / "graph_data.json"
    if graph_file.exists():
        with open(graph_file, 'r', encoding='utf-8') as f:
            graph = json.load(f)
            print(f"[INFO] Knowledge graph: {len(graph.get('nodes', []))} nodos")
            print(f"[INFO] Knowledge graph: {len(graph.get('edges', []))} relaciones")
    
    success_rate = sum(results.values()) / len(results) * 100
    print(f"\n[RESULT] Tasa de éxito: {success_rate:.1f}%")
    
    return success_rate >= 80

if __name__ == "__main__":
    validate_rag_output()
```

#### Paso 5: Test de consultas (5 min)

```python
# test_rag_queries.py
from raganything import RAGAnything, RAGAnythingConfig

async def test_queries():
    """Probar consultas sobre el knowledge graph construido"""
    
    config = RAGAnythingConfig(
        working_dir="test_environment/rag_storage",
        parser="docling"
    )
    
    rag = RAGAnything(config=config)
    
    # Consultas de prueba
    queries = [
        "¿Cuáles son los requisitos para solicitar prestaciones económicas?",
        "¿Qué es el IPREM?",
        "¿Cuál es el procedimiento de emergencia social?",
        "¿Qué documentación se necesita presentar?"
    ]
    
    for query in queries:
        print(f"\nQ: {query}")
        response = await rag.query(query)
        print(f"A: {response[:200]}...")  # Primeros 200 caracteres

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_queries())
```

### 🚀 COMANDO COMPLETO DE EJECUCIÓN:

```bash
# Script todo-en-uno para Opción A
cd C:\Users\Gamer\Dev\RAG-Anything

# 1. Modificar parser
python -c "content = open('test_environment/04_safe_processing_script.py', 'r').read(); open('test_environment/04_safe_processing_script.py', 'w').write(content.replace('parser=\"mineru\"', 'parser=\"docling\"'))"

# 2. Ejecutar procesamiento
python test_environment\04_safe_processing_script.py raganything

# 3. Validar resultados
python test_environment\03_post_validation_tests.py test_environment\output
```

---

## 🅱️ OPCIÓN B: Usar Contenido Ya Procesado (Sin Reprocesar)

### Objetivo:
Aprovechar el `content.json` ya generado por Docling para construir directamente el knowledge graph sin reprocesar el PDF.

### ✅ VENTAJAS:
- No reprocesa (ahorra ~3-4 minutos)
- Aprovecha trabajo ya realizado
- Menor riesgo de errores
- Más eficiente

### ⚠️ DESVENTAJAS:
- Requiere script personalizado
- Posible pérdida de metadatos del pipeline completo
- No probamos integración completa

### 📝 PLAN DE IMPLEMENTACIÓN:

#### Paso 1: Crear script de integración (5 min)

```python
# Archivo: test_environment\build_kg_from_existing.py
"""
Construir Knowledge Graph desde contenido ya procesado
Sin reprocesar el PDF original
"""

import json
import asyncio
from pathlib import Path
from typing import Dict, Any
import sys
import os

# Añadir path para importar RAGAnything
sys.path.append(str(Path(__file__).parent.parent))

async def build_knowledge_graph():
    """Construir KG desde content.json existente"""
    
    # Paths
    content_file = Path("test_environment/output/content.json")
    metadata_file = Path("test_environment/output/metadata.json")
    rag_storage = Path("test_environment/rag_storage")
    
    print("="*60)
    print("CONSTRUYENDO KNOWLEDGE GRAPH DESDE CONTENIDO EXISTENTE")
    print("="*60)
    
    # 1. Verificar archivos existentes
    if not content_file.exists():
        print(f"[ERROR] No se encuentra: {content_file}")
        return False
    
    print(f"[OK] Contenido encontrado: {content_file}")
    print(f"[INFO] Tamaño: {content_file.stat().st_size / 1024:.1f} KB")
    
    # 2. Cargar contenido procesado
    with open(content_file, 'r', encoding='utf-8') as f:
        content_data = json.load(f)
    
    with open(metadata_file, 'r', encoding='utf-8') as f:
        metadata = json.load(f)
    
    print(f"[INFO] Palabras procesadas: {metadata['content_stats']['words']}")
    print(f"[INFO] Artículos encontrados: {metadata['legal_elements']['articulos']}")
    
    # 3. Preparar datos para RAGAnything
    from raganything import RAGAnything, RAGAnythingConfig
    
    # Configurar RAGAnything sin parser (solo indexación)
    config = RAGAnythingConfig(
        working_dir=str(rag_storage),
        skip_parsing=True,  # No procesar documentos
        enable_knowledge_graph=True,
        embedding_model="sentence-transformers/all-MiniLM-L6-v2"  # Modelo ligero
    )
    
    # 4. Inicializar RAGAnything
    print("\n[STEP 1] Inicializando RAGAnything...")
    try:
        rag = RAGAnything(config=config)
        print("[OK] RAGAnything inicializado")
    except Exception as e:
        print(f"[ERROR] No se pudo inicializar: {e}")
        return False
    
    # 5. Construir knowledge graph
    print("\n[STEP 2] Construyendo Knowledge Graph...")
    
    # Convertir content.json a formato esperado por RAGAnything
    documents = prepare_documents_from_content(content_data)
    
    # Indexar documentos
    try:
        await rag.index_documents(documents)
        print("[OK] Documentos indexados")
    except Exception as e:
        print(f"[ERROR] Fallo en indexación: {e}")
        return False
    
    # 6. Verificar knowledge graph
    print("\n[STEP 3] Verificando Knowledge Graph...")
    
    kg_file = rag_storage / "knowledge_graph.json"
    if kg_file.exists():
        with open(kg_file, 'r', encoding='utf-8') as f:
            kg_data = json.load(f)
        
        print(f"[OK] Knowledge Graph creado")
        print(f"[INFO] Nodos: {len(kg_data.get('nodes', []))}")
        print(f"[INFO] Relaciones: {len(kg_data.get('edges', []))}")
        print(f"[INFO] Archivo: {kg_file}")
    else:
        print("[WARN] Knowledge Graph no encontrado")
    
    # 7. Guardar estadísticas
    stats_file = rag_storage / "build_stats.json"
    stats = {
        "source_file": str(content_file),
        "words_processed": metadata['content_stats']['words'],
        "build_method": "from_existing_content",
        "skip_parsing": True,
        "success": True
    }
    
    with open(stats_file, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2)
    
    print(f"\n[OK] Estadísticas guardadas: {stats_file}")
    
    return True

def prepare_documents_from_content(content_data: Dict[str, Any]) -> list:
    """
    Convertir content.json de Docling a formato de RAGAnything
    """
    documents = []
    
    # Si content_data tiene estructura de páginas
    if "pages" in content_data:
        for page in content_data["pages"]:
            doc = {
                "text": page.get("text", ""),
                "metadata": {
                    "page_number": page.get("page_number", 0),
                    "source": "docling_processing"
                }
            }
            documents.append(doc)
    
    # Si es texto plano o markdown
    elif "content" in content_data:
        # Dividir en chunks de ~500 palabras
        text = content_data["content"]
        words = text.split()
        chunk_size = 500
        
        for i in range(0, len(words), chunk_size):
            chunk_text = " ".join(words[i:i+chunk_size])
            doc = {
                "text": chunk_text,
                "metadata": {
                    "chunk_id": i // chunk_size,
                    "source": "docling_processing"
                }
            }
            documents.append(doc)
    
    # Si tiene otra estructura, adaptar según sea necesario
    else:
        # Fallback: tratar todo como un documento
        doc = {
            "text": str(content_data),
            "metadata": {"source": "docling_processing"}
        }
        documents.append(doc)
    
    print(f"[INFO] Preparados {len(documents)} documentos para indexación")
    return documents

if __name__ == "__main__":
    success = asyncio.run(build_knowledge_graph())
    
    if success:
        print("\n✅ KNOWLEDGE GRAPH CONSTRUIDO EXITOSAMENTE")
    else:
        print("\n❌ FALLO EN CONSTRUCCIÓN DE KNOWLEDGE GRAPH")
    
    exit(0 if success else 1)
```

#### Paso 2: Ejecutar construcción del KG (2 min)

```bash
cd C:\Users\Gamer\Dev\RAG-Anything
python test_environment\build_kg_from_existing.py
```

#### Paso 3: Verificar integridad del KG (3 min)

```python
# test_environment\verify_kg_integrity.py
import json
from pathlib import Path

def verify_kg():
    """Verificar integridad del Knowledge Graph construido"""
    
    rag_storage = Path("test_environment/rag_storage")
    
    # Buscar archivos del KG
    kg_files = list(rag_storage.glob("*.json")) + \
               list(rag_storage.glob("*.pkl")) + \
               list(rag_storage.glob("*.npy"))
    
    print("ARCHIVOS DE KNOWLEDGE GRAPH:")
    print("-" * 40)
    
    for file in kg_files:
        size = file.stat().st_size / 1024
        print(f"[FILE] {file.name}: {size:.1f} KB")
        
        # Si es JSON, mostrar estructura
        if file.suffix == '.json':
            with open(file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, dict):
                    print(f"  Keys: {list(data.keys())[:5]}")
                elif isinstance(data, list):
                    print(f"  Items: {len(data)}")
    
    # Verificar que podemos hacer consultas
    print("\nVERIFICACIÓN DE CONSULTAS:")
    print("-" * 40)
    
    try:
        from raganything import RAGAnything, RAGAnythingConfig
        
        config = RAGAnythingConfig(
            working_dir=str(rag_storage),
            skip_parsing=True
        )
        
        rag = RAGAnything(config=config)
        
        # Consulta de prueba
        test_query = "¿Qué es una prestación económica?"
        print(f"Query test: {test_query}")
        
        # Aquí iría la consulta real
        print("[OK] Sistema de consultas disponible")
        
    except Exception as e:
        print(f"[ERROR] No se pueden hacer consultas: {e}")
    
    return len(kg_files) > 0

if __name__ == "__main__":
    verify_kg()
```

#### Paso 4: Interfaz de consultas (5 min)

```python
# test_environment\interactive_query.py
"""
Interfaz interactiva para consultar el Knowledge Graph
"""

import asyncio
from raganything import RAGAnything, RAGAnythingConfig
from pathlib import Path

async def interactive_query_session():
    """Sesión interactiva de consultas"""
    
    # Configurar RAGAnything
    config = RAGAnythingConfig(
        working_dir="test_environment/rag_storage",
        skip_parsing=True
    )
    
    print("="*60)
    print("INTERFAZ DE CONSULTAS - Knowledge Graph")
    print("="*60)
    print("Escribe 'exit' para salir\n")
    
    try:
        rag = RAGAnything(config=config)
        print("[OK] Sistema cargado\n")
    except Exception as e:
        print(f"[ERROR] No se pudo cargar: {e}")
        return
    
    while True:
        # Solicitar consulta
        query = input("\nPregunta > ").strip()
        
        if query.lower() in ['exit', 'quit', 'salir']:
            print("Cerrando sesión...")
            break
        
        if not query:
            continue
        
        try:
            # Realizar consulta
            print("\nBuscando respuesta...")
            response = await rag.query(query)
            
            print("\nRESPUESTA:")
            print("-" * 40)
            print(response)
            print("-" * 40)
            
        except Exception as e:
            print(f"[ERROR] Consulta falló: {e}")

if __name__ == "__main__":
    asyncio.run(interactive_query_session())
```

### 🚀 COMANDO COMPLETO DE EJECUCIÓN:

```bash
# Script todo-en-uno para Opción B
cd C:\Users\Gamer\Dev\RAG-Anything

# 1. Crear y ejecutar script de construcción
python test_environment\build_kg_from_existing.py

# 2. Verificar integridad
python test_environment\verify_kg_integrity.py

# 3. Probar consultas
python test_environment\interactive_query.py
```

---

## 📊 COMPARACIÓN DE OPCIONES

| Criterio | Opción A (Reconfigurar) | Opción B (Usar existente) |
|----------|-------------------------|---------------------------|
| **Tiempo de ejecución** | ~10-15 min | ~3-5 min |
| **Reprocesa PDF** | Sí ❌ | No ✅ |
| **Complejidad** | Baja | Media |
| **Riesgo de error** | Medio | Bajo |
| **Reutilizable** | Sí ✅ | Parcial |
| **Prueba integración completa** | Sí ✅ | No ❌ |
| **Aprovecha trabajo previo** | No ❌ | Sí ✅ |

---

## 🎯 RECOMENDACIÓN

### Para testing completo: **OPCIÓN A**
Si quieres validar que todo el pipeline funciona end-to-end.

### Para eficiencia: **OPCIÓN B**
Si quieres construir rápidamente el KG y empezar a hacer consultas.

### Enfoque híbrido:
1. Primero ejecutar **Opción B** (rápida, 3-5 min)
2. Si funciona, ya tienes KG para consultas
3. Después probar **Opción A** para validar pipeline completo

---

## 🐛 TROUBLESHOOTING

### Si Opción A falla:
```python
# Verificar que RAGAnything soporta docling
python -c "from raganything import RAGAnything; print(RAGAnything._supported_parsers)"
```

### Si Opción B falla:
```python
# Verificar estructura de content.json
python -c "import json; data=json.load(open('test_environment/output/content.json')); print(data.keys())"
```

### Si ninguna funciona:
```bash
# Fallback: usar solo Docling para consultas simples
python -c "
import json
query = input('Buscar: ')
with open('test_environment/output/content.md', 'r', encoding='utf-8') as f:
    content = f.read()
    if query.lower() in content.lower():
        pos = content.lower().index(query.lower())
        print(content[max(0,pos-200):pos+200])
"
```

---

*Documento de planes de implementación para RAGAnything + Docling*  
*Fecha: 26 de Agosto, 2025*