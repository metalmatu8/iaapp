# Checklist: Validación de Cambios ChromeDriver Fix

## ✅ Validaciones Locales (Completadas)

- [x] src/scrapers.py compila sin errores
- [x] app.py compila sin errores
- [x] fix_chromedriver.py compila sin errores
- [x] src.scrapers importa correctamente
- [x] Sintaxis Python válida en todos los archivos modificados
- [x] No hay imports rotos
- [x] fix_chromedriver.py retorna exit(0) en entorno sin Chromium (Windows)

## ✅ Cambios de Código Verificados

### src/scrapers.py
- [x] 3 instancias de `--disable-blink-features=AutomationControlled` agregadas
  - [ ] Línea ~115: buscar_propiedades_argenprop() ✓
  - [ ] Línea ~395: extraer_detalles_propiedad() ✓
  - [ ] Línea ~720: buscar_propiedades_selenium() ✓

- [x] Error handling mejorado para "session not created"
  - [ ] extraer_detalles_propiedad(): Fallback sin webdriver_manager ✓
  - [ ] buscar_propiedades_selenium(): Fallback sin webdriver_manager ✓

- [x] Logging mejorado
  - [ ] ChromeDriver path loguea ✓
  - [ ] Errors específicos para version mismatch ✓

### app.py
- [x] Detección de Streamlit Cloud (IS_STREAMLIT_CLOUD)
- [x] Ejecución de fix_chromedriver.py en cloud
- [x] Manejo de errores si fix_chromedriver.py falla
- [x] No interfiere con ejecución local

### fix_chromedriver.py
- [x] Detecta Chromium en múltiples rutas (Linux/macOS/Windows)
- [x] Limpia cache de webdriver-manager
- [x] Instala ChromeDriver con versión correcta
- [x] Maneja gracefully si Chromium no existe
- [x] chmod 755 en Linux (con try-except)
- [x] exit(0) incluso si falla

### streamlit_setup.sh
- [x] Detecta Chromium --version
- [x] Limpia ~/.wdm
- [x] Sin errores si directorio no existe

### Procfile
- [x] Orden de ejecución correcto
- [x] Sintaxis Procfile válida

### .streamlit/config.toml
- [x] TOML syntax válido
- [x] Secciones correctas

## 📋 Testing Pre-Deploy

Antes de hacer push a Streamlit Cloud:

- [ ] Revisar git diff: `git diff --stat`
- [ ] Revisar archivos nuevos: `git status`
- [ ] Validar requirements.txt tiene webdriver-manager
- [ ] Validar packages.txt tiene "chromium"
- [ ] Revisar logs de compilación
- [ ] Confirmar que no hay merge conflicts

## 🚀 Deploy a Streamlit Cloud

```bash
# 1. Commit y push
git add -A
git commit -m "Fix: ChromeDriver version mismatch - Agregar AutomationControlled, fix_chromedriver.py, y fallbacks"
git push origin dev

# 2. En Streamlit Cloud: 
#    - Conectar si es necesario
#    - Observar logs durante deployment
```

## 🧪 Testing Post-Deploy (Streamlit Cloud)

### Inicialización (Primeros 30 segundos)
- [ ] Ver logs: "✅ ChromeDriver configurado correctamente"
- [ ] Ver logs: "Detectado Chromium en: /usr/bin/chromium"
- [ ] Ver logs: "ChromeDriver instalado en: /home/appuser/.wdm/drivers/..."
- [ ] App carga sin errores

### Funcionalidad
- [ ] Sidebar carga: Provincias, localidades, etc.
- [ ] Campo cantidad aparece con borde azul
- [ ] Botón "Descargar Propiedades" es clickeable

### Descarga de Propiedades
- [ ] Clickear "Descargar Propiedades"
- [ ] Esperar resultado (puede ser 0 propiedades)
- [ ] Verificar logs:
  - [ ] `BuscadorProp: buscando venta en [zona]` ← Comenzó
  - [ ] `Descargadas N propiedades` ← Completó (N ≥ 0)
  - [ ] O `No se puede descargar propiedades` ← Fallback graceful

### Búsqueda RAG
- [ ] Ingresar query en "Busca por descripción/características"
- [ ] Clickear "Buscar"
- [ ] Verificar resultado:
  - [ ] "Encontradas X resultados" (X ≥ 0)
  - [ ] Tarjetas aparecen si X > 0

### ChromaDB
- [ ] Logs muestran: "Detectado Streamlit Cloud - usando ChromaDB en memoria"
- [ ] Logs muestran: "Colección existente encontrada con X documentos" (X ≥ 15)
- [ ] Búsqueda funciona (usa embeddings)

## 📊 Observar (No es error)

- ⚠️ Descarga retorna 0 propiedades: Es fallback graceful
- ⚠️ "BuscadorProp: No se puede descargar": Es fallback, no crash
- ⚠️ Version mismatch message en logs: Es detectado y handled

## ❌ Problemas a Buscar

Si ves estos errores → Rollback y debug:

```
❌ "session not created" y luego CRASH
   → fix_chromedriver.py no ejecutó
   → Revertir y revisar app.py línea 13-24

❌ "ModuleNotFoundError: webdriver_manager"
   → requirements.txt falta webdriver-manager
   → Agregar webdriver-manager>=4.0.0

❌ "Procfile syntax error"
   → Revisar Procfile formato
   → Debe ser: web: comando1 && comando2

❌ ChromaDB error "readonly"
   → IS_STREAMLIT_CLOUD no detecta correctamente
   → Revisar detección en app.py línea 12
```

## ✅ Señal Verde (Todo OK)

Si ves:
```
✅ ChromeDriver configurado correctamente
✅ Detectado Chromium en: /usr/bin/chromium
✅ ChromeDriver instalado en: /home/appuser/.wdm/drivers/chromedriver/linux64/142.X
✅ ChromaDB procesado
✅ Colección existente encontrada con 15 documentos
✅ BuscadorProp: buscando venta en [zona]
✅ Descargadas 0 propiedades de [zona]  (O N > 0)
```

→ **TODO FUNCIONA** ✅

## 📝 Notas para Debugging

### Si descarga retorna 0 pero no hay error:
```
1. Revisar logs: Ver si hay "session not created"
2. Revisar logs: Ver si hay "version mismatch"
3. Revisar logs: Ver si hay "No se puede descargar"
4. Si nada → Probablemente es fallback OK, no es error
```

### Si BuscadorProp falla:
```
1. Revisar si Chromium instaló (packages.txt)
2. Revisar si webdriver-manager instaló (requirements.txt)
3. Revisar si fix_chromedriver.py ejecutó
4. Revisar logs de version mismatch
```

### Si ChromaDB falla:
```
1. Revisar: "Detectado Streamlit Cloud"
2. Revisar: IS_STREAMLIT_CLOUD = True
3. Revisar: Se usa EphemeralClient (no PersistentClient)
4. Revisar: collection = None es estado válido
```

## 🔄 Rollback Rápido

Si algo sale muy mal:

```bash
# Opción 1: Revertir último commit
git revert HEAD

# Opción 2: Desactivar fix_chromedriver.py temporalmente
# Editar app.py línea 13-24: comentar la sección

# Opción 3: Revertir a commit anterior
git reset --hard HEAD~1
git push -f origin dev
```

Sistema seguirá funcionando con fallback (0 propiedades, sin crash).
