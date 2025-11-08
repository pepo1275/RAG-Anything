"""LiteLLM adapter for RAG-Anything

This module provides adapters to use LiteLLM (https://github.com/BerriAI/litellm)
with RAG-Anything, enabling support for 100+ LLM providers with a unified interface.

IMPORTANT - API Keys:
    LiteLLM automatically reads API keys from environment variables based on the provider:
    - OpenAI: OPENAI_API_KEY
    - Anthropic: ANTHROPIC_API_KEY
    - Google: GOOGLE_API_KEY (or GEMINI_API_KEY)
    - Azure: AZURE_API_KEY
    - Ollama: No API key needed (local)

    Make sure to set the appropriate API key in your environment or .env file BEFORE
    using LiteLLM with that provider. Otherwise you'll get authentication errors.

Example:
    >>> from raganything.litellm_adapter import LiteLLMConfig, LiteLLMAdapter
    >>> # Set API key in environment first
    >>> import os
    >>> os.environ["ANTHROPIC_API_KEY"] = "your-key"
    >>>
    >>> config = LiteLLMConfig(llm_model="anthropic/claude-3-5-sonnet-20241022")
    >>> adapter = LiteLLMAdapter(config)
    >>> rag = RAGAnything(
    ...     llm_model_func=adapter.create_llm_func(),
    ...     embedding_func=adapter.create_embedding_func(),
    ...     vision_model_func=adapter.create_vision_func(),
    ... )
"""

from dataclasses import dataclass
from typing import Callable, Optional, List, Dict
import os
import warnings


# Mapping of provider prefixes to required environment variable names
PROVIDER_API_KEYS: Dict[str, List[str]] = {
    "openai": ["OPENAI_API_KEY"],
    "anthropic": ["ANTHROPIC_API_KEY"],
    "gemini": ["GOOGLE_API_KEY", "GEMINI_API_KEY"],
    "google": ["GOOGLE_API_KEY", "GEMINI_API_KEY"],
    "azure": ["AZURE_API_KEY", "AZURE_OPENAI_API_KEY"],
    "ollama": [],  # Local, no key needed
    "huggingface": ["HUGGINGFACE_API_KEY", "HF_TOKEN"],
    "groq": ["GROQ_API_KEY"],
    "together": ["TOGETHERAI_API_KEY"],
}


def check_provider_api_key(model: str, warn: bool = True) -> Optional[str]:
    """Check if the required API key for a provider is set in environment.

    Args:
        model: Model name in format "provider/model-name" (e.g., "openai/gpt-4o")
        warn: If True, emit warning when API key is missing

    Returns:
        The environment variable name that is set, or None if no key is needed/found
    """
    if "/" not in model:
        return None

    provider = model.split("/")[0].lower()

    # Check if provider requires API key
    if provider not in PROVIDER_API_KEYS:
        # Unknown provider, can't check
        return None

    required_keys = PROVIDER_API_KEYS[provider]

    # No key needed (e.g., ollama)
    if not required_keys:
        return None

    # Check if any of the required keys is set
    for key in required_keys:
        if os.getenv(key):
            return key

    # No key found
    if warn:
        key_list = " or ".join(required_keys)
        warnings.warn(
            f"Provider '{provider}' requires API key but none found in environment.\n"
            f"Please set {key_list} in your environment or .env file.\n"
            f"Example: export {required_keys[0]}='your-api-key-here'",
            UserWarning,
            stacklevel=2
        )

    return None


@dataclass
class LiteLLMConfig:
    """Configuration for LiteLLM models

    Attributes:
        llm_model: Model to use for LLM tasks (format: "provider/model-name")
                   Examples: "openai/gpt-4o", "anthropic/claude-3-5-sonnet-20241022",
                            "gemini/gemini-2.0-flash-exp", "ollama/llama2"
        embedding_model: Model to use for embeddings
                        Examples: "openai/text-embedding-3-large",
                                 "gemini/text-embedding-004"
        embedding_dim: Dimension of embedding vectors
        vision_model: Optional model for vision tasks (supports multimodal)
        temperature: Temperature for sampling (0.0 = deterministic)
        max_tokens: Maximum tokens in response
        api_key: Optional API key (if not set in environment)
        base_url: Optional base URL for API calls
    """
    llm_model: str = "openai/gpt-4o"
    embedding_model: str = "openai/text-embedding-3-large"
    embedding_dim: int = 3072
    vision_model: Optional[str] = "openai/gpt-4o"
    temperature: float = 0.0
    max_tokens: int = 32768
    api_key: Optional[str] = None
    base_url: Optional[str] = None

    @classmethod
    def from_env(cls, prefix: str = "LITELLM") -> "LiteLLMConfig":
        """Load configuration from environment variables

        Environment variables:
            LITELLM_LLM_MODEL: LLM model (default: openai/gpt-4o)
            LITELLM_EMBEDDING_MODEL: Embedding model (default: openai/text-embedding-3-large)
            LITELLM_EMBEDDING_DIM: Embedding dimension (default: 3072)
            LITELLM_VISION_MODEL: Vision model (default: openai/gpt-4o)
            LITELLM_TEMPERATURE: Temperature (default: 0.0)
            LITELLM_MAX_TOKENS: Max tokens (default: 32768)
            LITELLM_API_KEY: API key (optional)
            LITELLM_BASE_URL: Base URL (optional)

        Args:
            prefix: Prefix for environment variables (default: "LITELLM")

        Returns:
            LiteLLMConfig instance loaded from environment
        """
        return cls(
            llm_model=os.getenv(f"{prefix}_LLM_MODEL", "openai/gpt-4o"),
            embedding_model=os.getenv(
                f"{prefix}_EMBEDDING_MODEL", "openai/text-embedding-3-large"
            ),
            embedding_dim=int(os.getenv(f"{prefix}_EMBEDDING_DIM", "3072")),
            vision_model=os.getenv(f"{prefix}_VISION_MODEL", "openai/gpt-4o"),
            temperature=float(os.getenv(f"{prefix}_TEMPERATURE", "0.0")),
            max_tokens=int(os.getenv(f"{prefix}_MAX_TOKENS", "32768")),
            api_key=os.getenv(f"{prefix}_API_KEY"),
            base_url=os.getenv(f"{prefix}_BASE_URL"),
        )


