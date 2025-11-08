"""
PRE-TEST: Verificar el problema actual con vision_model_func faltante
======================================================================
Este test documenta el estado ANTES del fix para demostrar que:
1. El Knowledge Graph YA existe y está completo
2. Las consultas fallan por falta de vision_model_func
3. El error específico es "No LightRAG instance available"
"""

import asyncio
import json
import os
import sys
from pathlib import Path

# Agregar el directorio padre al path
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

from raganything import RAGAnything, RAGAnythingConfig
from lightrag.llm.openai import openai_complete_if_cache, openai_embed, gpt_4o_complete
from lightrag.utils import EmbeddingFunc


def print_section(title):
    """Helper para imprimir secciones"""
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


async def verify_kg_exists():
    """Verificar que el Knowledge Graph existe y está completo"""
    print_section("1. VERIFICACIÓN: KNOWLEDGE GRAPH EXISTENTE")
    
    rag_storage = Path("test_environment/rag_storage")
    
    # Verificar directorio
    if not rag_storage.exists():
        print("[ERROR] Directorio rag_storage NO existe")
        return False
    
    print(f"[OK] Directorio existe: {rag_storage}")
    
    # Verificar archivos críticos
    critical_files = [
        "kv_store_full_docs.json",
        "kv_store_doc_status.json", 
        "kv_store_full_entities.json",
        "kv_store_full_relations.json",
        "vdb_entities.json",
        "vdb_relationships.json",
        "graph_chunk_entity_relation.graphml"
    ]
    
    all_exist = True
    for file_name in critical_files:
        file_path = rag_storage / file_name
        if file_path.exists():
            size_kb = file_path.stat().st_size / 1024
            print(f"  [OK] {file_name}: {size_kb:.1f} KB")
        else:
            print(f"  [ERROR] {file_name}: NO EXISTE")
            all_exist = False
    
    # Verificar contenido de full_docs
    full_docs_path = rag_storage / "kv_store_full_docs.json"
    try:
        with open(full_docs_path, 'r', encoding='utf-8') as f:
            full_docs = json.load(f)
        print(f"\n[INFO] Documentos en full_docs: {len(full_docs)}")
        for doc_id in full_docs.keys():
            content_len = len(full_docs[doc_id].get('content', ''))
            print(f"  - {doc_id}: {content_len} caracteres")
    except Exception as e:
        print(f"[ERROR] No se pudo leer full_docs: {e}")
        all_exist = False
    
    return all_exist


async def test_query_without_vision():
    """Intentar query SIN vision_model_func - debe fallar"""
    print_section("2. TEST: QUERY SIN vision_model_func")
    
    try:
        # Configuración SIN vision_model_func (problema actual)
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("[ERROR] OPENAI_API_KEY no configurada")
            return None
        
        # Configurar funciones (igual que build_kg_from_docling.py)
        def llm_model_func(prompt, system_prompt=None, history_messages=[], **kwargs):
            return openai_complete_if_cache(
                "gpt-4o-mini",
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
        
        # Crear instancia SIN vision_model_func
        rag_storage = Path("test_environment/rag_storage")
        config = RAGAnythingConfig(working_dir=str(rag_storage))
        
        print("[INFO] Creando RAGAnything SIN vision_model_func...")
        rag = RAGAnything(
            config=config,
            llm_model_func=llm_model_func,
            # vision_model_func=vision_model_func,  # FALTA ESTO
            embedding_func=embedding_func
        )
        
        # Intentar query
        test_query = "¿Qué son las prestaciones económicas?"
        print(f"[INFO] Ejecutando query: {test_query}")
        
        response = await rag.aquery(test_query, mode="hybrid")
        
        # Si llegamos aquí, algo anda mal
        print(f"[UNEXPECTED] Query funcionó sin vision_model_func: {response[:100]}...")
        return "UNEXPECTED_SUCCESS"
        
    except ValueError as e:
        if "No LightRAG instance available" in str(e):
            print(f"[EXPECTED ERROR] {e}")
            return "EXPECTED_ERROR"
        else:
            print(f"[UNEXPECTED ERROR] {e}")
            return "UNEXPECTED_ERROR"
    except Exception as e:
        print(f"[ERROR] Excepción inesperada: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return "EXCEPTION"


async def test_query_with_vision():
    """Intentar query CON vision_model_func - debe funcionar"""
    print_section("3. TEST: QUERY CON vision_model_func")
    
    try:
        # Configuración CON vision_model_func (solución propuesta)
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("[ERROR] OPENAI_API_KEY no configurada")
            return None
        
        # Configurar funciones (igual que build_kg_from_docling.py)
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
                base64_images=image_data if isinstance(image_data, list) else [image_data] if image_data else [],
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
        
        # Crear instancia CON vision_model_func
        rag_storage = Path("test_environment/rag_storage")
        config = RAGAnythingConfig(working_dir=str(rag_storage))
        
        print("[INFO] Creando RAGAnything CON vision_model_func...")
        rag = RAGAnything(
            config=config,
            llm_model_func=llm_model_func,
            vision_model_func=vision_model_func,  # INCLUIDO
            embedding_func=embedding_func
        )
        
        # Intentar query
        test_query = "¿Qué son las prestaciones económicas?"
        print(f"[INFO] Ejecutando query: {test_query}")
        
        response = await rag.aquery(test_query, mode="hybrid")
        
        print(f"[SUCCESS] Query funcionó CON vision_model_func")
        print(f"[RESPONSE] {response[:200]}..." if len(str(response)) > 200 else f"[RESPONSE] {response}")
        return "SUCCESS"
        
    except Exception as e:
        print(f"[ERROR] Con vision_model_func: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return "ERROR"


async def main():
    """Ejecutar todos los pre-tests"""
    print_section("PRE-TEST: VISION_MODEL_FUNC EN QUERIES")
    print("Objetivo: Documentar el problema actual antes del fix")
    
    results = {}
    
    # 1. Verificar KG existe
    kg_exists = await verify_kg_exists()
    results['kg_exists'] = kg_exists
    
    if not kg_exists:
        print("\n[STOP] Knowledge Graph no existe. Ejecutar primero build_kg_from_docling.py")
        return results
    
    # 2. Test sin vision_model_func (debe fallar)
    result_without = await test_query_without_vision()
    results['query_without_vision'] = result_without
    
    # 3. Test con vision_model_func (debe funcionar)
    result_with = await test_query_with_vision()
    results['query_with_vision'] = result_with
    
    # Resumen
    print_section("RESUMEN DE PRE-TEST")
    print(f"1. Knowledge Graph existe: {results['kg_exists']}")
    print(f"2. Query SIN vision_model_func: {results['query_without_vision']}")
    print(f"3. Query CON vision_model_func: {results['query_with_vision']}")
    
    # Diagnóstico
    print("\n" + "=" * 60)
    if results['query_without_vision'] == "EXPECTED_ERROR" and results['query_with_vision'] == "SUCCESS":
        print("[DIAGNÓSTICO] CONFIRMADO: El problema es la falta de vision_model_func")
        print("[SOLUCIÓN] Agregar vision_model_func a la segunda instancia en línea 485")
        print("[ARCHIVO] test_environment/build_kg_from_docling.py")
    else:
        print("[DIAGNÓSTICO] Resultados inesperados - revisar manualmente")
    print("=" * 60)
    
    return results


if __name__ == "__main__":
    results = asyncio.run(main())
    
    # Exit code basado en resultados
    if results.get('query_without_vision') == "EXPECTED_ERROR":
        sys.exit(0)  # Comportamiento esperado documentado
    else:
        sys.exit(1)  # Algo inesperado