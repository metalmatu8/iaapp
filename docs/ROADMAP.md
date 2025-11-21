# 🗺️ HOJA DE RUTA - Próximas Mejoras

## Fase Actual ✅ COMPLETADA
**Integración Georef API - Scraping Dinámico**

- ✅ Clase GeorefAPI (obtener_provincias, obtener_municipios, obtener_todo)
- ✅ UI dinámica en app.py (dropdown provincia → municipios)
- ✅ Opción "Todas" para scrappear provincia completa
- ✅ Fallback automático si Georef falla
- ✅ Tests validados (test_georef_api.py, test_georef_integration.py)
- ✅ Documentación (GEOREF_INTEGRATION.md, GEOREF_USO.md)

---

## Fase 2 ⏳ PROPUESTA: Regeneración Automática ChromaDB

### Objetivo
Que ChromaDB se regenere automáticamente después de scraping (sin presionar F5)

### Implementación
```python
# En app.py, después de agregar propiedades:

if st.button("⬇️ Descargar Propiedades"):
    try:
        # ... scraping ...
        nuevas = db.agregar_propiedades(props)
        
        # NUEVO: Regenerar ChromaDB automáticamente
        from regenerar_chromadb import regenerar_chroma
        regenerar_chroma()
        
        st.success(f"✅ {nuevas} propiedades agregadas!")
        st.balloons()  # Celebración
    except Exception as e:
        st.error(f"Error: {e}")
```

### Ventajas
- ✅ Usuario no necesita presionar F5
- ✅ Búsqueda funciona inmediatamente con nuevas propiedades
- ✅ UX mejorada

### Esfuerzo: **1-2 horas**

---

## Fase 3 ⏳ PROPUESTA: Historial de Descargas

### Objetivo
Almacenar registro de cada scraping (fecha, zona, cantidad, portal)

### Tabla Nueva
```sql
CREATE TABLE IF NOT EXISTS download_history (
    id INTEGER PRIMARY KEY,
    fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
    provincia TEXT,
    localidades TEXT,  -- JSON array
    portal TEXT,
    tipo TEXT,
    cantidad_scrapeada INTEGER,
    cantidad_agregada INTEGER,
    tiempo_segundos FLOAT
);
```

### UI
```python
st.sidebar.markdown("## 📊 Historial de Descargas")
with st.sidebar.expander("Últimas descargas"):
    # Mostrar tabla con historial
    df_historial = db.obtener_historial_descargas()
    st.dataframe(df_historial)
```

### Esfuerzo: **2-3 horas**

---

## Fase 4 ⏳ PROPUESTA: Filtro de Precio en Scraping

### Objetivo
Permitir descargar solo propiedades dentro de rango de precio

### UI
```python
with col1:
    precio_min = st.number_input("Precio mín (USD)", 0, 1000000, 0)
with col2:
    precio_max = st.number_input("Precio máx (USD)", 1000, 10000000, 1000000)
```

### Implementación
```python
for localidad in localidades_seleccionadas:
    props = scraper.buscar_propiedades(
        zona=localidad,
        precio_min=precio_min,
        precio_max=precio_max  # NUEVO
    )
```

### Nota
Requiere modificar ArgenpropScraper y BuscadorPropScraper para soportar filtro de precio

### Esfuerzo: **3-4 horas**

---

## Fase 5 ⏳ PROPUESTA: Estadísticas por Zona

### Objetivo
Mostrar estadísticas de propiedades por zona (precio promedio, tipos, etc.)

### UI
```python
st.sidebar.markdown("## 📈 Estadísticas")
with st.sidebar.expander("Por zona"):
    stats = db.obtener_estadisticas_por_zona()
    for zona, datos in stats.items():
        st.metric(f"{zona}", f"{datos['cantidad']} props", 
                 f"Precio prom: USD {datos['precio_prom']:,}")
```

### Gráficos
- Precio promedio por zona
- Cantidad de propiedades por tipo
- Distribución de habitaciones
- Precio vs m² cubiertos

### Esfuerzo: **3-4 horas**

---

## Fase 6 ⏳ PROPUESTA: Exportar a Excel

### Objetivo
Exportar propiedades filtradas a Excel con formato

### UI
```python
if st.button("📥 Exportar a Excel"):
    excel_file = db.exportar_excel(propiedades, filename="propiedades.xlsx")
    st.download_button(
        label="Descargar Excel",
        data=excel_file,
        file_name="propiedades.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
```

### Funcionalidad
- Estilos (headers, colores)
- Filtros automáticos
- Formato de moneda
- Gráficos incrustados

