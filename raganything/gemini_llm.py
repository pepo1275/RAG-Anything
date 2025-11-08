"""
Google Gemini LLM wrapper for LightRAG integration

This module provides functions to integrate Google Gemini models with LightRAG
using the new google-genai library.
"""

import os
import asyncio
from typing import List, Dict, Any, Optional, Union
import logging
import google.genai as genai
from google.genai.types import GenerateContentConfig
import base64

logger = logging.getLogger(__name__)


def setup_gemini_client(api_key: str = None) -> genai.Client:
    """
    Setup Google Gemini client
    
    Args:
        api_key: Google API key. If None, will use GOOGLE_API_KEY environment variable
        
    Returns:
        Configured Gemini client
    """
    if api_key is None:
        api_key = os.getenv("GOOGLE_API_KEY")
    
    if not api_key:
        raise ValueError("Google API key is required. Set GOOGLE_API_KEY environment variable or pass api_key parameter")
    
    client = genai.Client(api_key=api_key)
    return client


def gemini_complete_if_cache(
    model: str,
    prompt: str,
    system_prompt: str = None,
    history_messages: List[Dict] = None,
    api_key: str = None,
    messages: List[Dict] = None,
    image_data: str = None,
    **kwargs
) -> str:
    """
    Complete text using Google Gemini models with caching support
    
    Args:
        model: Model name (e.g., 'gemini-1.5-flash', 'gemini-1.5-pro')
        prompt: The main prompt text
        system_prompt: Optional system prompt
        history_messages: Previous conversation history
        api_key: Google API key
        messages: Direct messages format (for multimodal)
        image_data: Base64 encoded image data
        **kwargs: Additional arguments
        
    Returns:
        Generated text response
    """
    try:
        client = setup_gemini_client(api_key)
        
        # Prepare the content for generation
        contents = []
        
        # Add system prompt if provided
        if system_prompt:
            contents.append(system_prompt)
        
        # Handle different input formats
        if messages:
            # Handle direct messages format (multimodal)
            for msg in messages:
                if msg and msg.get('role') == 'user':
                    content = msg.get('content', '')
                    if isinstance(content, list):
                        # Handle multimodal content
                        text_parts = []
                        for part in content:
                            if part.get('type') == 'text':
                                text_parts.append(part.get('text', ''))
                            elif part.get('type') == 'image_url':
                                # Handle base64 image
                                image_url = part.get('image_url', {}).get('url', '')
                                if image_url.startswith('data:image'):
                                    # Extract base64 data
                                    base64_data = image_url.split(',')[1]
                                    # Note: Gemini handles images differently
                                    text_parts.append(f"[Image data provided - base64 length: {len(base64_data)}]")
                        contents.append(' '.join(text_parts))
                    else:
                        contents.append(content)
        elif image_data:
            # Handle single image with prompt
            contents.append(f"{prompt}\n[Image data provided - base64 length: {len(image_data)}]")
        else:
            # Handle text-only prompt
            if history_messages:
                for msg in history_messages:
                    if msg.get('role') == 'user':
                        contents.append(f"User: {msg.get('content', '')}")
                    elif msg.get('role') == 'assistant':
                        contents.append(f"Assistant: {msg.get('content', '')}")
            
            contents.append(prompt)
        
        # Combine all content
        full_prompt = '\n'.join(contents)
        
        # Configure generation parameters
        config = GenerateContentConfig(
            temperature=kwargs.get('temperature', 0.0),
            max_output_tokens=kwargs.get('max_tokens', 8192),
            top_p=kwargs.get('top_p', 0.95),
            top_k=kwargs.get('top_k', 64),
        )
        
        # Generate response
        response = client.models.generate_content(
            model=model,
            contents=full_prompt,
            config=config
        )
        
        return response.text
        
    except Exception as e:
        logger.error(f"Error in Gemini completion: {str(e)}")
        raise


def gemini_embed(
    texts: List[str],
    model: str = "gemini-embedding-001",
    api_key: str = None,
    **kwargs
) -> List[List[float]]:
    """
    Generate embeddings using Google Gemini embedding models
    
    Args:
        texts: List of texts to embed
        model: Embedding model name (e.g., 'gemini-embedding-001')
        api_key: Google API key
        **kwargs: Additional arguments
        
    Returns:
        List of embedding vectors
    """
    try:
        client = setup_gemini_client(api_key)
        
        embeddings = []
        for text in texts:
            # Generate embedding for each text
            response = client.models.embed_content(
                model=model,
                contents=text,
                **kwargs
            )
            # Extract the actual embedding values from ContentEmbedding object
            if hasattr(response, 'embeddings') and len(response.embeddings) > 0:
                embedding_obj = response.embeddings[0]
                if hasattr(embedding_obj, 'values'):
                    embeddings.append(embedding_obj.values)
                else:
                    embeddings.append(embedding_obj)
            else:
                raise ValueError(f"No embeddings found in response: {response}")
        
        return embeddings
        
    except Exception as e:
        logger.error(f"Error in Gemini embedding: {str(e)}")
        raise


async def gemini_complete_if_cache_async(
    model: str,
    prompt: str,
    system_prompt: str = None,
    history_messages: List[Dict] = None,
    api_key: str = None,
    messages: List[Dict] = None,
    image_data: str = None,
    **kwargs
) -> str:
    """
    Async version of gemini_complete_if_cache
    """
    # For now, we'll run the sync version in a thread
    # Google GenAI library has async support that could be implemented here
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None, 
        gemini_complete_if_cache,
        model, prompt, system_prompt, history_messages, api_key, messages, image_data,
        **kwargs
    )


async def gemini_embed_async(
    texts: List[str],
    model: str = "gemini-embedding-001", 
    api_key: str = None,
    **kwargs
) -> List[List[float]]:
    """
    Async version of gemini_embed
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None,
        gemini_embed,
        texts, model, api_key,
        **kwargs
    )
