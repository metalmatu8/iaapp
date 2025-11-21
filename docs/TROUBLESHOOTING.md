# 🔧 TROUBLESHOOTING - Solución de Problemas

## Problema 1: "Error cargando geografía"

### Síntomas
```
❌ Error cargando geografía: ...
⚠️ Usando localidades por defecto...
```

### Causas Posibles
1. **Sin internet:** No hay conexión a API Georef
2. **API caída:** datos.gob.ar puede estar en mantenimiento
3. **Timeout:** API responde lentamente (>10s)
4. **Firewall/Proxy:** Bloquea conexión a datos.gob.ar

### Soluciones
```bash
# 1. Verificar conexión a API
curl https://apis.datos.gob.ar/georef/api/provincias?max=5

# 2. Verificar timeout (debe responder en <5s)
time python -c "
from scrapers import GeorefAPI
GeorefAPI.obtener_provincias()
"

# 3. Reintentar
streamlit run app.py

# 4. Si sigue fallando, usar fallback (es normal)
# Funciona con 13 zonas hardcodeadas
```

---

## Problema 2: "Dropdown de localidades está vacío"

### Síntomas
```
Provincia: "Córdoba"
Localidades a descargar: [vacío]
```

### Causas
1. Provincia seleccionada no tiene datos en Georef
2. GeorefAPI.obtener_todo() solo carga primeras 5 provincias (por performance)

### Soluciones
```python
# Verificar si provincia tiene municipios
from scrapers import GeorefAPI
geo = GeorefAPI.obtener_todo()
print(geo["municipios_por_provincia"].keys())
# Output: dict_keys(['Ciudad Autónoma de Buenos Aires', 'Neuquén', 'San Luis', 'Santa Fe', 'La Rioja'])

# Si quieres agregar más provincias, editar scrapers.py línea 66:
for prov in provincias[:5]:  # Cambiar 5 a 10, 15, etc.
```

---

## Problema 3: "Scraping tarda mucho (>5 minutos)"

### Síntomas
```
⏳ Descargando desde BuscadorProp... esto puede tomar 1-2 minutos
(después de 10 minutos sigue cargando)
```

### Causas
1. **Demasiadas zonas:** Seleccionaste "Todas" con 50+ municipios
2. **Props/zona muy alto:** 50-100 propiedades por zona es lento
3. **Portal lento:** BuscadorProp suele ser más lento que Argenprop
4. **Conexión lenta:** Tu internet es lento

### Soluciones
```python
# Reducir cantidad de zonas
# Antes: Seleccionar "Todas"
# Después: Seleccionar solo 2-3 zonas específicas

# Reducir props/zona
# Props/zona: 10 (en lugar de 50)

# Cambiar portal
# Argenprop suele ser más rápido que BuscadorProp

# Usar Ctrl+C para cancelar si tarda demasiado
```

---

## Problema 4: "¡Descargué 50 propiedades pero no las veo!"

### Síntomas
```
✅ 50 propiedades agregadas!
Total en BD: 86 propiedades
⚠️ Recarga la página para ver las nuevas propiedades (F5)
(presiono F5 pero sigo viendo solo 36)
```

### Causas
1. **ChromaDB no se regeneró:** Necesita recargar embeddings
2. **Caché de app:** Streamlit cachea los datos

### Soluciones
```bash
# 1. Presionar F5 (reload página)
# Esperar 3-5 segundos

# 2. Si sigue sin aparecer, regenerar ChromaDB manualmente
python regenerar_chromadb.py

# 3. Si aún no aparecen, reiniciar app
# Ctrl+C en terminal → streamlit run app.py

# 4. Última opción: limpiar caché Streamlit
rm -r ~/.streamlit/cache
streamlit run app.py
```

---

## Problema 5: "La búsqueda trae resultados raros/de otras zonas"

### Síntomas
```
Busco: "Temperley, 3 habitaciones"
Resultado: Palermo, 1 habitación
```

### Causas
1. **ChromaDB desincronizado:** Embeddings viejos vs BD nueva
2. **Búsqueda semántica confundida:** "Temperley" ≠ embedding esperado

### Soluciones
```bash
# 1. Regenerar ChromaDB
python regenerar_chromadb.py

# 2. Reiniciar app
Ctrl+C → streamlit run app.py

# 3. Limpiar caché
streamlit cache clear

# 4. Verificar que búsqueda incluya zona
Buscar: "3 habitaciones Temperley" (más específico)
```

---

## Problema 6: "SyntaxError en app.py"

### Síntomas
```
Traceback (most recent call last):
  File "app.py", line X, in <module>
    ^ SyntaxError: invalid syntax
```

