import pandas as pd
import chromadb
import streamlit as st
import os
from datetime import datetime, time as dt_time
import json
import logging
import time
import threading

# Configuración
st.set_page_config(page_title="Agente RAG Inmobiliario", page_icon="🏠", layout="wide")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 1-4. Cargar y preparar datos, embeddings y vector store (cacheado)
@st.cache_resource(show_spinner="Cargando base de datos de propiedades...")
def cargar_sistema():
    """Carga propiedades, genera embeddings y crea el vector store."""
    from src.scrapers import PropertyDatabase
    from sentence_transformers import SentenceTransformer
    
    # Cargar desde SQLite
    db = PropertyDatabase(db_path="data/properties.db")
    df = db.obtener_df()
    
    if df.empty:
        logger.warning("Base de datos vacía, cargando datos de ejemplo desde CSV")
        csv_files = ['data/properties_expanded.csv', 'data/properties.csv']
        for csv_file in csv_files:
            try:
                if os.path.exists(csv_file):
                    df = pd.read_csv(csv_file)
                    # Insertar en BD
                    db.agregar_propiedades(df.to_dict('records'))
                    logger.info(f"Cargadas {len(df)} propiedades desde {csv_file}")
                    break
            except Exception as e:
                logger.warning(f"Error cargando {csv_file}: {e}")
                continue
    
    if df.empty:
        logger.error("No se encontraron propiedades")
        return None, None, None
    
    # Filtrar filas con ID vacío o inválido
    df = df[df['id'].notna() & (df['id'].astype(str).str.len() > 0)]
    df = df.reset_index(drop=True)
    
    if df.empty:
        logger.error("No se encontraron propiedades válidas después de filtrar")
        return None, None, None
    
    logger.info(f"Cargadas {len(df)} propiedades de BD SQLite")
    
    def make_text(row):
        desc = row.get('descripcion', '') if isinstance(row, dict) else row['descripcion']
        return f"{row['tipo']} en {row['zona']}. {desc}"
    
    df['text'] = df.apply(make_text, axis=1)
    model = SentenceTransformer('all-MiniLM-L6-v2')
    embeddings = model.encode(df['text'].tolist())
    
    chroma_client = chromadb.PersistentClient(path="data/chroma_data")
    
    # Intentar obtener la colección existente
    try:
        collection = chroma_client.get_collection("propiedades")
        logger.info(f"Colección existente encontrada con {collection.count()} documentos")
        if collection.count() > 0:
            return model, collection, df
    except:
        pass
    
    # Si no existe o está vacía, crearla
    logger.info("Creando colección nueva...")
    try:
        chroma_client.delete_collection("propiedades")
    except:
        pass
    
    collection = chroma_client.create_collection("propiedades")
    logger.info(f"Agregando {len(df)} propiedades a ChromaDB...")
    
    for i, row in df.iterrows():
        # Validar ID
        row_id = str(row['id']).strip() if row['id'] else None
        if not row_id or row_id == "nan" or row_id == "None":
            logger.debug(f"Saltando fila {i}: ID vacío o inválido")
            continue
        
        # Limpiar metadatos
        metadata = row.to_dict()
        for key in metadata:
            if metadata[key] is None or (isinstance(metadata[key], float) and pd.isna(metadata[key])):
                metadata[key] = ""
        
        try:
            collection.add(
                documents=[row['text']],
                embeddings=[embeddings[i]],
                metadatas=[metadata],
                ids=[row_id]
            )
        except Exception as e:
            logger.debug(f"Error agregando a ChromaDB (fila {i}): {e}")
            continue
    
    logger.info(f"✅ ChromaDB listo con {collection.count()} documentos")
    return model, collection, df

model, collection, df_propiedades = cargar_sistema()

# Validar que se cargó correctamente
if model is None or collection is None or df_propiedades is None:
    st.error("❌ Error: No se pudo cargar la base de datos. Verifica que exista data/properties.db o data/properties_expanded.csv")
    st.stop()

