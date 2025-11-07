# PLAN DE INTEGRACIÓN: LITELLM EN RAG-ANYTHING

**Fecha:** 2025-11-07
**Branch Target:** `feature/multimodal-development-framework`
**Status:** ⏳ PENDIENTE - LISTO PARA EJECUTAR
**Objetivo:** Integrar LiteLLM para soporte de 100+ LLM providers con config-based switching

**Decisión:** ✅ ADOPTAR LITELLM (ver `INVESTIGACION_LITELLM_2025-11-07.md`)

---

## 📋 RESUMEN EJECUTIVO

**Problema:**
RAG-Anything requiere funciones wrapper manuales para cada LLM provider, limitando flexibilidad.

**Solución:**
Integrar LiteLLM como capa de abstracción unificada para 100+ providers.

**Resultado Esperado:**
```python
# Cambiar de OpenAI a Claude en 1 línea
config = LiteLLMConfig(llm_model="anthropic/claude-3-5-sonnet-20241022")
rag = RAGAnything(config=RAGAnythingConfig(litellm_config=config))
```

**Métricas de Éxito:**
- ✅ 3+ providers funcionando (OpenAI, Anthropic, Gemini)
- ✅ Tests 100% passing
- ✅ Backward compatible (funciones manuales funcionan)
- ✅ Documentación completa
- ✅ Ejemplos actualizados

---

## ⏱️ CRONOGRAMA

| Fase | Duración | Estado | Descripción |
|------|----------|--------|-------------|
| **FASE 0** | 10 min | ⏳ | Safety commit + branch verification |
| **FASE 1** | 1.5 horas | ⏳ | Instalación + Adapter creation |
| **FASE 2** | 1 hora | ⏳ | Integration con RAGAnything |
| **FASE 3** | 1 hora | ⏳ | Testing comprehensive |
| **FASE 4** | 30 min | ⏳ | Documentation + Examples |
| **TOTAL** | **~4 horas** | ⏳ | **End-to-end implementation** |

---

## 🚀 FASE 0: PREPARACIÓN (10 min)

### Objetivos:
- ✅ Safety commit del estado actual
- ✅ Verificar branch correcto
- ✅ Verificar tests baseline

### Tareas:

#### 1. Safety Commit
```bash
git add -A
git commit -m "safety: pre-litellm-integration snapshot $(date +%Y-%m-%d_%H-%M-%S)"
git push origin feature/multimodal-development-framework
```

#### 2. Verificar Branch
```bash
git status
# Debe mostrar: On branch feature/multimodal-development-framework
# Debe mostrar: nothing to commit, working tree clean
```

#### 3. Verificar Tests Baseline
```bash
export PYTHONIOENCODING=utf-8
python test_environment/03_post_validation_tests.py
# Debe mostrar: Tests pasados: 8/8 (100%)
```

### Criterios de Éxito:
- [ ] Safety commit creado y pushed
- [ ] Branch correcto (feature/multimodal-development-framework)
- [ ] Tests baseline 100% passing

### Checkpoint:
🛑 **STOP - Esperar aprobación del usuario para continuar a FASE 1**

---

## 🔧 FASE 1: INSTALACIÓN Y ADAPTER (1.5 horas)

### Objetivos:
- ✅ Instalar LiteLLM dependency
- ✅ Crear `litellm_adapter.py` con LiteLLMConfig y LiteLLMAdapter
- ✅ Implementar 3 factory methods (llm, embedding, vision)

### Tareas:

#### 1.1 Instalación de LiteLLM (5 min)

```bash
# Activar environment
cd C:\Users\Gamer\Dev\RAG-Anything
.\rag_anything_env\Scripts\activate

# Instalar LiteLLM
pip install litellm

# Verificar instalación
python -c "import litellm; print(f'LiteLLM {litellm.__version__} installed')"
```

**Actualizar requirements.txt:**
```bash
pip freeze | grep litellm >> requirements.txt
```

