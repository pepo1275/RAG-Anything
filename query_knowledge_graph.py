#!/usr/bin/env python3
"""
Script interactivo para hacer queries al Knowledge Graph generado por RAGAnything

Este script permite:
1. Cargar un Knowledge Graph existente desde rag_storage
2. Hacer queries interactivas en distintos modos
3. Ver resultados formateados
"""

import os
import sys
import asyncio
import argparse
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path=".env", override=False)

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

from lightrag.llm.openai import openai_complete_if_cache, openai_embed
from lightrag.utils import EmbeddingFunc, logger
from raganything import RAGAnything, RAGAnythingConfig


def print_banner():
    """Print welcome banner"""
    print("\n" + "="*80)
    print("   RAGANYTHING KNOWLEDGE GRAPH QUERY INTERFACE")
    print("="*80)
    print()


def print_help():
    """Print help information"""
    print("\n📖 COMANDOS DISPONIBLES:")
    print("  /help              - Mostrar esta ayuda")
    print("  /mode <mode>       - Cambiar modo de query (local, global, hybrid, mix, naive)")
    print("  /vlm <on|off>      - Activar/desactivar VLM enhanced queries")
    print("  /info              - Mostrar información del Knowledge Graph")
    print("  /exit, /quit       - Salir")
    print("\n🔍 MODOS DE QUERY:")
    print("  local    - Busca en chunks locales (rápido, preciso)")
    print("  global   - Busca en el grafo global (panorámica)")
    print("  hybrid   - Combina local + global (recomendado)")
    print("  mix      - Mezcla múltiples estrategias (más completo)")
    print("  naive    - Búsqueda simple sin grafo")
    print("\n💡 EJEMPLOS DE QUERIES:")
    print("  What is the main topic of the document?")
    print("  Explain the architecture shown in the images")
    print("  List all the key entities and relationships")
    print()


async def initialize_rag(working_dir: str, api_key: str, base_url: str = None) -> RAGAnything:
    """
    Initialize RAGAnything from existing storage

    Args:
        working_dir: Path to rag_storage directory
        api_key: OpenAI API key
        base_url: Optional API base URL

    Returns:
        RAGAnything: Initialized RAG instance
    """
    print(f"📂 Loading Knowledge Graph from: {working_dir}")

    # Verify rag_storage exists
    if not Path(working_dir).exists():
        raise FileNotFoundError(f"❌ RAG storage not found at: {working_dir}")

    # Check for required files
    required_files = ["kv_store_doc_status.json", "vdb_chunks.json"]
    for file in required_files:
        file_path = Path(working_dir) / file
        if not file_path.exists():
            raise FileNotFoundError(f"❌ Required file missing: {file}")

    print("✅ RAG storage validated")

    # Create config pointing to existing storage
    config = RAGAnythingConfig(
        working_dir=working_dir,
        parser="docling",  # Doesn't matter for query-only
        parse_method="auto",
        enable_image_processing=True,
        enable_table_processing=True,
        enable_equation_processing=True,
    )

    # Define LLM model function
    def llm_model_func(prompt, system_prompt=None, history_messages=[], **kwargs):
        return openai_complete_if_cache(
            "gpt-4o-mini",
            prompt,
            system_prompt=system_prompt,
            history_messages=history_messages,
            api_key=api_key,
            base_url=base_url,
            **kwargs,
        )

    # Define vision model function for VLM enhanced queries
    def vision_model_func(
        prompt,
        system_prompt=None,
        history_messages=[],
        image_data=None,
        messages=None,
        **kwargs,
    ):
        # If messages format is provided (for multimodal VLM enhanced query), use it directly
        if messages:
            return openai_complete_if_cache(
                "gpt-4o",
                "",
                system_prompt=None,
                history_messages=[],
                messages=messages,
                api_key=api_key,
                base_url=base_url,
                **kwargs,
            )
        # Traditional single image format
        elif image_data:
            return openai_complete_if_cache(
                "gpt-4o",
                "",
                system_prompt=None,
                history_messages=[],
                messages=[
                    {"role": "system", "content": system_prompt} if system_prompt else None,
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/jpeg;base64,{image_data}"},
                            },
                        ],
                    } if image_data else {"role": "user", "content": prompt},
                ],
                api_key=api_key,
                base_url=base_url,
                **kwargs,
            )
        # Pure text format
        else:
            return llm_model_func(prompt, system_prompt, history_messages, **kwargs)

    # Define embedding function
    # IMPORTANT: Must match the embedding model used when creating the KG
    # Check vdb_chunks.json "embedding_dim" or .env EMBEDDING_MODEL to verify
    embedding_func = EmbeddingFunc(
        embedding_dim=1536,  # text-embedding-3-small
        max_token_size=8192,
        func=lambda texts: openai_embed(
            texts,
            model="text-embedding-3-small",  # Must match original KG
            api_key=api_key,
            base_url=base_url,
        ),
    )

    print("🔧 Initializing RAGAnything...")

    # Initialize RAGAnything
    rag = RAGAnything(
        config=config,
        llm_model_func=llm_model_func,
        vision_model_func=vision_model_func,
        embedding_func=embedding_func,
    )

    # This will load from existing storage without processing new documents
    await rag._ensure_lightrag_initialized()

    print("✅ RAGAnything initialized and ready for queries\n")

    return rag


