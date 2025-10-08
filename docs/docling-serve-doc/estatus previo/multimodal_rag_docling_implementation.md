# 🚀 Implementación Definitiva: Demo RAG Multimodal con Docling

## 📋 **RESUMEN EJECUTIVO**

**Objetivo**: Demo RAG multimodal funcional en **1 hora** que permita fotografiar/subir documentos y consultarlos via chat.

**Stack Técnico Definitivo**:
- **🧠 LLM**: `gemma3:27b` (multimodal + español nativo)
- **🔍 Embedding**: `embeddinggemma` (#1 MTEB multilingüe)
- **👁️ VLM**: SmolDocling (por defecto en Docling)
- **🗄️ Vector DB**: Qdrant (local)
- **🖥️ Interfaz**: Streamlit
- **🎯 Hardware**: M3 Max 48GB (optimizado)

---

## 🏗️ **ESTRUCTURA DEL PROYECTO**

```
~/Devs/multimodal-RAG/
├── 📁 src/
│   ├── 📄 docling_processor.py      # Procesamiento documentos con Docling
│   ├── 📄 embedding_engine.py       # EmbeddingGemma integration
│   ├── 📄 vector_store.py          # Qdrant management
│   ├── 📄 llm_interface.py         # Gemma3:27b integration
│   └── 📄 rag_engine.py            # RAG orchestrator
├── 📁 interface/
│   ├── 📄 streamlit_app.py         # Main UI
│   └── 📄 components.py            # UI components
├── 📁 config/
│   ├── 📄 models_config.py         # Model configurations
│   └── 📄 settings.py              # App settings
├── 📁 data/
│   ├── 📁 uploads/                 # Uploaded documents
│   ├── 📁 processed/               # Processed documents
│   └── 📁 qdrant_storage/         # Vector database
├── 📁 scripts/
│   ├── 📄 setup_environment.py     # Environment setup
│   ├── 📄 install_models.py       # Model installation
│   └── 📄 test_pipeline.py        # Pipeline testing
├── 📄 requirements.txt             # Dependencies
├── 📄 setup.sh                    # Quick setup script
├── 📄 run_demo.py                 # Demo launcher
└── 📄 README.md                   # Instructions
```

---

## ⚡ **INSTALACIÓN RÁPIDA (15 minutos)**

### **1. Setup Inicial (OPTIMIZADO - Aprovecha tu infraestructura)**

```bash
# Crear directorio en Devs
mkdir -p ~/Devs/multimodal-RAG
cd ~/Devs/multimodal-RAG

# ✅ APROVECHAR entorno virtual existente (¡CLAVE!)
python3 -m venv venv --copies ~/docling-project/venv
source venv/bin/activate

# Verificar docling ya instalado
python -c "import docling; print(f'✅ Docling {docling.__version__} disponible')"

# Crear estructura
mkdir -p src interface config data/{uploads,processed,qdrant_storage} scripts
```

### **2. Dependencias (OPTIMIZADO - Solo las faltantes)**

```python
# requirements_additional.txt (solo las que faltan)
streamlit>=1.32.0
qdrant-client>=1.9.0
ollama>=0.3.0
python-multipart>=0.0.9
python-dotenv>=1.0.0
pandas>=2.0.0
matplotlib>=3.7.0
plotly>=5.17.0

# ✅ YA INSTALADAS EN TU ENTORNO:
# docling==2.50.0 ✅
# torch==2.8.0 ✅  
# transformers==4.56.0 ✅
# torchvision==0.23.0 ✅
# numpy, pillow, requests ✅
```

```bash
# Instalar SOLO las dependencias faltantes
pip install streamlit qdrant-client ollama python-multipart python-dotenv pandas matplotlib plotly

# ¡Ahorra ~15-20 minutos de instalación!
```

### **3. Configuración Ollama (YA INSTALADO)**

```bash
# ✅ Ollama ya está instalado (versión 0.11.11)
# Solo necesitamos activarlo y descargar modelos

# Verificar Ollama
ollama --version

# Iniciar servicio (si no está corriendo)
ollama serve &

# Instalar modelos (aprovecha tu M3 Max)
echo "🔄 Descargando Gemma3:27b (optimizado para Apple Silicon)..."
ollama pull gemma3:27b

echo "🔄 Descargando EmbeddingGemma..."
ollama pull embeddinggemma

# Verificar instalación
ollama list
```

---

## 🧩 **CÓDIGO PRINCIPAL**

### **1. Procesador Docling** (`src/docling_processor.py`)

```python
"""
Docling Document Processor
Maneja la conversión de documentos usando SmolDocling VLM
"""
import os
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List

from docling.document_converter import DocumentConverter
from docling.datamodel.base_models import InputFormat
from docling.pipeline.vlm_pipeline import VlmPipeline
from docling.datamodel.document import DoclingDocument

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DoclingProcessor:
    def __init__(self, use_vlm: bool = True):
        """
        Inicializa el procesador con SmolDocling VLM por defecto
        """
        self.use_vlm = use_vlm
        self.supported_formats = [
            InputFormat.PDF,
            InputFormat.IMAGE,
            InputFormat.DOCX,
            InputFormat.PPTX,
            InputFormat.HTML,
            InputFormat.MD,
            InputFormat.TXT
        ]
        
        # Configurar VLM Pipeline (SmolDocling por defecto)
        if self.use_vlm:
            self.vlm_pipeline = VlmPipeline()  # SmolDocling automático
            logger.info("🔥 SmolDocling VLM activado para procesamiento multimodal")
        
        # Configurar Document Converter
        self.converter = self._setup_converter()
        
    def _setup_converter(self) -> DocumentConverter:
        """Configura el convertidor con parámetros optimizados"""
        
        format_options = {}
        
        if self.use_vlm:
            # Usar VLM Pipeline para PDFs e imágenes
            from docling.document_converter import PdfFormatOption
            format_options[InputFormat.PDF] = PdfFormatOption(
                pipeline_cls=VlmPipeline
            )
        
        converter = DocumentConverter(
            allowed_formats=self.supported_formats,
            format_options=format_options
        )
        
        logger.info(f"✅ DocumentConverter configurado con {len(self.supported_formats)} formatos")
        return converter
    
    def process_document(self, file_path: str) -> Dict[str, Any]:
        """
        Procesa un documento y retorna contenido estructurado
        """
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                raise FileNotFoundError(f"Archivo no encontrado: {file_path}")
            
            logger.info(f"🔄 Procesando: {file_path.name}")
            
            # Convertir documento
            conv_result = self.converter.convert(file_path)
            
            if not conv_result.status.success:
                raise Exception(f"Error en conversión: {conv_result.status.errors}")
            
            doc: DoclingDocument = conv_result.document
            
            # Extraer contenido estructurado
            result = {
                "filename": file_path.name,
                "format": file_path.suffix.lower(),
                "success": True,
                "content": {
                    "markdown": doc.export_to_markdown(),
                    "text": doc.export_to_text(),
                    "json": doc.export_to_dict()
                },
                "metadata": {
                    "pages": len(doc.pages) if hasattr(doc, 'pages') else 1,
                    "elements": len(doc.texts) + len(doc.tables) + len(doc.figures),
                    "tables": len(doc.tables),
                    "figures": len(doc.figures),
                    "vlm_used": self.use_vlm
                },
                "chunks": self._create_chunks(doc)
            }
            
            logger.info(f"✅ Procesado exitoso: {result['metadata']['pages']} páginas, "
                       f"{result['metadata']['elements']} elementos")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error procesando {file_path}: {str(e)}")
            return {
                "filename": file_path.name if 'file_path' in locals() else "unknown",
                "success": False,
                "error": str(e),
                "content": None,
                "metadata": None,
                "chunks": []
            }
    
    def _create_chunks(self, doc: DoclingDocument, chunk_size: int = 512) -> List[Dict[str, Any]]:
        """
        Crea chunks semánticos del documento
        """
        chunks = []
        chunk_id = 0
        
        # Procesar por páginas si están disponibles
        if hasattr(doc, 'pages') and doc.pages:
            for page_num, page in enumerate(doc.pages):
                page_text = page.export_to_text() if hasattr(page, 'export_to_text') else str(page)
                
                # Dividir en chunks manteniendo contexto
                sentences = self._split_text_semantic(page_text, chunk_size)
                
                for sentence_chunk in sentences:
                    if len(sentence_chunk.strip()) > 50:  # Filtrar chunks muy pequeños
                        chunks.append({
                            "id": f"chunk_{chunk_id}",
                            "page": page_num + 1,
                            "content": sentence_chunk.strip(),
                            "length": len(sentence_chunk),
                            "type": "text"
                        })
                        chunk_id += 1
        else:
            # Procesar documento completo si no hay páginas
            full_text = doc.export_to_text()
            sentences = self._split_text_semantic(full_text, chunk_size)
            
            for sentence_chunk in sentences:
                if len(sentence_chunk.strip()) > 50:
                    chunks.append({
                        "id": f"chunk_{chunk_id}",
                        "page": 1,
                        "content": sentence_chunk.strip(),
                        "length": len(sentence_chunk),
                        "type": "text"
                    })
                    chunk_id += 1
        
        # Añadir chunks de tablas
        for idx, table in enumerate(doc.tables):
            table_text = table.export_to_markdown() if hasattr(table, 'export_to_markdown') else str(table)
            chunks.append({
                "id": f"table_{idx}",
                "page": getattr(table, 'page', 1),
                "content": table_text,
                "length": len(table_text),
                "type": "table"
            })
        
        logger.info(f"📄 Creados {len(chunks)} chunks ({len([c for c in chunks if c['type']=='text'])} texto, "
                   f"{len([c for c in chunks if c['type']=='table'])} tablas)")
        
        return chunks
    
    def _split_text_semantic(self, text: str, chunk_size: int) -> List[str]:
        """
        División semántica inteligente de texto
        """
        import re
        
        # Dividir por párrafos primero
        paragraphs = re.split(r'\n\s*\n', text)
        chunks = []
        current_chunk = ""
        
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue
                
            # Si el párrafo cabe en el chunk actual
            if len(current_chunk + paragraph) <= chunk_size:
                current_chunk += paragraph + "\n\n"
            else:
                # Guardar chunk actual si no está vacío
                if current_chunk:
                    chunks.append(current_chunk.strip())
                
                # Si el párrafo es muy largo, dividirlo por oraciones
                if len(paragraph) > chunk_size:
                    sentences = re.split(r'[.!?]+\s+', paragraph)
                    temp_chunk = ""
                    
                    for sentence in sentences:
                        if len(temp_chunk + sentence) <= chunk_size:
                            temp_chunk += sentence + ". "
                        else:
                            if temp_chunk:
                                chunks.append(temp_chunk.strip())
                            temp_chunk = sentence + ". "
                    
                    current_chunk = temp_chunk
                else:
                    current_chunk = paragraph + "\n\n"
        
        # Añadir último chunk si existe
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def batch_process(self, file_paths: List[str]) -> List[Dict[str, Any]]:
        """
        Procesa múltiples documentos en lote
        """
        results = []
        total_files = len(file_paths)
        
        logger.info(f"🔄 Iniciando procesamiento en lote: {total_files} archivos")
        
        for idx, file_path in enumerate(file_paths, 1):
            logger.info(f"📁 Procesando {idx}/{total_files}: {Path(file_path).name}")
            result = self.process_document(file_path)
            results.append(result)
        
        successful = len([r for r in results if r['success']])
        logger.info(f"✅ Procesamiento completado: {successful}/{total_files} exitosos")
        
        return results

# Función helper para uso rápido
def process_single_document(file_path: str, use_vlm: bool = True) -> Dict[str, Any]:
    """Función helper para procesar un documento rápidamente"""
    processor = DoclingProcessor(use_vlm=use_vlm)
    return processor.process_document(file_path)
```

### **2. Motor de Embeddings** (`src/embedding_engine.py`)

```python
"""
EmbeddingGemma Integration Engine
Motor optimizado para embeddings multilingües con Google EmbeddingGemma
"""
import logging
import numpy as np
import ollama
from typing import List, Dict, Any, Optional
import time
import asyncio
import aiohttp

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmbeddingEngine:
    def __init__(self, 
                 model_name: str = "embeddinggemma",
                 dimensions: int = 768,
                 batch_size: int = 32,
                 normalize: bool = True):
        """
        Inicializa motor de embeddings con EmbeddingGemma
        """
        self.model_name = model_name
        self.dimensions = dimensions
        self.batch_size = batch_size
        self.normalize = normalize
        
        # Verificar disponibilidad del modelo
        self._verify_model()
        
        # Estadísticas de rendimiento
        self.stats = {
            "total_embeddings": 0,
            "total_time": 0.0,
            "cache_hits": 0
        }
        
        # Cache simple para embeddings
        self._cache = {}
        
        logger.info(f"🚀 EmbeddingEngine inicializado con {model_name}")
        logger.info(f"📊 Dimensiones: {dimensions}, Batch size: {batch_size}")
    
    def _verify_model(self):
        """Verifica que el modelo esté disponible"""
        try:
            models = ollama.list()
            model_names = [model['name'] for model in models['models']]
            
            if self.model_name not in model_names and f"{self.model_name}:latest" not in model_names:
                logger.warning(f"⚠️ Modelo {self.model_name} no encontrado. Descargando...")
                ollama.pull(self.model_name)
                logger.info(f"✅ Modelo {self.model_name} descargado exitosamente")
            
            # Test básico
            test_result = ollama.embeddings(
                model=self.model_name,
                prompt="test embedding"
            )
            
            if 'embedding' in test_result:
                actual_dims = len(test_result['embedding'])
                logger.info(f"✅ Modelo verificado - Dimensiones reales: {actual_dims}")
                self.dimensions = actual_dims  # Actualizar dimensiones reales
            
        except Exception as e:
            logger.error(f"❌ Error verificando modelo: {e}")
            raise RuntimeError(f"No se puede inicializar {self.model_name}")
    
    def embed_text(self, text: str) -> np.ndarray:
        """
        Genera embedding para un texto individual
        """
        if not text or not text.strip():
            return np.zeros(self.dimensions)
        
        text = text.strip()
        
        # Verificar cache
        if text in self._cache:
            self.stats["cache_hits"] += 1
            return self._cache[text]
        
        try:
            start_time = time.time()
            
            # Generar embedding
            response = ollama.embeddings(
                model=self.model_name,
                prompt=text
            )
            
            if 'embedding' not in response:
                logger.error(f"❌ Respuesta inválida del modelo para texto: {text[:50]}...")
                return np.zeros(self.dimensions)
            
            embedding = np.array(response['embedding'])
            
            # Normalizar si se requiere
            if self.normalize:
                norm = np.linalg.norm(embedding)
                if norm > 0:
                    embedding = embedding / norm
            
            # Actualizar estadísticas
            elapsed = time.time() - start_time
            self.stats["total_embeddings"] += 1
            self.stats["total_time"] += elapsed
            
            # Cachear resultado
            self._cache[text] = embedding
            
            return embedding
            
        except Exception as e:
            logger.error(f"❌ Error generando embedding: {e}")
            return np.zeros(self.dimensions)
    
    def embed_batch(self, texts: List[str]) -> List[np.ndarray]:
        """
        Genera embeddings para un lote de textos
        """
        if not texts:
            return []
        
        # Filtrar textos vacíos
        texts = [text.strip() for text in texts if text and text.strip()]
        
        if not texts:
            return []
        
        logger.info(f"🔄 Generando embeddings para {len(texts)} textos...")
        
        embeddings = []
        
        # Procesar en batches para optimizar rendimiento
        for i in range(0, len(texts), self.batch_size):
            batch = texts[i:i + self.batch_size]
            batch_embeddings = []
            
            for text in batch:
                embedding = self.embed_text(text)
                batch_embeddings.append(embedding)
            
            embeddings.extend(batch_embeddings)
            
            # Log de progreso
            if len(texts) > self.batch_size:
                progress = min(i + self.batch_size, len(texts))
                logger.info(f"📊 Progreso: {progress}/{len(texts)} embeddings")
        
        avg_time = self.stats["total_time"] / max(1, self.stats["total_embeddings"])
        logger.info(f"✅ Embeddings completados - Tiempo promedio: {avg_time:.3f}s")
        
        return embeddings
    
    def embed_documents(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Procesa documentos completos con sus chunks
        """
        logger.info(f"🔄 Procesando embeddings para {len(documents)} documentos...")
        
        for idx, doc in enumerate(documents):
            if not doc.get('success') or not doc.get('chunks'):
                continue
            
            logger.info(f"📄 Documento {idx + 1}/{len(documents)}: {doc['filename']}")
            
            # Generar embeddings para chunks
            chunk_texts = [chunk['content'] for chunk in doc['chunks']]
            chunk_embeddings = self.embed_batch(chunk_texts)
            
            # Asignar embeddings a chunks
            for chunk, embedding in zip(doc['chunks'], chunk_embeddings):
                chunk['embedding'] = embedding.tolist()
                chunk['embedding_model'] = self.model_name
                chunk['embedding_dims'] = self.dimensions
        
        logger.info(f"✅ Embeddings de documentos completados")
        return documents
    
    def similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Calcula similitud coseno entre dos embeddings
        """
        if len(embedding1) == 0 or len(embedding2) == 0:
            return 0.0
        
        # Asegurar que son numpy arrays
        embedding1 = np.array(embedding1)
        embedding2 = np.array(embedding2)
        
        # Normalizar si no están normalizados
        norm1 = np.linalg.norm(embedding1)
        norm2 = np.linalg.norm(embedding2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        if not self.normalize:
            embedding1 = embedding1 / norm1
            embedding2 = embedding2 / norm2
        
        # Similitud coseno
        similarity = np.dot(embedding1, embedding2)
        return float(np.clip(similarity, -1.0, 1.0))
    
    def search_similar(self, 
                      query_embedding: np.ndarray, 
                      document_chunks: List[Dict[str, Any]], 
                      top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Busca chunks más similares a la query
        """
        if not document_chunks:
            return []
        
        # Calcular similitudes
        similarities = []
        
        for chunk in document_chunks:
            if 'embedding' not in chunk:
                continue
            
            chunk_embedding = np.array(chunk['embedding'])
            sim = self.similarity(query_embedding, chunk_embedding)
            
            similarities.append({
                **chunk,
                'similarity': sim
            })
        
        # Ordenar por similitud descendente
        similarities.sort(key=lambda x: x['similarity'], reverse=True)
        
        # Retornar top K
        return similarities[:top_k]
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Retorna estadísticas de rendimiento
        """
        avg_time = self.stats["total_time"] / max(1, self.stats["total_embeddings"])
        
        return {
            "model": self.model_name,
            "dimensions": self.dimensions,
            "total_embeddings": self.stats["total_embeddings"],
            "total_time": round(self.stats["total_time"], 2),
            "avg_time_per_embedding": round(avg_time, 4),
            "cache_hits": self.stats["cache_hits"],
            "cache_size": len(self._cache)
        }
    
    def clear_cache(self):
        """Limpia el cache de embeddings"""
        self._cache.clear()
        logger.info("🗑️ Cache de embeddings limpiado")
```

### **3. Vector Store** (`src/vector_store.py`)

```python
"""
Qdrant Vector Store Manager
Gestión optimizada de vectores con Qdrant local
"""
import logging
import os
import uuid
from pathlib import Path
from typing import List, Dict, Any, Optional
import numpy as np

try:
    from qdrant_client import QdrantClient
    from qdrant_client.http.models import (
        Distance, VectorParams, CollectionInfo,
        PointStruct, Filter, FieldCondition, 
        MatchValue, SearchRequest
    )
except ImportError:
    logging.error("❌ Qdrant client not installed. Run: pip install qdrant-client")
    raise

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QdrantVectorStore:
    def __init__(self, 
                 storage_path: str = "~/Devs/multimodal-RAG/data/qdrant_storage",
                 collection_name: str = "docling_documents",
                 vector_size: int = 768):
        """
        Inicializa Qdrant Vector Store local
        """
        self.storage_path = Path(storage_path).expanduser()
        self.collection_name = collection_name
        self.vector_size = vector_size
        
        # Crear directorio si no existe
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Inicializar cliente
        self.client = self._init_client()
        
        # Configurar colección
        self._setup_collection()
        
        logger.info(f"🗄️ QdrantVectorStore inicializado")
        logger.info(f"📁 Almacenamiento: {self.storage_path}")
        logger.info(f"📊 Colección: {collection_name} (dim: {vector_size})")
    
    def _init_client(self) -> QdrantClient:
        """Inicializa cliente Qdrant local"""
        try:
            client = QdrantClient(path=str(self.storage_path))
            
            # Verificar conexión
            collections = client.get_collections()
            logger.info(f"✅ Cliente Qdrant conectado - {len(collections.collections)} colecciones")
            
            return client
            
        except Exception as e:
            logger.error(f"❌ Error conectando a Qdrant: {e}")
            raise RuntimeError("No se puede inicializar Qdrant")
    
    def _setup_collection(self):
        """Configura la colección de vectores"""
        try:
            # Verificar si existe la colección
            try:
                collection_info = self.client.get_collection(self.collection_name)
                logger.info(f"✅ Colección '{self.collection_name}' ya existe")
                
                # Verificar compatibilidad de dimensiones
                current_size = collection_info.config.params.vectors.size
                if current_size != self.vector_size:
                    logger.warning(f"⚠️ Dimensiones no coinciden: esperado {self.vector_size}, actual {current_size}")
                    # Opcionalmente recrear colección
                    self._recreate_collection()
                
                return
                
            except Exception:
                # La colección no existe, crearla
                logger.info(f"🔧 Creando colección '{self.collection_name}'...")
                
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.vector_size,
                        distance=Distance.COSINE
                    )
                )
                
                logger.info(f"✅ Colección '{self.collection_name}' creada exitosamente")
                
        except Exception as e:
            logger.error(f"❌ Error configurando colección: {e}")
            raise
    
    def _recreate_collection(self):
        """Recrea la colección con nuevas especificaciones"""
        try:
            logger.warning(f"🔄 Recreando colección '{self.collection_name}'...")
            
            # Eliminar colección existente
            self.client.delete_collection(self.collection_name)
            
            # Crear nueva colección
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.vector_size,
                    distance=Distance.COSINE
                )
            )
            
            logger.info(f"✅ Colección recreada exitosamente")
            
        except Exception as e:
            logger.error(f"❌ Error recreando colección: {e}")
            raise
    
    def add_documents(self, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Añade documentos procesados al vector store
        """
        if not documents:
            return {"success": False, "message": "No documents provided"}
        
        points = []
        stats = {
            "total_documents": len(documents),
            "successful_chunks": 0,
            "failed_chunks": 0,
            "skipped_documents": 0
        }
        
        logger.info(f"🔄 Añadiendo {len(documents)} documentos al vector store...")
        
        for doc_idx, document in enumerate(documents):
            if not document.get('success') or not document.get('chunks'):
                stats["skipped_documents"] += 1
                continue
            
            logger.info(f"📄 Procesando documento {doc_idx + 1}: {document['filename']}")
            
            for chunk in document['chunks']:
                if 'embedding' not in chunk:
                    stats["failed_chunks"] += 1
                    continue
                
                try:
                    # Crear punto para Qdrant
                    point_id = str(uuid.uuid4())
                    
                    point = PointStruct(
                        id=point_id,
                        vector=chunk['embedding'],
                        payload={
                            # Metadatos del documento
                            "document_id": document.get('filename', 'unknown'),
                            "document_format": document.get('format', 'unknown'),
                            "document_pages": document.get('metadata', {}).get('pages', 1),
                            
                            # Metadatos del chunk
                            "chunk_id": chunk['id'],
                            "chunk_type": chunk['type'],
                            "chunk_page": chunk.get('page', 1),
                            "chunk_length": chunk['length'],
                            "content": chunk['content'],
                            
                            # Metadatos del modelo
                            "embedding_model": chunk.get('embedding_model', 'unknown'),
                            "embedding_dims": chunk.get('embedding_dims', self.vector_size)
                        }
                    )
                    
                    points.append(point)
                    stats["successful_chunks"] += 1
                    
                except Exception as e:
                    logger.error(f"❌ Error procesando chunk {chunk.get('id', 'unknown')}: {e}")
                    stats["failed_chunks"] += 1
        
        # Insertar puntos en lotes
        if points:
            try:
                batch_size = 100
                total_batches = (len(points) + batch_size - 1) // batch_size
                
                for i in range(0, len(points), batch_size):
                    batch = points[i:i + batch_size]
                    batch_num = (i // batch_size) + 1
                    
                    self.client.upsert(
                        collection_name=self.collection_name,
                        points=batch
                    )
                    
                    logger.info(f"📊 Lote {batch_num}/{total_batches}: {len(batch)} puntos insertados")
                
                # Verificar inserción
                collection_info = self.client.get_collection(self.collection_name)
                total_vectors = collection_info.points_count
                
                logger.info(f"✅ Inserción completada - Total vectores en colección: {total_vectors}")
                
                return {
                    "success": True,
                    "message": f"Documents added successfully",
                    "stats": stats,
                    "total_vectors": total_vectors
                }
                
            except Exception as e:
                logger.error(f"❌ Error insertando puntos: {e}")
                return {
                    "success": False,
                    "message": f"Error inserting points: {str(e)}",
                    "stats": stats
                }
        else:
            logger.warning("⚠️ No se generaron puntos válidos para insertar")
            return {
                "success": False,
                "message": "No valid points generated",
                "stats": stats
            }
    
    def search(self, 
              query_embedding: np.ndarray, 
              limit: int = 5,
              score_threshold: float = 0.5,
              filter_conditions: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Busca vectores similares en la colección
        """
        try:
            # Convertir embedding a lista si es numpy array
            if isinstance(query_embedding, np.ndarray):
                query_vector = query_embedding.tolist()
            else:
                query_vector = query_embedding
            
            # Construir filtros si se proporcionan
            query_filter = None
            if filter_conditions:
                filter_conditions_list = []
                for field, value in filter_conditions.items():
                    filter_conditions_list.append(
                        FieldCondition(
                            key=field,
                            match=MatchValue(value=value)
                        )
                    )
                
                if filter_conditions_list:
                    query_filter = Filter(must=filter_conditions_list)
            
            # Realizar búsqueda
            search_results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=limit,
                score_threshold=score_threshold,
                query_filter=query_filter,
                with_payload=True,
                with_vectors=False
            )
            
            # Formatear resultados
            formatted_results = []
            for result in search_results:
                formatted_results.append({
                    "id": result.id,
                    "score": result.score,
                    "content": result.payload.get("content", ""),
                    "document_id": result.payload.get("document_id", ""),
                    "chunk_type": result.payload.get("chunk_type", "text"),
                    "chunk_page": result.payload.get("chunk_page", 1),
                    "metadata": {
                        "chunk_id": result.payload.get("chunk_id", ""),
                        "document_format": result.payload.get("document_format", ""),
                        "document_pages": result.payload.get("document_pages", 1),
                        "chunk_length": result.payload.get("chunk_length", 0),
                        "embedding_model": result.payload.get("embedding_model", "")
                    }
                })
            
            logger.info(f"🔍 Búsqueda completada: {len(formatted_results)} resultados")
            return formatted_results
            
        except Exception as e:
            logger.error(f"❌ Error en búsqueda: {e}")
            return []
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas de la colección
        """
        try:
            collection_info = self.client.get_collection(self.collection_name)
            
            return {
                "collection_name": self.collection_name,
                "total_vectors": collection_info.points_count,
                "vector_size": collection_info.config.params.vectors.size,
                "distance_metric": collection_info.config.params.vectors.distance.value,
                "status": collection_info.status.value,
                "storage_path": str(self.storage_path)
            }
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo estadísticas: {e}")
            return {
                "error": str(e)
            }
    
    def clear_collection(self) -> bool:
        """
        Limpia todos los vectores de la colección
        """
        try:
            logger.warning(f"🗑️ Limpiando colección '{self.collection_name}'...")
            
            # Eliminar y recrear colección
            self.client.delete_collection(self.collection_name)
            self._setup_collection()
            
            logger.info(f"✅ Colección limpiada exitosamente")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error limpiando colección: {e}")
            return False
    
    def delete_document(self, document_id: str) -> bool:
        """
        Elimina todos los chunks de un documento específico
        """
        try:
            # Buscar puntos del documento
            filter_condition = Filter(
                must=[
                    FieldCondition(
                        key="document_id",
                        match=MatchValue(value=document_id)
                    )
                ]
            )
            
            # Eliminar puntos
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=filter_condition
            )
            
            logger.info(f"🗑️ Documento '{document_id}' eliminado del vector store")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error eliminando documento: {e}")
            return False
```

### **4. Interfaz LLM** (`src/llm_interface.py`)

```python
"""
Gemma3:27b LLM Interface
Interfaz optimizada para el modelo Gemma3 multimodal
"""
import logging
import ollama
import json
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class LLMResponse:
    content: str
    model_used: str
    tokens_used: int
    response_time: float
    metadata: Dict[str, Any]

class Gemma3Interface:
    def __init__(self, 
                 model_name: str = "gemma3:27b",
                 temperature: float = 0.7,
                 max_tokens: int = 2048,
                 system_prompt: Optional[str] = None):
        """
        Inicializa interfaz con Gemma3:27b
        """
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        # System prompt optimizado para RAG multimodal español
        self.system_prompt = system_prompt or """
Eres un asistente especializado en análisis de documentos multimodales.

CAPACIDADES:
- Analizas documentos PDF, imágenes, tablas y texto con precisión
- Respondes en español de forma clara y estructurada  
- Integras información de múltiples fuentes del documento
- Identificas elementos visuales, tablas, gráficos y texto

INSTRUCCIONES:
- Usa el contexto proporcionado para responder preguntas específicas
- Si la información no está en el contexto, indícalo claramente
- Proporciona citas específicas cuando sea relevante
- Mantén respuestas concisas pero completas
- Destaca información importante de tablas y gráficos
"""
        
        # Verificar modelo
        self._verify_model()
        
        # Estadísticas
        self.stats = {
            "total_queries": 0,
            "total_tokens": 0,
            "total_time": 0.0,
            "successful_queries": 0,
            "failed_queries": 0
        }
        
        logger.info(f"🧠 Gemma3Interface inicializado")
        logger.info(f"🎛️ Modelo: {model_name}, Temperatura: {temperature}")
    
    def _verify_model(self):
        """Verifica disponibilidad del modelo"""
        try:
            models = ollama.list()
            model_names = [model['name'] for model in models['models']]
            
            if self.model_name not in model_names and f"{self.model_name}:latest" not in model_names:
                logger.warning(f"⚠️ Modelo {self.model_name} no encontrado. Descargando...")
                ollama.pull(self.model_name)
                logger.info(f"✅ Modelo {self.model_name} descargado")
            
            # Test básico
            test_response = ollama.chat(
                model=self.model_name,
                messages=[{"role": "user", "content": "test"}],
                options={"num_predict": 10}
            )
            
            if test_response and 'message' in test_response:
                logger.info("✅ Modelo verificado correctamente")
            
        except Exception as e:
            logger.error(f"❌ Error verificando modelo: {e}")
            raise RuntimeError(f"No se puede inicializar {self.model_name}")
    
    def generate_response(self, 
                         query: str, 
                         context: List[Dict[str, Any]], 
                         conversation_history: Optional[List[Dict[str, str]]] = None) -> LLMResponse:
        """
        Genera respuesta basada en query y contexto
        """
        try:
            start_time = time.time()
            
            # Construir contexto enriquecido
            context_text = self._build_context(context)
            
            # Construir prompt completo
            full_prompt = self._build_prompt(query, context_text)
            
            # Preparar mensajes
            messages = []
            
            # System message
            if self.system_prompt:
                messages.append({
                    "role": "system",
                    "content": self.system_prompt
                })
            
            # Historial de conversación si existe
            if conversation_history:
                messages.extend(conversation_history[-6:])  # Últimos 6 intercambios
            
            # Query actual
            messages.append({
                "role": "user",
                "content": full_prompt
            })
            
            # Generar respuesta
            logger.info(f"🔄 Generando respuesta con {self.model_name}...")
            
            response = ollama.chat(
                model=self.model_name,
                messages=messages,
                options={
                    "temperature": self.temperature,
                    "num_predict": self.max_tokens,
                    "top_p": 0.9,
                    "stop": ["</respuesta>", "\n\nHuman:", "\n\nUsuario:"]
                }
            )
            
            # Procesar respuesta
            if not response or 'message' not in response:
                raise Exception("Respuesta inválida del modelo")
            
            content = response['message']['content'].strip()
            
            # Calcular métricas
            response_time = time.time() - start_time
            tokens_used = len(content.split())  # Aproximación
            
            # Actualizar estadísticas
            self.stats["total_queries"] += 1
            self.stats["successful_queries"] += 1
            self.stats["total_tokens"] += tokens_used
            self.stats["total_time"] += response_time
            
            logger.info(f"✅ Respuesta generada - Tokens: {tokens_used}, Tiempo: {response_time:.2f}s")
            
            return LLMResponse(
                content=content,
                model_used=self.model_name,
                tokens_used=tokens_used,
                response_time=response_time,
                metadata={
                    "context_chunks": len(context),
                    "query_length": len(query),
                    "temperature": self.temperature,
                    "conversation_turns": len(conversation_history) if conversation_history else 0
                }
            )
            
        except Exception as e:
            # Actualizar estadísticas de error
            self.stats["total_queries"] += 1
            self.stats["failed_queries"] += 1
            
            logger.error(f"❌ Error generando respuesta: {e}")
            
            # Respuesta de fallback
            fallback_content = f"Lo siento, hubo un error procesando tu consulta: {str(e)}"
            
            return LLMResponse(
                content=fallback_content,
                model_used=self.model_name,
                tokens_used=len(fallback_content.split()),
                response_time=0.0,
                metadata={"error": str(e)}
            )
    
    def _build_context(self, context_chunks: List[Dict[str, Any]]) -> str:
        """
        Construye contexto enriquecido a partir de chunks
        """
        if not context_chunks:
            return "No se encontró información relevante en los documentos."
        
        context_parts = []
        
        # Agrupar chunks por documento
        docs_dict = {}
        for chunk in context_chunks:
            doc_id = chunk.get('document_id', 'Documento desconocido')
            if doc_id not in docs_dict:
                docs_dict[doc_id] = []
            docs_dict[doc_id].append(chunk)
        
        # Construir contexto por documento
        for doc_id, chunks in docs_dict.items():
            context_parts.append(f"\n📄 **{doc_id}**")
            
            for chunk in chunks:
                chunk_type = chunk.get('chunk_type', 'texto')
                page = chunk.get('chunk_page', 1)
                score = chunk.get('score', 0.0)
                content = chunk.get('content', '').strip()
                
                # Formatear según tipo de chunk
                if chunk_type == 'table':
                    context_parts.append(f"\n🔢 **Tabla (Página {page}, Relevancia: {score:.2f})**")
                    context_parts.append(f"```\n{content}\n```")
                elif chunk_type == 'figure':
                    context_parts.append(f"\n🖼️ **Figura (Página {page}, Relevancia: {score:.2f})**")
                    context_parts.append(f"{content}")
                else:
                    context_parts.append(f"\n📝 **Texto (Página {page}, Relevancia: {score:.2f})**")
                    context_parts.append(f"{content}")
        
        return "\n".join(context_parts)
    
    def _build_prompt(self, query: str, context: str) -> str:
        """
        Construye prompt optimizado para RAG
        """
        prompt = f"""
CONTEXTO DE DOCUMENTOS:
{context}

PREGUNTA DEL USUARIO:
{query}

INSTRUCCIONES:
- Responde basándote únicamente en el contexto proporcionado
- Si la información no está disponible, indícalo claramente
- Proporciona referencias específicas (página, tabla, etc.) cuando sea relevante
- Mantén una respuesta estructurada y clara
- Si hay tablas o figuras relevantes, haz referencia a ellas específicamente

RESPUESTA:
"""
        return prompt
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas de uso"""
        avg_time = self.stats["total_time"] / max(1, self.stats["total_queries"])
        avg_tokens = self.stats["total_tokens"] / max(1, self.stats["successful_queries"])
        success_rate = self.stats["successful_queries"] / max(1, self.stats["total_queries"])
        
        return {
            "model": self.model_name,
            "total_queries": self.stats["total_queries"],
            "successful_queries": self.stats["successful_queries"],
            "failed_queries": self.stats["failed_queries"],
            "success_rate": round(success_rate * 100, 2),
            "total_tokens": self.stats["total_tokens"],
            "avg_tokens_per_query": round(avg_tokens, 2),
            "total_time": round(self.stats["total_time"], 2),
            "avg_time_per_query": round(avg_time, 3),
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }
    
    def clear_stats(self):
        """Limpia estadísticas"""
        self.stats = {
            "total_queries": 0,
            "total_tokens": 0,
            "total_time": 0.0,
            "successful_queries": 0,
            "failed_queries": 0
        }
        logger.info("📊 Estadísticas de LLM limpiadas")
```

### **5. Motor RAG Principal** (`src/rag_engine.py`)

```python
"""
RAG Engine - Orquestador Principal
Integra Docling + EmbeddingGemma + Qdrant + Gemma3:27b
"""
import logging
import time
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
import json

from .docling_processor import DoclingProcessor
from .embedding_engine import EmbeddingEngine
from .vector_store import QdrantVectorStore
from .llm_interface import Gemma3Interface, LLMResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RAGEngine:
    def __init__(self,
                 storage_path: str = "~/Devs/multimodal-RAG/data",
                 use_vlm: bool = True,
                 embedding_model: str = "embeddinggemma",
                 llm_model: str = "gemma3:27b",
                 collection_name: str = "docling_documents"):
        """
        Inicializa el motor RAG completo
        """
        self.storage_path = Path(storage_path).expanduser()
        self.use_vlm = use_vlm
        
        # Crear directorios necesarios
        self.storage_path.mkdir(parents=True, exist_ok=True)
        (self.storage_path / "uploads").mkdir(exist_ok=True)
        (self.storage_path / "processed").mkdir(exist_ok=True)
        
        logger.info("🚀 Inicializando RAG Engine...")
        
        # Inicializar componentes
        self.docling_processor = DoclingProcessor(use_vlm=use_vlm)
        self.embedding_engine = EmbeddingEngine(model_name=embedding_model)
        
        # Vector store con dimensiones del modelo de embeddings
        vector_size = self.embedding_engine.dimensions
        self.vector_store = QdrantVectorStore(
            storage_path=str(self.storage_path / "qdrant_storage"),
            collection_name=collection_name,
            vector_size=vector_size
        )
        
        self.llm_interface = Gemma3Interface(model_name=llm_model)
        
        # Estado de la sesión
        self.conversation_history = []
        self.current_documents = {}
        
        # Estadísticas globales
        self.global_stats = {
            "documents_processed": 0,
            "queries_answered": 0,
            "total_processing_time": 0.0,
            "total_query_time": 0.0
        }
        
        logger.info("✅ RAG Engine inicializado exitosamente")
        logger.info(f"📊 Configuración: VLM={use_vlm}, Embedding={embedding_model}, LLM={llm_model}")
    
    def process_document(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Procesa un documento completo: Docling + Embeddings + Vector Store
        """
        try:
            start_time = time.time()
            file_path = Path(file_path)
            
            logger.info(f"🔄 Iniciando procesamiento completo: {file_path.name}")
            
            # Paso 1: Procesamiento con Docling
            logger.info("1️⃣ Procesando con Docling...")
            docling_result = self.docling_processor.process_document(str(file_path))
            
            if not docling_result['success']:
                return {
                    "success": False,
                    "error": f"Error en Docling: {docling_result.get('error', 'Unknown error')}",
                    "stage": "docling_processing"
                }
            
            # Paso 2: Generar embeddings
            logger.info("2️⃣ Generando embeddings...")
            documents_with_embeddings = self.embedding_engine.embed_documents([docling_result])
            
            if not documents_with_embeddings or not documents_with_embeddings[0].get('chunks'):
                return {
                    "success": False,
                    "error": "No se pudieron generar embeddings",
                    "stage": "embedding_generation"
                }
            
            # Paso 3: Almacenar en vector store
            logger.info("3️⃣ Almacenando en vector store...")
            storage_result = self.vector_store.add_documents(documents_with_embeddings)
            
            if not storage_result['success']:
                return {
                    "success": False,
                    "error": f"Error almacenando vectores: {storage_result.get('message', 'Unknown error')}",
                    "stage": "vector_storage"
                }
            
            # Paso 4: Guardar documento procesado
            processed_doc = documents_with_embeddings[0]
            doc_id = processed_doc['filename']
            self.current_documents[doc_id] = processed_doc
            
            # Guardar en disco
            self._save_processed_document(processed_doc)
            
            # Actualizar estadísticas
            processing_time = time.time() - start_time
            self.global_stats["documents_processed"] += 1
            self.global_stats["total_processing_time"] += processing_time
            
            result = {
                "success": True,
                "document_id": doc_id,
                "processing_time": round(processing_time, 2),
                "statistics": {
                    "pages": processed_doc['metadata']['pages'],
                    "elements": processed_doc['metadata']['elements'],
                    "chunks": len(processed_doc['chunks']),
                    "vectors_stored": storage_result['stats']['successful_chunks'],
                    "vlm_used": processed_doc['metadata']['vlm_used']
                },
                "vector_store_stats": storage_result['stats']
            }
            
            logger.info(f"✅ Documento procesado completamente en {processing_time:.2f}s")
            logger.info(f"📊 {result['statistics']['chunks']} chunks, "
                       f"{result['statistics']['vectors_stored']} vectores almacenados")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error en procesamiento completo: {e}")
            return {
                "success": False,
                "error": str(e),
                "stage": "general_error"
            }
    
    def query(self, 
             question: str, 
             top_k: int = 5, 
             score_threshold: float = 0.5,
             include_conversation_history: bool = True) -> Dict[str, Any]:
        """
        Responde una pregunta usando RAG completo
        """
        try:
            start_time = time.time()
            
            logger.info(f"🔍 Procesando query: {question[:100]}...")
            
            # Paso 1: Generar embedding de la query
            logger.info("1️⃣ Generando embedding de la query...")
            query_embedding = self.embedding_engine.embed_text(question)
            
            if query_embedding is None or len(query_embedding) == 0:
                return {
                    "success": False,
                    "error": "No se pudo generar embedding para la query",
                    "stage": "query_embedding"
                }
            
            # Paso 2: Buscar contexto relevante
            logger.info("2️⃣ Buscando contexto relevante...")
            search_results = self.vector_store.search(
                query_embedding=query_embedding,
                limit=top_k,
                score_threshold=score_threshold
            )
            
            if not search_results:
                return {
                    "success": True,
                    "answer": "Lo siento, no encontré información relevante en los documentos para responder tu pregunta.",
                    "context": [],
                    "metadata": {
                        "query_time": time.time() - start_time,
                        "context_found": False,
                        "search_results": 0
                    }
                }
            
            # Paso 3: Generar respuesta con LLM
            logger.info("3️⃣ Generando respuesta con LLM...")
            conversation_hist = self.conversation_history if include_conversation_history else None
            
            llm_response = self.llm_interface.generate_response(
                query=question,
                context=search_results,
                conversation_history=conversation_hist
            )
            
            # Paso 4: Actualizar historial de conversación
            if include_conversation_history:
                self.conversation_history.extend([
                    {"role": "user", "content": question},
                    {"role": "assistant", "content": llm_response.content}
                ])
                
                # Mantener solo últimos 10 intercambios
                if len(self.conversation_history) > 20:
                    self.conversation_history = self.conversation_history[-20:]
            
            # Calcular métricas
            query_time = time.time() - start_time
            self.global_stats["queries_answered"] += 1
            self.global_stats["total_query_time"] += query_time
            
            result = {
                "success": True,
                "answer": llm_response.content,
                "context": search_results,
                "metadata": {
                    "query_time": round(query_time, 3),
                    "llm_response_time": round(llm_response.response_time, 3),
                    "llm_tokens": llm_response.tokens_used,
                    "context_chunks": len(search_results),
                    "min_similarity": min([r['score'] for r in search_results]) if search_results else 0,
                    "max_similarity": max([r['score'] for r in search_results]) if search_results else 0,
                    "model_used": llm_response.model_used
                }
            }
            
            logger.info(f"✅ Query respondida en {query_time:.3f}s")
            logger.info(f"📊 {len(search_results)} chunks de contexto, "
                       f"{llm_response.tokens_used} tokens generados")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error procesando query: {e}")
            return {
                "success": False,
                "error": str(e),
                "stage": "query_processing"
            }
    
    def batch_process_documents(self, file_paths: List[Union[str, Path]]) -> Dict[str, Any]:
        """
        Procesa múltiples documentos en lote
        """
        results = []
        successful = 0
        failed = 0
        
        logger.info(f"🔄 Procesando {len(file_paths)} documentos en lote...")
        
        for idx, file_path in enumerate(file_paths, 1):
            logger.info(f"📄 Procesando {idx}/{len(file_paths)}: {Path(file_path).name}")
            
            result = self.process_document(file_path)
            results.append(result)
            
            if result['success']:
                successful += 1
            else:
                failed += 1
        
        logger.info(f"✅ Procesamiento en lote completado: {successful} exitosos, {failed} fallidos")
        
        return {
            "total_documents": len(file_paths),
            "successful": successful,
            "failed": failed,
            "results": results,
            "success_rate": round((successful / len(file_paths)) * 100, 2)
        }
    
    def get_system_status(self) -> Dict[str, Any]:
        """
        Obtiene estado completo del sistema
        """
        try:
            # Estadísticas de componentes
            docling_available = True
            embedding_stats = self.embedding_engine.get_stats()
            vector_stats = self.vector_store.get_collection_stats()
            llm_stats = self.llm_interface.get_stats()
            
            return {
                "system_status": "operational",
                "components": {
                    "docling_processor": {
                        "available": docling_available,
                        "vlm_enabled": self.use_vlm
                    },
                    "embedding_engine": embedding_stats,
                    "vector_store": vector_stats,
                    "llm_interface": llm_stats
                },
                "global_stats": self.global_stats,
                "current_documents": {
                    "count": len(self.current_documents),
                    "documents": list(self.current_documents.keys())
                },
                "conversation": {
                    "history_length": len(self.conversation_history),
                    "turns": len(self.conversation_history) // 2
                }
            }
            
        except Exception as e:
            return {
                "system_status": "error",
                "error": str(e)
            }
    
    def clear_conversation_history(self):
        """Limpia el historial de conversación"""
        self.conversation_history.clear()
        logger.info("🗑️ Historial de conversación limpiado")
    
    def delete_document(self, document_id: str) -> bool:
        """Elimina un documento del sistema"""
        try:
            # Eliminar de vector store
            vector_deleted = self.vector_store.delete_document(document_id)
            
            # Eliminar de documentos actuales
            if document_id in self.current_documents:
                del self.current_documents[document_id]
            
            # Eliminar archivo procesado
            processed_file = self.storage_path / "processed" / f"{document_id}.json"
            if processed_file.exists():
                processed_file.unlink()
            
            logger.info(f"🗑️ Documento {document_id} eliminado del sistema")
            return vector_deleted
            
        except Exception as e:
            logger.error(f"❌ Error eliminando documento: {e}")
            return False
    
    def _save_processed_document(self, document: Dict[str, Any]):
        """Guarda documento procesado en disco"""
        try:
            processed_dir = self.storage_path / "processed"
            processed_dir.mkdir(exist_ok=True)
            
            filename = document['filename']
            save_path = processed_dir / f"{filename}.json"
            
            # Crear copia sin embeddings para ahorrar espacio
            doc_copy = document.copy()
            for chunk in doc_copy.get('chunks', []):
                if 'embedding' in chunk:
                    chunk['embedding_saved'] = True
                    del chunk['embedding']  # Remover embedding para ahorrar espacio
            
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(doc_copy, f, indent=2, ensure_ascii=False)
            
            logger.info(f"💾 Documento procesado guardado: {save_path}")
            
        except Exception as e:
            logger.error(f"❌ Error guardando documento procesado: {e}")

# Función helper para uso rápido
def create_rag_engine(config: Optional[Dict[str, Any]] = None) -> RAGEngine:
    """
    Crea instancia de RAGEngine con configuración personalizada
    """
    default_config = {
        "storage_path": "~/Devs/multimodal-RAG/data",
        "use_vlm": True,
        "embedding_model": "embeddinggemma",
        "llm_model": "gemma3:27b",
        "collection_name": "docling_documents"
    }
    
    if config:
        default_config.update(config)
    
    return RAGEngine(**default_config)
```

### **6. Aplicación Streamlit** (`interface/streamlit_app.py`)

```python
"""
Streamlit RAG Multimodal Interface
Interfaz web completa para demo RAG con Docling
"""
import streamlit as st
import tempfile
import time
from pathlib import Path
import json
import sys
import os
import logging

# Añadir path del proyecto
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.rag_engine import create_rag_engine

# Configurar logging para Streamlit
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuración de página
st.set_page_config(
    page_title="🚀 RAG Multimodal Demo - Docling",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 0.25rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 0.25rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .info-box {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        border-radius: 0.25rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .metric-card {
        background: linear-gradient(45deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        padding: 1rem;
        color: white;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Inicializar estado de la sesión
if 'rag_engine' not in st.session_state:
    st.session_state.rag_engine = None
if 'processing_status' not in st.session_state:
    st.session_state.processing_status = {}
if 'current_documents' not in st.session_state:
    st.session_state.current_documents = {}
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

def initialize_rag_engine():
    """Inicializa el motor RAG"""
    try:
        with st.spinner("🚀 Inicializando motor RAG..."):
            engine = create_rag_engine()
            st.session_state.rag_engine = engine
            st.success("✅ Motor RAG inicializado exitosamente")
            return True
    except Exception as e:
        st.error(f"❌ Error inicializando motor RAG: {str(e)}")
        return False

def display_header():
    """Muestra header principal"""
    st.markdown('<h1 class="main-header">🚀 RAG Multimodal Demo</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #666;">Powered by Docling + EmbeddingGemma + Gemma3:27b</p>', unsafe_allow_html=True)
    
    # Mostrar configuración del stack
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown('<div class="metric-card"><strong>📄 VLM</strong><br>SmolDocling</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="metric-card"><strong>🔍 Embedding</strong><br>EmbeddingGemma</div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="metric-card"><strong>🧠 LLM</strong><br>Gemma3:27b</div>', unsafe_allow_html=True)
    with col4:
        st.markdown('<div class="metric-card"><strong>🗄️ Vector DB</strong><br>Qdrant Local</div>', unsafe_allow_html=True)

def sidebar_controls():
    """Controles de la barra lateral"""
    st.sidebar.header("🎛️ Panel de Control")
    
    # Inicialización del sistema
    if st.session_state.rag_engine is None:
        st.sidebar.error("❌ Motor RAG no inicializado")
        if st.sidebar.button("🚀 Inicializar Sistema"):
            initialize_rag_engine()
        return False
    else:
        st.sidebar.success("✅ Sistema Operacional")
    
    # Estado del sistema
    with st.sidebar.expander("📊 Estado del Sistema"):
        if st.button("🔄 Actualizar Estado"):
            status = st.session_state.rag_engine.get_system_status()
            st.json(status)
    
    # Controles de conversación
    st.sidebar.header("💬 Controles de Chat")
    
    if st.sidebar.button("🗑️ Limpiar Conversación"):
        st.session_state.rag_engine.clear_conversation_history()
        st.session_state.chat_history = []
        st.sidebar.success("Conversación limpiada")
    
    # Configuración avanzada
    with st.sidebar.expander("⚙️ Configuración Avanzada"):
        top_k = st.slider("Top K resultados", 1, 10, 5)
        score_threshold = st.slider("Umbral de similitud", 0.0, 1.0, 0.5, 0.05)
        
        return {"top_k": top_k, "score_threshold": score_threshold}
    
    return {"top_k": 5, "score_threshold": 0.5}

def document_upload_section():
    """Sección de subida de documentos"""
    st.header("📄 Procesamiento de Documentos")
    
    # Información de formatos soportados
    with st.expander("ℹ️ Formatos Soportados"):
        st.markdown("""
        **Formatos Multimodales Compatibles:**
        - 📄 **PDF**: Documentos complejos con texto, imágenes y tablas
        - 🖼️ **Imágenes**: PNG, JPEG, GIF (OCR automático)
        - 📝 **Word**: DOCX con contenido multimedia
        - 📊 **PowerPoint**: PPTX con gráficos y texto
        - 🌐 **HTML**: Páginas web con contenido estructurado
        - 📋 **Markdown**: Documentación técnica
        - 📄 **Texto**: TXT plain text
        """)
    
    # Subida de archivos
    uploaded_files = st.file_uploader(
        "Selecciona documentos para procesar",
        type=['pdf', 'png', 'jpg', 'jpeg', 'docx', 'pptx', 'html', 'md', 'txt'],
        accept_multiple_files=True,
        help="Puedes subir múltiples archivos. Se procesarán con Docling + SmolDocling VLM"
    )
    
    if uploaded_files:
        st.subheader(f"📁 {len(uploaded_files)} archivo(s) seleccionado(s)")
        
        # Mostrar archivos seleccionados
        for file in uploaded_files:
            file_size = len(file.getvalue()) / (1024 * 1024)  # MB
            st.write(f"- **{file.name}** ({file_size:.2f} MB)")
        
        if st.button("🚀 Procesar Documentos", type="primary"):
            process_uploaded_documents(uploaded_files)

def process_uploaded_documents(uploaded_files):
    """Procesa documentos subidos"""
    if not st.session_state.rag_engine:
        st.error("❌ Motor RAG no inicializado")
        return
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    processed_files = []
    
    for idx, uploaded_file in enumerate(uploaded_files):
        # Actualizar progreso
        progress = (idx + 1) / len(uploaded_files)
        progress_bar.progress(progress)
        status_text.text(f"🔄 Procesando {idx + 1}/{len(uploaded_files)}: {uploaded_file.name}")
        
        try:
            # Guardar archivo temporal
            with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{uploaded_file.name}") as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_file_path = tmp_file.name
            
            # Procesar documento
            result = st.session_state.rag_engine.process_document(tmp_file_path)
            
            # Limpiar archivo temporal
            os.unlink(tmp_file_path)
            
            # Almacenar resultado
            processed_files.append({
                "filename": uploaded_file.name,
                "result": result
            })
            
        except Exception as e:
            st.error(f"❌ Error procesando {uploaded_file.name}: {str(e)}")
            processed_files.append({
                "filename": uploaded_file.name,
                "result": {"success": False, "error": str(e)}
            })
    
    # Mostrar resultados
    progress_bar.empty()
    status_text.empty()
    
    display_processing_results(processed_files)

def display_processing_results(processed_files):
    """Muestra resultados del procesamiento"""
    st.subheader("📊 Resultados del Procesamiento")
    
    successful = len([f for f in processed_files if f['result']['success']])
    failed = len(processed_files) - successful
    
    # Métricas globales
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("✅ Exitosos", successful, delta=f"{successful}/{len(processed_files)}")
    
    with col2:
        st.metric("❌ Fallidos", failed, delta=f"{failed}/{len(processed_files)}")
    
    with col3:
        success_rate = (successful / len(processed_files)) * 100
        st.metric("📈 Tasa de Éxito", f"{success_rate:.1f}%")
    
    # Detalles por archivo
    for file_info in processed_files:
        filename = file_info['filename']
        result = file_info['result']
        
        with st.expander(f"📄 {filename} - {'✅' if result['success'] else '❌'}"):
            if result['success']:
                st.markdown('<div class="success-box">', unsafe_allow_html=True)
                st.write("**✅ Procesamiento Exitoso**")
                
                stats = result['statistics']
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("📄 Páginas", stats['pages'])
                with col2:
                    st.metric("📊 Elementos", stats['elements'])
                with col3:
                    st.metric("🔤 Chunks", stats['chunks'])
                with col4:
                    st.metric("🎯 Vectores", stats['vectors_stored'])
                
                st.write(f"⏱️ **Tiempo de procesamiento**: {result['processing_time']}s")
                st.write(f"👁️ **VLM utilizado**: {'Sí' if stats['vlm_used'] else 'No'}")
                
                st.markdown('</div>', unsafe_allow_html=True)
                
            else:
                st.markdown('<div class="error-box">', unsafe_allow_html=True)
                st.write("**❌ Error en Procesamiento**")
                st.write(f"**Error**: {result.get('error', 'Error desconocido')}")
                st.write(f"**Etapa**: {result.get('stage', 'Desconocida')}")
                st.markdown('</div>', unsafe_allow_html=True)

def chat_interface():
    """Interfaz de chat RAG"""
    st.header("💬 Chat con Documentos")
    
    if not st.session_state.rag_engine:
        st.warning("⚠️ Necesitas inicializar el motor RAG primero")
        return
    
    # Configuración del chat
    config = sidebar_controls()
    if config is False:
        return
    
    # Historial de chat
    if st.session_state.chat_history:
        st.subheader("📜 Historial de Conversación")
        
        for i, exchange in enumerate(st.session_state.chat_history):
            with st.container():
                st.write(f"**👤 Usuario:** {exchange['question']}")
                st.write(f"**🤖 Asistente:** {exchange['answer']}")
                
                # Mostrar contexto si existe
                if exchange.get('context'):
                    with st.expander(f"📚 Contexto utilizado ({len(exchange['context'])} chunks)"):
                        for idx, chunk in enumerate(exchange['context']):
                            st.write(f"**Chunk {idx+1}** (Similitud: {chunk['score']:.3f})")
                            st.write(f"*Documento: {chunk['document_id']} - Página: {chunk['chunk_page']}*")
                            st.code(chunk['content'][:300] + "..." if len(chunk['content']) > 300 else chunk['content'])
                
                st.divider()
    
    # Nueva pregunta
    st.subheader("❓ Nueva Pregunta")
    
    question = st.text_area(
        "Escribe tu pregunta sobre los documentos:",
        placeholder="Ejemplo: ¿Cuáles son los principales hallazgos de este documento? ¿Qué información contienen las tablas?",
        height=100
    )
    
    col1, col2 = st.columns([1, 4])
    
    with col1:
        submit_button = st.button("🚀 Preguntar", type="primary")
    
    with col2:
        if st.button("🔄 Pregunta de Ejemplo"):
            example_questions = [
                "¿Cuáles son los puntos principales de este documento?",
                "¿Qué información contienen las tablas?",
                "Resume el contenido de las imágenes",
                "¿Hay datos numéricos importantes?",
                "Explica el contexto general del documento"
            ]
            import random
            question = random.choice(example_questions)
            st.rerun()
    
    if submit_button and question:
        process_question(question, config)

def process_question(question, config):
    """Procesa una pregunta del usuario"""
    with st.spinner("🔄 Buscando respuesta..."):
        try:
            # Procesar query
            result = st.session_state.rag_engine.query(
                question=question,
                top_k=config['top_k'],
                score_threshold=config['score_threshold']
            )
            
            if result['success']:
                # Mostrar respuesta
                st.subheader("🎯 Respuesta")
                st.markdown('<div class="success-box">', unsafe_allow_html=True)
                st.write(result['answer'])
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Mostrar métricas
                metadata = result['metadata']
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("⏱️ Tiempo Total", f"{metadata['query_time']}s")
                with col2:
                    st.metric("🧠 Tokens LLM", metadata['llm_tokens'])
                with col3:
                    st.metric("📚 Chunks Contexto", metadata['context_chunks'])
                with col4:
                    st.metric("🎯 Similitud Máx", f"{metadata['max_similarity']:.3f}")
                
                # Guardar en historial
                st.session_state.chat_history.append({
                    "question": question,
                    "answer": result['answer'],
                    "context": result['context'],
                    "metadata": metadata
                })
                
                # Mostrar contexto
                if result['context']:
                    with st.expander(f"📚 Contexto Utilizado ({len(result['context'])} chunks)"):
                        for idx, chunk in enumerate(result['context']):
                            st.write(f"**📄 Chunk {idx+1}** - Similitud: {chunk['score']:.3f}")
                            st.write(f"*🗂️ {chunk['document_id']} - Página {chunk['chunk_page']} - Tipo: {chunk['chunk_type']}*")
                            
                            # Colorear según tipo
                            if chunk['chunk_type'] == 'table':
                                st.markdown("**🔢 Contenido de Tabla:**")
                                st.code(chunk['content'], language='markdown')
                            elif chunk['chunk_type'] == 'figure':
                                st.markdown("**🖼️ Descripción de Figura:**")
                                st.info(chunk['content'])
                            else:
                                st.markdown("**📝 Contenido de Texto:**")
                                st.write(chunk['content'])
                            
                            st.divider()
                
            else:
                st.error(f"❌ Error procesando pregunta: {result.get('error', 'Error desconocido')}")
                
        except Exception as e:
            st.error(f"❌ Error inesperado: {str(e)}")

def system_monitoring():
    """Panel de monitoreo del sistema"""
    st.header("📊 Monitoreo del Sistema")
    
    if not st.session_state.rag_engine:
        st.warning("⚠️ Motor RAG no inicializado")
        return
    
    try:
        status = st.session_state.rag_engine.get_system_status()
        
        # Estado general
        st.subheader("🚦 Estado General")
        if status['system_status'] == 'operational':
            st.success("✅ Sistema Operacional")
        else:
            st.error(f"❌ Sistema con Problemas: {status.get('error', 'Error desconocido')}")
        
        # Estadísticas globales
        st.subheader("📈 Estadísticas Globales")
        global_stats = status['global_stats']
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📄 Documentos Procesados", global_stats['documents_processed'])
        with col2:
            st.metric("💬 Consultas Respondidas", global_stats['queries_answered'])
        with col3:
            avg_proc_time = global_stats['total_processing_time'] / max(1, global_stats['documents_processed'])
            st.metric("⏱️ Tiempo Promedio Proc.", f"{avg_proc_time:.2f}s")
        with col4:
            avg_query_time = global_stats['total_query_time'] / max(1, global_stats['queries_answered'])
            st.metric("⏱️ Tiempo Promedio Query", f"{avg_query_time:.3f}s")
        
        # Estado de componentes
        st.subheader("🧩 Estado de Componentes")
        
        components = status['components']
        
        # Docling
        with st.expander("📄 Procesador Docling"):
            docling = components['docling_processor']
            if docling['available']:
                st.success("✅ Disponible")
                st.write(f"👁️ VLM Habilitado: {'Sí' if docling['vlm_enabled'] else 'No'}")
            else:
                st.error("❌ No Disponible")
        
        # Embeddings
        with st.expander("🔍 Motor de Embeddings"):
            embedding = components['embedding_engine']
            st.success(f"✅ Modelo: {embedding['model']}")
            st.write(f"📊 Dimensiones: {embedding['dimensions']}")
            st.write(f"🔢 Total Embeddings: {embedding['total_embeddings']}")
            st.write(f"⏱️ Tiempo Promedio: {embedding['avg_time_per_embedding']}s")
            st.write(f"💾 Cache Hits: {embedding['cache_hits']}")
        
        # Vector Store
        with st.expander("🗄️ Vector Store"):
            vector = components['vector_store']
            if 'error' not in vector:
                st.success(f"✅ Colección: {vector['collection_name']}")
                st.write(f"🎯 Vectores Almacenados: {vector['total_vectors']}")
                st.write(f"📊 Dimensiones: {vector['vector_size']}")
                st.write(f"📏 Métrica: {vector['distance_metric']}")
                st.write(f"📁 Almacenamiento: {vector['storage_path']}")
            else:
                st.error(f"❌ Error: {vector['error']}")
        
        # LLM Interface
        with st.expander("🧠 Interfaz LLM"):
            llm = components['llm_interface']
            st.success(f"✅ Modelo: {llm['model']}")
            st.write(f"💬 Consultas Totales: {llm['total_queries']}")
            st.write(f"✅ Tasa de Éxito: {llm['success_rate']}%")
            st.write(f"🔤 Tokens Promedio: {llm['avg_tokens_per_query']}")
            st.write(f"⏱️ Tiempo Promedio: {llm['avg_time_per_query']}s")
            st.write(f"🌡️ Temperatura: {llm['temperature']}")
        
        # Documentos actuales
        st.subheader("📁 Documentos Cargados")
        current_docs = status['current_documents']
        
        if current_docs['count'] > 0:
            st.write(f"📊 Total: {current_docs['count']} documento(s)")
            for doc_name in current_docs['documents']:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"📄 {doc_name}")
                with col2:
                    if st.button(f"🗑️ Eliminar", key=f"delete_{doc_name}"):
                        if st.session_state.rag_engine.delete_document(doc_name):
                            st.success(f"✅ {doc_name} eliminado")
                            st.rerun()
                        else:
                            st.error(f"❌ Error eliminando {doc_name}")
        else:
            st.info("📭 No hay documentos cargados")
        
        # Historial de conversación
        st.subheader("💭 Estado de Conversación")
        conv_stats = status['conversation']
        st.write(f"📝 Longitud del historial: {conv_stats['history_length']} mensajes")
        st.write(f"🔄 Intercambios: {conv_stats['turns']} turnos")
        
    except Exception as e:
        st.error(f"❌ Error obteniendo estado del sistema: {str(e)}")

def main():
    """Función principal de la aplicación"""
    
    # Header
    display_header()
    
    # Tabs principales
    tab1, tab2, tab3 = st.tabs(["📄 Procesamiento", "💬 Chat RAG", "📊 Monitoreo"])
    
    with tab1:
        document_upload_section()
    
    with tab2:
        chat_interface()
    
    with tab3:
        system_monitoring()
    
    # Footer
    st.divider()
    st.markdown("""
    <div style="text-align: center; color: #666; font-size: 0.9rem;">
        🚀 <strong>RAG Multimodal Demo</strong> | 
        Powered by <strong>Docling</strong> + <strong>EmbeddingGemma</strong> + <strong>Gemma3:27b</strong> + <strong>Qdrant</strong>
        <br>
        🔧 Stack Técnico: SmolDocling VLM • EmbeddingGemma • Gemma3:27b • Qdrant Local • Streamlit
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
```

### **7. Script de Configuración** (`setup.sh`)

```bash
#!/bin/bash

echo "🚀 Configurando Demo RAG Multimodal con Docling"
echo "=============================================="

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Verificar directorio
if [[ ! -d "~/Devs" ]]; then
    echo -e "${YELLOW}Creando directorio ~/Devs...${NC}"
    mkdir -p ~/Devs
fi

# Cambiar al directorio del proyecto
cd ~/Devs/multimodal-RAG || {
    echo -e "${RED}❌ Error: No se pudo acceder al directorio del proyecto${NC}"
    exit 1
}

echo -e "${BLUE}📍 Directorio actual: $(pwd)${NC}"

# ✅ APROVECHAR entorno virtual existente de docling
echo -e "${YELLOW}📦 Configurando entorno virtual optimizado...${NC}"
if [[ -d "~/docling-project/venv" ]]; then
    echo -e "${GREEN}✅ Encontrado entorno docling existente, copiando...${NC}"
    python3 -m venv venv --copies ~/docling-project/venv
else
    echo -e "${YELLOW}⚠️ No se encontró ~/docling-project/venv, creando nuevo entorno...${NC}"
    python3 -m venv venv
fi

source venv/bin/activate

# Verificar Python y dependencias existentes
python_version=$(python --version 2>&1)
echo -e "${GREEN}🐍 Usando: $python_version${NC}"

# Verificar docling existente
if python -c "import docling" 2>/dev/null; then
    docling_version=$(python -c "import docling; print(docling.__version__)")
    echo -e "${GREEN}✅ Docling $docling_version ya disponible${NC}"
else
    echo -e "${YELLOW}📥 Instalando docling...${NC}"
    pip install docling
fi

# Instalar dependencias
echo -e "${YELLOW}📚 Instalando solo dependencias faltantes...${NC}"
pip install --upgrade pip

# Instalar requirements OPTIMIZADOS (solo las faltantes)
cat > requirements_additional.txt << 'EOF'
# Solo dependencias faltantes (docling ya está disponible)
streamlit>=1.32.0
fastapi>=0.100.0
qdrant-client>=1.9.0
ollama>=0.3.0
requests>=2.31.0
python-multipart>=0.0.9
pydantic>=2.8.0
python-dotenv>=1.0.0
pandas>=2.0.0
matplotlib>=3.7.0
plotly>=5.17.0
EOF

pip install -r requirements_additional.txt

# Verificar instalaciones críticas
echo -e "${YELLOW}🔍 Verificando instalaciones...${NC}"
python -c "import docling, streamlit, qdrant_client; print('✅ Dependencias críticas OK')"

# Verificar instalación Ollama (ya debería estar instalado)
echo -e "${YELLOW}🔧 Verificando Ollama...${NC}"
if command -v ollama &> /dev/null; then
    ollama_version=$(ollama --version 2>/dev/null || echo "version not readable")
    echo -e "${GREEN}✅ Ollama encontrado: $ollama_version${NC}"
    
    # Verificar si el servicio está corriendo
    if ! pgrep -f "ollama serve" > /dev/null; then
        echo -e "${YELLOW}🔄 Iniciando servicio Ollama...${NC}"
        ollama serve &
        sleep 2
    fi
    
    echo -e "${YELLOW}📥 Verificando y descargando modelos necesarios...${NC}"
    
    # Verificar si gemma3:27b ya está descargado
    if ollama list | grep -q "gemma3:27b"; then
        echo -e "${GREEN}✅ Gemma3:27b ya disponible${NC}"
    else
        echo -e "${BLUE}📥 Descargando Gemma3:27b (optimizado para M3 Max)...${NC}"
        ollama pull gemma3:27b
    fi
    
    # Verificar si embeddinggemma ya está descargado  
    if ollama list | grep -q "embeddinggemma"; then
        echo -e "${GREEN}✅ EmbeddingGemma ya disponible${NC}"
    else
        echo -e "${BLUE}📥 Descargando EmbeddingGemma...${NC}"
        ollama pull embeddinggemma
    fi
    
    # Verificar modelos
    echo -e "${GREEN}📋 Modelos instalados:${NC}"
    ollama list
else
    echo -e "${RED}❌ Ollama no encontrado${NC}"
    echo -e "${YELLOW}Por favor instala Ollama desde: https://ollama.ai${NC}"
    echo -e "${YELLOW}O verifica que esté en el PATH${NC}"
    exit 1
fi

# Crear estructura de directorios
echo -e "${YELLOW}📁 Creando estructura de directorios...${NC}"
mkdir -p data/{uploads,processed,qdrant_storage}
mkdir -p src interface config scripts

# Crear archivo de configuración
echo -e "${YELLOW}⚙️ Creando configuración...${NC}"
cat > config/settings.py << 'EOF'
"""
Configuración de la aplicación RAG Multimodal
"""
from pathlib import Path

# Rutas del proyecto
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
UPLOADS_DIR = DATA_DIR / "uploads"
PROCESSED_DIR = DATA_DIR / "processed"
VECTOR_STORE_DIR = DATA_DIR / "qdrant_storage"

# Configuración de modelos
MODELS_CONFIG = {
    "embedding_model": "embeddinggemma",
    "llm_model": "gemma3:27b",
    "use_vlm": True,
    "collection_name": "docling_documents"
}

# Configuración de la aplicación
APP_CONFIG = {
    "title": "RAG Multimodal Demo - Docling",
    "description": "Demo de RAG multimodal con Docling + EmbeddingGemma + Gemma3:27b",
    "version": "1.0.0"
}

# Límites y configuración
PROCESSING_CONFIG = {
    "max_file_size_mb": 100,
    "batch_size": 32,
    "chunk_size": 512,
    "top_k_default": 5,
    "score_threshold_default": 0.5
}
EOF

# Crear script de prueba
echo -e "${YELLOW}🧪 Creando script de prueba...${NC}"
cat > scripts/test_setup.py << 'EOF'
#!/usr/bin/env python3
"""
Script de prueba para verificar la instalación
"""
import sys
import logging
from pathlib import Path

# Añadir path del proyecto
sys.path.insert(0, str(Path(__file__).parent.parent))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_imports():
    """Prueba las importaciones principales"""
    try:
        import docling
        logger.info("✅ Docling importado")
        
        import qdrant_client
        logger.info("✅ Qdrant client importado")
        
        import ollama
        logger.info("✅ Ollama client importado")
        
        import streamlit
        logger.info("✅ Streamlit importado")
        
        return True
        
    except ImportError as e:
        logger.error(f"❌ Error de importación: {e}")
        return False

def test_ollama_models():
    """Prueba la disponibilidad de modelos Ollama"""
    try:
        import ollama
        
        models = ollama.list()
        model_names = [model['name'] for model in models['models']]
        
        logger.info(f"📋 Modelos disponibles: {model_names}")
        
        # Verificar modelos requeridos
        required_models = ['gemma3:27b', 'embeddinggemma']
        missing_models = []
        
        for model in required_models:
            if model not in model_names and f"{model}:latest" not in model_names:
                missing_models.append(model)
        
        if missing_models:
            logger.warning(f"⚠️ Modelos faltantes: {missing_models}")
            return False
        else:
            logger.info("✅ Todos los modelos requeridos están disponibles")
            return True
            
    except Exception as e:
        logger.error(f"❌ Error verificando modelos: {e}")
        return False

def test_rag_engine():
    """Prueba la inicialización del motor RAG"""
    try:
        from src.rag_engine import create_rag_engine
        
        logger.info("🔄 Inicializando motor RAG...")
        engine = create_rag_engine()
        
        # Obtener estado
        status = engine.get_system_status()
        
        if status['system_status'] == 'operational':
            logger.info("✅ Motor RAG inicializado correctamente")
            return True
        else:
            logger.error(f"❌ Motor RAG con problemas: {status}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error inicializando motor RAG: {e}")
        return False

def main():
    """Ejecuta todas las pruebas"""
    logger.info("🧪 Iniciando pruebas de instalación...")
    
    tests = [
        ("Importaciones", test_imports),
        ("Modelos Ollama", test_ollama_models),
        ("Motor RAG", test_rag_engine)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        logger.info(f"\n📋 Ejecutando prueba: {test_name}")
        
        if test_func():
            passed += 1
            logger.info(f"✅ {test_name}: PASÓ")
        else:
            logger.error(f"❌ {test_name}: FALLÓ")
    
    logger.info(f"\n📊 Resultados: {passed}/{total} pruebas pasaron")
    
    if passed == total:
        logger.info("🎉 ¡Instalación completada exitosamente!")
        logger.info("🚀 Ejecuta: streamlit run interface/streamlit_app.py")
    else:
        logger.error("⚠️ Algunas pruebas fallaron. Revisa la configuración.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
EOF

# Hacer ejecutable el script de prueba
chmod +x scripts/test_setup.py

# Crear launcher para demo
echo -e "${YELLOW}🎬 Creando launcher de demo...${NC}"
cat > run_demo.py << 'EOF'
#!/usr/bin/env python3
"""
Launcher para la demo RAG Multimodal
"""
import subprocess
import sys
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Ejecuta la demo"""
    
    # Verificar que estamos en el directorio correcto
    if not Path("interface/streamlit_app.py").exists():
        logger.error("❌ No se encuentra interface/streamlit_app.py")
        logger.error("Asegúrate de ejecutar este script desde el directorio del proyecto")
        return 1
    
    # Verificar entorno virtual
    if not Path("venv").exists():
        logger.error("❌ Entorno virtual no encontrado")
        logger.error("Ejecuta: source venv/bin/activate")
        return 1
    
    logger.info("🚀 Lanzando demo RAG Multimodal...")
    logger.info("🌐 La aplicación se abrirá en http://localhost:8501")
    
    try:
        # Ejecutar Streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run",
            "interface/streamlit_app.py",
            "--server.address", "0.0.0.0",
            "--server.port", "8501",
            "--server.headless", "false"
        ], check=True)
        
    except KeyboardInterrupt:
        logger.info("🛑 Demo detenida por el usuario")
        return 0
        
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Error ejecutando Streamlit: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
EOF

chmod +x run_demo.py

# Ejecutar pruebas
echo -e "${YELLOW}🧪 Ejecutando pruebas de verificación...${NC}"
python scripts/test_setup.py

# Resumen final
echo -e "${GREEN}"
echo "=============================================="
echo "🎉 ¡Instalación Completada!"
echo "=============================================="
echo -e "${NC}"

echo -e "${BLUE}📋 Para ejecutar la demo:${NC}"
echo -e "${YELLOW}1. Activa el entorno virtual:${NC} source venv/bin/activate"
echo -e "${YELLOW}2. Ejecuta la demo:${NC} python run_demo.py"
echo -e "${YELLOW}3. O directamente:${NC} streamlit run interface/streamlit_app.py"

echo -e "\n${BLUE}🎯 Funcionalidades disponibles:${NC}"
echo "• 📄 Procesamiento multimodal de documentos (PDF, imágenes, Word, etc.)"
echo "• 👁️ SmolDocling VLM para análisis visual"
echo "• 🔍 EmbeddingGemma para búsqueda semántica"
echo "• 🧠 Gemma3:27b para respuestas inteligentes"
echo "• 💬 Interfaz de chat interactiva"
echo "• 📊 Monitoreo del sistema en tiempo real"

echo -e "\n${GREEN}🚀 ¡Demo lista para usar!${NC}"
```

---

## 🚀 **INSTRUCCIONES DE USO RÁPIDO**

### **Instalación Optimizada (10 minutos)**
```bash
# 1. Crear proyecto aprovechando infraestructura existente
mkdir -p ~/Devs/multimodal-RAG
cd ~/Devs/multimodal-RAG

# 2. ✅ CLAVE: Copiar entorno virtual con docling funcionando
python3 -m venv venv --copies ~/docling-project/venv
source venv/bin/activate

# 3. Instalar solo dependencias faltantes
pip install streamlit qdrant-client ollama python-dotenv pandas plotly

# 4. Activar Ollama y descargar modelos
ollama serve &
ollama pull gemma3:27b embeddinggemma

# 5. Ejecutar setup optimizado
chmod +x setup.sh
./setup.sh

# 6. Lanzar demo
python run_demo.py
```

### **Uso de la Demo**
1. **📄 Subir documentos**: PDFs, imágenes, Word, PowerPoint
2. **🔄 Procesar automáticamente** con Docling + SmolDocling VLM
3. **💬 Hacer preguntas** en español sobre el contenido
4. **📊 Ver métricas** de rendimiento en tiempo real

### **Características Únicas**
- ✅ **Stack Google completo** (Gemma3 + EmbeddingGemma)
- ✅ **Multimodal real** (texto + imágenes + tablas)
- ✅ **Español nativo** optimizado
- ✅ **SmolDocling VLM** local y rápido
- ✅ **Qdrant local** sin dependencias externas
- ✅ **M3 Max optimizado** para máximo rendimiento

---

¡Demo RAG multimodal **lista para implementar en 1 hora** con la mejor configuración técnica disponible! 🎯