#### 1.2 Crear LiteLLMConfig (20 min)

**Archivo:** `raganything/litellm_adapter.py`

```python
"""LiteLLM adapter for RAG-Anything

This module provides adapters to use LiteLLM (https://github.com/BerriAI/litellm)
with RAG-Anything, enabling support for 100+ LLM providers with a unified interface.
"""

from dataclasses import dataclass, field
from typing import Callable, Optional, List
import os


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
```

#### 1.3 Crear LiteLLMAdapter (60 min)

**Continuar en:** `raganything/litellm_adapter.py`

```python
from litellm import completion, embedding
from lightrag import EmbeddingFunc


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
        """
        self.config = config

    def create_llm_func(self) -> Callable:
        """Create LLM function compatible with RAG-Anything

        Returns a function with signature:
            def llm_func(prompt, system_prompt=None, history_messages=[], **kwargs) -> str

        Returns:
            Callable that uses LiteLLM completion for LLM calls
        """
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

    def create_embedding_func(self) -> EmbeddingFunc:
        """Create embedding function compatible with LightRAG's EmbeddingFunc

        Returns a LightRAG EmbeddingFunc that uses LiteLLM for embeddings.

        Returns:
            EmbeddingFunc instance configured for LiteLLM embeddings
        """
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
```

#### 1.4 Verificar Sintaxis (5 min)

```bash
# Check syntax
python -m py_compile raganything/litellm_adapter.py

# Check imports
python -c "from raganything.litellm_adapter import LiteLLMConfig, LiteLLMAdapter; print('✅ Import successful')"
```

### Criterios de Éxito:
- [ ] LiteLLM instalado correctamente
- [ ] `litellm_adapter.py` creado (~250 líneas)
- [ ] LiteLLMConfig con from_env() method
- [ ] LiteLLMAdapter con 3 factory methods
- [ ] Imports funcionando sin errores

### Checkpoint:
🛑 **STOP - Verificar que adapter compila antes de continuar a FASE 2**

---

## 🔗 FASE 2: INTEGRACIÓN CON RAGANYTHING (1 hora)

### Objetivos:
- ✅ Modificar `config.py` para incluir litellm_config
- ✅ Modificar `raganything.py` para auto-initialization
- ✅ Mantener backward compatibility
- ✅ Añadir environment variable support

### Tareas:

#### 2.1 Modificar RAGAnythingConfig (15 min)

**Archivo:** `raganything/config.py`

**Añadir al final del archivo (antes de get_env_value si existe):**

```python
# LiteLLM Integration
try:
    from raganything.litellm_adapter import LiteLLMConfig
    LITELLM_AVAILABLE = True
except ImportError:
    LITELLM_AVAILABLE = False
    LiteLLMConfig = None


@dataclass
class RAGAnythingConfig:
    # ... existing fields ...

    # LiteLLM Configuration
    use_litellm: bool = field(default=False)
    """Enable LiteLLM for automatic model function creation.
    If True and no manual model functions provided, will auto-create from litellm_config.
    """

    litellm_config: Optional[LiteLLMConfig] = field(default=None)
    """Configuration for LiteLLM models (llm, embedding, vision).
    Only used if use_litellm=True. Can be loaded from environment variables.
    """
```

**Nota:** Verificar que no rompa estructura existente. RAGAnythingConfig ya existe, solo añadir campos.

#### 2.2 Modificar RAGAnything Auto-Initialization (30 min)

**Archivo:** `raganything/raganything.py`

**En el método `_ensure_lightrag_initialized` (aprox línea 267), añadir lógica:**