# Funciones de búsqueda
def buscar_propiedades(query, k=5):
    """Búsqueda RAG semántica."""
    # Búsqueda semántica (pedir más para paginación)
    k_expanded = min(max(k, 10), len(df_propiedades))  # Mínimo 10 para paginación
    query_emb = model.encode([query])
    results = collection.query(query_embeddings=query_emb.tolist(), n_results=k_expanded)
    
    # Retornar registros completos de BD
    propiedades_recomendadas = []
    for result_id in results['ids'][0]:
        if result_id in df_propiedades['id'].astype(str).values:
            # Obtener el registro completo de la BD
            prop_row = df_propiedades[df_propiedades['id'].astype(str) == result_id].iloc[0]
            propiedades_recomendadas.append(prop_row.to_dict())
    
    if not propiedades_recomendadas:
        return [], "No hay propiedades que combinen con tu búsqueda."
    
    return propiedades_recomendadas, None

def extraer_palabras_clave(texto):
    """Extrae palabras clave de un texto."""
    if not texto or not isinstance(texto, str):
        return []
    
    # Palabras clave relevantes para inmuebles
    palabras_relevantes = {
        'moderno', 'nuevo', 'reciclado', 'renovado', 'luminoso', 'amplio', 'espacioso',
        'jardín', 'patio', 'balcón', 'terraza', 'galpón', 'cochera', 'garaje',
        'aire', 'gas', 'calefacción', 'piscina', 'pileta', 'natatorio',
        'cocina', 'baño', 'livingcomedor', 'suite', 'dormitorio', 'estudio',
        'seguridad', 'vigilancia', 'alarma', 'portero', 'conserjería',
        'zona', 'céntrica', 'tranquila', 'residencial', 'comercial',
        'frente', 'contrafrente', 'lateral', 'esquina',
        'acceso', 'entrada', 'salida', 'puerta', 'ventanas'
    }
    
    texto_lower = texto.lower()
    palabras = []
    for palabra in palabras_relevantes:
        if palabra in texto_lower:
            palabras.append(palabra)
    
    return list(set(palabras))[:10]  # Máximo 10 palabras clave

def obtener_coordenadas(zona):
    """Obtiene coordenadas aproximadas por zona (datos predefinidos)."""
    coordenadas_zonas = {
        'temperley': {'lat': -34.7881, 'lng': -58.2819},
        'berazategui': {'lat': -34.7709, 'lng': -58.2064},
        'burzaco': {'lat': -34.8215, 'lng': -58.3179},
        'la plata': {'lat': -34.9205, 'lng': -57.9549},
        'lomas de zamora': {'lat': -34.7658, 'lng': -58.4047},
        'acoyte': {'lat': -34.7567, 'lng': -58.2817},
        'banfield': {'lat': -34.8076, 'lng': -58.2756},
        'flores': {'lat': -34.6339, 'lng': -58.4481},
        'flores sur': {'lat': -34.6339, 'lng': -58.4481},
        'constitución': {'lat': -34.6227, 'lng': -58.4306},
        'san justo': {'lat': -34.7506, 'lng': -58.5039},
        'ciudadela': {'lat': -34.6953, 'lng': -58.4672},
        'moron': {'lat': -34.6506, 'lng': -58.6233},
        'castelar': {'lat': -34.6603, 'lng': -58.6681},
        'merlo': {'lat': -34.6869, 'lng': -58.7267},
        'ituzaingo': {'lat': -34.6589, 'lng': -58.6617},
    }
    return coordenadas_zonas.get(zona.lower(), {'lat': -34.7, 'lng': -58.3})

def mostrar_mapa(zona):
    """Muestra un mapa interactivo de la zona."""
    coords = obtener_coordenadas(zona)
    folium_map = {
        'type': 'FeatureCollection',
        'features': [{
            'type': 'Feature',
            'geometry': {
                'type': 'Point',
                'coordinates': [coords['lng'], coords['lat']]
            },
            'properties': {
                'name': zona
            }
        }]
    }
    
    # Crear URL de Google Maps
    maps_url = f"https://www.google.com/maps/search/{zona}/@{coords['lat']},{coords['lng']},15z"
    return maps_url, coords

def formatear_propiedad(prop):
    """Formatea una propiedad para mostrar en la UI."""
    return {
        'id': prop['id'],
        'tipo': prop['tipo'],
        'zona': prop['zona'],
        'precio': prop['precio'],
        'habitaciones': prop['habitaciones'],
        'baños': prop['baños'],
        'pileta': prop['pileta'],
        'metros_cubiertos': prop['metros_cubiertos'],
        'metros_descubiertos': prop['metros_descubiertos'],
        'descripcion': prop['descripcion'],
        'amenities': prop['amenities'],
        'url': prop['url'],
        'palabras_clave': extraer_palabras_clave(prop.get('descripcion', '') + ' ' + prop.get('amenities', ''))
    }

