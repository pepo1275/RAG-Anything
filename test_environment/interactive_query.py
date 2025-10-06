#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Interactive Query Interface for Knowledge Base
"""

import os
import asyncio
from pathlib import Path
from raganything import RAGAnything
from raganything.config import RAGAnythingConfig
from lightrag.llm.openai import openai_complete_if_cache, openai_embed, gpt_4o_complete
from lightrag.utils import EmbeddingFunc

async def interactive_query():
    """Interactive query interface"""

    print("=" * 70)
    print("INTERACTIVE KNOWLEDGE BASE QUERY")
    print("=" * 70)
    print()

    # Get API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("[ERROR] OPENAI_API_KEY not found")
        return

    # Define model functions
    def llm_model_func(prompt, system_prompt=None, history_messages=[], **kwargs):
        return openai_complete_if_cache(
            "gpt-4o-mini",
            prompt,
            system_prompt=system_prompt,
            history_messages=history_messages,
            api_key=api_key,
            **kwargs
        )

    def vision_model_func(prompt, system_prompt=None, history_messages=[], image_data=None, **kwargs):
        return gpt_4o_complete(
            prompt,
            system_prompt=system_prompt,
            history_messages=history_messages,
            api_key=api_key,
            **kwargs
        )

    embedding_func = EmbeddingFunc(
        embedding_dim=3072,
        max_token_size=8192,
        func=lambda texts: openai_embed(
            texts,
            model="text-embedding-3-large",
            api_key=api_key
        )
    )

    # Initialize RAGAnything
    storage_path = Path("test_environment/rag_storage")

    print(f"Loading Knowledge Base from: {storage_path}")
    print("Initializing RAGAnything...")

    config = RAGAnythingConfig(
        working_dir=str(storage_path),
        parser="docling"
    )

    rag = RAGAnything(
        config=config,
        llm_model_func=llm_model_func,
        vision_model_func=vision_model_func,
        embedding_func=embedding_func
    )

    print("✓ Knowledge Base loaded successfully!")
    print()
    print("Available query modes:")
    print("  - naive: Simple retrieval")
    print("  - local: Entity-focused search")
    print("  - global: Document-level search")
    print("  - hybrid: Combined approach (default)")
    print()
    print("Commands:")
    print("  - Type 'exit' or 'quit' to stop")
    print("  - Type 'mode <mode_name>' to change mode (e.g., 'mode local')")
    print("  - Type 'help' for more info")
    print()
    print("-" * 70)

    current_mode = "hybrid"

    while True:
        try:
            # Get user input
            user_input = input(f"\n[{current_mode.upper()}] Query: ").strip()

            if not user_input:
                continue

            # Check for commands
            if user_input.lower() in ['exit', 'quit', 'q']:
                print("\nGoodbye!")
                break

            if user_input.lower() == 'help':
                print("\nHelp:")
                print("  Query Modes:")
                print("    - naive: Fast, simple keyword matching")
                print("    - local: Search based on entities and relationships")
                print("    - global: High-level document understanding")
                print("    - hybrid: Combines local + global (recommended)")
                print("\n  Commands:")
                print("    - mode <name>: Change query mode")
                print("    - help: Show this help")
                print("    - exit/quit: Exit the program")
                continue

            if user_input.lower().startswith('mode '):
                new_mode = user_input[5:].strip().lower()
                if new_mode in ['naive', 'local', 'global', 'hybrid']:
                    current_mode = new_mode
                    print(f"✓ Mode changed to: {current_mode}")
                else:
                    print(f"✗ Invalid mode: {new_mode}")
                    print("  Valid modes: naive, local, global, hybrid")
                continue

            # Execute query
            print(f"\nSearching Knowledge Base (mode: {current_mode})...")

            response = await rag.aquery(user_input, mode=current_mode)

            print("\n" + "=" * 70)
            print("RESPONSE:")
            print("=" * 70)
            print(response)
            print("=" * 70)

        except KeyboardInterrupt:
            print("\n\nInterrupted by user. Goodbye!")
            break
        except Exception as e:
            print(f"\n✗ Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(interactive_query())
