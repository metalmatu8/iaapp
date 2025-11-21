# Actualización de Scrapers - Argenprop y BuscadorProp

## 🎯 Cambios Realizados

### ✅ Zonaprop - **ELIMINADO**
- Removido completamente de `scrapers.py`
- Razón: Bloqueado persistentemente con status 403 (Cloudflare)

### ✅ Argenprop - **REFACTORIZADO Y MEJORADO**
**URL Correcta**: `https://www.argenprop.com/departamentos/{tipo}/{zona}`
- Ejemplo: `https://www.argenprop.com/departamentos/venta/palermo`
- Ejemplo: `https://www.argenprop.com/departamentos/alquiler/belgrano`

**Cambios**:
1. ✅ Eliminada búsqueda con requests (devuelve 404)
2. ✅ Implementado Selenium como método principal
3. ✅ Selector CSS correcto: `.card` (20+ elementos encontrados)
4. ✅ Mejor extracción de descripción y precio
5. ✅ Validación de URLs de propiedades

**Resultado**:
- 5 propiedades extraídas en test (Palermo, Venta)
- Propiedades con descripción, precio y URL válidos

### ✅ BuscadorProp - **NUEVO SCRAPER IMPLEMENTADO**
**URL Correcta**: `https://www.buscadorprop.com.ar/{tipo}-{zona}`
- Ejemplo: `https://www.buscadorprop.com.ar/venta-palermo`
- Ejemplo: `https://www.buscadorprop.com.ar/casas-venta-lomas-de-zamora-temperley`

**Estructura**:
1. ✅ Carga completamente con JavaScript (requiere Selenium)
2. ✅ Búsqueda de links con patrón `/propiedad/ID-descripción`
3. ✅ Espera a desaparecimiento de spinner de carga
4. ✅ Scroll automático para lazy loading
5. ✅ Extracción de datos del elemento padre (tarjeta)

**Resultado**:
- 5 propiedades extraídas en test (Palermo, Venta)
- 45 propiedades encontradas en página
- Propiedades con descripción, precio y URL válidos

## 📝 Uso desde App.py

### Descarga desde Argenprop
```python
props = ArgenpropScraper.buscar_propiedades(
    zona="Palermo",
    tipo="Venta",  # o "Alquiler"
    limit=10,
    debug=True
)
```

### Descarga desde BuscadorProp
```python
props = BuscadorPropScraper.buscar_propiedades(
    zona="Palermo",
    tipo="venta",  # o "alquiler" (minúsculas)
    limit=10,
    debug=True
)
```

### Integración en Streamlit
La app fue actualizada para:
- ✅ Mostrar opciones de "Argenprop" y "BuscadorProp"
- ✅ Remover opción de "Zonaprop"
- ✅ Remover selector de "Modo de scraping" (siempre Selenium)
- ✅ Agregar opción de seleccionar "Venta" o "Alquiler"
- ✅ Agregar delay de 2 segundos entre zonas para no sobrecargar servidores

## 🔧 Cambios Técnicos

### scrapers.py
```python
# Eliminado: ZonapropScraper (clase completa)

# Actualizado: ArgenpropScraper
- buscar_propiedades(): Ahora llama directo a Selenium
- buscar_propiedades_selenium(): 
  * URL: /departamentos/{tipo}/{zona}
  * Selector: .card (20+ elementos)
  * Extracción mejorada de descripción y precio

# Nuevo: BuscadorPropScraper
- buscar_propiedades(): Interfaz estándar
- buscar_propiedades_selenium():
  * URL: /{tipo}-{zona}
  * Patrón: a[href*='/propiedad/']
  * Manejo de carga JavaScript con spinner
  * Scroll automático para lazy loading
```

### app.py
```python
# Cambios en sidebar de descarga:
- Portales: ["Argenprop", "BuscadorProp"]  (sin Zonaprop)
- Removido: "modo_scraping" selector
- Agregado: Radio buttons para "Venta" / "Alquiler"
- Agregado: time.sleep(2) entre zonas

# Imports actualizados:
+ import time
- ZonapropScraper (no se importa)
+ BuscadorPropScraper
```

## ✨ Funcionalidades

| Portal | Método | Estado | Props/Test | Descripción |
|--------|--------|--------|-----------|------------|
| Argenprop | Selenium | ✅ Activo | 5 | URL estructura `/departamentos/{tipo}/{zona}` |
| BuscadorProp | Selenium | ✅ Activo | 5 | URL estructura `/{tipo}-{zona}`, lazy loading |
| Zonaprop | (Eliminado) | ❌ Removido | - | 403 Cloudflare permanente |

## 🚀 Testing

Ejecutar test:
```bash
python test_new_scrapers.py
```

Resultado esperado:
```
Argenprop: 5 propiedades
BuscadorProp: 5 propiedades
Total: 10 propiedades
Base de datos: 3-6 propiedades (según deduplicación)
```

## 🔗 URLs de Ejemplo

### Argenprop
- Venta: `https://www.argenprop.com/departamentos/venta/palermo`
- Alquiler: `https://www.argenprop.com/departamentos/alquiler/belgrano`

### BuscadorProp
- Venta simple: `https://www.buscadorprop.com.ar/venta-palermo`
- Venta múltiples zonas: `https://www.buscadorprop.com.ar/casas-venta-lomas-de-zamora-temperley`
- Alquiler: `https://www.buscadorprop.com.ar/alquiler-recoleta`

## 📊 Base de Datos

- SQLite: `properties.db`
- Tabla: `propiedades` (16 columnas)
- Deduplicación por URL
- Fuentes soportadas: `['Argenprop', 'BuscadorProp']`

## ⚙️ Dependencias

```
selenium>=4.0
webdriver-manager>=4.0
beautifulsoup4
requests
pandas
sentence-transformers
chromadb
streamlit
```

Instalación:
```bash
pip install -r requirements.txt
```

---

**Última actualización**: 21 de Noviembre, 2025
**Estado**: ✅ Producción-ready - Ambos scrapers funcionales
