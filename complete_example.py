#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de ejemplo completo para usar RAG-Anything
Basado en los ejemplos del repositorio oficial
"""

import asyncio
import os

async def main():
    print("[INICIO] Configurando RAG-Anything...")
    
    # Directorio base del proyecto
    base_dir = "C:\\Users\\Gamer\\Dev\\RAG-Anything"
    
    # Crear directorios necesarios si no existen
    directories = [
        os.path.join(base_dir, "data", "documents"),
        os.path.join(base_dir, "data", "output"),
        os.path.join(base_dir, "rag_storage")
    ]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"[CREADO] Directorio: {directory}")
    
    try:
        # Importar RAG-Anything después de configurar el entorno
        from raganything import RAGAnything, RAGAnythingConfig
        
        # Configuración de RAG-Anything
        config = RAGAnythingConfig(
            working_dir=os.path.join(base_dir, "rag_storage"),
            parser="mineru",
            parse_method="auto",
            enable_image_processing=True,
            enable_table_processing=True,
            enable_equation_processing=True,
        )
        
        # Inicializar RAG-Anything (versión básica sin LLM)
        rag = RAGAnything(config=config)
        print("[OK] RAG-Anything inicializado correctamente")
        
        # Mostrar información de configuración
        print("\n[CONFIGURACION]")
        print(f"  Directorio de trabajo: {config.working_dir}")
        print(f"  Parser: {config.parser}")
        print(f"  Método de parsing: {config.parse_method}")
        print(f"  Procesamiento de imágenes: {config.enable_image_processing}")
        print(f"  Procesamiento de tablas: {config.enable_table_processing}")
        print(f"  Procesamiento de ecuaciones: {config.enable_equation_processing}")
        
        # Verificar componentes instalados
        print("\n[COMPONENTES]")
        try:
            from raganything import RAGAnything
            print("[OK] RAG-Anything: Instalado")
        except Exception as e:
            print(f"[ERROR] RAG-Anything: {e}")
        
        try:
            import mineru
            print("[OK] MinerU: Instalado")
        except Exception as e:
            print(f"[ERROR] MinerU: {e}")
        
        # Verificar directorios
        print("\n[DIRECTORIOS]")
        for directory in directories:
            if os.path.exists(directory):
                print(f"[OK] {directory}")
            else:
                print(f"[ERROR] {directory}")
        
        print("\n[INSTRUCCIONES]")
        print("Para procesar documentos, coloque sus archivos en:")
        print(f"  {os.path.join(base_dir, 'data', 'documents')}")
        print("\nLos resultados se guardarán en:")
        print(f"  {os.path.join(base_dir, 'data', 'output')}")
        print("\nLa base de conocimiento se almacenará en:")
        print(f"  {os.path.join(base_dir, 'rag_storage')}")
        
        print("\n[EJEMPLO DE USO]")
        print("# Para procesar un documento PDF:")
        print("# await rag.process_document_complete(")
        print('#     file_path="ruta/al/documento.pdf",')
        print('#     output_dir="./data/output",')
        print('#     parse_method="auto"')
        print("# )")
        
        print("\n[FINALIZADO] RAG-Anything está listo para usar")
        
    except Exception as e:
        print(f"[ERROR] No se pudo inicializar RAG-Anything: {e}")
        print("Verifique que todas las dependencias estén instaladas correctamente.")

if __name__ == "__main__":
    asyncio.run(main())
