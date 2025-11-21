# Georef Integration - Modo de Uso

## 🎯 ¿Qué es?

La **integración de Georef** permite:
- ✅ Seleccionar dinámicamente provincias (24 opciones)
- ✅ Seleccionar localidades/municipios de la provincia
- ✅ Opción "Todas" para scrappear una provincia completa
- ✅ Scraping inteligente desde Argenprop o BuscadorProp
- ✅ Fallback automático si falla la API

## 📋 Cómo Usar

### Paso 1: Abre la aplicación

```bash
streamlit run app.py
```

### Paso 2: Ve a "📥 Descargar Propiedades"

En el sidebar izquierdo, haz click en "Descargar de Internet"

### Paso 3: Selecciona Provincia

```
Dropdown "Provincia"
├── Todas                              (scrappea todas las provincias)
├── Ciudad Autónoma de Buenos Aires   (15 municipios/comunas)
├── Buenos Aires                      (N municipios)
├── Córdoba                           (N municipios)
└── ... (24 provincias total)
```

### Paso 4: Selecciona Localidades

Después de elegir provincia, elige localidades:

```
Multiselect "Localidades a descargar"
├── Todas                      (scrappea TODO)
├── Comuna 1, 2, 3, ...
├── San Isidro, San Martín, etc.
└── ...
```

**Ejemplo CABA:**
- Selecciona "Todas" → scrappea todas las 15 comunas
- O selecciona "Comuna 1", "Comuna 15" → solo esas 2

**Ejemplo Buenos Aires:**
- Selecciona "Todas" → scrappea todos los municipios
- O selecciona zonas específicas

### Paso 5: Configura Scraping

```
Portal:           Argenprop / BuscadorProp
Props/zona:       5-100 (predeterminado: 10)
Tipo:             Venta / Alquiler
```

### Paso 6: Clickea "⬇️ Descargar Propiedades"

```
⏳ Descargando desde Argenprop... esto puede tomar 1-2 minutos

📍 Descargando Comuna 1...
📍 Descargando Comuna 2...
...
✅ 23 propiedades agregadas!
Total en BD: 36 propiedades
⚠️ Recarga la página para ver las nuevas propiedades (F5)
```

## 📊 Ejemplos

### Ejemplo 1: Scrappear Todo CABA

1. Provincia: "Ciudad Autónoma de Buenos Aires"
2. Localidades: "Todas"
3. Portal: "Argenprop"
4. Tipo: "Venta"
5. Props/zona: 20
6. Click "⬇️ Descargar"

**Resultado:** Scrappea 15 comunas × 20 props = hasta 300 propiedades

### Ejemplo 2: Scrappear Palermo + Recoleta

1. Provincia: "Todas" (vuelve a mostrar lista hardcodeada)
2. Localidades: Selecciona "Palermo", "Recoleta"
3. Portal: "BuscadorProp"
4. Tipo: "Alquiler"
5. Props/zona: 10
6. Click "⬇️ Descargar"

**Resultado:** Scrappea 2 zonas × 10 props = 20 propiedades

### Ejemplo 3: Scrappear Provincia Buenos Aires

1. Provincia: "Buenos Aires"
2. Localidades: Selecciona "Lomas de Zamora", "Temperley"
3. Portal: "BuscadorProp"
4. Tipo: "Venta"
5. Props/zona: 15
6. Click "⬇️ Descargar"

**Resultado:** Scrappea 2 zonas × 15 props = 30 propiedades

## ⚠️ Si Falla Georef

Si la API no responde:

```
❌ Error cargando geografía: ...
⚠️  Usando localidades por defecto...
```

Se usa una lista hardcodeada de 13 zonas (Buenos Aires + GBA):
- Palermo, Recoleta, San Isidro, Belgrano, Flores, Caballito, La Boca, 
- San Telmo, Villa Crespo, Colegiales, Lomas de Zamora, Temperley, La Matanza

El scraping funciona igual que con Georef.

## 🔄 Qué Pasa Después

1. **Scraping:** Descarga propiedades de Argenprop/BuscadorProp
2. **Deduplicación:** Compara URLs, no agrega duplicadas
3. **BD:** Inserta en properties.db
4. **CSV:** Exporta a properties_expanded.csv
5. **Mensaje:** "Recarga la página para ver nuevas propiedades (F5)"
6. **Búsqueda:** Ahora busca entre todas (36+ propiedades)

⚠️ **Importante:** Presiona F5 para actualizar y ver las nuevas propiedades

## 📈 Performance

- **Carga de Georef:** ~500ms (caché 1 minuto)
- **Scraping por zona:** 10-30 segundos (depende del portal)
- **Total para 15 zonas:** 2-8 minutos

## 🐛 Troubleshooting

### Q: "No me aparece el dropdown de provincias"
**A:** Georef falló. Usa fallback (localidades hardcodeadas)

### Q: "Scraping tarda mucho"
**A:** Normal. Baja Props/zona a 5-10 o intenta una sola zona

### Q: "Dice '23 propiedades agregadas' pero no las veo"
**A:** Presiona F5 para recargar la página (ChromaDB necesita regenerarse)

### Q: "Las propiedades no salen en búsqueda"
**A:** 
1. Presiona F5
2. Ejecuta `python regenerar_chromadb.py`
3. Reinicia la app

### Q: "Quiero scrappear de otra provincia"
**A:** Cambiar provincia en el dropdown. Las propiedades anteriores quedan en BD.

### Q: "¿Cuántas propiedades como máximo?"
**A:** Técnicamente ilimitadas, pero búsqueda es más lenta con >100

## 🎓 Datos Técnicos

- **API:** https://apis.datos.gob.ar/georef/api
- **Cobertura:** 24 provincias de Argentina
- **Municipios:** 2,000+ municipios/comunas/localidades
- **Actualización:** Diaria (datos.gob.ar)
- **Sin autenticación:** Acceso público

## 🚀 Próximas Mejoras

- [ ] Filtro de precio durante scraping
- [ ] Descarga automática después de scraping
- [ ] Historial de descargas (fecha, cantidad)
- [ ] Estadísticas por zona (precio promedio, tipos)
- [ ] Exportar a Excel con formato

---

**¿Necesitas ayuda?** Revisa los logs en terminal para errores específicos.