async def show_kg_info(rag: RAGAnything):
    """Show Knowledge Graph information"""
    import json

    print("\n📊 KNOWLEDGE GRAPH INFORMATION:")
    print("-" * 60)

    try:
        working_dir = Path(rag.config.working_dir)

        # Read doc status directly from JSON
        doc_status_file = working_dir / "kv_store_doc_status.json"
        if doc_status_file.exists():
            with open(doc_status_file, 'r', encoding='utf-8') as f:
                doc_status_data = json.load(f)
                print(f"📄 Documents indexed: {len(doc_status_data)}")
                for doc_id, status in list(doc_status_data.items())[:5]:  # Show first 5
                    file_path = status.get("file_path", "unknown")
                    print(f"   - {Path(file_path).name}")
                if len(doc_status_data) > 5:
                    print(f"   ... and {len(doc_status_data) - 5} more")

        # Read chunks
        chunks_file = working_dir / "vdb_chunks.json"
        if chunks_file.exists():
            with open(chunks_file, 'r', encoding='utf-8') as f:
                chunks_data = json.load(f)
                chunk_count = len(chunks_data.get("data", []))
                print(f"\n🧩 Text chunks: {chunk_count}")

        # Read entities
        entities_file = working_dir / "vdb_entities.json"
        if entities_file.exists():
            with open(entities_file, 'r', encoding='utf-8') as f:
                entities_data = json.load(f)
                entity_count = len(entities_data.get("data", []))
                print(f"🔗 Entities: {entity_count}")

        # Read relations
        relations_file = working_dir / "vdb_relationships.json"
        if relations_file.exists():
            with open(relations_file, 'r', encoding='utf-8') as f:
                relations_data = json.load(f)
                relation_count = len(relations_data.get("data", []))
                print(f"↔️  Relations: {relation_count}")

        # Read text chunks for additional info
        text_chunks_file = working_dir / "kv_store_text_chunks.json"
        if text_chunks_file.exists():
            with open(text_chunks_file, 'r', encoding='utf-8') as f:
                text_chunks_data = json.load(f)
                multimodal_count = sum(1 for chunk in text_chunks_data.values()
                                     if chunk.get("is_multimodal", False))
                print(f"🖼️  Multimodal chunks: {multimodal_count}")

        print("-" * 60)

    except Exception as e:
        print(f"❌ Error getting KG info: {e}")
        import traceback
        print(traceback.format_exc())


