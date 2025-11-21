import pandas as pd
from sentence_transformers import SentenceTransformer
import chromadb
import streamlit as st
import os
from datetime import datetime
import json
import logging
import time

# Configuración
st.set_page_config(page_title="Agente RAG Inmobiliario", page_icon="🏠", layout="wide")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 1-4. Cargar y preparar datos, embeddings y vector store (cacheado)
@st.cache_resource(show_spinner="Cargando base de datos de propiedades...")
def cargar_sistema():
    """Carga propiedades, genera embeddings y crea el vector store."""
    from scrapers import PropertyDatabase
    
    # Cargar desde SQLite
    db = PropertyDatabase()
    df = db.obtener_df()
    
    if df.empty:
        logger.warning("Base de datos vacía, cargando datos de ejemplo desde CSV")
        csv_files = ['properties_expanded.csv', 'properties.csv']
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
    
    chroma_client = chromadb.PersistentClient(path="./chroma_data")
    
    # Intentar obtener la colección existente
    try:
        collection = chroma_client.get_collection("propiedades")
        logger.info(f"Colección existente encontrada con {collection.count()} documentos")
        return model, collection, df
    except:
        logger.info("Creando colección nueva...")
    
    collection = chroma_client.create_collection("propiedades")
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
    
    return model, collection, df

model, collection, df_propiedades = cargar_sistema()

# Funciones de filtrado y búsqueda
def filtrar_por_metadatos(df, zona=None, precio_max=None, habitaciones_min=None, pileta=None):
    """Aplica filtros por metadatos antes de la búsqueda semántica."""
    resultado = df.copy()
    
    if zona:
        resultado = resultado[resultado['zona'].str.lower() == zona.lower()]
    
    if precio_max:
        resultado = resultado[resultado['precio'] <= precio_max]
    
    if habitaciones_min and habitaciones_min > 0:
        # Filtrar solo propiedades con habitaciones no-null y >= habitaciones_min
        resultado = resultado[resultado['habitaciones'].notna() & (resultado['habitaciones'] >= habitaciones_min)]
    
    if pileta is not None:
        resultado = resultado[resultado['pileta'] == pileta]
    
    return resultado

def buscar_propiedades(query, zona=None, precio_max=None, habitaciones_min=None, pileta=None, k=3):
    """Búsqueda RAG híbrida: semántica + filtros de metadatos."""
    # 1. Pre-filtrado por metadatos
    df_filtrado = filtrar_por_metadatos(df_propiedades, zona, precio_max, habitaciones_min, pileta)
    
    if df_filtrado.empty:
        return [], "No hay propiedades que cumplan los criterios especificados."
    
    # 2. Búsqueda semántica
    query_emb = model.encode([query])
    results = collection.query(query_embeddings=query_emb.tolist(), n_results=min(k, len(df_filtrado)))
    
    # 3. Filtrar resultados según metadatos y retornar registros completos de BD
    propiedades_recomendadas = []
    for result_id in results['ids'][0]:
        if result_id in df_filtrado['id'].astype(str).values:
            # Obtener el registro completo de la BD
            prop_row = df_filtrado[df_filtrado['id'].astype(str) == result_id].iloc[0]
            propiedades_recomendadas.append(prop_row.to_dict())
    
    if not propiedades_recomendadas:
        return [], "No hay propiedades que combinen con tu búsqueda semántica y los filtros aplicados."
    
    return propiedades_recomendadas, None

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
        'url': prop['url']
    }

# Interfaz de Streamlit
st.title("🏠 Agente RAG Inmobiliario")
st.markdown("### Encuentra tu vivienda ideal usando IA conversacional")

# Inicializar historial de chat
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Sidebar: Opciones de filtrado
st.sidebar.markdown("## 🔍 Filtros Avanzados")
zonas_unicas = sorted([z for z in df_propiedades['zona'].dropna().unique().tolist() if z])
zona_filter = st.sidebar.selectbox("Zona (opcional)", ["Todas"] + zonas_unicas)
zona_filter = None if zona_filter == "Todas" else zona_filter

precio_max_filter = st.sidebar.number_input("Precio máximo (USD)", min_value=0, value=0, step=10000)
precio_max_filter = None if precio_max_filter == 0 else precio_max_filter

habitaciones_min = st.sidebar.number_input("Habitaciones mínimas (0 = sin filtro)", min_value=0, value=0, step=1)
habitaciones_min = None if habitaciones_min == 0 else habitaciones_min

