#!/usr/bin/env python
"""
Example script demonstrating RAGAnything integration with Google Gemini

This example shows how to:
1. Use Google Gemini models for both LLM and embeddings
2. Process documents with RAGAnything using Gemini
3. Perform queries using Google's latest AI models
"""

import os
import argparse
import asyncio
import logging
import logging.config
from pathlib import Path

# Add project root directory to Python path
import sys
sys.path.append(str(Path(__file__).parent.parent))

from lightrag.utils import EmbeddingFunc, logger, set_verbose_debug
from raganything import RAGAnything, RAGAnythingConfig
from raganything.gemini_llm import gemini_complete_if_cache, gemini_embed

from dotenv import load_dotenv

load_dotenv(dotenv_path=".env", override=False)


def configure_logging():
    """Configure logging for the application"""
    log_dir = os.getenv("LOG_DIR", os.getcwd())
    log_file_path = os.path.abspath(os.path.join(log_dir, "gemini_example.log"))

    print(f"\nGemini RAGAnything example log file: {log_file_path}\n")
    os.makedirs(os.path.dirname(log_dir), exist_ok=True)

    log_max_bytes = int(os.getenv("LOG_MAX_BYTES", 10485760))  # Default 10MB
    log_backup_count = int(os.getenv("LOG_BACKUP_COUNT", 5))  # Default 5 backups

    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": "%(levelname)s: %(message)s",
                },
                "detailed": {
                    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                },
            },
            "handlers": {
                "console": {
                    "formatter": "default",
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stderr",
                },
                "file": {
                    "formatter": "detailed",
                    "class": "logging.handlers.RotatingFileHandler",
                    "filename": log_file_path,
                    "maxBytes": log_max_bytes,
                    "backupCount": log_backup_count,
                    "encoding": "utf-8",
                },
            },
            "loggers": {
                "lightrag": {
                    "handlers": ["console", "file"],
                    "level": "INFO",
                    "propagate": False,
                },
            },
        }
    )

    logger.setLevel(logging.INFO)
    set_verbose_debug(os.getenv("VERBOSE", "false").lower() == "true")


