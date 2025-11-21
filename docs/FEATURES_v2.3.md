# ✨ NUEVAS CARACTERÍSTICAS v2.3 - CONTROL DE SCRAPER

## 🎯 Resumen

Se agregaron dos features principales:

### 1️⃣ Botón para Detener Scraper ⏹️
- Detiene la descarga en cualquier momento
- Guarda las propiedades descargadas hasta ese momento
- Interfaz intuitiva con botón deshabilitado cuando no hay descarga activa

### 2️⃣ Tareas Programadas 🕐
- Configura descargas automáticas para horas específicas
- Se ejecutan diariamente sin intervención
- Almacenamiento de configuración en JSON
- Task scheduler independiente

---

## 📦 Archivos Creados/Modificados

### Modificados:
- **app.py**
  - Agregado session state para control de scraper
  - Botón "⏹️ Detener Descarga"
  - Sección "🕐 Tareas Programadas"
  - Barra de progreso en descargas
  - Manejo de banderas de parada

### Nuevos:
- **task_scheduler.py** - Ejecutor de tareas programadas
- **run_scheduler.bat** - Script para Windows
- **run_scheduler.sh** - Script para Linux/Mac
- **SCRAPER_CONTROL.md** - Documentación completa

---

## 🚀 Cómo Usar

### Detener Descarga

```
1. Sidebar → "Descargar de Internet"
2. Click "⬇️ Descargar Propiedades"
3. Se muestra barra de progreso
4. Click "⏹️ Detener Descarga" (aparece durante descarga)
5. Se detiene y guarda lo descargado
```

### Programar Tarea Automática

```
1. Sidebar → "Tareas Programadas"
2. Checkbox "Habilitar tarea programada" ✅
3. Seleccionar hora (ej: 22:00)
4. Configurar:
   - Zona: Palermo, Recoleta, etc.
   - Portal: Argenprop o BuscadorProp
   - Props: 5-50
   - Tipo: Venta o Alquiler
5. Click "💾 Guardar Configuración de Tarea"
```

### Ejecutar Task Scheduler

**Windows:**
```powershell
# Doble click en run_scheduler.bat
# O desde terminal:
python task_scheduler.py
```

**Linux/Mac:**
```bash
./run_scheduler.sh
# O:
python3 task_scheduler.py
```

---

## 📊 Características Técnicas

### Control de Scraper
```python
# Session state flags
st.session_state.scraper_running      # Si está descargando
st.session_state.scraper_stop_flag    # Flag para detener

# Verificación en loop
if st.session_state.scraper_stop_flag:
    # Detener y guardar
```

### Tareas Programadas
```json
{
  "id": "tarea_timestamp",
  "hora": "22:00",
  "zona": "Temperley",
  "portal": "BuscadorProp",
  "props": 20,
  "tipo": "Venta",
  "habilitada": true,
  "fecha_creacion": "2024-11-21 15:30:00"
}
```

### Task Scheduler
```python
class TaskScheduler:
    - cargar_tareas()         # Lee JSON
    - ejecutar_tarea()        # Ejecuta scraper
    - verificar_tareas_pendientes()  # Verifica hora
    - iniciar_scheduler()     # Loop principal
```

---

## 🎓 Ejemplos

### Ejemplo 1: Detener Descarga después de 3 zonas

```
Usuario:
1. Descarga: Palermo, Recoleta, San Isidro, Belgrano, Flores
2. Después de Recoleta → Click "⏹️"

Resultado:
✅ Palermo: 10 props
✅ Recoleta: 12 props
❌ San Isidro (no descargó)
Total guardado: 22 propiedades
```

### Ejemplo 2: Descarga automática diaria

```
Configuración:
- Hora: 22:00
- Zona: Temperley
- Portal: BuscadorProp
- Props: 20
- Tipo: Venta

Ejecución:
Todos los días a las 22:00:
  ✅ Descarga 20 propiedades de Temperley
  ✅ Las agrega a la BD
  ✅ Regenera ChromaDB
  ✅ Registra en logs
```

### Ejemplo 3: Múltiples tareas

```
Tarea 1: 10:00 - Palermo (Venta)
Tarea 2: 14:00 - Recoleta (Alquiler)
Tarea 3: 22:00 - Temperley (Venta)

Timeline:
10:00 → Ejecuta Tarea 1
14:00 → Ejecuta Tarea 2
22:00 → Ejecuta Tarea 3

Sin intervención del usuario
```

---

## 📈 Mejoras vs Versión Anterior

| Feature | v2.2 | v2.3 |
|---------|------|------|
| Descarga manual | ✅ | ✅ |
| Detener descarga | ❌ | ✅ |
| Barra de progreso | ❌ | ✅ |
| Tareas programadas | ❌ | ✅ |
| Task scheduler | ❌ | ✅ |
| Almacenamiento tareas | ❌ | ✅ (JSON) |

---

## ⚙️ Configuración

### Cambiar intervalo de verificación

En `task_scheduler.py` línea 86:
```python
scheduler.iniciar_scheduler(intervalo_verificacion=30)
# 30 segundos por defecto
# Cambiar a: 10, 15, 60, etc.
```

### Cambiar archivo de tareas

En `task_scheduler.py` línea 23:
```python
def __init__(self, config_file="scheduled_tasks.json"):
    # Cambiar nombre de archivo si necesitas
```

---

## 🔍 Monitoreo

### Ver estado de descarga en la app
```
- Barra de progreso
- Mensaje de estado
- Contador de propiedades
- Botón detener (habilitado/deshabilitado)
```

### Ver logs de scheduler
```
scheduler.log

2024-11-21 22:00:00 - INFO - 🚀 Ejecutando tarea: Temperley @ 22:00
2024-11-21 22:05:12 - INFO - ✅ Tarea completada: 20 propiedades agregadas
2024-11-21 22:05:15 - INFO - ✅ ChromaDB regenerado
```

---

## 🐛 Troubleshooting

### Problema: Botón "Detener" no aparece
**Solución:** Aparece solo durante descarga activa

### Problema: Tareas no se ejecutan
**Checklist:**
1. ¿Task scheduler está ejecutándose?
2. ¿Hora configurada es correcta (HH:MM)?
3. ¿Tarea está habilitada?
4. Ver `scheduler.log` para errores

### Problema: Se pierden propiedades al detener
**No pasa:** Se guardan automáticamente

### Problema: Scheduler usa mucha CPU
**Solución:** Aumentar `intervalo_verificacion` (30→60 segundos)

---

## 📋 Próximas Mejoras

- [ ] Base de datos para tareas (en lugar de JSON)
- [ ] Notificaciones (email/Telegram al completar)
- [ ] Dashboard de monitoreo
- [ ] Historial de ejecuciones
- [ ] Ejecutar en servidor remoto
- [ ] Retry automático si falla
- [ ] Notificación de errores

---

## 🎊 Resumen

✅ **Agregado:**
- Botón para detener scraper
- Tareas programadas automáticas
- Task scheduler independiente
- Barra de progreso
- Almacenamiento de tareas en JSON
- Scripts para ejecutar scheduler
- Documentación completa

✨ **Versión:** 2.3  
🎯 **Status:** ✅ PRODUCTION READY

---

Para más detalles, ver [SCRAPER_CONTROL.md](SCRAPER_CONTROL.md)
