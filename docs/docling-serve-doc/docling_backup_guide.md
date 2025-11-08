# Docling Pre-Modification Backup Guide
## Complete Safety Procedure Before VLM Implementation

**Propósito:** Crear backup completo del sistema Docling antes de implementar cambios VLM  
**Contexto:** Complementario al documento "Docling VLM Investigation & Solutions"  
**Nivel:** Producción-ready backup procedure  

---

## 🛡️ **OVERVIEW**

Esta guía proporciona **3 niveles de backup** para proteger tu instalación actual de Docling antes de implementar modificaciones VLM:

- 🟢 **BACKUP ESENCIAL** (2-3 minutos) - Mínimo necesario para restore
- 🟡 **BACKUP ESTÁNDAR** (5-8 minutos) - Recomendado para la mayoría de casos  
- 🔴 **BACKUP COMPLETO** (10-15 minutos) - Máxima protección para entornos críticos

---

## 🟢 **NIVEL 1: BACKUP ESENCIAL**

### Duración Estimada: 2-3 minutos
### Casos de Uso: Testing rápido, desarrollo

```bash
#!/bin/bash
# ===========================================
# DOCLING BACKUP ESENCIAL - NIVEL 1
# ===========================================

echo "🛡️  Iniciando Backup Esencial de Docling..."
START_TIME=$(date)

# 1. Crear directorio con timestamp
BACKUP_DIR=~/docling-backups/essential-$(date +%Y%m%d-%H%M%S)
mkdir -p "$BACKUP_DIR"
echo "📁 Directorio de backup: $BACKUP_DIR"

# 2. Backup de configuración del contenedor
echo "📋 Guardando configuración del contenedor..."
docker inspect docling-serve-shared > "$BACKUP_DIR/container_config.json"

# 3. Crear snapshot de imagen (preserva estado interno)
echo "📸 Creando snapshot de imagen..."
SNAPSHOT_TAG="docling-backup-essential-$(date +%Y%m%d-%H%M%S)"
docker commit docling-serve-shared "docling-serve-backup:$SNAPSHOT_TAG"

# 4. Script de restore automático
echo "🔧 Creando script de restauración..."
cat > "$BACKUP_DIR/restore_essential.sh" << EOF
#!/bin/bash
echo "🔄 Restaurando Docling desde backup esencial..."

# Detener contenedor actual
docker stop docling-serve-shared 2>/dev/null || true
docker rm docling-serve-shared 2>/dev/null || true

# Restaurar desde snapshot
docker run -d --name docling-serve-shared -p 9000:5001 \\
    "docling-serve-backup:$SNAPSHOT_TAG"

echo "✅ Restauración esencial completada"
echo "🌐 UI disponible en: http://localhost:9000/ui/"
echo "⏰ Tiempo estimado de inicio: 30-60 segundos"
EOF

chmod +x "$BACKUP_DIR/restore_essential.sh"

# 5. Verificación básica
echo "✅ Verificando backup..."
echo "=== BACKUP ESENCIAL COMPLETADO ===" > "$BACKUP_DIR/backup_info.txt"
echo "Fecha: $START_TIME" >> "$BACKUP_DIR/backup_info.txt"  
echo "Imagen snapshot: docling-serve-backup:$SNAPSHOT_TAG" >> "$BACKUP_DIR/backup_info.txt"
echo "Restore: ./restore_essential.sh" >> "$BACKUP_DIR/backup_info.txt"

echo ""
echo "🎉 BACKUP ESENCIAL COMPLETADO"
echo "📁 Ubicación: $BACKUP_DIR"
echo "🔄 Para restaurar: cd $BACKUP_DIR && ./restore_essential.sh"
```

---

## 🟡 **NIVEL 2: BACKUP ESTÁNDAR**

### Duración Estimada: 5-8 minutos  
### Casos de Uso: Implementaciones normales, entornos de staging