### Causas
1. **Error en edición:** Código incompleto/mal indentado
2. **Caracteres especiales:** Comillas, tabulaciones

### Soluciones
```bash
# 1. Verificar sintaxis
python -m py_compile app.py

# 2. Ver línea exacta del error
python app.py

# 3. Abrir en editor y verificar indentación
# (VS Code: selecciona todo Ctrl+A → Shift+Alt+F)

# 4. Si no ves el error, revertir cambios:
git diff app.py  # Ver cambios
git checkout app.py  # Revertir
```

---

## Problema 7: "ModuleNotFoundError: No module named 'scrapers'"

### Síntomas
```
ModuleNotFoundError: No module named 'scrapers'
```

### Causas
1. Estás en directorio equivocado
2. `scrapers.py` no existe

### Soluciones
```bash
# 1. Verificar ubicación
ls -la | grep scrapers.py
# Output: scrapers.py (debe estar en directorio actual)

# 2. Estar en directorio correcto
cd /ruta/a/iaapp
streamlit run app.py

# 3. Si scrapers.py no existe, copiar respaldo
git checkout scrapers.py
```

---

## Problema 8: "ChromaDB: database disk image is corrupted"

### Síntomas
```
Error: database disk image is corrupted
```

### Causas
1. **Cierre anormal:** Última ejecución cerró sin guardar
2. **Conflicto de acceso:** Múltiples instancias de app

### Soluciones
```bash
# 1. Eliminar base de datos corrupta
rm -rf chroma_data/

# 2. Regenerar desde cero
python regenerar_chromadb.py

# 3. Reiniciar app
streamlit run app.py

# 4. Verificar una sola instancia
# Cerrar todas las ventanas/terminales de app
# Abrir una única vez: streamlit run app.py
```

---

## Problema 9: "Argenprop/BuscadorProp no trae propiedades"

### Síntomas
```
📍 Descargando Palermo...
✅ 0 propiedades agregadas!
```

### Causas
1. **Portal caído/modificado:** Website cambió estructura HTML
2. **Zona inexistente:** Escribiste "Palrmo" (typo)
3. **Sin propiedades:** Esa zona no tiene listings en ese portal

### Soluciones
```bash
# 1. Probar en navegador
# Ir a:
# Argenprop: https://www.argenprop.com/
# BuscadorProp: https://www.buscadorprop.com/

# 2. Verificar zona
# Probar con zona popular: "Palermo", "Recoleta", "Belgrano"

# 3. Esperar y reintentar
# Portal puede estar bloqueando por rate-limiting
# Esperar 5 minutos → reintentar

# 4. Cambiar navegador/proxy (si está bloqueado)
# Los scrapers usan Selenium + User-Agent rotation
# Pero si IP está bloqueada, necesita cambiar

# 5. Ver logs detallados
python -c "
from scrapers import ArgenpropScraper
props = ArgenpropScraper.buscar_propiedades(zona='Palermo', debug=True)
print(f'Encontradas: {len(props)}')
"
```

---

## Problema 10: "requirements.txt falta algo"

### Síntomas
```
ModuleNotFoundError: No module named 'X'
```

### Soluciones
```bash
# 1. Instalar todos los requisitos
pip install -r requirements.txt

# 2. Si falta un módulo específico
pip install [nombre_modulo]

# 3. Verificar versiones
pip list

# 4. Si hay conflictos de versión
pip install --upgrade -r requirements.txt
```

---

## Checklist para Reportar Bug

Si nada de arriba funciona, reporta el bug con:

```markdown
### Descripción del problema
[Tu descripción aquí]

### Pasos para reproducir
1. Abre app.py
2. ...
3. [Error ocurre]

### Síntomas
- [Síntoma 1]
- [Síntoma 2]

### Sistema
- OS: Windows/Mac/Linux
- Python: 3.9/3.10/3.11
- Browser: Chrome/Firefox

### Logs
```bash
[Copia el output completo del error]
```

### Archivos adjuntos
- app.py (si lo editaste)
- Error log (si lo guardaste)
```

---

## Contacto/Soporte

Si tienes problema:

1. **Verificar este documento** (Ctrl+F para buscar)
2. **Ejecutar tests:**
   ```bash
   python test_georef_api.py
   python test_georef_integration.py
   ```
3. **Ver logs de app:**
   ```bash
   streamlit run app.py --logger.level=debug
   ```
4. **Revisar código comentado:**
   - `scrapers.py` línea 100-150 (debug mode)
   - `app.py` línea 50-100 (logging)

---

**Última actualización:** 2024  
**Versión:** 2.2 (con Georef)