async def interactive_query_loop(rag: RAGAnything):
    """Interactive query loop"""
    print_help()

    # Query settings
    current_mode = "hybrid"
    vlm_enhanced = True

    print(f"🔍 Query mode: {current_mode}")
    print(f"👁️  VLM enhanced: {'ON' if vlm_enhanced else 'OFF'}")
    print("\n" + "="*80)

    try:
        while True:
            # Get user input
            query = input("\n💬 Query > ").strip()

            if not query:
                continue

            # Handle commands
            if query.startswith("/"):
                cmd_parts = query.split()
                cmd = cmd_parts[0].lower()

                if cmd in ["/exit", "/quit"]:
                    print("\n👋 Goodbye!")
                    break

                elif cmd == "/help":
                    print_help()
                    continue

                elif cmd == "/mode":
                    if len(cmd_parts) < 2:
                        print("❌ Usage: /mode <local|global|hybrid|mix|naive>")
                    else:
                        new_mode = cmd_parts[1].lower()
                        if new_mode in ["local", "global", "hybrid", "mix", "naive"]:
                            current_mode = new_mode
                            print(f"✅ Query mode changed to: {current_mode}")
                        else:
                            print(f"❌ Unknown mode: {new_mode}")
                    continue

                elif cmd == "/vlm":
                    if len(cmd_parts) < 2:
                        print("❌ Usage: /vlm <on|off>")
                    else:
                        setting = cmd_parts[1].lower()
                        if setting in ["on", "1", "true"]:
                            vlm_enhanced = True
                            print("✅ VLM enhanced queries: ON")
                        elif setting in ["off", "0", "false"]:
                            vlm_enhanced = False
                            print("✅ VLM enhanced queries: OFF")
                        else:
                            print(f"❌ Unknown setting: {setting}")
                    continue

                elif cmd == "/info":
                    await show_kg_info(rag)
                    continue

                else:
                    print(f"❌ Unknown command: {cmd}")
                    print("Type /help for available commands")
                    continue

            # Execute query
            print(f"\n🔍 Searching (mode={current_mode}, vlm={vlm_enhanced})...")
            try:
                result = await rag.aquery(query, mode=current_mode, vlm_enhanced=vlm_enhanced)

                print("\n" + "="*80)
                print("📝 ANSWER:")
                print("-" * 80)
                print(result)
                print("="*80)

            except Exception as e:
                print(f"\n❌ Error executing query: {e}")
                import traceback
                print(traceback.format_exc())

    except KeyboardInterrupt:
        print("\n\n👋 Interrupted by user. Goodbye!")
    except EOFError:
        print("\n\n👋 EOF detected. Goodbye!")


async def main(working_dir: str, api_key: str, base_url: str = None):
    """Main async function"""
    print_banner()

    try:
        # Initialize RAG from existing storage
        rag = await initialize_rag(working_dir, api_key, base_url)

        # Show initial info
        await show_kg_info(rag)

        # Start interactive query loop
        await interactive_query_loop(rag)

    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        print(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Interactive Knowledge Graph Query Interface",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Query the KG from yesterday's processing
  python query_knowledge_graph.py test_environment/output/vlm_dedup_validation_2025-10-16_14-43-55/rag_storage

  # With custom API endpoint
  python query_knowledge_graph.py ./rag_storage --api-key YOUR_KEY --base-url http://localhost:8000/v1
        """
    )

    parser.add_argument(
        "working_dir",
        help="Path to rag_storage directory containing the Knowledge Graph"
    )
    parser.add_argument(
        "--api-key",
        default=os.getenv("OPENAI_API_KEY") or os.getenv("LLM_BINDING_API_KEY"),
        help="OpenAI API key (defaults to OPENAI_API_KEY or LLM_BINDING_API_KEY env var)"
    )
    parser.add_argument(
        "--base-url",
        default=os.getenv("OPENAI_API_BASE") or os.getenv("LLM_BINDING_HOST"),
        help="Optional API base URL (defaults to OPENAI_API_BASE or LLM_BINDING_HOST env var)"
    )

    args = parser.parse_args()

    # Validate API key
    if not args.api_key:
        print("❌ Error: OpenAI API key is required")
        print("Set OPENAI_API_KEY environment variable or use --api-key option")
        sys.exit(1)

    # Validate working directory
    if not Path(args.working_dir).exists():
        print(f"❌ Error: RAG storage directory not found: {args.working_dir}")
        sys.exit(1)

    # Run main async function
    asyncio.run(main(args.working_dir, args.api_key, args.base_url))
