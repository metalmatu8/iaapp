# 🛑 CONTROL DE SCRAPER Y TAREAS PROGRAMADAS

## ✅ Nuevas Características

### 1. Botón para Detener el Scraper ⏹️

**Ubicación:** Sidebar → "Descargar de Internet"

**Funcionalidad:**
- Detiene la descarga en cualquier momento
- Guarda las propiedades descargadas hasta el momento
- Muestra mensaje de confirmación

**Cómo usar:**
```
1. Inicia descarga: Click "⬇️ Descargar Propiedades"
2. Si necesitas detener: Click "⏹️ Detener Descarga"
3. Se detendrá al finalizar la zona actual
4. Se guardarán las propiedades descargadas
```

**Ventajas:**
- ✅ No pierdes propiedades descargadas
- ✅ Interrumpe sin errores
- ✅ Muestra cuántas se agregaron antes de detener

---

### 2. Tareas Programadas 🕐

**Ubicación:** Sidebar → "Tareas Programadas"

**Funcionalidad:**
- Configura descargas automáticas
- Se ejecutan a la hora especificada
- Se pueden crear múltiples tareas

#### A. Habilitar Tarea Programada

```
1. Checkbox: "Habilitar tarea programada" ✅
2. Seleccionar: "Hora de ejecución" (22:00)
3. Configurar:
   - Zona: Palermo, Recoleta, etc.
   - Portal: Argenprop o BuscadorProp
   - Props: 5-50 propiedades
   - Tipo: Venta o Alquiler
4. Click: "💾 Guardar Configuración de Tarea"
```

#### B. Ver Tareas Configuradas

```
Sección "📋 Tareas Configuradas"
- Muestra todas las tareas guardadas
- Hora de ejecución
- Zona y portal
- Tipo de búsqueda
- Botón para eliminar
```

---

## 🚀 Uso Completo

### Ejemplo 1: Detener Descarga

```
Usuario:
1. Abre app.py
2. Sidebar → "Descargar de Internet"
3. Selecciona: Zona "Palermo", Props "50"
4. Click: "⬇️ Descargar Propiedades"
5. Después de 3 zonas → Click: "⏹️ Detener Descarga"

Resultado:
✅ Se descargaron 3 zonas
✅ ~150 propiedades agregadas
✅ Se guardaron automáticamente
❌ No se descargó el resto
```

### Ejemplo 2: Configurar Tarea Automática Diaria

```
Usuario:
1. Abre app.py
2. Sidebar → "Tareas Programadas"
3. Checkbox: "Habilitar tarea programada" ✅
4. Hora: 22:00 (10 PM)
5. Zona: "Temperley"
6. Portal: "BuscadorProp"
7. Props: 20
8. Tipo: "Venta"
9. Click: "💾 Guardar Configuración de Tarea"

Resultado:
✅ Tarea configurada
✅ Se ejecutará diariamente a las 22:00
✅ Descargará 20 propiedades de Temperley
✅ Automáticamente
```

### Ejemplo 3: Múltiples Tareas Automáticas

```
Usuario puede crear:
- Tarea 1: 10:00 - Palermo (Venta, 15 props)
- Tarea 2: 14:00 - Recoleta (Alquiler, 10 props)
- Tarea 3: 22:00 - Temperley (Venta, 20 props)

Se ejecutarán automáticamente a sus horas
```

---

## 🖥️ Ejecutar Task Scheduler

### Windows

**Opción 1: Doble click**
```
1. Abre carpeta del proyecto
2. Doble click: run_scheduler.bat
3. Se abre terminal
4. Muestra: "Iniciando Task Scheduler..."
5. Presiona Ctrl+C para detener
```

**Opción 2: Línea de comandos**
```powershell
cd C:\ruta\a\iaapp
python task_scheduler.py
```

### Linux / Mac

**Opción 1: Ejecutar script**
```bash
chmod +x run_scheduler.sh
./run_scheduler.sh
```

**Opción 2: Python directo**
```bash
cd /ruta/a/iaapp
python3 task_scheduler.py
```

### Ejecutar en Background (Windows)

```powershell
# PowerShell
Start-Process python -ArgumentList "task_scheduler.py" -NoNewWindow

# O con cmd
start /B python task_scheduler.py
```

### Ejecutar en Background (Linux/Mac)

```bash
# Nohup
nohup python3 task_scheduler.py > scheduler.log 2>&1 &

# O con Screen
screen -d -m -S scheduler python3 task_scheduler.py

# Verificar
ps aux | grep task_scheduler
```

---

## 📁 Archivos Nuevos

### task_scheduler.py
```python
# Ejecutor de tareas programadas
# Lee scheduled_tasks.json
# Ejecuta tareas a sus horas configuradas
# Guarda logs en scheduler.log

Uso:
  python task_scheduler.py
```

### run_scheduler.bat (Windows)
```
Script para ejecutar scheduler
Doble click o desde cmd
```

### run_scheduler.sh (Linux/Mac)
```
Script para ejecutar scheduler
./run_scheduler.sh
```