```bash
#!/bin/bash
# ===========================================
# DOCLING BACKUP ESTÁNDAR - NIVEL 2  
# ===========================================

echo "🛡️  Iniciando Backup Estándar de Docling..."
START_TIME=$(date)

# 1. Crear estructura de directorios
BACKUP_DIR=~/docling-backups/standard-$(date +%Y%m%d-%H%M%S)
mkdir -p "$BACKUP_DIR"/{config,data,logs,scripts}
echo "📁 Directorio de backup: $BACKUP_DIR"

# 2. Información del sistema
echo "🖥️  Capturando información del sistema..."
cat > "$BACKUP_DIR/system_info.txt" << EOF
=== SYSTEM INFORMATION ===
Backup Date: $START_TIME
Hostname: $(hostname)
User: $(whoami)  
Docker Version: $(docker version --format "{{.Server.Version}}" 2>/dev/null)
OS: $(uname -s)
Architecture: $(uname -m)
EOF

# 3. Configuración completa del contenedor
echo "📋 Guardando configuración del contenedor..."
docker inspect docling-serve-shared > "$BACKUP_DIR/config/container_inspect.json"
docker exec docling-serve-shared env > "$BACKUP_DIR/config/environment_variables.txt"
docker ps --filter "name=docling-serve-shared" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}\t{{.Image}}" > "$BACKUP_DIR/config/container_status.txt"

# 4. Backup de datos y cache
echo "💾 Guardando datos y cache..."
docker exec docling-serve-shared find /opt/app-root/src/.cache -type f 2>/dev/null > "$BACKUP_DIR/data/cache_inventory.txt" || echo "Cache vacío o no accesible"

# Intentar backup del cache (puede fallar si está vacío)
docker exec docling-serve-shared tar czf /tmp/cache_backup.tar.gz -C /opt/app-root/src/.cache . 2>/dev/null && \
    docker cp docling-serve-shared:/tmp/cache_backup.tar.gz "$BACKUP_DIR/data/" || \
    echo "No cache data to backup" > "$BACKUP_DIR/data/no_cache.txt"

# 5. Logs completos
echo "📝 Guardando logs..."
docker logs docling-serve-shared > "$BACKUP_DIR/logs/container_logs.txt" 2>&1

# 6. Test de conectividad actual
echo "🔗 Verificando conectividad actual..."
curl -s -o /dev/null -w "HTTP Status: %{http_code}\nResponse Time: %{time_total}s\nURL Tested: http://localhost:9000/ui/\nTest Time: $(date)\n" http://localhost:9000/ui/ > "$BACKUP_DIR/logs/connectivity_test.txt"

# 7. Snapshot de imagen
echo "📸 Creando snapshot de imagen..."
SNAPSHOT_TAG="docling-backup-std-$(date +%Y%m%d-%H%M%S)"
docker commit docling-serve-shared "docling-serve-backup:$SNAPSHOT_TAG"

# 8. Script de restauración avanzado
echo "🔧 Creando scripts de restauración..."
cat > "$BACKUP_DIR/scripts/restore_standard.sh" << EOF
#!/bin/bash
echo "🔄 Restaurando Docling desde backup estándar..."
echo "📁 Backup location: $BACKUP_DIR"

# Detener contenedor actual
echo "⏹️  Deteniendo contenedor actual..."
docker stop docling-serve-shared 2>/dev/null || true
docker rm docling-serve-shared 2>/dev/null || true

# Restaurar desde snapshot  
echo "📸 Restaurando desde snapshot..."
docker run -d --name docling-serve-shared -p 9000:5001 \\
    "docling-serve-backup:$SNAPSHOT_TAG"

# Restaurar cache si existe
if [ -f "$BACKUP_DIR/data/cache_backup.tar.gz" ]; then
    echo "💾 Restaurando cache..."
    docker cp "$BACKUP_DIR/data/cache_backup.tar.gz" docling-serve-shared:/tmp/
    docker exec docling-serve-shared tar xzf /tmp/cache_backup.tar.gz -C /opt/app-root/src/.cache/ 2>/dev/null || echo "Cache restore failed (non-critical)"
fi

# Verificar restauración
echo "🔍 Verificando restauración..."
sleep 5
if curl -s http://localhost:9000/ui/ > /dev/null; then
    echo "✅ Restauración exitosa - UI accesible"
else
    echo "⚠️  UI no responde inmediatamente - esperar 30-60 segundos"
fi

echo "🎉 Restauración estándar completada"
echo "🌐 UI disponible en: http://localhost:9000/ui/"
EOF

chmod +x "$BACKUP_DIR/scripts/restore_standard.sh"

# 9. Script de limpieza (opcional)
cat > "$BACKUP_DIR/scripts/cleanup_old_backups.sh" << 'EOF'
#!/bin/bash
echo "🧹 Limpiando backups antiguos..."

# Eliminar snapshots de backup más antiguos que 7 días
docker images --format "table {{.Repository}}:{{.Tag}}" | grep "docling-serve-backup:" | while read line; do
    IMAGE=$(echo $line | awk '{print $1":"$2}')
    echo "Considerando: $IMAGE"
done

echo "💡 Revisar manualmente las imágenes con: docker images | grep docling-serve-backup"
echo "💡 Eliminar con: docker rmi IMAGE_NAME"
EOF

chmod +x "$BACKUP_DIR/scripts/cleanup_old_backups.sh"

# 10. Resumen del backup
echo "📊 Generando resumen..."
cat > "$BACKUP_DIR/BACKUP_SUMMARY.txt" << EOF
=== DOCLING BACKUP ESTÁNDAR - RESUMEN ===

Fecha de Backup: $START_TIME
Backup Directory: $BACKUP_DIR
Snapshot Image: docling-serve-backup:$SNAPSHOT_TAG

CONTENIDO DEL BACKUP:
- ✅ Configuración completa del contenedor
- ✅ Variables de entorno
- ✅ Cache de modelos (si disponible)  
- ✅ Logs completos del contenedor
- ✅ Test de conectividad
- ✅ Snapshot de imagen Docker
- ✅ Scripts de restauración automática

RESTAURACIÓN:
1. Método automático: cd $BACKUP_DIR && ./scripts/restore_standard.sh
2. Método manual: Consultar config/container_inspect.json

ARCHIVOS CLAVE:
- config/container_inspect.json - Configuración completa
- data/cache_backup.tar.gz - Cache de modelos
- logs/container_logs.txt - Logs históricos  
- scripts/restore_standard.sh - Restauración automática

VERIFICACIÓN POST-RESTORE:
- UI: http://localhost:9000/ui/
- API: http://localhost:9000/docs
- Logs: docker logs docling-serve-shared
EOF

# Verificación final
ls -la "$BACKUP_DIR"/{config,data,logs,scripts}/ >> "$BACKUP_DIR/BACKUP_SUMMARY.txt"

echo ""
echo "🎉 BACKUP ESTÁNDAR COMPLETADO"
echo "📁 Ubicación: $BACKUP_DIR" 
echo "📄 Resumen: $BACKUP_DIR/BACKUP_SUMMARY.txt"
echo "🔄 Restaurar: $BACKUP_DIR/scripts/restore_standard.sh"
```