```python
async def _ensure_lightrag_initialized(self):
    """Initialize LightRAG if not already initialized"""
    if self.lightrag is not None:
        return

    # Priority 1: Use provided model functions
    llm_func = self.llm_model_func
    embed_func = self.embedding_func
    vision_func = self.vision_model_func

    # Priority 2: Auto-create from LiteLLM if enabled
    if not llm_func and self.config.use_litellm:
        try:
            from raganything.litellm_adapter import LiteLLMAdapter, LiteLLMConfig

            # Load config from environment if not provided
            litellm_config = self.config.litellm_config
            if litellm_config is None:
                litellm_config = LiteLLMConfig.from_env()

            # Create adapter and functions
            adapter = LiteLLMAdapter(litellm_config)
            llm_func = adapter.create_llm_func()
            embed_func = adapter.create_embedding_func()
            vision_func = adapter.create_vision_func()

            logger.info(f"LiteLLM auto-initialized:")
            logger.info(f"  LLM: {litellm_config.llm_model}")
            logger.info(f"  Embedding: {litellm_config.embedding_model} (dim={litellm_config.embedding_dim})")
            if litellm_config.vision_model:
                logger.info(f"  Vision: {litellm_config.vision_model}")

        except ImportError:
            logger.warning("LiteLLM not installed. Install with: pip install litellm")
        except Exception as e:
            logger.error(f"LiteLLM initialization failed: {e}")

    # Priority 3: Require manual functions if no LiteLLM
    if not llm_func:
        raise ValueError(
            "No LLM model function provided. Either:\n"
            "1. Provide llm_model_func manually, OR\n"
            "2. Enable LiteLLM: RAGAnything(config=RAGAnythingConfig(use_litellm=True))"
        )

    # Store functions
    self.llm_model_func = llm_func
    self.embedding_func = embed_func
    self.vision_model_func = vision_func

    # Continue with existing LightRAG initialization...
    # (rest of method unchanged)
```

**Nota:** Integrar cuidadosamente con lógica existente. No romper backward compatibility.

#### 2.3 Actualizar env.example (10 min)

**Archivo:** `env.example`

**Añadir sección LiteLLM:**

```bash
# ============================================================
# LITELLM CONFIGURATION (OPTIONAL)
# ============================================================
# LiteLLM provides unified access to 100+ LLM providers
# Enable with: RAGAnything(config=RAGAnythingConfig(use_litellm=True))

# LLM Model (format: provider/model-name)
# Examples: openai/gpt-4o, anthropic/claude-3-5-sonnet-20241022,
#           gemini/gemini-2.0-flash-exp, ollama/llama2
LITELLM_LLM_MODEL=openai/gpt-4o

# Embedding Model
# Examples: openai/text-embedding-3-large, gemini/text-embedding-004
LITELLM_EMBEDDING_MODEL=openai/text-embedding-3-large
LITELLM_EMBEDDING_DIM=3072

# Vision Model (optional, for multimodal queries)
LITELLM_VISION_MODEL=openai/gpt-4o

# Model Parameters
LITELLM_TEMPERATURE=0.0
LITELLM_MAX_TOKENS=32768

# API Configuration (optional, if not using provider defaults)
# LITELLM_API_KEY=your-api-key-here
# LITELLM_BASE_URL=https://custom-endpoint.com
```

#### 2.4 Verificar Integration (5 min)

```bash
# Test import
python -c "from raganything import RAGAnything, RAGAnythingConfig; print('✅ Import successful')"

# Test config
python -c "
from raganything import RAGAnythingConfig
from raganything.litellm_adapter import LiteLLMConfig

config = RAGAnythingConfig(
    use_litellm=True,
    litellm_config=LiteLLMConfig(llm_model='openai/gpt-4o')
)
print('✅ Config creation successful')
"
```

### Criterios de Éxito:
- [ ] `config.py` modificado con litellm_config
- [ ] `raganything.py` con auto-initialization logic
- [ ] Backward compatible (tests existentes pasan)
- [ ] `env.example` actualizado
- [ ] Imports funcionando

### Checkpoint:
🛑 **STOP - Verificar integration antes de continuar a FASE 3**

---

## 🧪 FASE 3: TESTING COMPREHENSIVE (1 hora)