# Interfaz de Streamlit
st.title("🏠 Agente RAG Inmobiliario")
st.markdown("### Encuentra tu vivienda ideal usando IA conversacional")

# Inicializar historial de chat
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Sidebar: Opciones de filtrado
# Opción para descargar el CSV actualizado
st.sidebar.markdown("---")
st.sidebar.markdown("## 📤 Exportar Base de Datos")
import io
try:
    from src.scrapers import PropertyDatabase
    db = PropertyDatabase()
    df_export = db.obtener_df()
    if not df_export.empty:
        csv_bytes = df_export.to_csv(index=False).encode()
        st.sidebar.download_button(
            label="📥 Descargar CSV (desde SQLite)",
            data=csv_bytes,
            file_name="properties_export.csv",
            mime="text/csv"
        )
        st.sidebar.caption(f"Total: {len(df_export)} propiedades")
    else:
        st.sidebar.info("Base de datos vacía")
except Exception as e:
    st.sidebar.error(f"Error: {e}")

st.sidebar.markdown("**Base de datos**: SQLite (data/properties.db)")
st.sidebar.markdown("**Versión**: MVP 2.2 (RAG + Scraping Inteligente)")

# Inicializar session state para control de scraper
if "scraper_running" not in st.session_state:
    st.session_state.scraper_running = False
if "scraper_stop_flag" not in st.session_state:
    st.session_state.scraper_stop_flag = False
if "scheduled_tasks" not in st.session_state:
    st.session_state.scheduled_tasks = []

# Sección para gestionar base de datos
st.sidebar.markdown("## 📥 Base de Datos")
with st.sidebar.expander("Gestionar BD", expanded=False):
    st.markdown("**Acciones de BD:**")
    col_refresh, col_clean = st.columns(2)
    with col_refresh:
        btn_refresh_georef = st.button("🔄 Act. Georef", key="refresh_georef")
    with col_clean:
        btn_clean_bd = st.button("🗑️ Limpiar BD", key="clean_bd")
    
    # Refrescar caché de Georef
    if btn_refresh_georef:
        st.cache_data.clear()
        st.success("✅ Caché de Georef actualizado!")
        st.info("🔄 Actualizando datos...")
        time.sleep(1)
        st.rerun()
    
    # Limpiar base de datos
    if btn_clean_bd:
        try:
            import sqlite3
            import shutil
            from src.scrapers import PropertyDatabase
            
            # 1. Limpiar tabla de SQLite
            db = PropertyDatabase(db_path="data/properties.db")
            conn = sqlite3.connect(db.db_path)
            cursor = conn.cursor()
            cursor.execute("DROP TABLE IF EXISTS propiedades")
            conn.commit()
            conn.close()
            logger.info("Tabla propiedades eliminada de BD SQLite")
            
            # 2. Limpiar ChromaDB
            if os.path.exists("data/chroma_data"):
                shutil.rmtree("data/chroma_data")
                logger.info("Directorio ChromaDB eliminado")
            
            # 3. Limpiar cachés
            st.cache_resource.clear()
            st.cache_data.clear()
            
            st.success("✅ Base de datos limpiada completamente!")
            st.info("🔄 Cargando propiedades desde CSV...")
            
            # 4. Recargar desde CSV automáticamente
            time.sleep(1)
            st.rerun()
        except Exception as e:
            st.error(f"❌ Error al limpiar BD: {e}")
            logger.error(f"Error limpiando BD: {e}")

