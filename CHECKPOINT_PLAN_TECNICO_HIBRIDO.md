# 📋 CHECKPOINT - PLAN TÉCNICO HÍBRIDO

**Fecha:** 29 de Agosto, 2025  
**Fase:** FASE B - Plan técnico detallado basado en investigación completa  
**Estado:** Decisión estratégica documentada

---

## 🎯 DECISIÓN ESTRATÉGICA TOMADA

### **ENFOQUE SELECCIONADO:** Adaptar `build_kg_from_docling.py` con elementos híbridos

**Justificación:**
- ✅ No tocar archivos originales (metodología CLAUDE.md)
- ✅ Mantener registro de adaptaciones hasta validación
- ✅ Integrar lo mejor de investigación completa
- ✅ Un solo archivo final vs múltiples versiones

---

## 🔍 INVESTIGACIÓN COMPLETADA - FUENTES IDENTIFICADAS

### **FUENTE 1: Ejemplo oficial** (`examples/insert_content_list_example.py`)
**Elementos clave extraídos:**
- Configuración RAGAnythingConfig correcta
- Funciones LLM/embedding requeridas (llm_model_func, vision_model_func, embedding_func)  
- Método insert_content_list() con parámetros oficiales
- Formato content_list estándar: `[{"type": "text", "text": "...", "page_idx": 0}]`
- Queries de prueba con aquery()

### **FUENTE 2: Script existente** (`test_environment/build_kg_from_existing.py`)
**Elementos valiosos identificados:**
- Verificaciones robustas de prerequisitos
- Carga y procesamiento de metadata.json
- Validación exhaustiva de archivos generados
- Estadísticas completas de construcción
- Manejo de errores comprehensive
- **PROBLEMA:** Usa method incorrecto `index_documents()` vs `insert_content_list()`

### **FUENTE 3: Implementación real** (`raganything/processor.py`)
**Especificaciones técnicas:**
- Firma exacta del método insert_content_list()
- Parámetros opcionales: split_by_character, doc_id, display_stats
- Tipos de contenido soportados: text, image, table, equation
- Estructura requerida para cada tipo

---

## 📋 PLAN DE ADAPTACIÓN HÍBRIDA

### **ARCHIVO OBJETIVO:** `test_environment/build_kg_from_docling.py`

### **ELEMENTOS A INTEGRAR:**

#### **1. VERIFICACIONES (de build_kg_from_existing.py)**
```python
# Prerequisitos detallados
- Verificar content.json existe y es válido
- Verificar metadata.json existe  
- Verificar API key disponible
- Verificar RAGAnything importable
- Verificar estructura content.json correcta
```

#### **2. CONFIGURACIÓN (de insert_content_list_example.py)**
```python
config = RAGAnythingConfig(
    working_dir="test_environment/rag_storage",
    enable_image_processing=True,
    enable_table_processing=True,
    enable_equation_processing=True,
    display_content_stats=True
)

llm_model_func = lambda prompt, **kwargs: openai_complete_if_cache(...)
vision_model_func = lambda prompt, **kwargs: openai_complete_if_cache("gpt-4o", ...)
embedding_func = EmbeddingFunc(embedding_dim=3072, func=lambda texts: openai_embed(...))
```

#### **3. CONVERSIÓN DATOS (investigación propia)**
```python
def convert_docling_to_content_list(docling_data):
    # Procesar docling_data["texts"] → content_list format oficial
    # Extraer page_idx desde bbox o estructura
    # Soportar tables, images si existen
    # Validar estructura final
```

#### **4. MÉTODO CORRECTO (de investigación)**
```python
await rag.insert_content_list(
    content_list=content_list,
    file_path="12.1-ORDENANZA-ESPECIFICA-REGULADORA-DE-LAS-PRESTACIONES-ECONOMICAS.pdf",
    doc_id="ordenanza-prestaciones-001",
    display_stats=True
)
```

