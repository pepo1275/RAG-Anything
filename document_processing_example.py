#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ejemplo de procesamiento de documento con RAG-Anything
"""

import asyncio
import os
from raganything import RAGAnything, RAGAnythingConfig

async def process_sample_document():
    print("[INICIO] Procesamiento de documento de ejemplo...")
    
    # Directorio base del proyecto
    base_dir = "C:\\Users\\Gamer\\Dev\\RAG-Anything"
    
    # Configuración de RAG-Anything
    config = RAGAnythingConfig(
        working_dir=os.path.join(base_dir, "rag_storage"),
        parser="mineru",
        parse_method="auto",
        enable_image_processing=True,
        enable_table_processing=True,
        enable_equation_processing=True,
    )
    
    try:
        # Inicializar RAG-Anything
        rag = RAGAnything(config=config)
        print("[OK] RAG-Anything inicializado")
        
        # Verificar si hay documentos para procesar
        documents_dir = os.path.join(base_dir, "data", "documents")
        documents = [f for f in os.listdir(documents_dir) if f.lower().endswith(('.pdf', '.docx', '.txt', '.md'))]
        
        if documents:
            print(f"[ENCONTRADOS] {len(documents)} documento(s) para procesar:")
            for doc in documents:
                print(f"  - {doc}")
            
            # Procesar el primer documento encontrado
            first_doc = os.path.join(documents_dir, documents[0])
            output_dir = os.path.join(base_dir, "data", "output")
            
            print(f"\n[PROCESANDO] {documents[0]}...")
            print(f"  Ruta del documento: {first_doc}")
            print(f"  Directorio de salida: {output_dir}")
            
            # Aquí normalmente procesaríamos el documento, pero lo dejamos comentado
            # ya que requiere un documento real y posiblemente una API key
            print("\n[NOTA] El procesamiento real requiere:")
            print("  1. Un documento real en la carpeta de documentos")
            print("  2. Configuración de API key para LLM (opcional)")
            print("  3. Configuración de funciones LLM (opcional)")
            
            # Ejemplo de cómo se haría el procesamiento real:
            print("\n[EJEMPLO DE CÓDIGO PARA PROCESAMIENTO REAL]")
            print("# await rag.process_document_complete(")
            print(f'#     file_path="{first_doc}",')
            print(f'#     output_dir="{output_dir}",')
            print('#     parse_method="auto"')
            print("# )")
        else:
            print("[INFO] No se encontraron documentos para procesar")
            print("[INSTRUCCIONES] Coloque documentos PDF, DOCX, TXT o MD en:")
            print(f"  {documents_dir}")
            
        print("\n[FINALIZADO] Ejemplo de procesamiento completado")
        
    except Exception as e:
        print(f"[ERROR] {e}")

if __name__ == "__main__":
    asyncio.run(process_sample_document())