class LiteLLMAdapter:
    """Adapter to create RAG-Anything compatible model functions using LiteLLM

    This adapter converts LiteLLM's API to the function signatures expected by
    RAG-Anything, enabling seamless integration with 100+ LLM providers.

    Example:
        >>> config = LiteLLMConfig(llm_model="anthropic/claude-3-5-sonnet-20241022")
        >>> adapter = LiteLLMAdapter(config)
        >>> rag = RAGAnything(
        ...     llm_model_func=adapter.create_llm_func(),
        ...     embedding_func=adapter.create_embedding_func(),
        ...     vision_model_func=adapter.create_vision_func(),
        ... )
    """

    def __init__(self, config: LiteLLMConfig):
        """Initialize adapter with LiteLLM configuration

        Args:
            config: LiteLLMConfig instance with model settings

        Warnings:
            Emits UserWarning if required API keys are not found in environment
        """
        self.config = config

        # Check API keys for all configured models
        check_provider_api_key(config.llm_model, warn=True)
        check_provider_api_key(config.embedding_model, warn=True)
        if config.vision_model:
            check_provider_api_key(config.vision_model, warn=True)

    def create_llm_func(self) -> Callable:
        """Create LLM function compatible with RAG-Anything

        Returns a function with signature:
            def llm_func(prompt, system_prompt=None, history_messages=[], **kwargs) -> str

        Returns:
            Callable that uses LiteLLM completion for LLM calls
        """
        from litellm import completion

        config = self.config

        def llm_func(
            prompt: str,
            system_prompt: Optional[str] = None,
            history_messages: List = [],
            **kwargs
        ) -> str:
            """LLM function using LiteLLM"""
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.extend(history_messages)
            messages.append({"role": "user", "content": prompt})

            # Build call kwargs
            call_kwargs = {
                "model": config.llm_model,
                "messages": messages,
                "temperature": config.temperature,
                "max_tokens": config.max_tokens,
            }

            # Add optional parameters
            if config.api_key:
                call_kwargs["api_key"] = config.api_key
            if config.base_url:
                call_kwargs["base_url"] = config.base_url

            # Override with user kwargs
            call_kwargs.update(kwargs)

            # Call LiteLLM
            response = completion(**call_kwargs)
            return response.choices[0].message.content

        return llm_func

    def create_embedding_func(self):
        """Create embedding function compatible with LightRAG's EmbeddingFunc

        Returns a LightRAG EmbeddingFunc that uses LiteLLM for embeddings.

        Returns:
            EmbeddingFunc instance configured for LiteLLM embeddings
        """
        from litellm import embedding
        from lightrag.base import EmbeddingFunc

        config = self.config

        def embed_func(texts: List[str]) -> List[List[float]]:
            """Embedding function using LiteLLM"""
            results = []
            for text in texts:
                call_kwargs = {
                    "model": config.embedding_model,
                    "input": text,
                }

                # Add optional parameters
                if config.api_key:
                    call_kwargs["api_key"] = config.api_key
                if config.base_url:
                    call_kwargs["base_url"] = config.base_url

                response = embedding(**call_kwargs)
                results.append(response.data[0].embedding)

            return results

        return EmbeddingFunc(
            embedding_dim=config.embedding_dim,
            max_token_size=8192,
            func=embed_func
        )

    def create_vision_func(self) -> Optional[Callable]:
        """Create vision function compatible with RAG-Anything

        Returns a function with signature:
            def vision_func(prompt, system_prompt=None, history_messages=[],
                          image_data=None, messages=None, **kwargs) -> str

        Returns:
            Callable that uses LiteLLM completion for vision calls,
            or None if vision_model is not configured
        """
        if not self.config.vision_model:
            return None

        from litellm import completion

        config = self.config

        def vision_func(
            prompt: str,
            system_prompt: Optional[str] = None,
            history_messages: List = [],
            image_data: Optional[str] = None,
            messages: Optional[List] = None,
            **kwargs
        ) -> str:
            """Vision function using LiteLLM"""

            if messages:
                # Multimodal format already provided (VLM-enhanced query)
                call_msgs = messages
            else:
                # Build messages from prompt + image_data
                call_msgs = []
                if system_prompt:
                    call_msgs.append({"role": "system", "content": system_prompt})
                call_msgs.extend(history_messages)

                # Build content with text and image
                content = [{"type": "text", "text": prompt}]
                if image_data:
                    content.append({
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}
                    })

                call_msgs.append({"role": "user", "content": content})

            # Build call kwargs
            call_kwargs = {
                "model": config.vision_model,
                "messages": call_msgs,
                "temperature": config.temperature,
                "max_tokens": config.max_tokens,
            }

            # Add optional parameters
            if config.api_key:
                call_kwargs["api_key"] = config.api_key
            if config.base_url:
                call_kwargs["base_url"] = config.base_url

            # Override with user kwargs
            call_kwargs.update(kwargs)

            # Call LiteLLM
            response = completion(**call_kwargs)
            return response.choices[0].message.content

        return vision_func


# Export main classes
__all__ = ["LiteLLMConfig", "LiteLLMAdapter"]
