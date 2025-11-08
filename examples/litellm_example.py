"""Example: Using LiteLLM with RAG-Anything

This example demonstrates how to use LiteLLM to switch between different
LLM providers (OpenAI, Anthropic, Gemini, Ollama) with minimal code changes.

Features:
- Config-based provider switching
- Support for 100+ providers
- Automatic model function creation
- Environment variable configuration

Usage:
    python examples/litellm_example.py
"""

import asyncio
import os
from pathlib import Path

from raganything import RAGAnything, RAGAnythingConfig
from raganything.litellm_adapter import LiteLLMConfig


async def example_openai():
    """Example 1: OpenAI (default)"""
    print("=" * 70)
    print("Example 1: OpenAI GPT-4o")
    print("=" * 70)

    config_openai = LiteLLMConfig(
        llm_model="openai/gpt-4o",
        embedding_model="openai/text-embedding-3-large",
        embedding_dim=3072,
        vision_model="openai/gpt-4o",
    )

    rag_openai = RAGAnything(
        config=RAGAnythingConfig(
            use_litellm=True,
            litellm_config=config_openai,
            working_dir="./rag_storage_litellm_openai"
        )
    )

    print("✅ RAGAnything initialized with OpenAI")
    print(f"   LLM: {config_openai.llm_model}")
    print(f"   Embedding: {config_openai.embedding_model} (dim={config_openai.embedding_dim})")
    return rag_openai


async def example_anthropic():
    """Example 2: Anthropic Claude"""
    print("\n" + "=" * 70)
    print("Example 2: Anthropic Claude 3.5 Sonnet")
    print("=" * 70)

    config_claude = LiteLLMConfig(
        llm_model="anthropic/claude-3-5-sonnet-20241022",
        embedding_model="openai/text-embedding-3-large",  # Claude doesn't have embeddings
        embedding_dim=3072,
        vision_model="anthropic/claude-3-5-sonnet-20241022",  # Claude supports vision
    )

    rag_claude = RAGAnything(
        config=RAGAnythingConfig(
            use_litellm=True,
            litellm_config=config_claude,
            working_dir="./rag_storage_litellm_claude"
        )
    )

    print("✅ RAGAnything initialized with Claude")
    print(f"   LLM: {config_claude.llm_model}")
    print(f"   Embedding: {config_claude.embedding_model}")
    return rag_claude


async def example_gemini():
    """Example 3: Google Gemini"""
    print("\n" + "=" * 70)
    print("Example 3: Google Gemini 2.0 Flash")
    print("=" * 70)

    config_gemini = LiteLLMConfig(
        llm_model="gemini/gemini-2.0-flash-exp",
        embedding_model="gemini/text-embedding-004",
        embedding_dim=768,  # Gemini embedding dimension
        vision_model="gemini/gemini-2.0-flash-exp",
    )

    rag_gemini = RAGAnything(
        config=RAGAnythingConfig(
            use_litellm=True,
            litellm_config=config_gemini,
            working_dir="./rag_storage_litellm_gemini"
        )
    )

    print("✅ RAGAnything initialized with Gemini")
    print(f"   LLM: {config_gemini.llm_model}")
    print(f"   Embedding: {config_gemini.embedding_model} (dim={config_gemini.embedding_dim})")
    return rag_gemini


async def example_from_env():
    """Example 4: Load from Environment Variables"""
    print("\n" + "=" * 70)
    print("Example 4: Load from Environment Variables")
    print("=" * 70)

    # Set environment variables (or put in .env file)
    os.environ["LITELLM_LLM_MODEL"] = "openai/gpt-4o-mini"
    os.environ["LITELLM_EMBEDDING_MODEL"] = "openai/text-embedding-3-small"
    os.environ["LITELLM_EMBEDDING_DIM"] = "1536"

    config_env = LiteLLMConfig.from_env()

    rag_env = RAGAnything(
        config=RAGAnythingConfig(
            use_litellm=True,
            litellm_config=config_env,
            working_dir="./rag_storage_litellm_env"
        )
    )

    print("✅ RAGAnything initialized from env vars")
    print(f"   LLM: {config_env.llm_model}")
    print(f"   Embedding: {config_env.embedding_model} (dim={config_env.embedding_dim})")
    return rag_env


async def example_cost_optimization():
    """Example 5: Cost Optimization Strategy"""
    print("\n" + "=" * 70)
    print("Example 5: Cost Optimization (Cheap Models)")
    print("=" * 70)

    config_cheap = LiteLLMConfig(
        llm_model="openai/gpt-4o-mini",  # 60x cheaper than gpt-4o
        embedding_model="openai/text-embedding-3-small",  # 5x cheaper than large
        embedding_dim=1536,
        vision_model="openai/gpt-4o-mini",
    )

    rag_cheap = RAGAnything(
        config=RAGAnythingConfig(
            use_litellm=True,
            litellm_config=config_cheap,
            working_dir="./rag_storage_litellm_cheap"
        )
    )

    print("✅ RAGAnything initialized with cost-optimized models")
    print(f"   LLM: {config_cheap.llm_model}")
    print(f"   Embedding: {config_cheap.embedding_model}")
    print("   💰 Estimated cost savings: 90% vs GPT-4o + large embeddings")
    return rag_cheap


async def main():
    """Run all examples"""
    print("\n" + "=" * 70)
    print("LITELLM INTEGRATION EXAMPLES")
    print("=" * 70)
    print()

    try:
        # Run examples
        await example_openai()
        await example_anthropic()
        await example_gemini()
        await example_from_env()
        await example_cost_optimization()

        print("\n" + "=" * 70)
        print("✅ All Examples Completed Successfully!")
        print("=" * 70)
        print("\nSwitching providers is as simple as changing 1 line:")
        print('  config.llm_model = "provider/model-name"')
        print("\nSupported providers: 100+")
        print("  - OpenAI, Anthropic, Google, Azure")
        print("  - Ollama, HuggingFace, Groq, Together")
        print("  - And many more!")
        print("\nFor full provider list, see:")
        print("  https://docs.litellm.ai/docs/providers")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nNote: Make sure you have:")
        print("  1. LiteLLM installed: pip install litellm")
        print("  2. API keys set in environment (OPENAI_API_KEY, etc.)")
        print("  3. Required provider dependencies installed")


if __name__ == "__main__":
    asyncio.run(main())