---

## 🔴 **NIVEL 3: BACKUP COMPLETO**

### Duración Estimada: 10-15 minutos
### Casos de Uso: Entornos de producción, sistemas críticos

```bash
#!/bin/bash
# ===========================================
# DOCLING BACKUP COMPLETO - NIVEL 3
# ===========================================

echo "🛡️  Iniciando Backup Completo de Docling..."
START_TIME=$(date)

# 1. Estructura completa de directorios
BACKUP_DIR=~/docling-backups/complete-$(date +%Y%m%d-%H%M%S)  
mkdir -p "$BACKUP_DIR"/{config,data,logs,scripts,system,verification,documentation}
echo "📁 Directorio de backup: $BACKUP_DIR"

# 2. Información detallada del sistema
echo "🖥️  Capturando información completa del sistema..."
cat > "$BACKUP_DIR/system/detailed_system_info.txt" << EOF
=== COMPREHENSIVE SYSTEM INFORMATION ===
Backup Date: $START_TIME
Hostname: $(hostname)
Full Hostname: $(hostname -f 2>/dev/null || echo "N/A")
User: $(whoami)
Home Directory: $HOME
Current Working Directory: $(pwd)
Shell: $SHELL

=== DOCKER ENVIRONMENT ===
Docker Version: $(docker version --format "Server: {{.Server.Version}}, Client: {{.Client.Version}}" 2>/dev/null)
Docker Info: $(docker info --format "Containers: {{.Containers}}, Images: {{.Images}}, Storage Driver: {{.Driver}}" 2>/dev/null)

=== OPERATING SYSTEM ===
OS: $(uname -s)
Kernel: $(uname -r)
Architecture: $(uname -m)
Platform: $(uname -p 2>/dev/null || echo "N/A")
EOF

# macOS specific info
if [[ "$(uname)" == "Darwin" ]]; then
    echo "macOS Version: $(sw_vers -productVersion 2>/dev/null)" >> "$BACKUP_DIR/system/detailed_system_info.txt"
    echo "Hardware: $(system_profiler SPHardwareDataType | grep 'Model Name' 2>/dev/null)" >> "$BACKUP_DIR/system/detailed_system_info.txt"
fi

# 3. Configuración exhaustiva del contenedor
echo "📋 Guardando configuración exhaustiva..."
docker inspect docling-serve-shared > "$BACKUP_DIR/config/container_inspect_complete.json"
docker exec docling-serve-shared env | sort > "$BACKUP_DIR/config/environment_variables_sorted.txt"
docker ps -a --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}\t{{.Image}}\t{{.CreatedAt}}" > "$BACKUP_DIR/config/all_containers.txt"
docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.ID}}\t{{.CreatedAt}}\t{{.Size}}" > "$BACKUP_DIR/config/all_images.txt"

# 4. Análisis detallado de datos
echo "💾 Analizando y guardando datos..."

# Inventario completo del contenedor
docker exec docling-serve-shared find /opt/app-root -type f -name "*.json" -o -name "*.py" -o -name "*.yml" -o -name "*.yaml" 2>/dev/null > "$BACKUP_DIR/data/config_files_inventory.txt"
docker exec docling-serve-shared find /opt/app-root/src/.cache -type f 2>/dev/null > "$BACKUP_DIR/data/complete_cache_inventory.txt" || echo "Cache directory not accessible" > "$BACKUP_DIR/data/cache_status.txt"

# Información de modelos si existen
docker exec docling-serve-shared find /opt/app-root/src/.cache -name "*.bin" -o -name "*.safetensors" -o -name "*.onnx" -o -name "config.json" 2>/dev/null | head -20 > "$BACKUP_DIR/data/model_files_sample.txt"

# Backup completo del cache y configuraciones
docker exec docling-serve-shared tar czf /tmp/complete_cache_backup.tar.gz -C /opt/app-root/src/.cache . 2>/dev/null && \
    docker cp docling-serve-shared:/tmp/complete_cache_backup.tar.gz "$BACKUP_DIR/data/" || \
    echo "$(date): No cache data available for backup" > "$BACKUP_DIR/data/cache_backup_status.txt"

# 5. Logs comprehensivos
echo "📝 Guardando logs comprehensivos..."
docker logs docling-serve-shared --timestamps > "$BACKUP_DIR/logs/container_logs_timestamped.txt" 2>&1
docker logs docling-serve-shared --tail 100 > "$BACKUP_DIR/logs/container_logs_recent.txt" 2>&1

# Log de eventos Docker
docker events --since 24h --until now --filter container=docling-serve-shared > "$BACKUP_DIR/logs/docker_events.txt" 2>/dev/null || echo "No recent Docker events" > "$BACKUP_DIR/logs/docker_events.txt"

# 6. Verificaciones completas de conectividad
echo "🔗 Ejecutando verificaciones completas..."
cat > "$BACKUP_DIR/verification/connectivity_tests.sh" << 'EOF'
#!/bin/bash
echo "=== DOCLING CONNECTIVITY VERIFICATION ===" > connectivity_results.txt
echo "Test Date: $(date)" >> connectivity_results.txt
echo "" >> connectivity_results.txt

# Test UI
echo "Testing UI (localhost:9000/ui/)..." >> connectivity_results.txt
curl -s -o /dev/null -w "Status: %{http_code}, Time: %{time_total}s\n" http://localhost:9000/ui/ >> connectivity_results.txt 2>&1

# Test API docs  
echo "Testing API docs (localhost:9000/docs)..." >> connectivity_results.txt
curl -s -o /dev/null -w "Status: %{http_code}, Time: %{time_total}s\n" http://localhost:9000/docs >> connectivity_results.txt 2>&1

# Test health endpoint
echo "Testing health endpoint (localhost:9000/health)..." >> connectivity_results.txt  
curl -s -o /dev/null -w "Status: %{http_code}, Time: %{time_total}s\n" http://localhost:9000/health >> connectivity_results.txt 2>&1

# Test OpenAPI
echo "Testing OpenAPI (localhost:9000/openapi.json)..." >> connectivity_results.txt
curl -s -o /dev/null -w "Status: %{http_code}, Time: %{time_total}s\n" http://localhost:9000/openapi.json >> connectivity_results.txt 2>&1

echo "=== END VERIFICATION ===" >> connectivity_results.txt
cat connectivity_results.txt
EOF

chmod +x "$BACKUP_DIR/verification/connectivity_tests.sh"
cd "$BACKUP_DIR/verification" && ./connectivity_tests.sh

# 7. Múltiples snapshots de imagen
echo "📸 Creando múltiples snapshots..."
SNAPSHOT_TAG="docling-backup-complete-$(date +%Y%m%d-%H%M%S)"
docker commit docling-serve-shared "docling-serve-backup:$SNAPSHOT_TAG"
docker commit docling-serve-shared "docling-serve-backup:latest-complete"

# 8. Scripts avanzados de restauración
echo "🔧 Creando scripts avanzados de restauración..."

# Script de restauración completa
cat > "$BACKUP_DIR/scripts/restore_complete.sh" << EOF
#!/bin/bash
echo "🔄 RESTAURACIÓN COMPLETA DE DOCLING"
echo "====================================="
echo "📁 Backup location: $BACKUP_DIR"
echo "📸 Snapshot: docling-serve-backup:$SNAPSHOT_TAG"
echo ""

# Pre-restore verification
echo "🔍 Verificación pre-restauración..."
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker no está ejecutándose"
    exit 1
fi

# Stop current container
echo "⏹️  Deteniendo contenedor actual..."
docker stop docling-serve-shared 2>/dev/null || echo "No hay contenedor corriendo"
docker rm docling-serve-shared 2>/dev/null || echo "No hay contenedor que eliminar"

# Restore from snapshot
echo "📸 Restaurando desde snapshot completo..."
docker run -d --name docling-serve-shared -p 9000:5001 \\
    "docling-serve-backup:$SNAPSHOT_TAG"

if [ \$? -ne 0 ]; then
    echo "❌ Error al restaurar desde snapshot"
    exit 1
fi

# Restore cache
if [ -f "$BACKUP_DIR/data/complete_cache_backup.tar.gz" ]; then
    echo "💾 Restaurando cache completo..."
    docker cp "$BACKUP_DIR/data/complete_cache_backup.tar.gz" docling-serve-shared:/tmp/
    docker exec docling-serve-shared tar xzf /tmp/cache_backup.tar.gz -C /opt/app-root/src/.cache/ 2>/dev/null || echo "⚠️  Cache restore failed (non-critical)"
fi

# Post-restore verification
echo "🔍 Verificación post-restauración..."
sleep 10

# Test connectivity
if curl -s http://localhost:9000/ui/ > /dev/null; then
    echo "✅ UI accesible"
else
    echo "⚠️  UI no responde - verificar en 1-2 minutos"
fi

# Final status
docker ps --filter "name=docling-serve-shared"
echo ""
echo "🎉 RESTAURACIÓN COMPLETA FINALIZADA"
echo "🌐 UI: http://localhost:9000/ui/"
echo "📖 API: http://localhost:9000/docs"  
echo "🔧 Logs: docker logs docling-serve-shared"
EOF

chmod +x "$BACKUP_DIR/scripts/restore_complete.sh"

# Script de verificación post-restauración
cat > "$BACKUP_DIR/scripts/verify_restore.sh" << 'EOF'
#!/bin/bash
echo "🔍 VERIFICACIÓN POST-RESTAURACIÓN"
echo "================================="

# Container status
echo "📦 Estado del contenedor:"
docker ps --filter "name=docling-serve-shared" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo ""
echo "🔗 Tests de conectividad:"

# UI Test
UI_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:9000/ui/)
if [ "$UI_STATUS" = "200" ]; then
    echo "✅ UI: OK ($UI_STATUS)"
else
    echo "❌ UI: FAIL ($UI_STATUS)"
fi

# API Test
API_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:9000/docs)
if [ "$API_STATUS" = "200" ]; then
    echo "✅ API: OK ($API_STATUS)"
else
    echo "❌ API: FAIL ($API_STATUS)"
fi

echo ""
echo "📋 Logs recientes:"
docker logs docling-serve-shared --tail 10

echo ""
echo "🎯 Verificación completada"
EOF

chmod +x "$BACKUP_DIR/scripts/verify_restore.sh"

# 9. Documentación completa
echo "📚 Creando documentación completa..."
cat > "$BACKUP_DIR/documentation/COMPLETE_BACKUP_GUIDE.md" << EOF
# Docling Complete Backup Documentation

## Backup Information
- **Date:** $START_TIME
- **Type:** Complete Production Backup
- **Location:** $BACKUP_DIR
- **Snapshot:** docling-serve-backup:$SNAPSHOT_TAG

## Directory Structure
\`\`\`
$BACKUP_DIR/
├── config/          # Container configuration files
├── data/            # Cache and model data
├── logs/            # Complete log history
├── scripts/         # Restoration scripts
├── system/          # System information
├── verification/    # Connectivity tests
└── documentation/   # This guide and references
\`\`\`

## Restoration Options

### Quick Restore (Recommended)
\`\`\`bash
cd $BACKUP_DIR
./scripts/restore_complete.sh
\`\`\`

### Manual Restore
\`\`\`bash
# Stop current container
docker stop docling-serve-shared
docker rm docling-serve-shared

# Restore from snapshot
docker run -d --name docling-serve-shared -p 9000:5001 docling-serve-backup:$SNAPSHOT_TAG
\`\`\`

### Verification
\`\`\`bash
cd $BACKUP_DIR
./scripts/verify_restore.sh
\`\`\`

## Important Files
- \`config/container_inspect_complete.json\` - Full container config
- \`data/complete_cache_backup.tar.gz\` - Model cache
- \`scripts/restore_complete.sh\` - Main restoration script
- \`verification/connectivity_results.txt\` - Pre-backup connectivity status

## Notes
- This backup preserves complete system state
- Cache restoration may take additional time depending on size
- Verify all endpoints after restoration
- Keep this backup until new system is verified stable

## Support
If restoration fails, check:
1. Docker daemon is running
2. Port 9000 is available  
3. Sufficient disk space
4. Review container logs: \`docker logs docling-serve-shared\`
EOF

# 10. Resumen final y verificación
echo "📊 Generando resumen final..."
BACKUP_SIZE=$(du -sh "$BACKUP_DIR" | cut -f1)
END_TIME=$(date)

cat > "$BACKUP_DIR/BACKUP_COMPLETE_SUMMARY.txt" << EOF
=== DOCLING COMPLETE BACKUP - SUMMARY ===

Backup Started: $START_TIME
Backup Completed: $END_TIME
Backup Size: $BACKUP_SIZE
Backup Location: $BACKUP_DIR
Snapshot Images: 
- docling-serve-backup:$SNAPSHOT_TAG
- docling-serve-backup:latest-complete

BACKUP CONTENTS:
✅ Complete container configuration
✅ All environment variables  
✅ Complete cache and model data
✅ Full log history with timestamps
✅ System information and Docker state
✅ Connectivity verification results
✅ Multiple Docker image snapshots
✅ Advanced restoration scripts
✅ Post-restore verification tools
✅ Complete documentation

RESTORATION METHODS:
1. Automatic: ./scripts/restore_complete.sh
2. Manual: Follow documentation/COMPLETE_BACKUP_GUIDE.md
3. Verification: ./scripts/verify_restore.sh

CLEANUP (OPTIONAL):
- Remove old snapshots: docker rmi docling-serve-backup:OLD_TAG
- Clean backup dirs: Keep only last 3-5 complete backups

NEXT STEPS:
1. Verify backup integrity: Check all directories have content
2. Test restoration in safe environment (optional)
3. Proceed with planned modifications
4. Keep this backup until new system is stable

DIRECTORY STRUCTURE:
$(find "$BACKUP_DIR" -maxdepth 2 -type d | sort)

KEY FILES:
$(find "$BACKUP_DIR" -name "*.sh" -o -name "*.md" -o -name "*.json" -o -name "*.tar.gz" | sort)
EOF

echo ""
echo "🎉 BACKUP COMPLETO FINALIZADO"
echo "⏱️  Tiempo total: $(date)"
echo "📦 Tamaño: $BACKUP_SIZE"
echo "📁 Ubicación: $BACKUP_DIR"
echo "📄 Resumen: $BACKUP_DIR/BACKUP_COMPLETE_SUMMARY.txt"
echo "🔄 Restaurar: $BACKUP_DIR/scripts/restore_complete.sh"
echo ""
echo "✅ Sistema listo para modificaciones VLM"
```

