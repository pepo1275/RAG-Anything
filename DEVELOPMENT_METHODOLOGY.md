# 📋 METODOLOGÍA DE DESARROLLO PROFESIONAL - RAG-ANYTHING PROJECT

## 🎯 PRINCIPIO FUNDAMENTAL

**NUNCA pasar del plan a la acción sin aprobación explícita del usuario**

---

## 🔀 ESTRATEGIA GIT & GITHUB

### ESTRUCTURA DE BRANCHES

1. **main** - Producción estable
2. **feature/multimodal-***  - Características procesamiento multimodal
3. **feature/rag-***  - Mejoras sistema RAG y retrieval
4. **feature/modal-processors-***  - Procesadores especializados de contenido
5. **feature/knowledge-graph-***  - Knowledge graph multimodal
6. **hotfix/*** - Fixes urgentes

### NOMENCLATURA DE COMMITS
```
type(scope): descripción breve

Detalles adicionales si son necesarios
- Cambio 1
- Cambio 2

Refs: #issue-number
```

**Tipos válidos:** feat, fix, docs, test, refactor, style, chore

---

## 📊 PIPELINE DE DESARROLLO - 7 FASES

### 🆕 FASE 0: SETUP INICIAL
**Checkpoint obligatorio** - **STOP hasta aprobación**

1. **Verificación del entorno**
   ```bash
   git status
   git branch --show-current
   ```

2. **Configuración de herramientas**
   - Dependencias instaladas (requirements.txt)
   - Variables de entorno configuradas (.env)
   - RAG-Anything + dependencias verificadas
   - Linters (ruff) - Test runners (pytest)
   - Environment setup validated

3. **🛑 CHECKPOINT 0:** Confirmar setup → **Esperar aprobación explícita**

---

### 🔍 FASE 1: ANÁLISIS Y DOCUMENTACIÓN
**Checkpoint obligatorio** - **STOP hasta aprobación**

1. **Análisis de requisitos**
   - Entender el problema completamente
   - Identificar dependencias multimodales
   - Mapear impacto en el sistema RAG

2. **Investigación técnica**
   - Revisar código existente multimodal
   - Identificar patrones y convenciones RAG-Anything
   - Evaluar herramientas disponibles (modal processors)

3. **Documentación inicial**
   - README técnico específico
   - Notas de investigación multimodal
   - Decisiones técnicas arquitectura

4. **🛑 CHECKPOINT 1:** Análisis completado → **Esperar aprobación explícita**

---

### 📝 FASE 2: PLANIFICACIÓN DETALLADA
**Checkpoint obligatorio** - **STOP hasta aprobación**

1. **Arquitectura del sistema**
   - Diseño de componentes multimodales
   - Interfaces y APIs RAG
   - Flujo de datos end-to-end
   - Diseño pipeline: Documents → Processors → Knowledge Graph → Query
   - Configuración modal processors especializados
   - Flujo de procesamiento documents con contenido mixto
   - Integration con LightRAG base

2. **Plan de implementación**
   - Breakdowns de tareas multimodales
   - Estimaciones de tiempo
   - Identificación de riesgos

3. **Estrategia de testing**
   - Tests unitarios por modalidad
   - Tests de integración multimodal
   - Coverage objectives sistema completo

4. **Plan de commits**
   - Commits atómicos por componente
   - Mensajes descriptivos
   - Frecuencia de push

5. **🛑 CHECKPOINT 2:** Plan detallado → **Esperar aprobación explícita**

---

### 🎨 FASE 3: DISEÑO TÉCNICO
**Checkpoint obligatorio** - **STOP hasta aprobación**

1. **Diseño de interfaces**
   - APIs públicas multimodales
   - Contratos de datos entre procesadores
   - Manejo de errores específicos

2. **Patrones de diseño**
   - Principios SOLID aplicados a RAG
   - Patrones apropiados para multimodal
   - Convenciones del proyecto

3. **Configuración de pipelines**
   - Document processing workflows
   - Modal processor orchestration
   - Knowledge graph construction

4. **🛑 CHECKPOINT 3:** Diseño técnico → **Esperar aprobación explícita**

---

### 🛡️ FASE 4: PREPARACIÓN Y BACKUP
**Checkpoint obligatorio** - **STOP hasta aprobación**

1. **Safety commit obligatorio**
   ```bash
   git add -A
   git commit -m "safety: pre-[action] snapshot"
   git push origin $(git branch --show-current)
   ```

2. **Backup de configuraciones críticas**
   - RAG storage (rag_storage/)
   - Configuraciones del sistema (.env)
   - Documentos de prueba
   - Estados previos processing

3. **Preparación del entorno**
   - Instalación de dependencias
   - Configuración de herramientas
   - Setup de testing environment

4. **🛑 CHECKPOINT 4:** Backup realizado → **Esperar aprobación explícita**

---

### 🔄 FASE 5: DESARROLLO ITERATIVO

1. **Ciclo de desarrollo**
   ```bash
   # Desarrollo local
   git add <files>
   git commit -m "feat(scope): implement feature"
   
   # Push periódico
   git push origin feature/branch-name
   
   # Tests locales
   python test_environment/01_pretest_requirements.py
   python test_environment/03_post_validation_tests.py
   python project_status.py
   ruff check .
   mypy raganything/
   ```

2. **Commits estructurados**
   - Frecuencia: Cada componente funcional
   - Tamaño: Máximo 200 líneas por commit
   - Push: Al menos 1 vez al día

3. **Quality assurance**
   - Tests pasan antes de commit
   - No errores de linting
   - Coverage mantenido

---

### 📝 FASE 6: PULL REQUEST PROCESS
**Checkpoint obligatorio** - **STOP hasta aprobación**

1. **Self-review checklist**
   - [ ] Código sigue convenciones RAG-Anything
   - [ ] Tests pasan localmente
   - [ ] Documentación actualizada
   - [ ] No hay secretos/credenciales
   - [ ] Commits son descriptivos
   - [ ] Modal processors funcionan correctamente
   - [ ] Knowledge graph construction verificada

2. **PR Template**
   ```markdown
   ## 🎯 Objetivo
   [Descripción breve del cambio multimodal]
   
   ## 📋 Cambios realizados
   - [ ] Feature multimodal implementada
   - [ ] Modal processors actualizados
   - [ ] Tests añadidos
   - [ ] Documentación actualizada
   
   ## 🧪 Testing
   - [ ] Tests pre-requirements: X/X passing
   - [ ] Tests post-validation: X/X passing
   - [ ] Coverage: XX%
   - [ ] Modal processing verified
   
   ## ✅ Checklist
   - [ ] Self-review completado
   - [ ] Tests pasan
   - [ ] Documentación actualizada
   - [ ] Multimodal functionality verified
   ```

3. **🛑 CHECKPOINT 6:** PR listo → **Esperar aprobación explícita**

---

### 🚀 FASE 7: INTEGRACIÓN Y RELEASE
**Checkpoint obligatorio** - **STOP hasta aprobación**

1. **Preparación para merge**
   - Rebase con rama objetivo
   - Squash commits si necesario
   - Update documentation

2. **Merge strategy**
   - Squash and merge para features
   - Merge commit para releases
   - Rebase and merge para hotfixes

3. **Post-merge**
   - Tag de versión si aplica
   - Actualizar documentación
   - Cleanup de branches

4. **🛑 CHECKPOINT 7:** Pre-release → **Esperar aprobación explícita**

---

## 🛠️ HERRAMIENTAS Y COMANDOS

### Comandos de Validación
```bash
# Verificar setup completo del proyecto RAG-Anything
python project_status.py

# Verificar dependencias y configuración
python -c "import raganything; print('✅ RAG-Anything OK')"
python test_environment/01_pretest_requirements.py

# Validar procesamiento de documentos
python complete_example.py
python document_processing_example.py

# Verificar tests
python test_environment/03_post_validation_tests.py

# Verificar calidad de código
ruff check .
mypy raganything/
```

### Comandos Git Útiles
```bash
# Estado actual
git status && git log --oneline -5

# Guardar trabajo temporal
git stash push -m "WIP: descripción"

# Sincronizar con upstream
git fetch origin && git rebase origin/main

# Ver diferencias antes de commit
git diff --staged

# Amend último commit
git commit --amend
```

---

## 📊 MÉTRICAS DE CALIDAD

### Objetivos Mínimos
- **Coverage de tests:** >80%
- **Linting:** Sin errores
- **Type checking:** Sin errores (donde aplicable)
- **Documentación:** Funciones públicas documentadas
- **Processing time:** <30s para documentos estándar
- **Modal processing:** Soporte verificado para text, images, tables

---

## 🚨 RECUPERACIÓN DE ERRORES

### Conflictos de Merge
```bash
git status
# Resolver conflictos manualmente
git add .
git rebase --continue
```

### Commits en Rama Equivocada
```bash
git cherry-pick <commit>
git reset --hard HEAD~1
```

### Deshacer Push
```bash
git revert <commit>
git push
```

---

## 🔴 CONDICIONES DE PARADA INMEDIATA

1. **Errores de API:** 401, 403, rate limits (OpenAI, Gemini, etc.)
2. **Tests fallando:** Cualquier test en test_environment/ roto
3. **Import errors:** Dependencias faltantes (raganything, docling, etc.)
4. **Environment errors:** Variables de entorno no configuradas
5. **Processing errors:** Fallas en modal processors
6. **Storage errors:** Problemas con rag_storage/
7. **Sin aprobación:** Usuario no ha confirmado proceder
8. **Regression detectada:** Funcionalidad existente afectada

---

## 💡 RECORDATORIOS CRÍTICOS

### En Cada Sesión DEBES:
1. ✅ Leer CLAUDE.md completo
2. ✅ Verificar branch actual: `git branch --show-current`
3. ✅ Verificar estado: `git status`
4. ✅ Revisar TodoWrite pendientes
5. ✅ Confirmar con usuario antes de cambios

### NUNCA Debes:
1. ❌ Trabajar en `main` directamente
2. ❌ Hacer cambios sin backup previo
3. ❌ Proceder sin tests pasando
4. ❌ Ignorar checkpoints de aprobación
5. ❌ Commitear sin mensaje descriptivo

---

*Documento de metodología para desarrollo profesional - Proyecto RAG-Anything*
*Última actualización: 2025-08-29*
*Versión: 1.0-RAG-Anything*