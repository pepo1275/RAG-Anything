#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de resumen del estado del proyecto RAG-Anything
"""

import os
import sys
import subprocess

def check_project_status():
    print("=" * 60)
    print("           RESUMEN DEL PROYECTO RAG-ANYTHING")
    print("=" * 60)
    
    # Directorio base del proyecto
    base_dir = "C:\\Users\\Gamer\\Dev\\RAG-Anything"
    
    print(f"Directorio del proyecto: {base_dir}")
    print()
    
    # Verificar componentes instalados
    print("COMPONENTES INSTALADOS:")
    print("-" * 30)
    
    # Verificar RAG-Anything
    try:
        from raganything import RAGAnything
        print("[OK] RAG-Anything: Instalado")
    except ImportError:
        print("[ERROR] RAG-Anything: No instalado")
    
    # Verificar MinerU
    try:
        import mineru
        print("[OK] MinerU: Instalado")
    except ImportError:
        print("[ERROR] MinerU: No instalado")
    
    # Verificar LibreOffice
    try:
        # Primero intentar con el PATH
        result = subprocess.run(["soffice", "--version"], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            version = result.stdout.strip().split('\n')[0]
            print(f"[OK] LibreOffice: {version}")
        else:
            # Intentar con la ruta directa
            result = subprocess.run(["C:\\Program Files\\LibreOffice\\program\\soffice.exe", "--version"], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                version = result.stdout.strip().split('\n')[0]
                print(f"[OK] LibreOffice: {version}")
            else:
                print("[ERROR] LibreOffice: No accesible")
    except (FileNotFoundError, subprocess.TimeoutExpired):
        # Intentar con la ruta directa
        try:
            result = subprocess.run(["C:\\Program Files\\LibreOffice\\program\\soffice.exe", "--version"], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                version = result.stdout.strip().split('\n')[0]
                print(f"[OK] LibreOffice: {version}")
            else:
                print("[ERROR] LibreOffice: No accesible")
        except:
            print("[ERROR] LibreOffice: No encontrado")
    
    # Verificar Python
    print(f"[OK] Python: {sys.version.split()[0]}")
    
    print()
    
    # Verificar directorios
    print("DIRECTORIOS:")
    print("-" * 30)
    
    directories = {
        "Proyecto": base_dir,
        "Documentos": os.path.join(base_dir, "data", "documents"),
        "Resultados": os.path.join(base_dir, "data", "output"),
        "Base de conocimiento": os.path.join(base_dir, "rag_storage"),
        "Entorno virtual": os.path.join(base_dir, "rag_anything_env")
    }
    
    for name, path in directories.items():
        if os.path.exists(path):
            # Contar archivos en el directorio
            if os.path.isdir(path):
                try:
                    file_count = len([f for f in os.listdir(path) if not f.startswith('.')])
                    print(f"[OK] {name}: {path} ({file_count} elementos)")
                except:
                    print(f"[OK] {name}: {path} (accesible)")
            else:
                print(f"[OK] {name}: {path}")
        else:
            print(f"[ERROR] {name}: {path} (NO EXISTE)")
    
    print()
    
    # Verificar documentos
    documents_dir = os.path.join(base_dir, "data", "documents")
    if os.path.exists(documents_dir):
        documents = [f for f in os.listdir(documents_dir) 
                    if f.lower().endswith(('.pdf', '.docx', '.txt', '.md'))]
        print(f"DOCUMENTOS ENCONTRADOS: {len(documents)}")
        print("-" * 30)
        if documents:
            for doc in documents[:5]:  # Mostrar solo los primeros 5
                print(f"  - {doc}")
            if len(documents) > 5:
                print(f"  ... y {len(documents) - 5} mas")
        else:
            print("  No se encontraron documentos")
    else:
        print("[ERROR] Directorio de documentos no encontrado")
    
    print()
    
    # Scripts disponibles
    print("SCRIPTS DISPONIBLES:")
    print("-" * 30)
    
    scripts = {
        "complete_example.py": "Ejemplo completo de configuracion",
        "document_processing_example.py": "Ejemplo de procesamiento de documentos",
        "example_script.py": "Script de ejemplo basico"
    }
    
    for script, description in scripts.items():
        script_path = os.path.join(base_dir, script)
        if os.path.exists(script_path):
            print(f"[OK] {script}: {description}")
        else:
            print(f"[ERROR] {script}: No encontrado")
    
    print()
    print("=" * 60)
    print("¡RAG-Anything esta listo para usar!")
    print("Coloque sus documentos en la carpeta 'data/documents' y ejecute")
    print("los scripts de ejemplo para comenzar a procesarlos.")
    print("=" * 60)

if __name__ == "__main__":
    check_project_status()