with st.sidebar.expander("Descargar de Internet", expanded=False):
    st.markdown("""
    Obtén propiedades reales de portales inmobiliarios usando Georef API:
    """)
    
    # Cargar datos geográficos
    @st.cache_data(show_spinner="Cargando geografía...")
    def cargar_georef():
        from src.scrapers import GeorefAPI
        return GeorefAPI.obtener_todo()
    
    try:
        geo_data = cargar_georef()
        
        # Selección de provincia
        provincias_list = ["Todas"] + [p["nombre"] for p in geo_data.get("provincias", [])]
        provincia = st.selectbox("Provincia", provincias_list)
        
        # Selección de localidades/municipios
        if provincia == "Todas":
            # Mostrar localidades hardcodeadas para CABA
            localidades_list = ["Todas", "Palermo", "Recoleta", "San Isidro", "Belgrano", "Flores", 
                               "Caballito", "La Boca", "San Telmo", "Villa Crespo", "Colegiales",
                               "Lomas de Zamora", "Temperley", "La Matanza"]
        else:
            # Obtener localidades de la provincia seleccionada
            municipios = geo_data.get("municipios_por_provincia", {}).get(provincia, [])
            localidades_list = ["Todas"] + [m["nombre"] for m in municipios]
        
        col1, col2 = st.columns([2, 1])
        with col1:
            localidades_seleccionadas = st.multiselect(
                "Localidades a descargar",
                localidades_list,
                default=["Todas"] if "Todas" in localidades_list else localidades_list[:1]
            )
        with col2:
            limite = st.number_input("Props/zona", 5, 100, 10)
        
        # Si selecciona "Todas", descargar de todas
        if "Todas" in localidades_seleccionadas:
            localidades_seleccionadas = [l for l in localidades_list if l != "Todas"]
        
        # Portal y tipo
        portal = st.selectbox("Portal", ["Argenprop", "BuscadorProp"])
        tipo_prop = st.radio("Tipo", ["Venta", "Alquiler"], horizontal=True)
        
        # Botones de control
        col_download, col_stop = st.columns(2)
        with col_download:
            start_download = st.button("⬇️ Descargar Propiedades", key="descargar_props_portal")
        with col_stop:
            stop_download = st.button("⏹️ Detener Descarga", key="stop_scraper", disabled=not st.session_state.scraper_running)
        
        if stop_download:
            st.session_state.scraper_stop_flag = True
            st.warning("⏹️ Deteniendo descarga...")
        
        if start_download:
            st.session_state.scraper_running = True
            st.session_state.scraper_stop_flag = False
            st.info(f"⏳ Descargando desde {portal}... esto puede tomar 1-2 minutos")
            try:
                from src.scrapers import ArgenpropScraper, BuscadorPropScraper, PropertyDatabase
                db = PropertyDatabase()
                total_nuevas = 0
                progress_bar = st.progress(0)
                
                for idx, localidad in enumerate(localidades_seleccionadas):
                    # Verificar si se solicitó detener
                    if st.session_state.scraper_stop_flag:
                        st.warning(f"❌ Descarga detenida en {localidad}. {total_nuevas} propiedades agregadas")
                        st.session_state.scraper_running = False
                        break
                    
                    st.write(f"📍 Descargando {localidad}...")
                    if portal == "Argenprop":
                        props = ArgenpropScraper.buscar_propiedades(zona=localidad, tipo=tipo_prop, limit=limite, debug=True, stop_flag=st.session_state)
                    elif portal == "BuscadorProp":
                        props = BuscadorPropScraper.buscar_propiedades(zona=localidad, tipo=tipo_prop.lower(), limit=limite, debug=True, stop_flag=st.session_state)
                    else:
                        props = []
                    
                    nuevas = db.agregar_propiedades(props)
                    total_nuevas += nuevas
                    time.sleep(2)  # Delay entre zonas
                    
                    # Actualizar barra de progreso
                    progress = (idx + 1) / len(localidades_seleccionadas)
                    progress_bar.progress(progress)
                
                if not st.session_state.scraper_stop_flag:
                    db.guardar_csv("data/properties_expanded.csv")
                    stats = db.obtener_estadisticas()
                    st.success(f"✅ {total_nuevas} propiedades agregadas!")
                    st.info(f"Total en BD: {stats['total_propiedades']} propiedades")
                    st.warning("⚠️ Recarga la página para ver las nuevas propiedades (F5)")
                
                st.session_state.scraper_running = False
                st.session_state.scraper_stop_flag = False
            except ImportError as ie:
                st.error(f"❌ Falta instalar: {ie}")
                st.session_state.scraper_running = False
            except Exception as e:
                st.error(f"Error: {str(e)}")
                st.session_state.scraper_running = False
    
    except Exception as e:
        st.error(f"Error cargando geografía: {e}")
        st.markdown("Usando localidades por defecto...")
        
        # Fallback: localidades hardcodeadas
        portal_fb = st.selectbox("Portal", ["Argenprop", "BuscadorProp"], key="portal_fallback")
        col1, col2 = st.columns([2, 1])
        with col1:
            zonas_seleccionadas = st.multiselect(
                "Zonas a descargar",
                ["Palermo", "Recoleta", "San Isidro", "Belgrano", "Flores", 
                 "Caballito", "La Boca", "San Telmo", "Villa Crespo", "Colegiales",
                 "Lomas de Zamora", "Temperley", "La Matanza"],
                default=["Palermo"]
            )
        with col2:
            limite = st.number_input("Props/zona", 5, 100, 10, key="limite_fallback")
        
        tipo_prop = st.radio("Tipo", ["Venta", "Alquiler"], horizontal=True, key="tipo_fallback")
        
        # Botones de control para fallback
        col_download_fb, col_stop_fb = st.columns(2)
        with col_download_fb:
            start_download_fb = st.button("⬇️ Descargar Propiedades", key="descargar_props_fallback")
        with col_stop_fb:
            stop_download_fb = st.button("⏹️ Detener Descarga", key="stop_scraper_fb", disabled=not st.session_state.scraper_running)
        
        if stop_download_fb:
            st.session_state.scraper_stop_flag = True
            st.warning("⏹️ Deteniendo descarga...")
        
        if start_download_fb:
            st.session_state.scraper_running = True
            st.session_state.scraper_stop_flag = False
            st.info(f"⏳ Descargando desde {portal_fb}... esto puede tomar 1-2 minutos")
            try:
                from src.scrapers import ArgenpropScraper, BuscadorPropScraper, PropertyDatabase
                db = PropertyDatabase()
                total_nuevas = 0
                progress_bar = st.progress(0)
                
                for idx, zona in enumerate(zonas_seleccionadas):
                    # Verificar si se solicitó detener
                    if st.session_state.scraper_stop_flag:
                        st.warning(f"❌ Descarga detenida en {zona}. {total_nuevas} propiedades agregadas")
                        st.session_state.scraper_running = False
                        break
                    
                    st.write(f"📍 Descargando {zona}...")
                    if portal_fb == "Argenprop":
                        props = ArgenpropScraper.buscar_propiedades(zona=zona, tipo=tipo_prop, limit=limite, debug=True, stop_flag=st.session_state)
                    elif portal_fb == "BuscadorProp":
                        props = BuscadorPropScraper.buscar_propiedades(zona=zona, tipo=tipo_prop.lower(), limit=limite, debug=True, stop_flag=st.session_state)
                    else:
                        props = []
                    
                    nuevas = db.agregar_propiedades(props)
                    total_nuevas += nuevas
                    time.sleep(2)
                    
                    # Actualizar barra de progreso
                    progress = (idx + 1) / len(zonas_seleccionadas)
                    progress_bar.progress(progress)
                
                if not st.session_state.scraper_stop_flag:
                    db.guardar_csv("data/properties_expanded.csv")
                    stats = db.obtener_estadisticas()
                    st.success(f"✅ {total_nuevas} propiedades agregadas!")
                    st.info(f"Total en BD: {stats['total_propiedades']} propiedades")
                    st.warning("⚠️ Recarga la página para ver las nuevas propiedades (F5)")
                
                st.session_state.scraper_running = False
                st.session_state.scraper_stop_flag = False
            except ImportError as ie:
                st.error(f"❌ Falta instalar: {ie}")
                st.session_state.scraper_running = False
            except Exception as e:
                st.error(f"Error: {str(e)}")
                st.session_state.scraper_running = False