#### **5. VALIDACIÓN (de build_kg_from_existing.py mejorado)**
```python
# Verificar archivos generados en rag_storage/
# Cargar y validar estructura KG si existe
# Ejecutar consulta de prueba básica
# Generar estadísticas completas
```

---

## 🧪 METODOLOGÍA TEST PRE/POST REQUERIDA

### **ANTES DE IMPLEMENTAR ADAPTACIONES:**

#### **TESTS PRE específicos necesarios:**
1. **Estado actual:** Verificar que content.json y metadata.json siguen válidos
2. **API keys:** Confirmar OpenAI API disponible  
3. **Imports:** Verificar que RAGAnything y dependencias funcionan
4. **Espacio:** Verificar espacio disponible para rag_storage/
5. **Permisos:** Verificar permisos escritura en test_environment/

#### **CRITERIOS DE ACEPTACIÓN PRE:**
- content.json existe y > 280KB
- metadata.json existe y válido JSON
- OpenAI API key disponible y funcional
- RAGAnything importable sin errores
- Directorio test_environment/ con permisos escritura

### **DESPUÉS DE IMPLEMENTAR ADAPTACIONES:**

#### **TESTS POST específicos necesarios:**
1. **Construcción exitosa:** rag_storage/ creado con archivos
2. **Knowledge Graph:** Archivos KG generados y válidos
3. **Estadísticas:** build_stats.json con success=true
4. **Consultas:** Query de prueba funcional
5. **Integridad:** Archivos no corruptos

#### **CRITERIOS DE ACEPTACIÓN POST:**
- rag_storage/ existe con archivos > 0 bytes
- build_stats.json indica success=true
- Al menos 1 archivo de KG generado
- Query básica responde sin errores
- Tiempo construcción < 5 minutos

---

## 🚦 PRÓXIMOS PASOS METODOLOGÍA

### **PASO 1: TESTS PRE específicos** 🛑 **STOP - APROBAR**
Ejecutar validaciones específicas antes de tocar build_kg_from_docling.py

### **PASO 2: ADAPTAR ARCHIVO** 🛑 **STOP - APROBAR** 
Integrar elementos identificados en build_kg_from_docling.py

### **PASO 3: TESTS POST específicos** 🛑 **STOP - APROBAR**
Validar resultado con criterios de aceptación definidos

### **PASO 4: SAFETY COMMIT** 🛑 **STOP - APROBAR**
Guardar estado si tests POST exitosos

---

## 📝 REGISTRO DE DECISIONES

### **DECISIONES TOMADAS:**
1. ✅ **No modificar archivos originales** - Mantener backup intacto
2. ✅ **Adaptar build_kg_from_docling.py** - Un archivo híbrido final  
3. ✅ **Integrar 3 fuentes** - Ejemplo oficial + script existente + investigación
4. ✅ **Metodología completa** - Tests PRE/POST + criterios específicos

### **DECISIONES PENDIENTES:**
- [ ] **Manejo de errores:** Nivel de detalle en logging
- [ ] **Timeout:** Tiempo máximo para construcción KG
- [ ] **Cleanup:** Limpiar archivos temporales si falla

---

## ⚠️ RIESGOS IDENTIFICADOS

1. **API Rate Limits:** Construcción KG puede consumir muchas llamadas OpenAI
2. **Espacio disco:** Archivos KG pueden ser grandes
3. **Dependencias:** Versiones específicas de RAGAnything requeridas
4. **Formato datos:** Estructura Docling puede cambiar

---

## 🎯 RESULTADO ESPERADO

**Al completar adaptación híbrida:**
- ✅ Script build_kg_from_docling.py funcional completo
- ✅ Knowledge Graph construido desde content.json Docling  
- ✅ Sistema responde consultas sobre ordenanza prestaciones
- ✅ Tests POST validan construcción exitosa
- ✅ Documentación completa del proceso

---

**💾 CHECKPOINT GUARDADO**

*Este documento registra la decisión estratégica y plan técnico antes de implementar*

*Próximo: Ejecutar TESTS PRE específicos para validar precondiciones*

*Fecha: 29 de Agosto, 2025*