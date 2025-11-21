# Integración de Georef API - Scraping Mejorado

## Resumen de Cambios

Se ha integrado la **API Georef** (datos.gob.ar) en la sección de descarga de propiedades para hacer el scraping más dinámico e inteligente.

### ¿Qué cambió?

#### 1. **Clase GeorefAPI en `scrapers.py`** (líneas 29-72)

Tres métodos estáticos:

```python
# 1. Obtener todas las provincias de Argentina
provincias = GeorefAPI.obtener_provincias()
# Retorna: [{"id": "01", "nombre": "Ciudad Autónoma de Buenos Aires"}, ...]

# 2. Obtener municipios de una provincia
municipios = GeorefAPI.obtener_municipios(provincia_id="01")
# Retorna: [{"id": "0101", "nombre": "Comuna 1"}, ...]

# 3. Obtener todo (provincias + municipios) - para caché
datos = GeorefAPI.obtener_todo()
# Retorna: {"provincias": [...], "municipios_por_provincia": {...}}
```

**Features:**
- Conexión a https://apis.datos.gob.ar/georef/api
- Timeout: 10 segundos
- Manejo de excepciones robusto
- Caching con `@st.cache_data` en app.py

#### 2. **UI Mejorada en `app.py`** (líneas 222-317)

**Antes (hardcodeado):**
```python
zonas_seleccionadas = st.multiselect("Zonas", ["Palermo", "Recoleta", ...])
```

**Ahora (dinámico):**
```
1. Dropdown "Provincia": Todas + 24 provincias de Argentina
2. Dropdown "Localidades": Dinámico basado en provincia seleccionada
3. Si selecciona "Todas": scrappea todos los municipios
4. Selector de portal (Argenprop/BuscadorProp)
5. Radio button: Venta/Alquiler
6. Límite de propiedades por zona (5-100)
```

### Flujo Actual

```
Usuario abre app.py
    ↓
Carga GeorefAPI.obtener_todo() (caché 1 minuto)
    ↓
Muestra dropdown "Provincia" con 24 opciones
    ↓
Usuario selecciona provincia
    ↓
Cargas municipios dinámicamente
    ↓
Usuario selecciona "Todas" o zonas específicas
    ↓
Clickea "⬇️ Descargar Propiedades"
    ↓
Scrappea cada zona con ArgenpropScraper/BuscadorPropScraper
    ↓
Agrega a BD (deduplicación por URL)
    ↓
Regenera ChromaDB automático
    ↓
"Recarga la página para ver nuevas propiedades"
```

### Fallback (error Georef)

Si Georef API falla (conexión, timeout):
- Muestra mensaje de error
- Usa lista hardcodeada de zonas (CABA + GBA)
- Mismo flujo de scraping

### Instalación/Requisitos

✅ Ya incluido en `requirements.txt`:
- `requests` → para HTTP requests a Georef
- `streamlit` → para UI
- `pandas`, `chromadb`, `sentence-transformers` → para RAG

No necesita nuevas instalaciones.

### Testing

Ejecutar para verificar:
```bash
python test_georef_api.py
```

Output esperado:
```
=== Test API Georef (Argentina) ===

Provincias encontradas: 24
Primeras 5: ['Ciudad Autónoma de Buenos Aires', 'Neuquén', ...]

Provincias con datos: 5
  Ciudad Autónoma de Buenos Aires: 10 municipios
    Primeros 3: ['Comuna 3', 'Comuna 7', 'Comuna 10']
  Neuquén: 10 municipios
  ...
```

### Próximos Pasos

1. ✅ Integración Georef en app.py (HECHO)
2. ⏳ Opción "Todas" para scrappear provincia completa
3. ⏳ Regeneración automática de ChromaDB post-scraping
4. ⏳ Almacenar historial de descargas (fecha, zona, cantidad)
5. ⏳ Métricas: propiedades por zona, precios promedio, etc.

### Troubleshooting

**Problema:** "Error cargando geografía"
**Solución:** Usa fallback. Verifica tu conexión a internet.

**Problema:** "Dropdown de municipios está vacío"
**Solución:** Algunos municipios pueden no tener datos. Prueba otra provincia.

**Problema:** "Scraping no trae propiedades"
**Solución:** 
1. Verifica que el portal está disponible
2. Intenta con otro tipo (Venta/Alquiler)
3. Aumenta el límite (10-20)

**Problema:** "ChromaDB no se regeneró"
**Solución:** 
1. Reinicia la app (F5)
2. Ejecuta manualmente: `python regenerar_chromadb.py`

### API Georef - Documentación

https://apis.datos.gob.ar/georef/api

Endpoints:
- `GET /provincias` → todas las provincias
- `GET /municipios` → municipios (filtrable por provincia)
- `GET /localidades` → localidades específicas

Parámetros:
- `max=N` → máximo de resultados
- `provincia=ID` → filtrar por provincia
- Completo: https://apis.datos.gob.ar/georef/api/provincias?max=24

### Métricas

- **24 provincias** en Argentina
- **Municipios por provincia:** 5-50 (varía)
- **Conexión:** ~500ms por request
- **Caché:** 1 minuto en Streamlit

### Cambios de Código Detallados

```python
# ANTES
zonas = ["Palermo", "Recoleta", ...]  # Hardcodeado
user_zones = st.multiselect("Zonas", zonas)

# DESPUÉS
from scrapers import GeorefAPI

geo = GeorefAPI.obtener_todo()  # Dinámico
provincia = st.selectbox("Provincia", [p["nombre"] for p in geo["provincias"]])
municipios = geo["municipios_por_provincia"][provincia]
user_zones = st.multiselect("Municipios", [m["nombre"] for m in municipios])
```

---

**Versión:** 2.2  
**Fecha:** 2024  
**Estado:** ✅ Funcional
