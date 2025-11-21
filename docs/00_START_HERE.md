# 🚀 GETTING STARTED - Georef Integration

## 📌 Resumen Rápido

Se integró **API Georef** (datos.gob.ar) para scraping dinámico:
- ✅ 24 provincias Argentina (dinámico, no hardcodeado)
- ✅ Municipios/localidades dinámicas por provincia
- ✅ Opción "Todas" para scrappear provincia completa
- ✅ Fallback automático si falla la API

**Versión:** 2.2  
**Estado:** ✅ Production Ready

---

## ⚡ Quick Start (5 minutos)

### 1. Ejecutar App
```bash
streamlit run app.py
```

### 2. Ir a Sidebar → "Descargar de Internet"
Haz click en "Descargar de Internet"

### 3. Seleccionar Provincia
```
Provincia: "Ciudad Autónoma de Buenos Aires"
```

### 4. Seleccionar Localidades
```
Localidades: Selecciona "Todas" o zonas específicas
```

### 5. Configurar Scraping
```
Portal:     Argenprop
Tipo:       Venta
Props/zona: 10
```

### 6. Descargar
Clickea "⬇️ Descargar Propiedades"

### 7. Ver Resultados
Presiona **F5** para actualizar

**¡Listo!** Ahora busca con las nuevas propiedades.

---

## 📚 Documentación

### Para Usuarios
1. **[GEOREF_USO.md](GEOREF_USO.md)** - Manual completo
   - Paso a paso
   - 3 ejemplos de uso
   - Troubleshooting básico

2. **[GEOREF_INTEGRATION.md](GEOREF_INTEGRATION.md)** - Documentación técnica
   - Cómo funciona Georef
   - API documentada
   - Cambios de código

### Para Desarrolladores
1. **[ROADMAP.md](ROADMAP.md)** - Próximas 10 fases
   - Orden de prioridad
   - Estimaciones de esfuerzo
   - Timeline de 4 semanas

2. **[COMPLETION_CHECKLIST.md](COMPLETION_CHECKLIST.md)** - Lo que se completó
   - Todas las tareas ✅
   - Validaciones realizadas
   - Métricas

3. **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Solución de problemas
   - 10 problemas comunes
   - Soluciones paso a paso
   - Comandos de debug

### Para DevOps
1. **[GEOREF_SUMMARY.md](GEOREF_SUMMARY.md)** - Resumen ejecutivo
   - Cambios de código
   - Performance metrics
   - Ventajas/limitaciones

---

## 🎯 Cambios Principales

### En `scrapers.py` (líneas 29-72)
Nueva clase **GeorefAPI**:
```python
from scrapers import GeorefAPI

# Obtener 24 provincias
provincias = GeorefAPI.obtener_provincias()

# Obtener municipios de una provincia
municipios = GeorefAPI.obtener_municipios(provincia_id="01")

# Obtener todo para caché
datos = GeorefAPI.obtener_todo()
```

### En `app.py` (líneas 222-317)
UI mejorada:
```
ANTES: Dropdown hardcodeado de 13 zonas
DESPUÉS: Dropdown dinámico con 24 provincias + municipios
```

---

## ✅ Validación

Todo ha sido testeado y validado:

```bash
# Verificar sintaxis
✅ python -m py_compile app.py
✅ python -m py_compile scrapers.py

# Test API Georef
✅ python test_georef_api.py
   Output: 24 provincias, municipios funcional

# Test Integración
✅ python test_georef_integration.py
   Output: Todos los tests pasaron
```

---

## 🔧 Troubleshooting Rápido

### "Error cargando geografía"
→ Usa fallback automático (13 zonas hardcodeadas)

### "No veo las nuevas propiedades"
→ Presiona F5 para recargar página

### "Scraping tarda mucho"
→ Reduce Props/zona a 5-10

### "Las nuevas propiedades no aparecen en búsqueda"
→ Ejecuta: `python regenerar_chromadb.py`

