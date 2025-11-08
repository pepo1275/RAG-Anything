import asyncio
import os
from raganything import RAGAnything, RAGAnythingConfig
from lightrag.llm.openai import openai_complete_if_cache, openai_embed
from lightrag.utils import EmbeddingFunc
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

async def procesar_documento():
    print("🚀 Iniciando procesamiento...")
    
    # Obtener API key del archivo .env
    api_key = os.getenv("LLM_BINDING_API_KEY")
    base_url = os.getenv("LLM_BINDING_HOST")  # Opcional
    
    if not api_key:
        print("❌ Error: No se encontró LLM_BINDING_API_KEY en el archivo .env")
        return
    
    print("🔑 API key cargada correctamente")
    
    # Configuración básica
    config = RAGAnythingConfig(
        working_dir="./rag_storage",
        parser="mineru",
        parse_method="auto",
        enable_image_processing=True,
        enable_table_processing=True,
        enable_equation_processing=True,
    )
    
    # Definir función del modelo LLM
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
    
    # Definir función de embedding
    embedding_func = EmbeddingFunc(
        embedding_dim=3072,
        max_token_size=8192,
        func=lambda texts: openai_embed(
            texts,
            model="text-embedding-3-large",
            api_key=api_key,
            base_url=base_url,
        ),
    )
    
    # Iniciar RAG-Anything con configuración completa
    rag = RAGAnything(
        config=config,
        llm_model_func=llm_model_func,
        embedding_func=embedding_func,
    )
    print("✅ RAG-Anything listo")
    
    # Listar documentos disponibles
    documentos = [f for f in os.listdir("./data/documents") if f.endswith('.pdf')]
    
    if documentos:
        documento = documentos[0]  # Tomar el primero
        print(f"📄 Procesando: {documento}")
        
        # Procesar documento
        await rag.process_document_complete(
            file_path=f"./data/documents/{documento}",
            output_dir="./data/output",
            parse_method="auto"
        )
        print("🎉 ¡Documento procesado exitosamente!")
        
        # Hacer algunas consultas de prueba
        print("\n🔍 Realizando consultas de prueba...")
        
        consultas = [
            "¿Cuál es el contenido principal de este documento?",
            "¿De qué trata la ordenanza?",
        ]
        
        for i, consulta in enumerate(consultas, 1):
            print(f"\n[Consulta {i}]: {consulta}")
            try:
                resultado = await rag.aquery(consulta, mode="hybrid")
                print(f"Respuesta: {resultado}")
            except Exception as e:
                print(f"Error en consulta: {e}")
    else:
        print("❌ No hay documentos PDF en la carpeta")

# Ejecutar
asyncio.run(procesar_documento())