### Requisitos: `pip install openpyxl`

### Esfuerzo: **2-3 horas**

---

## Fase 7 ⏳ PROPUESTA: Scraping Programado

### Objetivo
Ejecutar scraping cada 24 horas automáticamente

### Implementación
```python
import schedule
import threading

def scraping_diario():
    """Ejecuta scraping de zonas predefinidas"""
    db = PropertyDatabase()
    for zona in ["Palermo", "Recoleta", "Temperley"]:
        props = BuscadorPropScraper.buscar_propiedades(zona=zona)
        db.agregar_propiedades(props)
    regenerar_chroma()

# En background thread
schedule.every().day.at("22:00").do(scraping_diario)
```

### Esfuerzo: **2-3 horas**

---

## Fase 8 ⏳ PROPUESTA: Notificaciones

### Objetivo
Notificar cambios en propiedades (precios, nuevas, eliminadas)

### Tipos
- **Nuevas propiedades:** Notificar cuando se scrappean propiedades nuevas
- **Cambios de precio:** Alertar si una propiedad bajó/subió de precio
- **Propiedades eliminadas:** Registrar cuando desaparecen

### Canales
- Email
- Telegram
- Push notifications (mobile)

### Esfuerzo: **4-6 horas**

---

## Fase 9 ⏳ PROPUESTA: Machine Learning

### Objetivo
Predecir precios basados en características de propiedades

### Modelo
```python
from sklearn.ensemble import RandomForestRegressor

# Entrenar con propiedades existentes
X = df[['habitaciones', 'baños', 'metros_cubiertos', 'zona_encoded']]
y = df['precio']

model = RandomForestRegressor()
model.fit(X, y)

# Predecir precio para nueva propiedad
precio_predicho = model.predict(nueva_propiedad)
```

### UI
```python
st.markdown("### 🤖 Predicción de Precio")
precio_estimado = ml_model.predecir(
    habitaciones=3,
    baños=2,
    metros_cubiertos=100,
    zona="Palermo"
)
st.metric("Precio Estimado", f"USD {precio_estimado:,}")
```

### Esfuerzo: **5-7 horas**

---

## Fase 10 ⏳ PROPUESTA: Mobile App

### Objetivo
Acceso desde teléfono (no solo desktop)

### Opciones
1. **Streamlit Mobile:** Usar Streamlit Cloud (lo más simple)
2. **React Native:** App nativa iOS/Android (complejo)
3. **PWA:** Progressive Web App (intermedio)

### Esfuerzo: **2 horas (Streamlit Cloud) - 20+ horas (nativa)**

---

## Priorización

### 🚀 Más Impacto (hacer primero)
1. **Fase 2:** Regeneración automática ChromaDB (impacto alto, esfuerzo bajo)
2. **Fase 5:** Estadísticas por zona (impacto medio, esfuerzo bajo)
3. **Fase 3:** Historial de descargas (impacto medio, esfuerzo bajo)

### 📊 Medio Impacto
4. **Fase 4:** Filtro de precio (impacto medio, esfuerzo medio)
5. **Fase 6:** Exportar a Excel (impacto medio, esfuerzo bajo)
6. **Fase 9:** ML Predicción de precios (impacto alto, esfuerzo alto)

### 💎 Nice-to-Have
7. **Fase 7:** Scraping programado (impacto bajo, esfuerzo bajo)
8. **Fase 8:** Notificaciones (impacto bajo, esfuerzo alto)
9. **Fase 10:** Mobile app (impacto medio, esfuerzo muy alto)

---

## Timeline Estimado

```
Semana 1:
  Lunes:   Fase 2 (Regeneración ChromaDB)
  Martes:  Fase 5 (Estadísticas)
  Miércoles: Fase 3 (Historial)
  Jueves:  Fase 6 (Excel export)
  Viernes: Testing + bugfixes

Semana 2:
  Fase 4 (Filtro de precio)
  Fase 7 (Scraping programado)
  Testing

Semana 3:
  Fase 9 (ML)
  Testing

Semana 4:
  Fase 8 (Notificaciones) o Fase 10 (Mobile)
  Polish
```

---

## Criterios de Éxito

- ✅ Cada fase debe tener tests
- ✅ Documentación actualizada
- ✅ No romper funcionalidad existente
- ✅ Performance < 2 segundos por operación
- ✅ ChromaDB siempre sincronizado con BD

---

**Última actualización:** 2024  
**Estado:** Hoja de ruta activa para próximas 4 semanas