Más info en [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

---

## 📊 Especificaciones Técnicas

| Especificación | Detalle |
|---------------|---------|
| **API** | https://apis.datos.gob.ar/georef/api |
| **Provincias** | 24 (todas de Argentina) |
| **Municipios** | 2,000+ (dinámico) |
| **Timeout** | 10 segundos |
| **Caché** | 1 minuto (Streamlit) |
| **Fallback** | 13 zonas si falla API |
| **Python** | 3.11+ |
| **Streamlit** | 1.28+ |

---

## 🚀 Funcionalidades

### ✅ Completadas
- [x] Clase GeorefAPI (3 métodos)
- [x] UI dinámica provincia → municipios
- [x] Opción "Todas" para scrappear provincia
- [x] Fallback automático
- [x] Tests validados
- [x] Documentación completa

### ⏳ Próximas Fases
- [ ] Regeneración automática ChromaDB
- [ ] Estadísticas por zona
- [ ] Historial de descargas
- [ ] Exportar a Excel
- [ ] ML prediction de precios
- [ ] Scraping programado (cada 24h)

Ver [ROADMAP.md](ROADMAP.md) para timeline completo.

---

## 💡 Ejemplos de Uso

### Ejemplo 1: Scrappear Todo CABA
```
Provincia: "Ciudad Autónoma de Buenos Aires"
Localidades: "Todas"
Portal: "Argenprop"
Tipo: "Venta"
Props/zona: 20
```
→ Scrappea 15 comunas × 20 = hasta 300 propiedades

### Ejemplo 2: Scrappear Buenos Aires
```
Provincia: "Buenos Aires"
Localidades: "Lomas de Zamora", "Temperley"
Portal: "BuscadorProp"
Tipo: "Alquiler"
Props/zona: 10
```
→ Scrappea 2 zonas × 10 = 20 propiedades

### Ejemplo 3: Si Falla Georef
```
(API no responde)
→ Fallback automático a 13 zonas
→ Scraping funciona igual
```

---

## 🎓 Cómo Aprovechar

### Para Usuarios Básicos
1. Abre `GEOREF_USO.md` para instrucciones paso a paso
2. Sigue los 3 ejemplos
3. Si hay problema, ve a TROUBLESHOOTING.md

### Para Usuarios Avanzados
1. Modifica `scrapers.py` línea 66 para más provincias
2. Customiza fallback en `app.py` línea 255
3. Implementa próximas fases del ROADMAP.md

### Para Desarrolladores
1. Lee `GEOREF_INTEGRATION.md` para entender API
2. Revisa `COMPLETION_CHECKLIST.md` para lo que se hizo
3. Consulta `ROADMAP.md` para próximas tareas

---

## 📝 Archivos Nuevos

| Archivo | Propósito |
|---------|-----------|
| `scrapers.py` (modificado) | Agregada clase GeorefAPI |
| `app.py` (modificado) | Agregada UI dinámica |
| `test_georef_api.py` | Test de API Georef |
| `test_georef_integration.py` | Test de integración |
| `GEOREF_INTEGRATION.md` | Documentación técnica |
| `GEOREF_USO.md` | Manual de usuario |
| `GEOREF_SUMMARY.md` | Resumen ejecutivo |
| `ROADMAP.md` | 10 fases futuras |
| `TROUBLESHOOTING.md` | Solución de problemas |
| `COMPLETION_CHECKLIST.md` | Tareas completadas |

---

## 🎉 Conclusión

✅ **Georef Integration completada exitosamente**

- API integrada y funcionando
- UI dinámica con 24 provincias × N municipios
- Fallback automático si falla
- Documentación completa (5 archivos)
- Tests validados

**Próximo paso:** Implementar Fase 2 (Regeneración automática ChromaDB) - ver [ROADMAP.md](ROADMAP.md)

---

## ❓ Preguntas Frecuentes

**Q: ¿Es necesario cambiar algo en mi workflow?**  
A: No. Funciona igual que antes, pero con opciones dinámicas.

**Q: ¿Si Georef falla qué pasa?**  
A: Usa fallback automático (13 zonas predefinidas).

**Q: ¿Cuánto tiempo tarda el scraping?**  
A: 2-8 minutos dependiendo de cantidad de zonas y propiedades.

**Q: ¿Necesito instalar algo nuevo?**  
A: No. Todo está en requirements.txt.

**Q: ¿Se pierden las propiedades antiguas?**  
A: No. Se agregan a la BD (deduplicadas por URL).

**Q: ¿Cómo veo las nuevas propiedades?**  
A: Presiona F5 para recargar.

---

**Para más ayuda, consulta:**
- 📖 [GEOREF_USO.md](GEOREF_USO.md) - Manual detallado
- 🔧 [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Solución de problemas
- 🚀 [ROADMAP.md](ROADMAP.md) - Próximas mejoras
- ✅ [COMPLETION_CHECKLIST.md](COMPLETION_CHECKLIST.md) - Tareas completadas

---

**Última actualización:** 2024  
**Versión:** 2.2 (Georef Integration)  
**Status:** ✅ PRODUCTION READY