async def process_with_gemini_rag(
    file_path: str,
    output_dir: str,
    api_key: str,
    working_dir: str = None,
    parser: str = None,
    llm_model: str = "gemini-2.5-pro",
    vision_model: str = "gemini-2.5-pro",
    embedding_model: str = "gemini-embedding-001",
):
    """
    Process document with RAGAnything using Google Gemini models
    
    Args:
        file_path: Path to the document
        output_dir: Output directory for RAG results
        api_key: Google API key
        working_dir: Working directory for RAG storage
        parser: Document parser to use
        llm_model: Gemini model for text generation
        vision_model: Gemini model for vision tasks
        embedding_model: Gemini model for embeddings
    """
    try:
        # Create RAGAnything configuration
        config = RAGAnythingConfig(
            working_dir=working_dir or "./rag_storage",
            parser=parser or "mineru",
            parse_method="auto",
            enable_image_processing=True,
            enable_table_processing=True,
            enable_equation_processing=True,
        )

        # Define LLM model function using Gemini
        def llm_model_func(prompt, system_prompt=None, history_messages=[], **kwargs):
            return gemini_complete_if_cache(
                llm_model,
                prompt,
                system_prompt=system_prompt,
                history_messages=history_messages,
                api_key=api_key,
                **kwargs,
            )

        # Define vision model function for image processing using Gemini
        def vision_model_func(
            prompt,
            system_prompt=None,
            history_messages=[],
            image_data=None,
            messages=None,
            **kwargs,
        ):
            return gemini_complete_if_cache(
                vision_model,
                prompt,
                system_prompt=system_prompt,
                history_messages=history_messages,
                api_key=api_key,
                messages=messages,
                image_data=image_data,
                **kwargs,
            )

        # Define embedding function using Gemini
        embedding_func = EmbeddingFunc(
            embedding_dim=3072,  # gemini-embedding-001 dimensions
            max_token_size=8192,
            func=lambda texts: gemini_embed(
                texts,
                model=embedding_model,
                api_key=api_key,
            ),
        )

        # Initialize RAGAnything with Gemini models
        rag = RAGAnything(
            config=config,
            llm_model_func=llm_model_func,
            vision_model_func=vision_model_func,
            embedding_func=embedding_func,
        )

        # Process document
        logger.info(f"Processing document: {file_path}")
        logger.info(f"Using Gemini models - LLM: {llm_model}, Vision: {vision_model}, Embedding: {embedding_model}")
        
        await rag.process_document_complete(
            file_path=file_path, output_dir=output_dir, parse_method="auto"
        )

        # Example queries
        logger.info("\nQuerying processed document with Gemini:")

        # Text queries
        text_queries = [
            "What is the main content of the document?",
            "What are the key topics discussed?",
            "Summarize the most important points",
        ]

        for query in text_queries:
            logger.info(f"\n[Text Query]: {query}")
            result = await rag.aquery(query, mode="hybrid")
            logger.info(f"Answer: {result}")

        # Multimodal query example
        logger.info("\n[Multimodal Query]: Analyzing performance data")
        multimodal_result = await rag.aquery_with_multimodal(
            "Compare this performance data with any similar results mentioned in the document",
            multimodal_content=[
                {
                    "type": "table",
                    "table_data": """Method,Accuracy,Processing_Time
                                Gemini_RAG,96.8%,110ms
                                Traditional_RAG,87.3%,180ms
                                Baseline,82.1%,200ms""",
                    "table_caption": "Performance comparison with Gemini",
                }
            ],
            mode="hybrid",
        )
        logger.info(f"Answer: {multimodal_result}")

        logger.info("\n✅ Document processing and querying completed successfully with Google Gemini!")

    except Exception as e:
        logger.error(f"Error processing with Gemini RAG: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())


def main():
    """Main function to run the Gemini example"""
    parser = argparse.ArgumentParser(description="RAGAnything with Google Gemini Example")
    parser.add_argument("file_path", help="Path to the document to process")
    parser.add_argument(
        "--working_dir", "-w", default="./rag_storage", help="Working directory path"
    )
    parser.add_argument(
        "--output", "-o", default="./output", help="Output directory path"
    )
    parser.add_argument(
        "--api-key",
        default=os.getenv("GOOGLE_API_KEY"),
        help="Google API key (defaults to GOOGLE_API_KEY env var)",
    )
    parser.add_argument(
        "--parser",
        default=os.getenv("PARSER", "mineru"),
        help="Document parser to use (mineru or docling)",
    )
    parser.add_argument(
        "--llm-model",
        default="gemini-2.5-pro",
        help="Gemini model for text generation (default: gemini-2.5-pro)",
    )
    parser.add_argument(
        "--vision-model",
        default="gemini-2.5-pro",
        help="Gemini model for vision tasks (default: gemini-2.5-pro)",
    )
    parser.add_argument(
        "--embedding-model",
        default="gemini-embedding-001",
        help="Gemini model for embeddings (default: gemini-embedding-001)",
    )

    args = parser.parse_args()

    # Check if API key is provided
    if not args.api_key:
        logger.error("Error: Google API key is required")
        logger.error("Set GOOGLE_API_KEY environment variable or use --api-key option")
        return

    # Create output directory if specified
    if args.output:
        os.makedirs(args.output, exist_ok=True)

    # Process with Gemini RAG
    asyncio.run(
        process_with_gemini_rag(
            args.file_path,
            args.output,
            args.api_key,
            args.working_dir,
            args.parser,
            args.llm_model,
            args.vision_model,
            args.embedding_model,
        )
    )


if __name__ == "__main__":
    # Configure logging first
    configure_logging()

    print("RAGAnything + Google Gemini Example")
    print("=" * 40)
    print("Processing document with Google Gemini models")
    print("=" * 40)

    main()
