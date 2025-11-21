# ⚡ Quick Start Guide v2.3

## 30 segundos para empezar

### Opción A: Control Manual (Botón Detener)

```powershell
# 1. Abre la app
streamlit run app.py

# 2. En el navegador:
#    - Ve a "Descargar de Internet"
#    - Selecciona zonas
#    - Click "⬇️ Descargar"
#    - Mientras está descargando, puedes hacer click "⏹️ Detener"
#    - ¡Listo!
```

---

### Opción B: Tareas Programadas Automáticas

#### Paso 1: Configurar en la app (5 minutos)

```
1. Abre la app: streamlit run app.py

2. Ve al sidebar → "🕐 Tareas Programadas"

3. Configura:
   ☑ Habilitar tarea programada
   ⏰ Hora de ejecución: 22:00
   📍 Zona: Temperley
   🏢 Portal: BuscadorProp
   🔢 Props: 20
   📌 Tipo: Venta

4. Click "💾 Guardar Configuración de Tarea"

5. Verás tu tarea listada bajo "📋 Tareas Configuradas"
```

#### Paso 2: Ejecutar scheduler (2 comandos)

```powershell
# Terminal 1: Mantén la app corriendo
streamlit run app.py

# Terminal 2: Ejecuta el scheduler
python task_scheduler.py

# ¡El scheduler comenzará a monitorear!
# A las 22:00 se ejecutará automáticamente.
```

#### Monitoreo en tiempo real

```powershell
# En una tercera terminal, monitorea los logs:
Get-Content scheduler.log -Wait

# Verás eventos como:
# 2025-11-21 22:00:00 - ⏱️ Ejecutando tarea: Temperley @ 22:00
# 2025-11-21 22:01:30 - ✅ Descargadas 20 propiedades
# 2025-11-21 22:01:35 - ✅ ChromaDB regenerada
```

---

## ✨ Nuevas Características Principales

### 1. Botón ⏹️ Detener Scraper

**Qué hace**:
- Detiene la descarga sin perder datos ya descargados
- Aparece automáticamente cuando hay descarga en curso
- Después de detener, los datos están guardados en la BD

**Cuándo usar**:
- Si te equivocaste de zona
- Si necesitas pausar rápidamente
- Si quieres cambiar de portal a mitad del proceso

### 2. 🕐 Tareas Programadas

**Qué hace**:
- Ejecuta descargas automáticamente a una hora específica
- Puedes tener múltiples tareas con diferentes horarios
- Se regenera ChromaDB automáticamente

**Cuándo usar**:
- Para descargas nocturnas (evita usar la app durante el día)
- Para actualizar datos regularmente
- Para múltiples portales/zonas en paralelo

### 3. Barra de Progreso

**Qué hace**:
- Muestra el progreso en tiempo real
- Indica cuántas zonas se han completado

**Cuándo usar**:
- Para saber cuánto falta
- Para monitorear el progreso

---

## Ejemplos Prácticos

### Ejemplo 1: Descargar Temperley + Detener a mitad

```
Paso 1: App → "Descargar de Internet"
Paso 2: Seleccionar:
  ☑ Temperley
  ☑ Berazategui
  ☑ Burzaco
  Portal: BuscadorProp
  Props: 15

Paso 3: Click "⬇️ Descargar"

Paso 4: Esperar a que empiece (verás barra progreso)

Paso 5: Si cambias de idea, click "⏹️ Detener"
        → Se detiene después de Temperley
        → Los 15 de Temperley están guardados
```

### Ejemplo 2: Automatizar descarga diaria a las 6 AM

```
Paso 1: Configurar tarea:
  ⏰ Hora: 06:00
  📍 Zona: Temperley
  🏢 Portal: Argenprop
  🔢 Props: 50
  📌 Tipo: Venta
  [💾 Guardar]

Paso 2: En terminal, ejecutar scheduler:
  python task_scheduler.py

Paso 3: Todos los días a las 06:00 se ejecutará automáticamente
  - Descargará 50 propiedades
  - Las guardará en la BD
  - Regenerará ChromaDB
  - Registrará en scheduler.log
```

### Ejemplo 3: Múltiples tareas programadas

```
Tarea 1:
  06:00 → Temperley (Venta, Argenprop, 30 props)

Tarea 2:
  14:00 → Berazategui (Alquiler, BuscadorProp, 20 props)

Tarea 3:
  20:00 → Burzaco (Venta, Argenprop, 25 props)

El scheduler ejecutará cada una a su hora.
```