### scheduled_tasks.json (Generado)
```json
[
  {
    "id": "tarea_1234567890",
    "hora": "22:00",
    "zona": "Temperley",
    "portal": "BuscadorProp",
    "props": 20,
    "tipo": "Venta",
    "habilitada": true,
    "fecha_creacion": "2024-11-21 15:30:00"
  }
]
```

---

## 🔄 Flujo de Ejecución

### Descarga Manual

```
Usuario clickea "Descargar"
    ↓
Scraper inicia
    ↓
Descarga zona 1
    ↓
[Usuario puede hacer click "Detener"]
    ↓
Descarga zona 2
    ↓
... (más zonas)
    ↓
Scraper termina
    ↓
Propiedades se guardan
```

### Tareas Programadas

```
Task Scheduler inicia
    ↓
Verifica hora actual cada 30 segundos
    ↓
¿Es hora de ejecutar una tarea?
    ├─ SÍ:
    │   ↓
    │   Obtiene configuración de tarea
    │   ↓
    │   Ejecuta scraper
    │   ↓
    │   Descarga propiedades
    │   ↓
    │   Regenera ChromaDB
    │   ↓
    │   Registra en logs
    │
    └─ NO:
        ↓
        Espera 30 segundos
        ↓
        Verifica nuevamente
```

---

## 📊 Logs y Monitoreo

### Ver Logs de Descarga Manual

```
Directamente en la app
- Barra de progreso
- Mensajes de estado
- Contador de propiedades
```

### Ver Logs de Task Scheduler

**Windows:**
```powershell
# Tiempo real
Get-Content scheduler.log -Wait

# Últimas líneas
Get-Content scheduler.log -Tail 20
```

**Linux/Mac:**
```bash
# Tiempo real
tail -f scheduler.log

# Últimas líneas
tail -20 scheduler.log

# Buscar errores
grep ERROR scheduler.log
```

---

## ⚙️ Configuración Avanzada

### Cambiar Intervalo de Verificación

En `task_scheduler.py`, línea ~85:
```python
scheduler.iniciar_scheduler(intervalo_verificacion=30)
# Cambiar 30 a otro número de segundos
# Menor = más frecuente (consume más CPU)
# Mayor = menos frecuente (puede perder hora exacta)
```

### Cambiar Puerto/Host (Futuro)

Para ejecutar scheduler en servidor remoto:
```python
# Próxima versión:
# - Guardar tareas en BD en lugar de JSON
# - API REST para gestionar tareas
# - Ejecutar en servidor separado
```

---

## 🐛 Troubleshooting

### P: La descarga no se detiene al clickear "Detener"

**R:** Se detiene al terminar la zona actual. Espera ~30 segundos.

### P: El scheduler no ejecuta las tareas

**R:** Verificar:
1. Está ejecutándose `task_scheduler.py`
2. La hora configurada es correcta (HH:MM)
3. Ver `scheduler.log` para errores

### P: ¿Pierdo propiedades si detengo a mitad?

**R:** No. Se guardan las que se descargaron hasta el momento.

### P: ¿Puedo ejecutar scheduler y app juntos?

**R:** Sí. En dos terminales diferentes:
```
Terminal 1: streamlit run app.py
Terminal 2: python task_scheduler.py
```

### P: ¿Las tareas se ejecutan incluso si cierro la app?

**R:** Sí. El scheduler es independiente. Necesita estar ejecutándose en terminal.

---

## 🎯 Casos de Uso

### Uso 1: Descarga Manual Controlada
```
Usuario descarga manualmente
Puede detener si se demora mucho
Guarda propiedades descargadas
```

### Uso 2: Descarga Diaria Automática
```
Configura tarea a las 22:00
Se ejecuta automáticamente cada día
Descarga Temperley automáticamente
```

### Uso 3: Múltiples Descargas Distribuidas
```
Tarea 1: 10:00 - Palermo
Tarea 2: 14:00 - Recoleta
Tarea 3: 22:00 - Temperley
Se ejecutan sin intervención
```

### Uso 4: Desarrollo/Testing
```
Descarga manual mientras develops
Detén cuando necesites
Prueba nuevas features
```

---

## 📝 Notas Importantes

### Performance
- Cada zona tarda 10-30 segundos
- Con detención, ahorras tiempo
- Tareas programadas no bloquean app

### Seguridad
- Tareas guardadas en JSON (local)
- No require servidor
- Se ejecutan en la misma máquina

### Integraciones Futuras
- [ ] Ejecutar tareas en servidor remoto
- [ ] API REST para gestionar tareas
- [ ] Notificaciones (email/Telegram)
- [ ] Dashboard de monitoreo
- [ ] Historial de ejecuciones

---

## 🎓 Resumen

**Lo que agregaste:**
1. ✅ Botón para detener scraper
2. ✅ Configuración de tareas programadas
3. ✅ Task scheduler para ejecutar automáticamente
4. ✅ Scripts para iniciar scheduler
5. ✅ Almacenamiento de tareas en JSON

**Próximas mejoras:**
- [ ] Base de datos para tareas
- [ ] Notificaciones
- [ ] Dashboard de monitoreo
- [ ] Ejecutar en servidor remoto

---

**Última actualización:** 2024  
**Versión:** 2.3  
**Features:** Stop Scraper + Scheduled Tasks
