# Git Workflow - RAG-Anything

**Última actualización:** 2025-11-08
**Estrategia:** Git Flow simplificado

---

## 🌳 Estructura de Branches

```
main (production)
  ↑
  │ PR cuando stable
  │
develop (staging/testing)
  ↑
  │ PR para features
  │
feature/* (development)
```

### Branches Principales

#### `main`
- **Propósito:** Código en producción
- **Protección:** ✅ Protected branch
- **Merges:** Solo desde `develop` después de testing
- **Tags:** Releases versionados (v1.0.0, v1.1.0, etc.)

#### `develop`
- **Propósito:** Integración y testing
- **Base para:** Feature branches
- **Merge a:** `main` cuando esté estable
- **Testing:** Completo antes de merge a main

#### `feature/*`
- **Propósito:** Desarrollo de features
- **Naming:** `feature/descripcion-corta`
- **Base:** `develop`
- **Merge a:** `develop` via PR

---

## 🔄 Flujo de Trabajo

### 1. Crear Feature Branch

```bash
# Asegurarse que develop está actualizado
git checkout develop
git pull origin develop

# Crear feature branch
git checkout -b feature/mi-nueva-feature

# Trabajar en la feature
git add .
git commit -m "feat: descripción del cambio"

# Push al remote
git push -u origin feature/mi-nueva-feature
```

### 2. Pull Request a Develop

```bash
# Crear PR usando GitHub CLI
gh pr create --base develop --head feature/mi-nueva-feature \
  --title "feat: Título del Feature" \
  --body "Descripción detallada"

# O vía web UI
# https://github.com/pepo1275/RAG-Anything/compare/develop...feature/mi-nueva-feature
```

### 3. Review y Merge

- ✅ Code review
- ✅ Tests passing
- ✅ No conflicts
- ✅ Squash and merge (recomendado)

### 4. Merge Develop → Main

```bash
# Cuando develop esté estable
gh pr create --base main --head develop \
  --title "release: v1.x.x" \
  --body "Release notes..."

# Después del merge, tag el release
git checkout main
git pull origin main
git tag -a v1.x.x -m "Release v1.x.x"
git push origin v1.x.x
```

---

## 📋 Convenciones de Commits

### Formato
```
<type>(<scope>): <description>

<body>

<footer>
```

### Types
- `feat`: Nueva funcionalidad
- `fix`: Bug fix
- `docs`: Documentación
- `test`: Tests
- `refactor`: Refactoring (sin cambios funcionales)
- `perf`: Performance improvements
- `chore`: Mantenimiento (dependencias, config, etc.)
- `safety`: Safety commits antes de cambios críticos

### Ejemplos
```bash
feat(litellm): add support for 100+ providers
fix(parser): correct encoding for special characters
docs(readme): update installation instructions
test(integration): add Ollama provider tests
refactor(config): simplify configuration loading
perf(embeddings): optimize batch processing
chore(deps): update LiteLLM to v1.80.0
safety: pre-litellm-integration snapshot
```

---

## 🔐 Branch Protection Rules

### `main`
- ✅ Require pull request reviews
- ✅ Require status checks to pass
- ✅ No direct pushes
- ✅ Admins cannot bypass

### `develop`
- ✅ Require status checks to pass
- ⚠️ Direct pushes: Solo en emergencias
- ✅ Delete head branches after merge

---

## 🚀 Hotfix Workflow

Para fixes urgentes en producción:

```bash
# Crear hotfix desde main
git checkout main
git pull origin main
git checkout -b hotfix/critical-bug

# Fix y commit
git commit -m "fix: descripción del hotfix"

# PR directo a main Y develop
gh pr create --base main --head hotfix/critical-bug
gh pr create --base develop --head hotfix/critical-bug

# Tag después del merge
git tag -a v1.x.y -m "Hotfix v1.x.y"
git push origin v1.x.y
```

---

## 📊 Estado Actual (2025-11-08)

### Active Branches

```
main                                     77a221e (production)
develop                                  77a221e (staging)
feature/multimodal-development-framework 2164274 (11 commits ahead)
  └─ PR #1: feat: LiteLLM Integration
```

### Recent PRs

| PR | Status | Branch | Target |
|----|--------|--------|--------|
| #1 | Open | feature/multimodal-development-framework | develop |

---

## 🎯 Best Practices

### DO ✅

1. **Siempre partir de develop** para features
2. **Commits atómicos** (una responsabilidad por commit)
3. **PR descriptions completas** (qué, por qué, cómo)
4. **Tests antes de merge** (pre y post validation)
5. **Squash commits** en feature branches antes de merge
6. **Delete feature branches** después de merge
7. **Safety commits** antes de cambios críticos

### DON'T ❌

1. ❌ Commits directos a `main`
2. ❌ Merge sin tests passing
3. ❌ Feature branches con nombres genéricos (`test`, `fix`, `update`)
4. ❌ Commits con mensajes vagos ("fix", "update", "WIP")
5. ❌ PR con conflictos sin resolver
6. ❌ Mix de features en un solo PR
7. ❌ Merge de features incompletas

---

## 🔄 Sincronización

### Mantener feature branch actualizado

```bash
# Opción A: Rebase (recomendado para features limpias)
git checkout feature/mi-feature
git fetch origin
git rebase origin/develop

# Resolver conflictos si hay
git rebase --continue

# Force push (solo si no hay colaboradores)
git push --force-with-lease

# Opción B: Merge (si hay colaboradores)
git checkout feature/mi-feature
git merge origin/develop
git push
```

---

## 📝 Ejemplo Completo: LiteLLM Integration

Este fue el flujo seguido para LiteLLM:

```bash
# 1. Create feature branch (ya existía)
git checkout feature/multimodal-development-framework

# 2. Develop and commit
git add raganything/litellm_adapter.py
git commit -m "feat: complete LiteLLM integration for 100+ provider support"

git add raganything/litellm_adapter.py env.example
git commit -m "feat: add API key validation and Ollama testing for LiteLLM"

git add docs/LITELLM_*.md
git commit -m "docs: add LiteLLM architecture and known issues documentation"

# 3. Push to remote
git push origin feature/multimodal-development-framework

# 4. Create develop branch (nuevo workflow)
git checkout -b develop origin/main
git push -u origin develop

# 5. Create PR to develop
gh pr create --base develop --head feature/multimodal-development-framework \
  --title "feat: LiteLLM Integration - 100+ Provider Support"

# 6. Review, test, merge
# (via GitHub UI)

# 7. Later: develop → main cuando esté estable
```

---

## 🛠️ Comandos Útiles

```bash
# Ver estado de branches
git branch -vv

# Ver diferencias entre branches
git log develop..feature/mi-feature --oneline

# Limpiar branches mergeadas
git branch --merged develop | grep -v "develop" | xargs git branch -d

# Ver último commit de cada branch
git for-each-ref --sort=-committerdate refs/heads/ --format='%(HEAD) %(refname:short) - %(contents:subject) - %(authorname) (%(committerdate:relative))'

# Verificar si PR es posible
git log --oneline develop..feature/mi-feature
```

---

## 📚 Referencias

- [Git Flow](https://nvie.com/posts/a-successful-git-branching-model/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [GitHub Flow](https://guides.github.com/introduction/flow/)

---

**Documento creado:** 2025-11-08
**Mantenedor:** RAG-Anything Team
**Updates:** Revisar cuando cambie estrategia de branching