### Objetivos:
- ✅ Crear test suite para LiteLLM adapter
- ✅ Verificar 3 providers (OpenAI, Anthropic, Gemini)
- ✅ Test backward compatibility
- ✅ Validar que tests existentes no se rompan

### Tareas:

#### 3.1 Crear Test Suite LiteLLM (40 min)

**Archivo:** `test_environment/test_litellm_integration.py`

```python
"""Test suite for LiteLLM integration with RAG-Anything

Tests:
1. LiteLLMConfig creation and from_env()
2. LiteLLMAdapter factory methods
3. Integration with RAGAnything
4. Multiple providers (OpenAI, Anthropic, Gemini)
5. Backward compatibility
"""

import os
import sys
import unittest
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from raganything.litellm_adapter import LiteLLMConfig, LiteLLMAdapter
from raganything import RAGAnything, RAGAnythingConfig


class TestLiteLLMConfig(unittest.TestCase):
    """Test LiteLLMConfig"""

    def test_default_config(self):
        """Test default configuration"""
        config = LiteLLMConfig()
        self.assertEqual(config.llm_model, "openai/gpt-4o")
        self.assertEqual(config.embedding_model, "openai/text-embedding-3-large")
        self.assertEqual(config.embedding_dim, 3072)
        self.assertEqual(config.vision_model, "openai/gpt-4o")

    def test_custom_config(self):
        """Test custom configuration"""
        config = LiteLLMConfig(
            llm_model="anthropic/claude-3-5-sonnet-20241022",
            embedding_model="openai/text-embedding-3-small",
            embedding_dim=1536,
        )
        self.assertEqual(config.llm_model, "anthropic/claude-3-5-sonnet-20241022")
        self.assertEqual(config.embedding_dim, 1536)

    def test_from_env(self):
        """Test loading from environment variables"""
        os.environ["LITELLM_LLM_MODEL"] = "gemini/gemini-2.0-flash-exp"
        os.environ["LITELLM_EMBEDDING_DIM"] = "768"

        config = LiteLLMConfig.from_env()
        self.assertEqual(config.llm_model, "gemini/gemini-2.0-flash-exp")
        self.assertEqual(config.embedding_dim, 768)

        # Cleanup
        del os.environ["LITELLM_LLM_MODEL"]
        del os.environ["LITELLM_EMBEDDING_DIM"]


class TestLiteLLMAdapter(unittest.TestCase):
    """Test LiteLLMAdapter"""

    def setUp(self):
        """Setup test configuration"""
        self.config = LiteLLMConfig(
            llm_model="openai/gpt-4o-mini",  # Use mini for testing
            embedding_model="openai/text-embedding-3-small",
            embedding_dim=1536,
        )
        self.adapter = LiteLLMAdapter(self.config)

    def test_create_llm_func(self):
        """Test LLM function creation"""
        llm_func = self.adapter.create_llm_func()
        self.assertIsNotNone(llm_func)
        self.assertTrue(callable(llm_func))

    def test_create_embedding_func(self):
        """Test embedding function creation"""
        embed_func = self.adapter.create_embedding_func()
        self.assertIsNotNone(embed_func)
        self.assertEqual(embed_func.embedding_dim, 1536)

    def test_create_vision_func(self):
        """Test vision function creation"""
        vision_func = self.adapter.create_vision_func()
        self.assertIsNotNone(vision_func)
        self.assertTrue(callable(vision_func))

    def test_vision_func_none_when_no_model(self):
        """Test vision function is None when vision_model not configured"""
        config = LiteLLMConfig(vision_model=None)
        adapter = LiteLLMAdapter(config)
        vision_func = adapter.create_vision_func()
        self.assertIsNone(vision_func)


class TestRAGAnythingIntegration(unittest.TestCase):
    """Test RAGAnything integration with LiteLLM"""

    @unittest.skipIf(
        not os.getenv("OPENAI_API_KEY"),
        "OPENAI_API_KEY not set, skipping integration test"
    )
    def test_auto_initialization(self):
        """Test auto-initialization with LiteLLM"""
        config = RAGAnythingConfig(
            use_litellm=True,
            litellm_config=LiteLLMConfig(
                llm_model="openai/gpt-4o-mini",
                embedding_model="openai/text-embedding-3-small",
                embedding_dim=1536,
            )
        )

        # This should not raise (auto-initialization)
        rag = RAGAnything(config=config)
        self.assertIsNotNone(rag)

    def test_manual_functions_priority(self):
        """Test that manual functions take priority over LiteLLM"""
        def custom_llm(prompt, **kwargs):
            return "custom response"

        config = RAGAnythingConfig(
            use_litellm=True,
            litellm_config=LiteLLMConfig()
        )

        rag = RAGAnything(
            config=config,
            llm_model_func=custom_llm  # This should take priority
        )

        self.assertEqual(rag.llm_model_func, custom_llm)

    def test_backward_compatibility(self):
        """Test backward compatibility (manual functions still work)"""
        def custom_llm(prompt, **kwargs):
            return "response"

        # Old way (no LiteLLM) should still work
        rag = RAGAnything(llm_model_func=custom_llm)
        self.assertIsNotNone(rag.llm_model_func)


class TestMultipleProviders(unittest.TestCase):
    """Test multiple provider configurations"""

    def test_openai_config(self):
        """Test OpenAI configuration"""
        config = LiteLLMConfig(
            llm_model="openai/gpt-4o",
            embedding_model="openai/text-embedding-3-large",
            embedding_dim=3072,
        )
        self.assertTrue(config.llm_model.startswith("openai/"))

    def test_anthropic_config(self):
        """Test Anthropic (Claude) configuration"""
        config = LiteLLMConfig(
            llm_model="anthropic/claude-3-5-sonnet-20241022",
            embedding_model="openai/text-embedding-3-large",  # Anthropic doesn't have embeddings
            embedding_dim=3072,
        )
        self.assertTrue(config.llm_model.startswith("anthropic/"))

    def test_gemini_config(self):
        """Test Google Gemini configuration"""
        config = LiteLLMConfig(
            llm_model="gemini/gemini-2.0-flash-exp",
            embedding_model="gemini/text-embedding-004",
            embedding_dim=768,  # Gemini embedding dimension
        )
        self.assertTrue(config.llm_model.startswith("gemini/"))

    def test_ollama_config(self):
        """Test Ollama (local) configuration"""
        config = LiteLLMConfig(
            llm_model="ollama/llama2",
            embedding_model="ollama/nomic-embed-text",
            embedding_dim=768,
        )
        self.assertTrue(config.llm_model.startswith("ollama/"))


if __name__ == "__main__":
    print("=" * 60)
    print("LITELLM INTEGRATION TEST SUITE")
    print("=" * 60)

    # Run tests
    unittest.main(verbosity=2)
```