pileta_filter = st.sidebar.selectbox("¿Con pileta?", ["Indiferente", "Sí", "No"])
pileta_filter = None if pileta_filter == "Indiferente" else (pileta_filter == "Sí")


# Opción para descargar el CSV actualizado
st.sidebar.markdown("---")
st.sidebar.markdown("## 📤 Exportar Base de Datos")
import io
try:
    from scrapers import PropertyDatabase
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

st.sidebar.markdown("**Base de datos**: SQLite (properties.db)")
st.sidebar.markdown("**Versión**: MVP 2.1 (RAG + Scraping)")

# Sección para descargar propiedades de internet

st.sidebar.markdown("## 📥 Descargar Propiedades")
with st.sidebar.expander("Descargar de Internet", expanded=False):
    st.markdown("""
    Obtén propiedades reales de portales inmobiliarios:
    """)
    portal = st.selectbox("Portal", ["Argenprop", "BuscadorProp"])
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
        limite = st.number_input("Props/zona", 5, 100, 10)
    
    tipo_prop = st.radio("Tipo", ["Venta", "Alquiler"], horizontal=True)
    
    if st.button("⬇️ Descargar Propiedades", key="descargar_props_portal"):
        st.info(f"⏳ Descargando desde {portal}... esto puede tomar 1-2 minutos")
        try:
            from scrapers import ArgenpropScraper, BuscadorPropScraper, PropertyDatabase
            db = PropertyDatabase()
            total_nuevas = 0
            for zona in zonas_seleccionadas:
                st.write(f"📍 Descargando {zona}...")
                if portal == "Argenprop":
                    props = ArgenpropScraper.buscar_propiedades(zona=zona, tipo=tipo_prop, limit=limite, debug=True)
                elif portal == "BuscadorProp":
                    props = BuscadorPropScraper.buscar_propiedades(zona=zona, tipo=tipo_prop.lower(), limit=limite, debug=True)
                else:
                    props = []
                nuevas = db.agregar_propiedades(props)
                total_nuevas += nuevas
                time.sleep(2)  # Delay entre zonas
            db.guardar_csv("properties_expanded.csv")
            stats = db.obtener_estadisticas()
            st.success(f"✅ {total_nuevas} propiedades agregadas!")
            st.info(f"Total en BD: {stats['total_propiedades']} propiedades")
            st.warning("⚠️ Recarga la página para ver las nuevas propiedades (F5)")
        except ImportError as ie:
            st.error(f"❌ Falta instalar: {ie}")
        except Exception as e:
            st.error(f"Error: {str(e)}")


st.sidebar.markdown("---")

# Chat principal
st.markdown("### 💬 Conversación")
perfil = st.text_input(
    "Describe tu familia y preferencias:",
    placeholder="Ej: Familia de 4 personas, buscan casa luminosa en Palermo con 3 habitaciones",
    key="user_input"
)

col1, col2 = st.columns([4, 1])
with col2:
    buscar_btn = st.button("🔍 Buscar", use_container_width=True)

if buscar_btn and perfil:
    # Guardar en historial
    timestamp = datetime.now().strftime("%H:%M:%S")
    st.session_state.chat_history.append({
        "rol": "usuario",
        "mensaje": perfil,
        "timestamp": timestamp,
        "filtros": {
            "zona": zona_filter,
            "precio_max": precio_max_filter,
            "habitaciones_min": habitaciones_min,
            "pileta": pileta_filter
        }
    })
    
    # Buscar propiedades
    propiedades, error = buscar_propiedades(
        perfil,
        zona=zona_filter,
        precio_max=precio_max_filter,
        habitaciones_min=habitaciones_min,
        pileta=pileta_filter,
        k=3
    )
    
    if error:
        st.warning(f"⚠️ {error}")
    else:
        st.session_state.chat_history.append({
            "rol": "asistente",
            "mensaje": f"Encontré {len(propiedades)} propiedad(es) que se ajusta(n) a tu perfil.",
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "propiedades": propiedades
        })
        
        st.success(f"✅ Encontré {len(propiedades)} propiedad(es) relevante(s):")
        
        for i, prop in enumerate(propiedades, 1):
            with st.expander(f"**{i}. {prop['tipo']} en {prop['zona']}** - USD {prop['precio']}", expanded=(i==1)):
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
                
                st.markdown(f"**Descripción:** {prop.get('descripcion', 'N/A')}")
                st.markdown(f"**Amenities:** {prop.get('amenities', 'N/A')}")
                if prop.get('url'):
                    st.markdown(f"[🔗 Ver propiedad]({prop['url']})")
                
                # Feedback (prep para fase 2)
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
