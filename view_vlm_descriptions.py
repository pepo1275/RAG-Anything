#!/usr/bin/env python3
"""
Script para visualizar las descripciones VLM generadas en formato legible
"""

import json
from pathlib import Path


def view_vlm_descriptions(rag_storage_path: str):
    """
    Lee y muestra las descripciones VLM de imágenes generadas

    Args:
        rag_storage_path: Ruta al directorio rag_storage
    """
    chunks_file = Path(rag_storage_path) / "kv_store_text_chunks.json"

    if not chunks_file.exists():
        print(f"❌ No se encontró el archivo: {chunks_file}")
        return

    # Leer chunks
    with open(chunks_file, 'r', encoding='utf-8') as f:
        chunks_data = json.load(f)

    # Filtrar solo chunks de imágenes (multimodales)
    image_chunks = {
        chunk_id: chunk_data
        for chunk_id, chunk_data in chunks_data.items()
        if chunk_data.get("is_multimodal", False) and chunk_data.get("original_type") == "image"
    }

    print(f"\n{'='*80}")
    print(f"📊 DESCRIPCIONES VLM GENERADAS")
    print(f"{'='*80}\n")
    print(f"Total de imágenes procesadas: {len(image_chunks)}\n")

    # Mostrar cada descripción
    for idx, (chunk_id, chunk_data) in enumerate(sorted(image_chunks.items(), key=lambda x: x[1].get("chunk_order_index", 0)), start=1):
        # Extraer path de la imagen del content
        content = chunk_data.get("content", "")
        lines = content.split("\n")

        image_path = "N/A"
        visual_analysis = ""

        # Parsear el content
        for i, line in enumerate(lines):
            if line.startswith("Image Path:"):
                image_path = line.replace("Image Path:", "").strip()
            if line.startswith("Visual Analysis:"):
                # Todo lo que sigue es la descripción VLM
                visual_analysis = "\n".join(lines[i+1:]).strip()
                break

        # Metadata
        entity_name = chunk_data.get("modal_entity_name", "N/A")
        tokens = chunk_data.get("tokens", 0)
        page_idx = chunk_data.get("page_idx", "N/A")

        print(f"\n{'─'*80}")
        print(f"🖼️  IMAGEN #{idx}")
        print(f"{'─'*80}")
        print(f"Chunk ID: {chunk_id}")
        print(f"Image Path: {Path(image_path).name}")
        print(f"Entity Name: {entity_name}")
        print(f"Page Index: {page_idx}")
        print(f"Tokens: {tokens}")
        print(f"\n📝 VISUAL ANALYSIS (VLM Description):\n")
        print(visual_analysis)
        print(f"\n{'─'*80}\n")

    print(f"\n{'='*80}")
    print(f"✅ Total: {len(image_chunks)} descripciones VLM generadas")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python view_vlm_descriptions.py <rag_storage_path>")
        print("\nExample:")
        print("  python view_vlm_descriptions.py test_environment/output/vlm_dedup_validation_2025-10-16_14-43-55/rag_storage")
        sys.exit(1)

    rag_storage_path = sys.argv[1]
    view_vlm_descriptions(rag_storage_path)