#### 3.2 Ejecutar Tests (10 min)

```bash
# Activate environment
cd C:\Users\Gamer\Dev\RAG-Anything
.\rag_anything_env\Scripts\activate

# Set UTF-8 encoding
export PYTHONIOENCODING=utf-8

# Run LiteLLM tests
python test_environment/test_litellm_integration.py

# Expected output: All tests passing (may skip API tests if no key)
```

#### 3.3 Verificar Tests Existentes (10 min)

```bash
# Run existing test suite to verify no regression
python test_environment/03_post_validation_tests.py

# Expected: 8/8 tests passing (same as baseline)
```

### Criterios de Éxito:
- [ ] Test suite creado (~200 líneas)
- [ ] Tests unitarios passing (8+ tests)
- [ ] Integration tests passing (con API key)
- [ ] Tests existentes no se rompieron (8/8 passing)
- [ ] 3+ providers configurados correctamente

### Checkpoint:
🛑 **STOP - Verificar tests antes de continuar a FASE 4**

---

## 📚 FASE 4: DOCUMENTACIÓN Y EJEMPLOS (30 min)

### Objetivos:
- ✅ Crear ejemplo completo con LiteLLM
- ✅ Actualizar README con sección LiteLLM
- ✅ Crear guía de migración
- ✅ Documentar provider switching