---

## Troubleshooting Rápido

| Problema | Solución |
|----------|----------|
| "El botón ⏹️ no aparece" | Primero haz click en "Descargar" |
| "La tarea no se ejecutó a las 22:00" | ¿Está corriendo `python task_scheduler.py`? |
| "Error de sintaxis en app.py" | Ejecuta: `python -m py_compile app.py` |
| "scheduler.log no se crea" | El scheduler crea el log la primera vez que se ejecuta |
| "ChromaDB no se regeneró" | Verifica que `regenerar_chromadb.py` existe |

---

## Archivos Importantes

```
📁 Proyecto
├── app.py                      ← Interfaz Streamlit (MODIFICADO)
├── task_scheduler.py           ← Scheduler automático (NUEVO)
├── scheduled_tasks.json        ← Config de tareas (GENERADO)
├── scheduler.log               ← Logs de scheduler (GENERADO)
│
├── run_scheduler.bat           ← Script Windows (NUEVO)
├── run_scheduler.sh            ← Script Linux/Mac (NUEVO)
│
├── RELEASE_v2_3.md             ← Documentación oficial (NUEVO)
├── ARCHITECTURE_v2_3.md        ← Diagramas y arquitectura (NUEVO)
├── SCRAPER_CONTROL.md          ← Guía detallada (NUEVO)
├── FEATURES_v2.3.md            ← Resumen de features (NUEVO)
│
├── test_v2_3_features.py       ← Tests unitarios (NUEVO)
│
└── [archivos existentes sin cambios]
```

---

## Verificación Rápida

```powershell
# ✅ Verificar sintaxis
python -m py_compile app.py task_scheduler.py

# ✅ Ejecutar tests
python test_v2_3_features.py

# ✅ Probar que app.py carga
python -c "import app; print('✅ OK')"

# ✅ Ver si scheduled_tasks.json existe
Test-Path scheduled_tasks.json
```

---

## Próximos Pasos

1. **Inmediato**: 
   - `streamlit run app.py` → Prueba el botón detener
   
2. **Configurar automatización**:
   - Crea una tarea en "🕐 Tareas Programadas"
   - En otra terminal: `python task_scheduler.py`
   
3. **Monitorear**:
   - Lee `scheduler.log` para ver qué está pasando
   - Verifica `scheduled_tasks.json` para ver tareas guardadas

4. **Optimizar**:
   - Ajusta cantidad de props según tu zona
   - Configura horarios donde no usas la app
   - Agrega más tareas si necesitas múltiples portales

---

## Comandos Útiles

```powershell
# Iniciar app
streamlit run app.py

# Iniciar scheduler
python task_scheduler.py

# Monitorear logs (Windows)
Get-Content scheduler.log -Wait

# Monitorear logs (Linux/Mac)
tail -f scheduler.log

# Ver tareas configuradas
Get-Content scheduled_tasks.json

# Limpiar logs
Remove-Item scheduler.log

# Eliminar una tarea (editar JSON manualmente)
# O usar la UI: sidebar → 🗑️ Eliminar junto a tarea
```

---

## Preguntas Frecuentes

**P: ¿Qué pasa si cierro la app mientras está descargando?**
R: Si cierras la app antes de hacer click en "Detener", se interrumpirá. Pero los datos descargados hasta ese momento estarán guardados.

**P: ¿Puedo ejecutar múltiples tareas a la misma hora?**
R: Sí, pero se ejecutarán secuencialmente (una después de la otra), no en paralelo.

**P: ¿Qué pasa si el scheduler se cae?**
R: Se registrará un error en `scheduler.log`. Reinicia con `python task_scheduler.py` y continuará normalmente.

**P: ¿Cómo cambio la hora de una tarea?**
R: En el sidebar, junto a la tarea hay un botón 🗑️ Eliminar. Elimínala y crea una nueva con la hora correcta.

**P: ¿Puedo editar `scheduled_tasks.json` a mano?**
R: Sí, pero ten cuidado. La estructura JSON debe ser válida. Mejor usa la UI de Streamlit.

---

## Soporte

- 📖 Guía detallada: `SCRAPER_CONTROL.md`
- 🏗️ Arquitectura: `ARCHITECTURE_v2_3.md`
- ✨ Features: `FEATURES_v2.3.md`
- 🔍 Logs: `scheduler.log`

---

## Status

✅ **PRODUCTION READY**

Todas las features están validadas y listas para usar.