# Sección de tareas programadas
st.sidebar.markdown("## 🕐 Tareas Programadas")
with st.sidebar.expander("Configurar Descarga Automática", expanded=False):
    st.markdown("""
    Configura descargas automáticas de propiedades:
    """)
    
    col1, col2 = st.columns(2)
    with col1:
        habilitar_tarea = st.checkbox("Habilitar tarea programada")
    with col2:
        hora_ejecucion = st.time_input("Hora de ejecución", value=dt_time(22, 0))
    
    if habilitar_tarea:
        st.info("⏰ Tarea programada: Se ejecutará diariamente")
        
        col1, col2 = st.columns(2)
        with col1:
            zona_automatica = st.selectbox(
                "Zona para descarga automática",
                ["Palermo", "Recoleta", "San Isidro", "Belgrano", "Temperley"],
                key="zona_auto"
            )
        with col2:
            portal_automatico = st.selectbox(
                "Portal para descarga automática",
                ["BuscadorProp", "Argenprop"],
                key="portal_auto"
            )
        
        props_automaticas = st.slider("Props a descargar", 5, 50, 10, key="props_auto")
        tipo_automatico = st.radio("Tipo de descarga automática", ["Venta", "Alquiler"], key="tipo_auto")
        
        if st.button("💾 Guardar Configuración de Tarea"):
            tarea_config = {
                "id": f"tarea_{datetime.now().timestamp()}",
                "hora": str(hora_ejecucion),
                "zona": zona_automatica,
                "portal": portal_automatico,
                "props": props_automaticas,
                "tipo": tipo_automatico,
                "habilitada": True,
                "fecha_creacion": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # Guardar en archivo JSON
            try:
                tareas_file = "scheduled_tasks.json"
                tareas_existentes = []
                if os.path.exists(tareas_file):
                    with open(tareas_file, 'r') as f:
                        tareas_existentes = json.load(f)
                
                tareas_existentes.append(tarea_config)
                
                with open(tareas_file, 'w') as f:
                    json.dump(tareas_existentes, f, indent=2)
                
                st.success(f"✅ Tarea programada para {hora_ejecucion} en {zona_automatica}")
                st.session_state.scheduled_tasks = tareas_existentes
            except Exception as e:
                st.error(f"Error guardando tarea: {e}")
    
    # Mostrar tareas programadas existentes
    try:
        tareas_file = "scheduled_tasks.json"
        if os.path.exists(tareas_file):
            with open(tareas_file, 'r') as f:
                tareas = json.load(f)
            
            if tareas:
                st.markdown("### 📋 Tareas Configuradas")
                for idx, tarea in enumerate(tareas):
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.write(f"""
                        **Tarea {idx + 1}**
                        - ⏰ Hora: {tarea['hora']}
                        - 📍 Zona: {tarea['zona']}
                        - 🏢 Portal: {tarea['portal']}
                        - 📊 Props: {tarea['props']}
                        - 🔄 Tipo: {tarea['tipo']}
                        - ✅ Habilitada: {'Sí' if tarea['habilitada'] else 'No'}
                        """)
                    with col2:
                        if st.button("🗑️ Eliminar", key=f"delete_task_{idx}"):
                            tareas.pop(idx)
                            with open(tareas_file, 'w') as f:
                                json.dump(tareas, f, indent=2)
                            st.success("Tarea eliminada")
                            st.rerun()
    except Exception as e:
        st.warning(f"No hay tareas configuradas aún")

st.sidebar.markdown("---")

# Chat principal
st.markdown("### 💬 Búsqueda Inteligente")

# Inicializar session state para búsqueda automática
if "search_query" not in st.session_state:
    st.session_state.search_query = ""
if "search_results" not in st.session_state:
    st.session_state.search_results = []
if "search_page" not in st.session_state:
    st.session_state.search_page = 0
if "last_input_time" not in st.session_state:
    st.session_state.last_input_time = 0

# Callback que se ejecuta cuando el usuario escribe
def on_search_input_change():
    st.session_state.last_input_time = time.time()
    st.session_state.search_page = 0

perfil = st.text_input(
    "Describe tu familia y preferencias:",
    placeholder="Ej: Familia de 4 personas, buscan casa luminosa en Palermo con 3 habitaciones",
    key="user_input",
    on_change=on_search_input_change
)

# Búsqueda automática con debounce (2 segundos)
if perfil:
    elapsed = time.time() - st.session_state.last_input_time
    
    # Si han pasado 2 segundos desde que dejó de escribir, ejecutar búsqueda
    if elapsed >= 2.0 and perfil != st.session_state.search_query:
        st.session_state.search_query = perfil
        st.session_state.search_page = 0
        
        # Buscar propiedades
        propiedades, error = buscar_propiedades(
            perfil,
            k=5
        )
        if not error:
            st.session_state.search_results = propiedades
        else:
            st.session_state.search_results = []
    elif elapsed < 2.0 and perfil != st.session_state.search_query:
        # Mostrar placeholder mientras espera
        with st.spinner("⏳ Esperando para buscar..."):
            time.sleep(0.1)
        st.rerun()
else:
    st.session_state.search_results = []
    st.session_state.search_query = ""

# Mostrar resultados con paginación
if st.session_state.search_results:
    # Paginación
    props_per_page = 5
    total_pages = (len(st.session_state.search_results) + props_per_page - 1) // props_per_page
    
    col1, col2, col3 = st.columns([1, 3, 1])
    with col1:
        if st.button("⬅️ Anterior", disabled=st.session_state.search_page == 0):
            st.session_state.search_page -= 1
            st.rerun()
    with col2:
        st.write(f"📄 Página {st.session_state.search_page + 1} de {total_pages} ({len(st.session_state.search_results)} resultados)")
    with col3:
        if st.button("Siguiente ➡️", disabled=st.session_state.search_page >= total_pages - 1):
            st.session_state.search_page += 1
            st.rerun()
    
    st.markdown("---")
    
    # Mostrar propiedades de la página actual
    start_idx = st.session_state.search_page * props_per_page
    end_idx = start_idx + props_per_page
    propiedades = st.session_state.search_results[start_idx:end_idx]
    
    st.success(f"✅ Encontré {len(st.session_state.search_results)} propiedad(es) relevante(s):")
    
    for i, prop in enumerate(propiedades, start=start_idx + 1):
        with st.expander(f"**{i}. {prop['tipo']} en {prop['zona']}** - USD {prop['precio']}", expanded=(i==start_idx+1)):
            # Información básica en 2 columnas
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Habitaciones", prop.get('habitaciones') or "N/A")
                st.metric("Baños", prop.get('baños') or "N/A")
                st.metric("M² Cubiertos", prop.get('metros_cubiertos') or "N/A")
            with col2:
                st.metric("M² Descubiertos", prop.get('metros_descubiertos') or "N/A")
                pileta_text = "✅ Sí" if prop.get('pileta') else "❌ No"
                st.metric("Pileta", pileta_text)
                try:
                    precio_num = float(str(prop.get('precio', 0)).replace('USD', '').replace('$', '').split()[0])
                    st.metric("Precio", f"USD {precio_num:,.0f}")
                except:
                    st.metric("Precio", prop.get('precio', 'N/A'))
            
            # Descripción
            st.markdown("### 📝 Descripción")
            st.write(prop.get('descripcion', 'N/A'))
            
            # Amenities
            st.markdown("### 🏠 Amenities")
            st.write(prop.get('amenities', 'N/A'))
            
            # Palabras clave
            palabras_clave = prop.get('palabras_clave', [])
            if palabras_clave:
                st.markdown("### 🔑 Características Destacadas")
                cols = st.columns(len(palabras_clave))
                for idx, palabra in enumerate(palabras_clave):
                    with cols[idx % len(palabras_clave)]:
                        st.info(f"• {palabra.capitalize()}")
            
            # Ubicación
            st.markdown("### 📍 Ubicación")
            maps_url, coords = mostrar_mapa(prop.get('zona', ''))
            col_map, col_coords = st.columns([2, 1])
            with col_map:
                st.markdown(f"[🗺️ Ver en Google Maps]({maps_url})")
            with col_coords:
                st.caption(f"Lat: {coords['lat']:.4f}, Lng: {coords['lng']:.4f}")
            
            # Link a la propiedad
            if prop.get('url'):
                st.markdown(f"[🔗 Ver propiedad en portal]({prop['url']})")
            
            # Feedback
            st.markdown("### 👍 Tu opinión")
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("👍 Me interesa", key=f"like_{prop['id']}"):
                    st.session_state.chat_history.append({
                        "rol": "feedback",
                        "tipo": "positivo",
                        "propiedad_id": prop['id'],
                        "timestamp": datetime.now().strftime("%H:%M:%S")
                    })
                    st.success("Feedback registrado")
            with col3:
                if st.button("👎 No es para mí", key=f"dislike_{prop['id']}"):
                    st.session_state.chat_history.append({
                        "rol": "feedback",
                        "tipo": "negativo",
                        "propiedad_id": prop['id'],
                        "timestamp": datetime.now().strftime("%H:%M:%S")
                    })
                    st.info("Feedback registrado")

# Mostrar historial
if st.session_state.chat_history:
    st.markdown("---")
    st.markdown("### 📋 Historial de Búsqueda")
    for entrada in st.session_state.chat_history:
        if entrada['rol'] == 'usuario':
            st.write(f"**Usuario ({entrada['timestamp']}):** {entrada['mensaje']}")
        elif entrada['rol'] == 'asistente':
            st.write(f"**Asistente ({entrada['timestamp']}):** {entrada['mensaje']}")
        elif entrada['rol'] == 'feedback':
            emoji = "👍" if entrada['tipo'] == 'positivo' else "👎"
            st.write(f"{emoji} Feedback en propiedad #{entrada['propiedad_id']}")