### Tareas:

#### 4.1 Crear Ejemplo LiteLLM (15 min)

**Archivo:** `examples/litellm_example.py`

```python
"""Example: Using LiteLLM with RAG-Anything

This example demonstrates how to use LiteLLM to switch between different
LLM providers (OpenAI, Anthropic, Gemini, Ollama) with minimal code changes.

Features:
- Config-based provider switching
- Support for 100+ providers
- Automatic model function creation
- Environment variable configuration
"""

import asyncio
import os
from pathlib import Path

from raganything import RAGAnything, RAGAnythingConfig
from raganything.litellm_adapter import LiteLLMConfig


async def main():
    # Example 1: OpenAI (default)
    print("=" * 60)
    print("Example 1: OpenAI GPT-4o")
    print("=" * 60)

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


    # Example 2: Anthropic Claude
    print("\n" + "=" * 60)
    print("Example 2: Anthropic Claude 3.5 Sonnet")
    print("=" * 60)

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


    # Example 3: Google Gemini
    print("\n" + "=" * 60)
    print("Example 3: Google Gemini 2.0 Flash")
    print("=" * 60)

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


    # Example 4: From Environment Variables
    print("\n" + "=" * 60)
    print("Example 4: Load from Environment Variables")
    print("=" * 60)

    # Set environment variables (or put in .env file)
    os.environ["LITELLM_LLM_MODEL"] = "openai/gpt-4o"
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

    print(f"✅ RAGAnything initialized from env vars")
    print(f"   LLM: {config_env.llm_model}")
    print(f"   Embedding: {config_env.embedding_model} (dim={config_env.embedding_dim})")


    # Example 5: Cost Optimization Strategy
    print("\n" + "=" * 60)
    print("Example 5: Cost Optimization (Cheap Models)")
    print("=" * 60)

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
    print("   Estimated cost savings: 90% vs GPT-4o + large embeddings")


    print("\n" + "=" * 60)
    print("✅ All Examples Completed Successfully!")
    print("=" * 60)
    print("\nSwitching providers is as simple as changing 1 line:")
    print('  config.llm_model = "provider/model-name"')
    print("\nSupported providers: 100+")
    print("  - OpenAI, Anthropic, Google, Azure")
    print("  - Ollama, HuggingFace, Groq, Together")
    print("  - And many more!")


if __name__ == "__main__":
    asyncio.run(main())
```

#### 4.2 Actualizar README (10 min)

**Archivo:** `README.md`

**Añadir sección después de "Quick Start":**

```markdown
## 🚀 Using LiteLLM (100+ Providers)

RAG-Anything now supports [LiteLLM](https://github.com/BerriAI/litellm) for unified access to 100+ LLM providers!

### Quick Start with LiteLLM

```python
from raganything import RAGAnything, RAGAnythingConfig
from raganything.litellm_adapter import LiteLLMConfig

# Switch between providers in 1 line!
config = LiteLLMConfig(
    llm_model="anthropic/claude-3-5-sonnet-20241022",  # or "openai/gpt-4o", "gemini/...", etc.
    embedding_model="openai/text-embedding-3-large",
    embedding_dim=3072,
)

rag = RAGAnything(
    config=RAGAnythingConfig(use_litellm=True, litellm_config=config)
)

