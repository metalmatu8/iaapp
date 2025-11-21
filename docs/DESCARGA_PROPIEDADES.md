# 🌐 Guía de Descarga de Propiedades Reales

## ¿Qué es esto?

Ahora tu app puede descargar **propiedades reales de internet** desde MercadoLibre Inmuebles. Puedes llegar a tener **cientos de miles de propiedades** en tu base de datos.

## 📥 3 Formas de Descargar

### Opción 1: Desde la Interfaz (Recomendada)

1. Ejecuta la app:
```bash
streamlit run app.py
```

2. En el sidebar izquierdo, abre "📥 Descargar Propiedades"
3. Selecciona las zonas
4. Haz clic en "⬇️ Descargar Propiedades"
5. Espera 1-2 minutos
6. Recarga la página (F5)

**Resultado**: Se crea `properties_expanded.csv` con todas las propiedades

### Opción 2: Script de Descarga Masiva

Para descargar **todas las zonas de Buenos Aires** automáticamente:

```bash
python download_properties.py
```

Esto descarga:
- 20 zonas de Capital Federal
- 10 zonas de Gran Buenos Aires
- ~2,600 propiedades (aprox 50-100 por zona)

**Tiempo**: 20-30 minutos

### Opción 3: Descarga Personalizada

Descargar solo zonas específicas:

```bash
python download_properties.py Palermo Recoleta "San Isidro"
```

---

## 📊 Qué Información Obtiene

De cada propiedad:
```
✅ ID único
✅ Tipo (Casa, Departamento, etc.)
✅ Zona
✅ Precio en USD
✅ Descripción completa
✅ Latitud y Longitud
✅ URL original (enlace a MercadoLibre)
✅ Fecha de descarga
✅ Fuente (MercadoLibre, Zonaprop, etc.)

⚠️ Nota: MercadoLibre API no proporciona detalles como habitaciones, baños
```

---

## 💾 Cómo Funciona el Almacenamiento

### Archivos
```
properties.csv                  ← Dataset original (10 propiedades)
properties_expanded.csv         ← Dataset expandido (tu nueva base de datos)
```

### Tamaño Esperado
```
100 propiedades    = ~50 KB
1,000 propiedades  = ~500 KB
10,000 propiedades = ~5 MB
100,000 propiedades = ~50 MB
1,000,000 propiedades = ~500 MB (sí, es posible)
```

---

## 🚀 Cómo Llegar a 1 Millón de Propiedades

### Paso 1: Descargar de múltiples fuentes (16-20 horas)
```bash
# Ejecutar múltiples veces para diferentes búsquedas
python download_properties.py
# Luego buscar términos diferentes:
python download_properties.py "casa moderna"
python download_properties.py "depto inversión"
python download_properties.py "ph luminoso"
```

### Paso 2: Automatizar Descarga Periódica
Crear `scheduler.py`:

```python
from apscheduler.schedulers.background import BackgroundScheduler
from download_properties import descargar_propiedades_personalizado

scheduler = BackgroundScheduler()

# Descargar cada 6 horas
scheduler.add_job(
    descargar_propiedades_personalizado,
    'interval',
    hours=6,
    args=[["Palermo", "Recoleta", "San Isidro"]]
)

scheduler.start()
```

### Paso 3: Escalar con Base de Datos
Migrar de CSV a PostgreSQL para mejor rendimiento:

```bash
pip install sqlalchemy psycopg2
# Ver DEVELOPMENT.md § 2.3
```

---

## ⚠️ Consideraciones Legales

1. **MercadoLibre**: Tiene API pública, permitida para investigación
2. **Zonaprop/Argenprop**: Revisar su `robots.txt` antes
3. **Ética**: No hacer scraping agresivo (respetar rate limits)
4. **Datos**: No usar información personal para malos fines

**Recomendación**: Usar APIs oficiales cuando sea posible

---

## 🔧 Troubleshooting

### Error: "requests no existe"
```bash
pip install requests
```

### Error: "API no responde"
- Espera 5 minutos (rate limit)
- Verifica conexión a internet
- Intenta desde navegador: https://api.mercadolibre.com/sites/MLA/search?q=casa

### App lenta con muchas propiedades
- Solución: Migrar a PostgreSQL
- Ver `config.py` para cambiar `VECTOR_DB_TYPE`

---

## 📈 Estadísticas Esperadas

```
Descargas en 1 hora:
━━━━━━━━━━━━━━━━━━━━━
 Propiedades:        2,000-5,000
 Zonas únicas:       50-100
 Precio promedio:    $200,000-500,000
 Archivos:           ~10-20 MB CSV
```

---

## 🎯 Próximo Paso

1. Ejecuta: `streamlit run app.py`
2. Descarga algunas propiedades
3. Busca con términos naturales: "Casa en Palermo con pileta"
4. Verás decenas de propiedades reales!

---

**¿Necesitas más propiedades?** Ver `DEVELOPMENT.md` para integrar APIs pagadas o scraping avanzado.
