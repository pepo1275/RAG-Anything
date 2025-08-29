# RAG-Anything - Implementación Local

Este proyecto implementa RAG-Anything en un entorno local de Windows, configurado específicamente para el equipo del usuario.

## 📋 Estructura del Proyecto

```
C:\Users\Gamer\Dev\RAG-Anything\
├── data\
│   ├── documents\          # Documentos para procesar
│   └── output\            # Resultados del procesamiento
├── rag_storage\           # Base de conocimiento de RAG
├── rag_anything_env\      # Entorno virtual de Python
├── examples\              # Ejemplos del repositorio original
├── raganything\           # Código fuente de RAG-Anything
└── Scripts\
    ├── complete_example.py           # Ejemplo completo de configuración
    ├── document_processing_example.py # Ejemplo de procesamiento de documentos
    └── example_script.py             # Script de ejemplo básico
```

## 🚀 Configuración Inicial

El entorno ya ha sido configurado con:

- Python 3.13.5
- RAG-Anything instalado con todas las dependencias (`[all]`)
- LibreOffice 25.8.0.4 instalado para procesamiento de documentos Office
- Entorno virtual activo en `rag_anything_env`
- Directorios necesarios creados

## 📁 Directorios Importantes

- **Documentos**: `C:\Users\Gamer\Dev\RAG-Anything\data\documents\`
- **Resultados**: `C:\Users\Gamer\Dev\RAG-Anything\data\output\`
- **Base de conocimiento**: `C:\Users\Gamer\Dev\RAG-Anything\rag_storage\`

## ▶️ Ejecutar Ejemplos

### Ejemplo Completo de Configuración
```bash
python complete_example.py
```

### Ejemplo de Procesamiento de Documentos
```bash
python document_processing_example.py
```

## 📄 Procesamiento de Documentos

Para procesar documentos:

1. Coloque sus archivos en `data\documents\`
2. Formatos soportados: PDF, DOCX, TXT, MD
3. Ejecute el script de procesamiento

### Ejemplo de Código para Procesamiento
```python
import asyncio
from raganything import RAGAnything, RAGAnythingConfig

async def process_document():
    config = RAGAnythingConfig(
        working_dir="./rag_storage",
        parser="mineru",
        parse_method="auto",
        enable_image_processing=True,
        enable_table_processing=True,
        enable_equation_processing=True,
    )
    
    rag = RAGAnything(config=config)
    
    await rag.process_document_complete(
        file_path="ruta/al/documento.pdf",
        output_dir="./data/output",
        parse_method="auto"
    )

asyncio.run(process_document())
```

## ⚙️ Componentes Instalados

- **RAG-Anything**: ✅ Instalado
- **MinerU**: ✅ Instalado
- **LibreOffice**: ✅ Instalado (versión 25.8.0.4)
- **Python**: ✅ Versión 3.13.5

## 🎯 Características Habilitadas

- ✅ Procesamiento de texto
- ✅ Procesamiento de imágenes
- ✅ Procesamiento de tablas
- ✅ Procesamiento de ecuaciones matemáticas
- ✅ Soporte para documentos PDF
- ✅ Soporte para documentos Office (DOCX, PPTX, XLSX)
- ✅ Soporte para archivos de texto (TXT, MD)

## 📞 Soporte

Para cualquier problema con la implementación, verifique:

1. Que el entorno virtual esté activo
2. Que todas las dependencias estén instaladas
3. Que LibreOffice esté correctamente instalado
4. Que los directorios existan y tengan permisos adecuados