# Process and query - same code, any provider!
await rag.process_document("document.pdf")
result = await rag.aquery("What's in this document?")
```

### Supported Providers

✅ **OpenAI** - GPT-4o, GPT-4, GPT-3.5
✅ **Anthropic** - Claude 3.5 Sonnet, Claude 3
✅ **Google** - Gemini 2.0, Gemini Pro
✅ **Azure OpenAI** - All Azure models
✅ **Ollama** - Local models (Llama, Mistral, etc.)
✅ **100+ more** - See [LiteLLM docs](https://docs.litellm.ai/docs/providers)

### Environment Configuration

Add to `.env`:

```bash
LITELLM_LLM_MODEL=anthropic/claude-3-5-sonnet-20241022
LITELLM_EMBEDDING_MODEL=openai/text-embedding-3-large
LITELLM_EMBEDDING_DIM=3072
```

Then:

```python
config = LiteLLMConfig.from_env()
rag = RAGAnything(config=RAGAnythingConfig(use_litellm=True, litellm_config=config))
```

See `examples/litellm_example.py` for more examples!
```

#### 4.3 Crear Migration Guide (5 min)

**Archivo:** `docs/LITELLM_MIGRATION_GUIDE.md`

```markdown
# LiteLLM Migration Guide

This guide helps you migrate from manual model functions to LiteLLM.

## Before (Manual Functions)

```python
from raganything import RAGAnything

def llm_model_func(prompt, system_prompt=None, history_messages=[], **kwargs):
    return openai_complete_if_cache("gpt-4o", prompt, **kwargs)

rag = RAGAnything(llm_model_func=llm_model_func)
```

## After (LiteLLM)

```python
from raganything import RAGAnything, RAGAnythingConfig
from raganything.litellm_adapter import LiteLLMConfig

config = LiteLLMConfig(llm_model="openai/gpt-4o")
rag = RAGAnything(config=RAGAnythingConfig(use_litellm=True, litellm_config=config))
```

## Benefits

✅ Switch providers in 1 line (no code changes)
✅ 100+ providers supported
✅ Enterprise features (retry, fallback, cost tracking)
✅ Environment variable configuration

## Provider Examples

### OpenAI
```python
config = LiteLLMConfig(llm_model="openai/gpt-4o")
```

### Anthropic Claude
```python
config = LiteLLMConfig(llm_model="anthropic/claude-3-5-sonnet-20241022")
```

### Google Gemini
```python
config = LiteLLMConfig(llm_model="gemini/gemini-2.0-flash-exp")
```

### Ollama (Local)
```python
config = LiteLLMConfig(llm_model="ollama/llama2")
```

## Backward Compatibility

Manual functions still work! LiteLLM is optional.

```python
# This still works
rag = RAGAnything(llm_model_func=my_custom_function)
```
```

### Criterios de Éxito:
- [ ] Ejemplo LiteLLM creado (5 casos de uso)
- [ ] README actualizado con sección LiteLLM
- [ ] Migration guide creado
- [ ] Documentación clara y completa

### Checkpoint:
🛑 **STOP - Revisar documentación antes de commit final**

---

## ✅ CRITERIOS DE ACEPTACIÓN FINAL

### Funcionalidad:
- [ ] LiteLLM instalado y funcionando
- [ ] `litellm_adapter.py` implementado (~250 líneas)
- [ ] Integration con RAGAnythingConfig completa
- [ ] Auto-initialization funcionando
- [ ] 3+ providers configurables (OpenAI, Anthropic, Gemini)

### Testing:
- [ ] Test suite LiteLLM: 8+ tests passing
- [ ] Tests existentes: 8/8 passing (no regression)
- [ ] Integration tests con API key funcionando

### Documentación:
- [ ] Ejemplo completo (`examples/litellm_example.py`)
- [ ] README actualizado
- [ ] Migration guide creado
- [ ] `env.example` actualizado

### Backward Compatibility:
- [ ] Funciones manuales siguen funcionando
- [ ] No breaking changes
- [ ] Priority: manual > LiteLLM > error

---

## 🔄 COMMITS RECOMENDADOS

