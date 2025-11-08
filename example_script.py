#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de ejemplo para usar RAG-Anything
"""

import asyncio
import os

async def main():
    # Importar RAG-Anything después de configurar el entorno
    from raganything import RAGAnything, RAGAnythingConfig
    
    # Configuración de RAG-Anything
    config = RAGAnythingConfig(
        working_dir="./rag_storage",
        parser="mineru",
        parse_method="auto",
        enable_image_processing=True,
        enable_table_processing=True,
        enable_equation_processing=True,
    )
    
    # Inicializar RAG-Anything (sin funciones LLM por ahora)
    rag = RAGAnything(config=config)
    
    print("[OK] RAG-Anything inicializado correctamente")
    print("Los directorios estan configurados:")
    print(f"  - Documentos: {os.path.abspath('./data/documents')}")
    print(f"  - Resultados: {os.path.abspath('./data/output')}")
    print(f"  - Base de conocimiento: {os.path.abspath('./rag_storage')}")
    
    # Verificar instalación de componentes
    try:
        from raganything import RAGAnything
        print("[OK] RAG-Anything: OK")
    except Exception as e:
        print(f"[ERROR] RAG-Anything: {e}")
    
    try:
        import mineru
        print("[OK] MinerU: OK")
    except Exception as e:
        print(f"[ERROR] MinerU: {e}")
    
    # Verificar directorios
    dirs_to_check = ['./data/documents', './data/output', './rag_storage']
    for dir_path in dirs_to_check:
        if os.path.exists(dir_path):
            print(f"[OK] Directorio {dir_path}: OK")
        else:
            print(f"[ERROR] Directorio {dir_path}: No encontrado")

if __name__ == "__main__":
    asyncio.run(main())
