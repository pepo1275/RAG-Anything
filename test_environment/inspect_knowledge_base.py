#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Knowledge Base Inspector
Inspecciona el contenido de la Knowledge Base de LightRAG
"""

import json
from pathlib import Path
from datetime import datetime

def inspect_kb(storage_path: str = "test_environment/rag_storage"):
    """Inspecciona el contenido de la Knowledge Base"""

    storage_dir = Path(storage_path)

    print("=" * 70)
    print("KNOWLEDGE BASE INSPECTION")
    print("=" * 70)
    print(f"Storage: {storage_dir.absolute()}\n")

    # 1. Build Stats
    print("[BUILD STATISTICS]")
    print("-" * 70)
    build_stats_file = storage_dir / "build_stats.json"
    if build_stats_file.exists():
        with open(build_stats_file, 'r', encoding='utf-8') as f:
            stats = json.load(f)

        timestamp = datetime.fromtimestamp(stats.get('timestamp', 0))
        print(f"  Build Date: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"  Source File: {stats.get('source_file', 'N/A')}")
        print(f"  Build Method: {stats.get('build_method', 'N/A')}")
        print(f"  Build Time: {stats.get('build_time_seconds', 0):.2f}s")
        print(f"  Content Elements: {stats.get('content_elements', 0)}")
        print(f"  Words Processed: {stats.get('words_processed', 0)}")
        print(f"  Total Size: {stats.get('total_size_mb', 0):.2f} MB")
        print(f"  Success: {stats.get('success', False)}")
    else:
        print("  [WARNING] build_stats.json not found")

    # 2. Documents
    print("\n[DOCUMENTS]")
    print("-" * 70)
    doc_status_file = storage_dir / "kv_store_doc_status.json"
    if doc_status_file.exists():
        with open(doc_status_file, 'r', encoding='utf-8') as f:
            docs = json.load(f)

        print(f"  Total Documents: {len(docs)}")
        for doc_id, doc_info in docs.items():
            print(f"\n  Document ID: {doc_id}")
            print(f"    Status: {doc_info.get('status', 'N/A')}")
            print(f"    Chunks: {doc_info.get('chunks_count', 0)}")
            print(f"    Content Length: {doc_info.get('content_length', 0)} chars")
            print(f"    Created: {doc_info.get('created_at', 'N/A')}")
            print(f"    Updated: {doc_info.get('updated_at', 'N/A')}")
            print(f"    File Path: {doc_info.get('file_path', 'N/A')}")
            print(f"    Multimodal: {doc_info.get('multimodal_processed', False)}")

            # Show summary preview
            summary = doc_info.get('content_summary', '')
            if summary:
                preview = summary[:200] + "..." if len(summary) > 200 else summary
                print(f"    Summary: {preview}")
    else:
        print("  [WARNING] kv_store_doc_status.json not found")

    # 3. Entities
    print("\n[ENTITIES]")
    print("-" * 70)
    entities_file = storage_dir / "kv_store_full_entities.json"
    if entities_file.exists():
        with open(entities_file, 'r', encoding='utf-8') as f:
            entities_data = json.load(f)

        total_entities = sum(len(doc_entities.get('entity_names', []))
                           for doc_entities in entities_data.values())

        print(f"  Total Entities: {total_entities}")
        print(f"  Documents with Entities: {len(entities_data)}")

        # Show sample entities from first document
        if entities_data:
            first_doc_id = list(entities_data.keys())[0]
            first_doc_entities = entities_data[first_doc_id].get('entity_names', [])
            print(f"\n  Sample Entities (from {first_doc_id}):")
            for i, entity in enumerate(first_doc_entities[:10], 1):
                print(f"    {i}. {entity}")
            if len(first_doc_entities) > 10:
                print(f"    ... and {len(first_doc_entities) - 10} more")
    else:
        print("  [WARNING] kv_store_full_entities.json not found")

    # 4. Relations
    print("\n[RELATIONSHIPS]")
    print("-" * 70)
    relations_file = storage_dir / "kv_store_full_relations.json"
    if relations_file.exists():
        with open(relations_file, 'r', encoding='utf-8') as f:
            relations_data = json.load(f)

        total_relations = sum(len(doc_relations.get('relationships', []))
                            for doc_relations in relations_data.values())

        print(f"  Total Relationships: {total_relations}")
        print(f"  Documents with Relationships: {len(relations_data)}")

        # Show sample relationships
        if relations_data:
            first_doc_id = list(relations_data.keys())[0]
            first_doc_rels = relations_data[first_doc_id].get('relationships', [])
            print(f"\n  Sample Relationships (from {first_doc_id}):")
            for i, rel in enumerate(first_doc_rels[:5], 1):
                src = rel.get('src_id', 'Unknown')
                tgt = rel.get('tgt_id', 'Unknown')
                desc = rel.get('description', 'No description')
                print(f"    {i}. {src} → {tgt}")
                print(f"       {desc[:100]}{'...' if len(desc) > 100 else ''}")
            if len(first_doc_rels) > 5:
                print(f"    ... and {len(first_doc_rels) - 5} more")
    else:
        print("  [WARNING] kv_store_full_relations.json not found")

    # 5. Text Chunks
    print("\n[TEXT CHUNKS]")
    print("-" * 70)
    chunks_file = storage_dir / "kv_store_text_chunks.json"
    if chunks_file.exists():
        with open(chunks_file, 'r', encoding='utf-8') as f:
            chunks_data = json.load(f)

        print(f"  Total Chunks: {len(chunks_data)}")

        # Show sample chunk
        if chunks_data:
            first_chunk_id = list(chunks_data.keys())[0]
            first_chunk = chunks_data[first_chunk_id]
            print(f"\n  Sample Chunk ({first_chunk_id}):")
            content = first_chunk.get('content', '')
            preview = content[:200] + "..." if len(content) > 200 else content
            print(f"    Content: {preview}")
            print(f"    Token Count: {first_chunk.get('tokens', 0)}")
    else:
        print("  [WARNING] kv_store_text_chunks.json not found")

    # 6. Graph
    print("\n[KNOWLEDGE GRAPH]")
    print("-" * 70)
    graph_file = storage_dir / "graph_chunk_entity_relation.graphml"
    if graph_file.exists():
        graph_size = graph_file.stat().st_size / 1024
        print(f"  Graph File: graph_chunk_entity_relation.graphml")
        print(f"  Graph Size: {graph_size:.2f} KB")
        print(f"  Format: GraphML (can be opened with Gephi, Cytoscape, etc.)")
    else:
        print("  [WARNING] graph_chunk_entity_relation.graphml not found")

    # 7. Storage Files Summary
    print("\n[STORAGE FILES]")
    print("-" * 70)
    files = list(storage_dir.glob("*"))
    total_size = sum(f.stat().st_size for f in files if f.is_file()) / (1024 * 1024)

    print(f"  Total Files: {len(files)}")
    print(f"  Total Size: {total_size:.2f} MB")
    print("\n  Files:")
    for file in sorted(files):
        if file.is_file():
            size_kb = file.stat().st_size / 1024
            print(f"    - {file.name:<40} {size_kb:>10.2f} KB")

    print("\n" + "=" * 70)
    print("INSPECTION COMPLETE")
    print("=" * 70)

if __name__ == "__main__":
    inspect_kb()
