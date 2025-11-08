# LiteLLM Integration - Known Issues

**Última actualización:** 2025-11-08
**Branch:** feature/multimodal-development-framework
**Status:** Ready for PR with documented workaround

---

## 🐛 Issue #1: Gemini Embeddings - TypeError Async Wrapper

### Descripción
Al usar embeddings de Gemini via LiteLLM, se produce un error de tipo:
```
TypeError: object list can't be used in 'await' expression
```

### Impacto
- **Severidad:** 🟡 Media
- **Afecta:** Solo embeddings de Gemini via LiteLLM
- **NO afecta:** LLM de Gemini (funciona perfectamente)
- **NO afecta:** Ollama embeddings
- **NO afecta:** Sistema legacy de embeddings

### Reproducción
```python
from raganything import RAGAnything, RAGAnythingConfig
from raganything.litellm_adapter import LiteLLMConfig

# Esto falla en embeddings (LLM funciona bien)
config = LiteLLMConfig(
    llm_model="gemini/gemini-2.5-pro",  # ✅ Funciona
    embedding_model="gemini/gemini-embedding-001"  # ❌ Falla
)

rag = RAGAnything(config=RAGAnythingConfig(
    use_litellm=True,
    litellm_config=config
))

# LLM funciona:
await rag._ensure_lightrag_initialized()
response = rag.llm_model_func("Hello")  # ✅ OK

# Embeddings fallan:
embeddings = await rag.embedding_func(["test"])  # ❌ TypeError
```

### Causa Raíz
La función `embed_func` en `litellm_adapter.py` es **síncrona**:
```python
# raganything/litellm_adapter.py:253
def embed_func(texts: List[str]) -> List[List[float]]:  # Síncrono
    results = []
    for text in texts:
        response = embedding(**call_kwargs)  # litellm.embedding es síncrono
        results.append(response.data[0].embedding)
    return results
```

Pero LightRAG la envuelve en un wrapper async que espera una función async-compatible.

### Workaround (Solución temporal)

**Opción A: Usar sistema legacy para embeddings**
```python
# .env
EMBEDDING_BINDING=ollama  # O tu preferido
EMBEDDING_MODEL=nomic-embed-text
EMBEDDING_DIM=768

# Código
config = LiteLLMConfig(
    llm_model="gemini/gemini-2.5-pro",  # Solo LLM via LiteLLM
    # NO configurar embedding_model, usar legacy
)
```

**Opción B: Usar Ollama para embeddings**
```bash
ollama pull nomic-embed-text
```

```python
config = LiteLLMConfig(
    llm_model="gemini/gemini-2.5-pro",
    embedding_model="ollama/nomic-embed-text",  # Local, funciona
    embedding_dim=768
)
```

**Opción C: Combinar providers**
```python
# Gemini para LLM, OpenAI/Ollama para embeddings
config = LiteLLMConfig(
    llm_model="gemini/gemini-2.5-pro",
    embedding_model="openai/text-embedding-3-small",  # Si tienes créditos
    embedding_dim=1536
)
```

### Fix Planificado
```python
# Solución: Hacer la función async-compatible
async def embed_func(texts: List[str]) -> List[List[float]]:
    """Async embedding function using LiteLLM"""
    results = []
    for text in texts:
        call_kwargs = {
            "model": config.embedding_model,
            "input": text,
        }
        # Envolver llamada síncrona en async
        response = await asyncio.to_thread(embedding, **call_kwargs)
        results.append(response.data[0].embedding)
    return results
```

**Estimación:** 15-20 minutos
**Prioridad:** Media (workaround disponible)
**Milestone:** Next iteration after PR merge

---

## ✅ Issues Resueltos

### ~~Issue: Falta validación de API keys~~
**Status:** ✅ Resuelto en commit e79a646

- Implementado `check_provider_api_key()`
- Warnings automáticos cuando falta API key
- Mapeo de 8 providers comunes

### ~~Issue: Sin tests con modelos reales~~
**Status:** ✅ Resuelto

- Tests con Ollama: 2/2 PASS
- Tests con Gemini LLM: ✅ PASS
- Tests unitarios: 6/6 PASS
- Tests existentes: 8/8 PASS

---

## 📝 Notas para Siguiente Iteración

### Mejoras Sugeridas
1. **Fix Gemini embeddings async** (Prioridad: Media)
2. **Añadir más tests de integración** con diferentes providers
3. **Documentar best practices** para selección de embeddings
4. **Performance testing** con grandes volúmenes

### No Planificado (Fuera de Scope)
- ❌ Gestionar embeddings de Docling/MinerU (decisión: mantener internos)
- ❌ Soporte para providers exóticos sin API key mapping
- ❌ Auto-detection de modelos disponibles en Ollama

---

**Documento creado:** 2025-11-08
**Mantenedor:** RAG-Anything Team
**Contacto:** Reportar issues en GitHub