### Commit 1: Adapter Creation
```bash
git add raganything/litellm_adapter.py requirements.txt
git commit -m "feat: add LiteLLM adapter for 100+ provider support

- Create LiteLLMConfig dataclass with from_env() method
- Create LiteLLMAdapter with llm, embedding, vision factories
- Support OpenAI, Anthropic, Gemini, Ollama, and 100+ providers
- Add litellm dependency to requirements.txt

Part of LiteLLM integration (Phase 1/4)"
```

### Commit 2: Integration
```bash
git add raganything/config.py raganything/raganything.py env.example
git commit -m "feat: integrate LiteLLM with RAGAnything auto-initialization

- Add use_litellm and litellm_config to RAGAnythingConfig
- Implement auto-initialization in _ensure_lightrag_initialized
- Maintain backward compatibility with manual functions
- Add LiteLLM env vars to env.example

Part of LiteLLM integration (Phase 2/4)"
```

### Commit 3: Testing
```bash
git add test_environment/test_litellm_integration.py
git commit -m "test: add comprehensive test suite for LiteLLM integration

- Test LiteLLMConfig creation and from_env()
- Test LiteLLMAdapter factory methods
- Test RAGAnything integration and auto-init
- Test multiple providers (OpenAI, Anthropic, Gemini, Ollama)
- Test backward compatibility

Part of LiteLLM integration (Phase 3/4)"
```

### Commit 4: Documentation
```bash
git add examples/litellm_example.py README.md docs/LITELLM_MIGRATION_GUIDE.md
git commit -m "docs: add LiteLLM examples and migration guide

- Add litellm_example.py with 5 usage examples
- Update README with LiteLLM quick start section
- Create migration guide for existing users
- Document provider switching and configuration

Part of LiteLLM integration (Phase 4/4)

✅ LiteLLM integration complete - 100+ providers now supported!"
```

---

## 🎯 SIGUIENTE SESIÓN: PASOS DE REANUDACIÓN

### Quick Start Commands:

```bash
# 1. Verificar branch
git status
# Expected: On branch feature/multimodal-development-framework

# 2. Ver último commit
git log -1
# Expected: "docs: session checkpoint 2025-11-07" or later

# 3. Verificar tests baseline
export PYTHONIOENCODING=utf-8
python test_environment/03_post_validation_tests.py
# Expected: 8/8 passing

# 4. Comenzar FASE 0
# Ver sección FASE 0 arriba para comandos
```

### Archivos Clave para Revisión:

1. **Este plan:** `docs/workflows/PLAN_INTEGRACION_LITELLM_2025-11-07.md`
2. **Investigación:** `docs/workflows/INVESTIGACION_LITELLM_2025-11-07.md`
3. **Plan original:** `PLAN_DESARROLLO_MULTIMODAL.md` (actualizado)
4. **Checkpoint:** `CONTINUIDAD_SESION_2025-11-07.md`

---

## 📊 MÉTRICAS DE ÉXITO

| Métrica | Target | Medición |
|---------|--------|----------|
| **Tiempo desarrollo** | 4 horas | Real time tracking |
| **Providers soportados** | 3+ | OpenAI, Anthropic, Gemini mínimo |
| **Tests passing** | 100% | Test suite + existing tests |
| **Code coverage** | Adapter 100% | Unit tests coverage |
| **Documentation** | Completa | Example + README + guide |
| **Backward compat** | 100% | No breaking changes |
| **User satisfaction** | Alto | Easy provider switching |

---

## 🚨 RIESGOS Y MITIGACIONES

| Riesgo | Probabilidad | Mitigación |
|--------|--------------|------------|
| API keys no disponibles | Media | Skip integration tests, unit tests suficientes |
| Import conflicts | Baja | Lazy imports, try/except blocks |
| Performance overhead | Muy baja | <10ms overhead aceptable |
| Breaking changes future | Media | Pin version, comprehensive tests |

---

**Plan creado:** 2025-11-07
**Estimación total:** 4 horas
**Status:** ⏳ READY TO EXECUTE
**Siguiente paso:** Obtener aprobación para FASE 0