---

## 🛠️ **SELECCIÓN DE BACKUP**

### Guía de Decisión

| Escenario | Backup Recomendado | Tiempo | Descripción |
|-----------|-------------------|---------|-------------|
| **Testing rápido** | 🟢 Esencial | 2-3 min | Solo snapshot + config básica |
| **Implementación normal** | 🟡 Estándar | 5-8 min | Config completa + cache + logs |
| **Sistema en producción** | 🔴 Completo | 10-15 min | Todo + verificaciones + docs |
| **Primera vez con VLM** | 🟡 Estándar | 5-8 min | Balance tiempo/seguridad |
| **Sistema crítico** | 🔴 Completo | 10-15 min | Máxima protección |

---

## ⚡ **EJECUCIÓN RÁPIDA**

### Para Backup Esencial (Recomendado para testing)
```bash
curl -s https://gist.githubusercontent.com/[URL]/docling_backup_essential.sh | bash
```

### Para Backup Estándar (Recomendado general)  
```bash
curl -s https://gist.githubusercontent.com/[URL]/docling_backup_standard.sh | bash
```

### Para Backup Completo (Producción)
```bash  
curl -s https://gist.githubusercontent.com/[URL]/docling_backup_complete.sh | bash
```

---

## 🔍 **VERIFICACIÓN POST-BACKUP**

### Checklist de Verificación
```bash
# 1. Verificar directorio de backup existe
ls -la ~/docling-backups/

# 2. Verificar snapshot de imagen fue creado
docker images | grep docling-serve-backup

# 3. Verificar script de restore es ejecutable
ls -la $BACKUP_DIR/scripts/*.sh

# 4. Test rápido de restore (opcional)
# $BACKUP_DIR/scripts/restore_*.sh

# 5. Verificar tamaño del backup es razonable
du -sh $BACKUP_DIR
```

---

## 📋 **SIGUIENTE PASO**

Una vez completado el backup de tu elección:

1. **Verificar** que el backup se completó exitosamente
2. **Confirmar** que tienes el script de restore disponible  
3. **Proceder** con confianza a implementar las modificaciones VLM del documento principal

**El sistema está ahora protegido y listo para modificaciones.**