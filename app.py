import pandas as pd
import chromadb
import streamlit as st
import os
from datetime import datetime, time as dt_time
import json
import logging
import time
import threading
import shutil

# Configuración
st.set_page_config(
    page_title="Agente RAG Inmobiliario", 
    page_icon="🏠", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado para diseño premium
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        width: 375px !important;
        min-width: 375px !important;
        max-width: 375px !important;
        box-shadow: 2px 0 15px rgba(0, 0, 0, 0.08) !important;
    }
    
    [data-testid="stSidebar"]::after {
        display: none !important;
    }
    
    .st-emotion-cache-10oheav {
        width: 375px !important;
        flex-shrink: 0 !important;
    }
    
    [data-testid="collapseSidebarButton"] {
        display: block !important;
    }
    
    /* Headers */
    h1, h2, h3 {
        font-weight: 700 !important;
        letter-spacing: -0.5px !important;
        word-wrap: break-word !important;
        overflow-wrap: break-word !important;
    }
    
    h1 {
        font-size: 2.5rem !important;
        margin-bottom: 0.5rem !important;
    }
    
    /* Text wrapping - palabras completas sin saltos incómodos */
    p, span, div, li, label, caption {
        word-wrap: break-word !important;
        overflow-wrap: break-word !important;
        word-break: normal !important;
    }
    
    /* Captions y pequeño texto */
    .stCaption, [data-testid="stCaption"] {
        word-wrap: break-word !important;
        overflow-wrap: break-word !important;
        white-space: normal !important;
    }
    
    /* Markdown containers */
    [data-testid="stMarkdownContainer"] {
        word-wrap: break-word !important;
        overflow-wrap: break-word !important;
    }
    
    /* Expanders - texto visible completo */
    [data-testid="stExpander"] [data-testid="stMarkdownContainer"] {
        word-wrap: break-word !important;
        overflow-wrap: break-word !important;
    }
    
    /* Cards y containers */
    [data-testid="stMetricContainer"] {
        border-radius: 12px !important;
        padding: 1.5rem !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06) !important;
        transition: all 0.3s ease !important;
    }
    
    [data-testid="stMetricContainer"]:hover {
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1) !important;
        transform: translateY(-2px) !important;
    }
    
    /* Buttons - Simple y directo */
    /* ESTILOS ÚNICOS Y CONSISTENTES PARA TODOS LOS BOTONES */
    .stButton {
        width: 100% !important;
    }
    
    .stButton > button,
    [data-testid="stButton"] button {
        width: 100% !important;
        height: 48px !important;
        min-height: 48px !important;
        max-height: 48px !important;
        border-radius: 8px !important;
        border: none !important;
        font-weight: 600 !important;
        padding: 0 1.5rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.25) !important;
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%) !important;
        color: white !important;
        font-size: 15px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        line-height: 1 !important;
    }
    
    .stButton > button:hover:not(:disabled),
    [data-testid="stButton"] button:hover:not(:disabled) {
        transform: translateY(-3px) !important;
        box-shadow: 0 8px 24px rgba(59, 130, 246, 0.35) !important;
    }
    
    .stButton > button:active:not(:disabled),
    [data-testid="stButton"] button:active:not(:disabled) {
        transform: translateY(-1px) !important;
    }
    
    .stButton > button:disabled,
    [data-testid="stButton"] button:disabled {
        background: linear-gradient(135deg, #d1d5db 0%, #9ca3af 100%) !important;
        opacity: 0.6 !important;
        cursor: not-allowed !important;
    }
    
    /* Container de botones - alineación vertical */
    [data-testid="stButton"] {
        width: 100% !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }
    
    /* Botones en la TERCERA COLUMNA (derecha) con altura doble */
    [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(3) [data-testid="stButton"] button {
        height: 88px !important;
        min-height: 88px !important;
        max-height: 88px !important;
    }
    
    /* Botón "Detener Descarga" (stop_scraper) con altura doble */
    [data-testid="stButton"] button[data-testid*="stop_scraper"],
    [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(2) [data-testid="stButton"] button {
        height: 88px !important;
        min-height: 88px !important;
        max-height: 88px !important;
    }
    
    /* Ocultar botón de toggle sidebar */
    [data-testid="stButton"] button[aria-label*="toggle_sidebar_btn"],
    button[data-testid*="toggle_sidebar_btn"] {
        display: none !important;
    }

    /* Ocultar input de búsqueda en multiselect y selectbox */
    [data-testid="stMultiSelect"] input::placeholder,
    [data-testid="stSelectbox"] input::placeholder {
        color: transparent !important;
    }
    
    [data-testid="stMultiSelect"] input,
    [data-testid="stSelectbox"] input {
        color: transparent !important;
        caret-color: transparent !important;
        font-size: 0 !important;
        padding: 0 !important;
        border: none !important;
        background: transparent !important;
        height: 0 !important;
        min-height: 0 !important;
    }
    

    /* Input fields - Improved for search bar */
    input, textarea, [data-testid="stTextInput"], [data-testid="stTextArea"] {
        border-radius: 10px !important;
        border: 2px solid rgba(200, 200, 200, 0.4) !important;
        padding: 0.95rem 1.2rem !important;
        transition: all 0.3s ease !important;
        background: #ffffff !important;
        font-size: 16px !important;
        line-height: 1.5 !important;
    }
    
    input::placeholder, textarea::placeholder {
        color: rgba(107, 114, 128, 0.6) !important;
        font-weight: 400 !important;
    }
    
    input:hover, textarea:hover {
        border-color: rgba(59, 130, 246, 0.4) !important;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.1) !important;
    }
    
    input:focus, textarea:focus {
        border-color: rgba(59, 130, 246, 0.8) !important;
        box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.15), inset 0 0 0 1px rgba(59, 130, 246, 0.3) !important;
        outline: none !important;
    }
    
    [data-testid="stTextInput"] input {
        border-color: rgba(200, 200, 200, 0.5) !important;
    }
    
    [data-testid="stTextInput"] input:hover {
        border-color: rgba(59, 130, 246, 0.5) !important;
    }
    
    /* Estilos especiales para columnas de búsqueda */
    [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
        gap: 1rem !important;
    }
    

    /* Mejora visual de dividers */
    hr {
        border: none !important;
        border-top: 2px solid rgba(200, 200, 200, 0.2) !important;
        margin: 2rem 0 !important;
    }
    
    /* Success/Info/Warning messages */
    [data-testid="stSuccess"], [data-testid="stInfo"], [data-testid="stWarning"] {
        border-radius: 10px !important;
        border-left: 4px solid !important;
        padding: 1rem !important;
        background: rgba(240, 253, 250, 0.5) !important;
    }
    
    [data-testid="stSuccess"] {
        border-left-color: #10b981 !important;
        background: rgba(240, 253, 250, 0.7) !important;
    }
    
    [data-testid="stInfo"] {
        border-left-color: #3b82f6 !important;
        background: rgba(239, 246, 255, 0.7) !important;
    }
    
    [data-testid="stWarning"] {
        border-left-color: #f59e0b !important;
        background: rgba(255, 250, 235, 0.7) !important;
    }
    [data-testid="stExpander"] {
        border: 1.5px solid rgba(200, 200, 200, 0.3) !important;
        border-radius: 8px !important;
        overflow: hidden !important;
        transition: all 0.3s ease !important;
    }
    
    [data-testid="stExpander"]:hover {
        border-color: rgba(59, 130, 246, 0.4) !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05) !important;
    }
    
    [data-testid="stExpander"] button {
        border-radius: 7px 7px 0 0 !important;
        transition: all 0.3s ease !important;
    }
    
    [data-testid="stExpander"] button:hover {
        background-color: rgba(59, 130, 246, 0.05) !important;
    }
    
    /* Ocultar icono de Material Design */
    [data-testid="stExpander"] [data-testid="stIconMaterial"] {
        display: none !important;
    }
    
    /* Agregar flecha antes del texto del expander */
    [data-testid="stExpander"] summary::before {
        content: "▼ " !important;
        color: rgba(59, 130, 246, 0.8) !important;
        font-weight: bold !important;
        margin-right: 0.25rem !important;
        transition: transform 0.3s ease !important;
        display: inline-block !important;
    }
    
    /* Rotar flecha cuando está abierto */
    details[open] summary::before {
        transform: rotate(-180deg) !important;
    }
    
    /* Ocultar ícono de expander */
    [data-testid="stIconMaterial"] {
        display: none !important;
    }
    
    /* Mejorar estilo del number input (Cantidad) */
    [data-testid="stNumberInput"] input {
        font-size: 16px !important;
        font-weight: 500 !important;
        text-align: center !important;
        padding: 12px !important;
        border: 2px solid #3b82f6 !important;
        border-radius: 8px !important;
        background: white !important;
        transition: all 0.3s ease !important;
        outline: none !important;
    }
    
    [data-testid="stNumberInput"] input:hover {
        border-color: #2563eb !important;
        box-shadow: 0 0 10px rgba(59, 130, 246, 0.4) !important;
    }
    
    [data-testid="stNumberInput"] input:focus {
        border-color: #1d4ed8 !important;
        box-shadow: 0 0 15px rgba(59, 130, 246, 0.6) !important;
        outline: none !important;
    }
    
    [data-testid="stNumberInput"] label {
        font-weight: 600 !important;
        color: rgb(49, 51, 63) !important;
        font-size: 15px !important;
    }
    
    /* Reglas de botones consolidadas arriba - evitar duplicados */
    
    /* Tabs */
    [data-testid="stTabs"] [role="tab"] {
        border-radius: 8px 8px 0 0 !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
    }
    
    /* Dividers */
    hr {
        border: none !important;
        height: 1px !important;
        margin: 1.5rem 0 !important;
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        font-size: 2rem !important;
        font-weight: 700 !important;
    }
    
    /* Markdown text */
    .stMarkdown {
        line-height: 1.6 !important;
    }
    
    /* Images */
    img {
        border-radius: 8px !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1) !important;
    }
    
    /* Chat messages */
    [data-testid="stChatMessage"] {
        border-radius: 12px !important;
        padding: 1rem !important;
        margin: 0.5rem 0 !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05) !important;
    }
    
    /* Scrollbar personalizado */
    ::-webkit-scrollbar {
        width: 8px !important;
    }
    
    ::-webkit-scrollbar-track {
        background: transparent !important;
    }
    
    ::-webkit-scrollbar-thumb {
        border-radius: 4px !important;
    }
    
    /* Alineación del botón "Ver Todas" con el input de búsqueda */
    .stHorizontalBlock [data-testid="stColumn"]:first-child [data-testid="stButton"] button {
        height: 88px !important;
        min-height: 88px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        padding: 0 !important;
    }
    
    [data-testid="stTextInput"] input {
        height: 44px !important;
        min-height: 44px !important;
        padding: 10px 12px !important;
    }
</style>
""", unsafe_allow_html=True)
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
        logger.warning("Base de datos vacía - lista para descargar propiedades desde Internet")
        # Intentar cargar desde CSV si existe
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
    
    # Si sigue vacía, devolver setup inicial vacío pero funcional
    if df.empty:
        logger.info("Inicializando sistema con BD vacía - usuario puede descargar propiedades")
        # Crear estructura mínima pero válida
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer('all-MiniLM-L6-v2')
        chroma_client = chromadb.PersistentClient(path="data/chroma_data")
        # Crear colección vacía
        try:
            chroma_client.delete_collection("propiedades")
        except:
            pass
        collection = chroma_client.create_collection(name="propiedades")
        return model, collection, pd.DataFrame()  # Retorna DataFrame vacío pero válido
    
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
        docs_existentes = collection.count()
        logger.info(f"Colección existente encontrada con {docs_existentes} documentos")
        
        # IMPORTANTE: Si tiene menos documentos que la BD actual, regenerar
        # Esto evita cachés obsoletos o incompletos
        if docs_existentes >= len(df) * 0.8:  # Si tiene al menos 80% de las propiedades, usar
            return model, collection, df
        else:
            logger.warning(f"Colección incompleta ({docs_existentes}/{len(df)} docs). Regenerando...")
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
if model is None or collection is None:
    st.error("❌ Error: No se pudo cargar la base de datos. Verifica que exista data/properties.db")
    st.stop()

# df_propiedades puede estar vacío inicialmente (usuario descargará propiedades después)
if df_propiedades is None:
    df_propiedades = pd.DataFrame()

bd_vacia = df_propiedades.empty

# Funciones de búsqueda
def buscar_propiedades(query, k=5):
    """Búsqueda RAG semántica mejorada con procesamiento inteligente sin API."""
    # Si la BD está vacía, no hay nada que buscar
    if bd_vacia:
        return [], "Base de datos vacía. Descarga propiedades primero desde 'Descargar de Internet'"
    
    # Procesar la query para entender mejor la intención
    search_query = mejorar_query(query)
    
    # Búsqueda semántica (pedir más para paginación)
    k_expanded = min(max(k, 50), len(df_propiedades))  # Mínimo 50 para mejor cobertura de zonas
    query_emb = model.encode([search_query])
    results = collection.query(query_embeddings=query_emb.tolist(), n_results=k_expanded)
    
    # Retornar registros completos de BD
    propiedades_recomendadas = []
    for result_id in results['ids'][0]:
        if result_id in df_propiedades['id'].astype(str).values:
            # Obtener el registro completo de la BD
            prop_row = df_propiedades[df_propiedades['id'].astype(str) == result_id].iloc[0]
            propiedades_recomendadas.append(prop_row.to_dict())
    
    if not propiedades_recomendadas:
        return [], "No hay propiedades que combinen con tu búsqueda. Intenta con otros criterios."
    
    return propiedades_recomendadas, None

def mejorar_query(query):
    """Mejora la query usando procesamiento inteligente sin API."""
    if not query:
        return query
    
    query_lower = query.lower()
    
    # Diccionario de expansiones semánticas para criterios comunes
    expansiones = {
        'moderno': ['nuevo', 'renovado', 'contemporáneo', 'actualizado'],
        'luminoso': ['luz', 'iluminado', 'ventanas'],
        'amplio': ['espacioso', 'grande', 'tamaño', 'metros'],
        'tranquilo': ['paz', 'quieto', 'residencial', 'alejado'],
        'céntrico': ['centro', 'central', 'ubicación', 'acceso'],
        'familia': ['habitaciones', 'dormitorios', 'niños', 'personas'],
        'campo': ['rural', 'chacra', 'terreno', 'naturales'],
        'ciudad': ['urbano', 'zona', 'barrio', 'localidad'],
        'pequeño': ['compacto', 'estudio', 'monoambiente', 'reducido'],
        'balcón': ['terraza', 'vista', 'aire libre'],
        'jardin': ['patio', 'verde', 'exterior', 'plantas'],
        'piscina': ['pileta', 'natatorio', 'agua'],
        'seguridad': ['vigilancia', 'alarma', 'portero', 'cerradura'],
        'cocina': ['cocina equipada', 'amoblada', 'electrodomésticos'],
        'baño': ['baños', 'toilette', 'espacio sanitario'],
        'parking': ['cochera', 'garaje', 'estacionamiento', 'auto'],
    }
    
    # Expandir query con sinónimos relevantes
    query_expandida = query
    for palabra_clave, sinonimos in expansiones.items():
        if palabra_clave in query_lower:
            # Agregar sinónimos para mejor búsqueda semántica
            query_expandida += " " + " ".join(sinonimos)
    
    # Detectar intenciones específicas y agregar contexto
    intenciones = {
        'número en familia': ['personas', 'miembros', 'tamaño familia'],
        'presupuesto': ['máximo', 'mínimo', 'precio', 'renta', 'valor'],
        'superficie': ['m2', 'metros', 'tamaño', 'superficie'],
        'época': ['ahora', 'pronto', 'urgente', 'inmediato'],
        'característica especial': ['con', 'tiene', 'debe', 'necesita'],
    }
    
    # Agregar palabras de contexto según lo que detectemos
    if any(x in query_lower for x in ['cuántas', 'cuantas', 'cantidad', 'número', 'personas']):
        query_expandida += " tamaño distribución espacial dormitorios"
    
    if any(x in query_lower for x in ['cuánto', 'cuanto', 'precio', 'costo', 'valor']):
        query_expandida += " precio valor inversión"
    
    if any(x in query_lower for x in ['dónde', 'donde', 'zona', 'ubicación', 'barrio']):
        query_expandida += " localidad ubicación zona área"
    
    return query_expandida

def reranquear_propiedades_localmente(query, propiedades):
    """
    Re-rankea propiedades con búsqueda INTELIGENTE y FLEXIBLE.
    Usa coincidencias exactas pero NO descarta si no encuentra.
    Sistema de puntuación que prioriza lo que el usuario buscó.
    """
    if not propiedades:
        return []
    
    import re
    query_lower = query.lower()
    
    # DICCIONARIO DE AMENITIES - Mapear palabras clave a campos reales
    amenities_mapping = {
        'pileta': ['pileta', 'piscina', 'natatorio'],
        'piscina': ['pileta', 'piscina', 'natatorio'],
        'jardín': ['jardín', 'patio', 'parque', 'verde'],
        'patio': ['jardín', 'patio', 'parque'],
        'aire': ['aire', 'clima', 'acondicionado'],
        'gas': ['gas', 'calefacción'],
        'garage': ['garage', 'cochera', 'estacionamiento', 'parking', 'auto'],
        'cochera': ['garage', 'cochera', 'estacionamiento', 'parking'],
        'terraza': ['terraza', 'balcón', 'vista'],
        'balcón': ['terraza', 'balcón', 'vista'],
        'cocina': ['cocina'],
        'nuevo': ['nuevo', 'renovado', 'moderno', 'recién'],
        'renovado': ['renovado', 'nuevo', 'moderno'],
        'moderno': ['moderno', 'nuevo', 'renovado', 'contemporáneo'],
        'seguridad': ['seguridad', 'vigilancia', 'alarma', 'portero'],
        'luminoso': ['luz', 'iluminado', 'ventanas'],
        'amplio': ['amplio', 'espacioso', 'grande'],
    }
    
    # DICCIONARIO DE ZONAS
    zonas_mapping = {
        'san isidro': ['san isidro', 'isidro'],
        'palermo': ['palermo', 'soho', 'hollywood', 'chico'],
        'recoleta': ['recoleta'],
        'belgrano': ['belgrano'],
        'caballito': ['caballito', 'primera junta'],
        'flores': ['flores', 'parque chacabuco'],
        'puerto madero': ['puerto madero', 'madero'],
        'la boca': ['la boca', 'boca'],
        'san nicolás': ['san nicolás', 'nicolás'],
        'centro': ['centro', 'retiro', 'microcentro'],
        'caba': ['caba', 'buenos aires'],
    }
    
    # EXTRAER LO QUE EL USUARIO BUSCA
    criterios_buscados = {
        'amenities': [],
        'zona': None,
        'tipo': None,
        'habitaciones': None,
        'precio_aprox': None,
    }
    
    # 1. Detectar amenities buscados
    for amenity, keywords in amenities_mapping.items():
        for kw in keywords:
            if kw in query_lower:
                if amenity not in criterios_buscados['amenities']:
                    criterios_buscados['amenities'].append(amenity)
                break
    
    # 2. Detectar zona buscada
    for zona_key, zona_keywords in zonas_mapping.items():
        for kw in zona_keywords:
            if kw in query_lower:
                criterios_buscados['zona'] = zona_key
                break
        if criterios_buscados['zona']:
            break
    
    # 3. Detectar tipo
    tipos_search = ['casa', 'departamento', 'dpto', 'apt', 'apartamento', 'piso', 'loft', 'estudio', 'monoambiente']
    for tipo in tipos_search:
        if tipo in query_lower:
            criterios_buscados['tipo'] = tipo
            break
    
    # 4. Detectar número de habitaciones
    numeros_query = re.findall(r'\d+', query)
    for num_str in numeros_query:
        num = int(num_str)
        if 2 <= num <= 8:  # Probablemente habitaciones
            criterios_buscados['habitaciones'] = num
            break
        elif num > 100000:  # Probablemente precio
            criterios_buscados['precio_aprox'] = num
            break
    
    # SCORING: Dar puntos según coincidencias, SIN descartar nada
    scores = []
    
    for prop in propiedades:
        score = 0
        desc = str(prop.get('descripcion', '')).lower()
        amenities = str(prop.get('amenities', '')).lower()
        zona_prop = str(prop.get('zona', '')).lower()
        tipo_prop = str(prop.get('tipo', '')).lower()
        hab_prop = prop.get('habitaciones', '')
        
        # ZONA: Máxima prioridad si se especificó
        if criterios_buscados['zona']:
            zona_key = criterios_buscados['zona']
            zona_keywords = zonas_mapping[zona_key]
            zona_match = any(kw in zona_prop for kw in zona_keywords)
            if zona_match:
                score += 500  # Coincidencia exacta de zona = PRIORIDAD MÁXIMA
            else:
                # Penalidad leve si buscó zona específica pero no coincide
                score -= 50
        
        # AMENITIES: Puntos por cada uno encontrado
        for amenity in criterios_buscados['amenities']:
            keywords = amenities_mapping.get(amenity, [])
            amenity_found = False
            
            # Verificar en campo específico si existe (ej: pileta)
            if amenity == 'pileta':
                if prop.get('pileta') or any(kw in amenities for kw in keywords):
                    score += 100
                    amenity_found = True
            else:
                # Verificar en amenities o descripción
                if any(kw in amenities for kw in keywords) or any(kw in desc for kw in keywords):
                    score += 80
                    amenity_found = True
            
            if not amenity_found:
                # Penalidad menor si buscó algo específico pero no está
                score -= 20
        
        # TIPO: Bonificación si coincide
        if criterios_buscados['tipo']:
            if criterios_buscados['tipo'] in tipo_prop:
                score += 150
            else:
                score -= 30
        
        # HABITACIONES: Exacta es mejor, pero acepta >= buscado
        if criterios_buscados['habitaciones']:
            try:
                hab_int = int(hab_prop) if hab_prop else 0
                if hab_int == criterios_buscados['habitaciones']:
                    score += 200  # Coincidencia exacta
                elif hab_int >= criterios_buscados['habitaciones']:
                    score += 100  # Tiene al menos las buscadas
                else:
                    score -= 40   # Tiene menos que lo buscado
            except:
                pass
        
        # BONIFICACIÓN GENERAL: Palabras del query en descripción
        keywords_query = [kw.strip() for kw in query_lower.split() if len(kw.strip()) > 2]
        for kw in keywords_query:
            if kw not in ['san', 'isidro', 'palermo', 'recoleta']:  # Evitar duplicar zona
                if kw in desc:
                    score += 10
                if kw in amenities:
                    score += 8
        
        scores.append((prop, score))
    
    # Ordenar por score descendente
    propiedades_ranked = sorted(scores, key=lambda x: x[1], reverse=True)
    
    # Retornar todas pero ordenadas por relevancia
    return [prop for prop, score in propiedades_ranked]

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

def es_imagen_propiedad_valida(url):
    """Verifica si una URL es una imagen válida de una propiedad (no logo, ícono, banner, etc.)."""
    if not url or not isinstance(url, str):
        return False
    
    url_lower = url.lower()
    
    # Palabras clave que indican que NO es una propiedad
    palabras_excluidas = [
        # Elementos de UI
        'logo', 'icon', 'placeholder', 'avatar', 'sprite', 'button',
        'header', 'footer', 'nav', 'menu', 'banner', 'badge',
        'mark', 'seal', 'watermark', 'star', 'rating',
        # Social media
        'instagram', 'facebook', 'youtube', 'twitter', 'tiktok', 'social', 'share', 'like',
        # Genéricos
        'arrow', 'cursor', 'pointer', 'default', 'hover', 'active',
        'up', 'down', 'left', 'right', 'prev', 'next',
        # Sliders/carrouseles sin contenido
        'slide-', 'carousel-', 'gallery-thumb', 'thumbnail', 'thumb-',
        # Contenido genérico
        'placeholder-', 'no-image', 'not-found', 'empty',
        # Branding del sitio
        'buscadorprop', 'zonaprop', 'inmuebles', 'realtor',
        # Patrones típicos de logos
        '/logo/', '/brand/', '/mark/', '/seal/',
        # Fotos muy pequeñas (probablemente decorativas)
        'favicon', 'apple-touch', 'icon-',
    ]
    
    # Excluir si contiene palabras sospechosas
    if any(kw in url_lower for kw in palabras_excluidas):
        return False
    
    # Excluir si es muy corta (probablemente no es una imagen real)
    if len(url) < 50:
        return False
    
    # Verificar extensión válida
    extensiones_validas = ('.jpg', '.jpeg', '.png', '.webp', '.gif', '.bmp')
    if not any(ext in url_lower for ext in extensiones_validas):
        return False
    
    # Palabras clave que indican que SÍ es una propiedad
    palabras_positivas = [
        'prop', 'inmueble', 'casa', 'departamento', 'piso', 'vivienda',
        'habitacion', 'bedroom', 'living', 'cocina', 'kitchen',
        'exterior', 'interior', 'fachada', 'facade',
        'ambiente', 'room', 'space',
    ]
    
    # Si tiene palabras positivas, es probablemente una propiedad
    if any(kw in url_lower for kw in palabras_positivas):
        return True
    
    # Heurística: si tiene números de proporción típicos (parámetros de tamaño),
    # probablemente sea una imagen de contenido real
    import re
    # Busca patrones como ?w=800&h=600 o /800x600/
    tamaño_pattern = r'(?:w|width|h|height|size|wh)=?\d{2,4}|/\d{3,4}x\d{3,4}/'
    if re.search(tamaño_pattern, url_lower):
        return True
    
    # Por defecto, si pasó todos los filtros, asumir que es válida
    return True

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
    """Muestra un mapa interactivo de la zona con Folium."""
    try:
        import folium
        from streamlit_folium import st_folium
    except ImportError:
        # Si no está instalado, retornar None y usar fallback
        coords = obtener_coordenadas(zona)
        maps_url = f"https://www.google.com/maps/search/{zona}/@{coords['lat']},{coords['lng']},15z"
        return maps_url, coords, None
    
    coords = obtener_coordenadas(zona)
    
    # Crear mapa con Folium
    mapa = folium.Map(
        location=[coords['lat'], coords['lng']],
        zoom_start=15,
        tiles='OpenStreetMap'
    )
    
    # Agregar marcador en la zona
    folium.Marker(
        location=[coords['lat'], coords['lng']],
        popup=f"📍 {zona}",
        tooltip=zona,
        icon=folium.Icon(color='blue', icon='home', prefix='fa')
    ).add_to(mapa)
    
    # Crear URL de Google Maps como fallback
    maps_url = f"https://www.google.com/maps/search/{zona}/@{coords['lat']},{coords['lng']},15z"
    
    return maps_url, coords, mapa

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

# Botón flotante para toggle sidebar
st.markdown("""
<style>
    /* Contenedor flotante para el botón */
    .floating-toggle {
        position: fixed;
        top: 20px;
        left: 20px;
        z-index: 9999;
    }
</style>
""", unsafe_allow_html=True)

# Inicializar estado para sidebar
if "sidebar_collapsed" not in st.session_state:
    st.session_state.sidebar_collapsed = False

# Crear un contenedor flotante con el botón (OCULTO)
col_toggle = st.columns([0.08])[0]
# Botón ocultado - no se muestra
# with col_toggle:
#     if st.button("☰", key="toggle_sidebar_btn", help="Mostrar/Ocultar menú"):
#         st.session_state.sidebar_collapsed = not st.session_state.sidebar_collapsed
#         st.rerun()

# Aplicar CSS para ocultar sidebar si es necesario
if st.session_state.sidebar_collapsed:
    st.markdown("""
    <style>
        [data-testid="stSidebar"] {
            display: none !important;
        }
        [data-testid="stMainBlockContainer"] {
            margin-left: 0 !important;
        }
    </style>
    """, unsafe_allow_html=True)

# Interfaz de Streamlit
st.header("🏠 Agente RAG Inmobiliario")

# Mostrar advertencia si BD está vacía
if bd_vacia:
    st.warning("""
    ⚠️ **Base de datos vacía** - Descarga propiedades desde Internet (sidebar izquierdo)
    """)

# Inicializar historial de chat y preferencias
if "chat_history" not in st.session_state:
    # Cargar feedback guardado en BD
    from src.scrapers import PropertyDatabase
    db = PropertyDatabase()
    feedback_guardado = db.obtener_feedback()
    
    # Convertir feedback de BD a formato de chat_history
    chat_history = []
    for fb in feedback_guardado:
        chat_history.append({
            "rol": "feedback",
            "tipo": fb.get('tipo'),
            "propiedad_id": fb.get('propiedad_id'),
            "timestamp": fb.get('timestamp', '')
        })
    
    st.session_state.chat_history = chat_history

# Inicializar modo oscuro (DESHABILITADO)
# if "dark_mode" not in st.session_state:
#     st.session_state.dark_mode = False

st.session_state.dark_mode = False  # Mantener siempre en modo claro

# Sidebar: Opciones de filtrado
# Botón para alternar modo oscuro/claro (DESHABILITADO)
# st.sidebar.markdown("---")
# col_theme = st.sidebar.columns([1])[0]
# with col_theme:
#     if st.button(f"{'🌙 Modo Oscuro' if not st.session_state.dark_mode else '☀️ Modo Claro'}", 
#                  use_container_width=True, 
#                  key="theme_toggle_btn"):
#         st.session_state.dark_mode = not st.session_state.dark_mode
#         st.rerun()

# Aplicar estilos CSS basado en modo oscuro
if st.session_state.dark_mode:
    dark_css = """
    <style>
        /* Modo oscuro - estilos base */
        body, .stApp, [data-testid="stMainBlockContainer"] {
            background: linear-gradient(135deg, #1a1d29 0%, #16213e 100%) !important;
            color: #ffffff !important;
        }
        
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0f1419 0%, #1a1d29 100%) !important;
            color: #ffffff !important;
        }
        
        /* Texto general */
        p, span, label, div {
            color: #ffffff !important;
        }
        
        /* Headers oscuros */
        h1, h2, h3, h4, h5, h6 {
            color: #60a5fa !important;
        }
        
        /* Cards oscuras */
        [data-testid="stMetricContainer"] {
            background: rgba(30, 35, 50, 0.8) !important;
            border: 1px solid rgba(96, 165, 250, 0.2) !important;
            color: #ffffff !important;
        }
        
        [data-testid="stMetricContainer"]:hover {
            background: rgba(30, 35, 50, 0.95) !important;
            border-color: rgba(96, 165, 250, 0.4) !important;
            box-shadow: 0 8px 25px rgba(96, 165, 250, 0.15) !important;
        }
        
        [data-testid="stMetricValue"] {
            color: #60a5fa !important;
        }
        
        [data-testid="stMetricLabel"] {
            color: #a0aec0 !important;
        }
        
        /* Botones oscuros */
        .stButton > button {
            background: linear-gradient(135deg, #3b82f6 0%, #1e40af 100%) !important;
            color: white !important;
        }
        
        .stButton > button:hover {
            background: linear-gradient(135deg, #2563eb 0%, #1e3a8a 100%) !important;
            box-shadow: 0 6px 20px rgba(59, 130, 246, 0.5) !important;
        }
        
        /* Inputs oscuros */
        input, textarea, [data-testid="stTextInput"] {
            background-color: rgba(20, 25, 40, 0.8) !important;
            color: #ffffff !important;
            border: 1.5px solid rgba(96, 165, 250, 0.2) !important;
        }
        
        input::placeholder, textarea::placeholder {
            color: #a0aec0 !important;
        }
        
        input:focus, textarea:focus {
            border-color: #3b82f6 !important;
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2) !important;
        }
        
        /* Expanders oscuros - contorno uniforme */
        [data-testid="stExpander"] {
            border: 1.5px solid rgba(96, 165, 250, 0.25) !important;
            background: rgba(20, 25, 40, 0.5) !important;
            border-radius: 8px !important;
            overflow: hidden !important;
            transition: all 0.3s ease !important;
        }
        
        [data-testid="stExpander"]:hover {
            border-color: rgba(96, 165, 250, 0.45) !important;
            box-shadow: 0 4px 12px rgba(59, 130, 246, 0.15) !important;
        }
        
        [data-testid="stExpander"] button {
            background: rgba(30, 35, 50, 0.6) !important;
            color: #60a5fa !important;
            border-radius: 7px 7px 0 0 !important;
            transition: all 0.3s ease !important;
        }
        
        [data-testid="stExpander"] button:hover {
            background: rgba(30, 35, 50, 0.85) !important;
        }
        
        /* Contenido del expander */
        [data-testid="stExpander"] [data-testid="stMarkdownContainer"] {
            color: #ffffff !important;
        }
        
        /* Tabs oscuros */
        [data-testid="stTabs"] [role="tab"] {
            color: #a0aec0 !important;
        }
        
        [data-testid="stTabs"] [role="tab"][aria-selected="true"] {
            background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%) !important;
            color: white !important;
        }
        
        /* Chat messages oscuros */
        [data-testid="stChatMessage"] {
            background: rgba(30, 35, 50, 0.7) !important;
            color: #ffffff !important;
        }
        
        /* Dividers oscuros */
        hr {
            background: linear-gradient(90deg, rgba(96, 165, 250, 0) 0%, rgba(96, 165, 250, 0.3) 50%, rgba(96, 165, 250, 0) 100%) !important;
        }
        
        /* Scrollbar oscuro */
        ::-webkit-scrollbar-track {
            background: rgba(30, 35, 50, 0.3) !important;
        }
        
        ::-webkit-scrollbar-thumb {
            background: linear-gradient(180deg, #3b82f6 0%, #1e40af 100%) !important;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: linear-gradient(180deg, #2563eb 0%, #1e3a8a 100%) !important;
        }
        
        /* Selectbox y dropdowns */
        [data-testid="stSelectbox"], [data-testid="stMultiSelect"] {
            color: #ffffff !important;
        }
        
        /* Info, warning, error boxes */
        .stInfo, .stWarning, .stError, .stSuccess {
            color: #ffffff !important;
        }
        
        /* Captions y textos pequeños */
        .st-emotion-cache-3qzj0x {
            color: #a0aec0 !important;
        }
        
        /* Texto en todos los elementos */
        * {
            color: #ffffff !important;
        }
        
        /* Excepto para items específicos que necesitan color especial */
        h1, h2, h3, h4, h5, h6 {
            color: #60a5fa !important;
        }
    </style>
    """
    st.markdown(dark_css, unsafe_allow_html=True)

st.sidebar.markdown("---")
# Opción para descargar el CSV actualizado (DESHABILITADA)
# st.sidebar.markdown("## 📤 Exportar Base de Datos")
# import io
# try:
#     from src.scrapers import PropertyDatabase
#     db = PropertyDatabase()
#     df_export = db.obtener_df()
#     if not df_export.empty:
#         csv_bytes = df_export.to_csv(index=False).encode()
#         st.sidebar.download_button(
#             label="📥 Descargar CSV (desde SQLite)",
#             data=csv_bytes,
#             file_name="properties_export.csv",
#             mime="text/csv"
#         )
#         st.sidebar.caption(f"Total: {len(df_export)} propiedades")
#     else:
#         st.sidebar.info("Base de datos vacía")
# except Exception as e:
#     st.sidebar.error(f"Error: {e}")

# st.sidebar.markdown("**Base de datos**: SQLite (data/properties.db)")
# st.sidebar.markdown("**Versión**: MVP 2.2 (RAG + Scraping Inteligente)")

# Inicializar session state para control de scraper (DESHABILITADO)
# if "scraper_running" not in st.session_state:
#     st.session_state.scraper_running = False
# if "scraper_stop_flag" not in st.session_state:
#     st.session_state.scraper_stop_flag = False
# if "scheduled_tasks" not in st.session_state:
#     st.session_state.scheduled_tasks = []

# Sección para gestionar base de datos (DESHABILITADA)
# st.sidebar.markdown("## 📥 Base de Datos")
# DESHABILITADO - Sección de gestión de BD
# with st.sidebar.expander("Gestionar BD", expanded=False):
#     # [TODO: Sección de gestión de BD - 285 líneas comentadas]

st.sidebar.markdown("## 📥 Descarga de Propiedades")

with st.sidebar.expander("Descargar de Internet", expanded=False):
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
        
        localidad_seleccionada = st.multiselect(
            "📍 Localidad",
            localidades_list,
            default=["Palermo"]
        )
        localidades_seleccionadas = localidad_seleccionada if localidad_seleccionada else ["Palermo"]
        
        limite = st.number_input("📊 Cantidad", 1, 100, 10)
        
        # Si selecciona "Todas", descargar de todas
        if "Todas" in localidades_seleccionadas:
            localidades_seleccionadas = [l for l in localidades_list if l != "Todas"]
        
        # Portal fijo a BuscadorProp (ocultar selectbox)
        portal = "BuscadorProp"
        tipo_prop = st.radio("Tipo", ["Venta", "Alquiler"], horizontal=True)
        
        # Botones de control
        col_download, col_stop = st.columns(2)
        with col_download:
            start_download = st.button("⬇️ Descargar Propiedades", key="descargar_props_portal")
        with col_stop:
            stop_download = st.button("⏹️ Detener Descarga", key="stop_scraper")
        
        if stop_download:
            st.session_state.scraper_stop_flag = True
            st.session_state.scraper_running = False
            st.warning("⏹️ Detención solicitada... por favor espera")
        
        if start_download:
            st.session_state.scraper_running = True
            st.session_state.scraper_stop_flag = False
            st.info(f"⏳ Descargando Propiedades... esto puede tomar 1-2 minutos")
            
            # Crear contenedores para feedback en tiempo real
            status_container = st.empty()
            progress_container = st.empty()
            details_container = st.empty()
            stats_container = st.empty()
            
            try:
                from src.scrapers import ArgenpropScraper, BuscadorPropScraper, PropertyDatabase
                db = PropertyDatabase()
                total_nuevas = 0
                total_descargadas = 0
                # Calcular total esperado de propiedades a descargar
                total_esperado = limite * len(localidades_seleccionadas)
                
                for idx, localidad in enumerate(localidades_seleccionadas):
                    # Verificar si se solicitó detener
                    if st.session_state.scraper_stop_flag:
                        status_container.warning(f"❌ Descarga detenida en {localidad}. {total_nuevas} propiedades agregadas")
                        st.session_state.scraper_running = False
                        break
                    
                    # Mostrar progreso de zona (antes de descargar)
                    porcentaje_zona = (idx / len(localidades_seleccionadas)) * 100
                    progress_container.progress(porcentaje_zona / 100.0, text=f"📍 Descargando **{localidad}**... ({idx + 1}/{len(localidades_seleccionadas)} zonas)")
                    details_container.info(f"⏳ Buscando propiedades de {localidad}...")
                    
                    # Descargar propiedades
                    props = BuscadorPropScraper.buscar_propiedades(zona=localidad, tipo=tipo_prop.lower(), limit=limite, debug=True, stop_flag=st.session_state)
                    
                    # Mostrar contador durante descarga
                    props_encontradas = len(props)
                    total_descargadas += props_encontradas
                    
                    stats_container.metric(
                        f"🏠 {localidad}",
                        f"{props_encontradas} propiedades encontradas"
                    )
                    
                    nuevas = db.agregar_propiedades(props)
                    total_nuevas += nuevas
                    
                    # Actualizar detalles con información detallada
                    details_container.success(
                        f"✓ {localidad}: "
                        f"**{props_encontradas}** encontradas → "
                        f"**{nuevas}** nuevas agregadas | "
                        f"Total acumulado: **{total_nuevas}**"
                    )
                    
                    # Actualizar barra DESPUÉS de descargar esta zona
                    porcentaje_completado = ((idx + 1) / len(localidades_seleccionadas)) * 100
                    progress_container.progress(porcentaje_completado / 100.0, text=f"✅ **{total_descargadas}** propiedades descargadas ({int(porcentaje_completado)}%)")
                
                if not st.session_state.scraper_stop_flag:
                    status_container.success(f"✅ ¡Descarga completada!")
                    db.guardar_csv("data/properties_expanded.csv")
                    stats = db.obtener_estadisticas()
                    
                    # Mostrar resumen final
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("✨ Nuevas propiedades", total_nuevas)
                    with col2:
                        st.metric("📊 Total en BD", stats['total_propiedades'])
                    with col3:
                        st.metric("💰 Precio promedio", stats.get('promedio_precio', 'N/A'))
                    
                    details_container.empty()
                    progress_container.progress(1.0)
                    
                    # Limpiar caché para recargar datos
                    st.cache_resource.clear()
                    st.rerun()
                
                st.session_state.scraper_running = False
                st.session_state.scraper_stop_flag = False
            except ImportError as ie:
                status_container.error(f"❌ Falta instalar: {ie}")
                st.session_state.scraper_running = False
            except Exception as e:
                status_container.error(f"❌ Error: {str(e)}")
                st.session_state.scraper_running = False
    
    except Exception as e:
        st.error(f"Error cargando geografía: {e}")
        st.markdown("Usando localidades por defecto...")
        
        # Fallback: localidades hardcodeadas - Portal fijo a BuscadorProp
        portal_fb = "BuscadorProp"
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
            limite = st.number_input("Cantidad", 1, 100, 10, key="limite_fallback")
        
        tipo_prop = st.radio("Tipo", ["Venta", "Alquiler"], horizontal=True, key="tipo_fallback")
        
        # Botones de control para fallback
        col_download_fb, col_stop_fb = st.columns(2)
        with col_download_fb:
            start_download_fb = st.button("⬇️ Descargar Propiedades", key="descargar_props_fallback")
        with col_stop_fb:
            stop_download_fb = st.button("⏹️ Detener Descarga", key="stop_scraper_fb")
        
        if stop_download_fb:
            st.session_state.scraper_stop_flag = True
            st.session_state.scraper_running = False
            st.warning("⏹️ Detención solicitada... por favor espera")
        
        if start_download_fb:
            st.session_state.scraper_running = True
            st.session_state.scraper_stop_flag = False
            st.info(f"⏳ Descargando Propiedades... esto puede tomar 1-2 minutos")
            
            # Crear contenedores para feedback en tiempo real
            status_container = st.empty()
            progress_container = st.empty()
            details_container = st.empty()
            stats_container = st.empty()
            
            try:
                from src.scrapers import ArgenpropScraper, BuscadorPropScraper, PropertyDatabase
                db = PropertyDatabase()
                total_nuevas = 0
                total_descargadas = 0
                # Calcular total esperado de propiedades a descargar
                total_esperado = limite * len(zonas_seleccionadas)
                
                for idx, zona in enumerate(zonas_seleccionadas):
                    # Verificar si se solicitó detener
                    if st.session_state.scraper_stop_flag:
                        status_container.warning(f"❌ Descarga detenida en {zona}. {total_nuevas} propiedades agregadas")
                        st.session_state.scraper_running = False
                        break
                    
                    # Mostrar progreso de zona (antes de descargar)
                    porcentaje_zona = (idx / len(zonas_seleccionadas)) * 100
                    progress_container.progress(porcentaje_zona / 100.0, text=f"📍 Descargando **{zona}**... ({idx + 1}/{len(zonas_seleccionadas)} zonas)")
                    details_container.info(f"⏳ Buscando propiedades de {zona}...")
                    
                    # Descargar propiedades
                    props = BuscadorPropScraper.buscar_propiedades(zona=zona, tipo=tipo_prop.lower(), limit=limite, debug=True, stop_flag=st.session_state)
                    
                    # Mostrar contador durante descarga
                    props_encontradas = len(props)
                    total_descargadas += props_encontradas
                    
                    stats_container.metric(
                        f"🏠 {zona}",
                        f"{props_encontradas} propiedades encontradas"
                    )
                    
                    nuevas = db.agregar_propiedades(props)
                    total_nuevas += nuevas
                    
                    # Actualizar detalles con información detallada
                    details_container.success(
                        f"✓ {zona}: "
                        f"**{props_encontradas}** encontradas → "
                        f"**{nuevas}** nuevas agregadas | "
                        f"Total acumulado: **{total_nuevas}**"
                    )
                    
                    # Actualizar barra DESPUÉS de descargar esta zona
                    porcentaje_completado = ((idx + 1) / len(zonas_seleccionadas)) * 100
                    progress_container.progress(porcentaje_completado / 100.0, text=f"✅ **{total_descargadas}** propiedades descargadas ({int(porcentaje_completado)}%)")
                
                if not st.session_state.scraper_stop_flag:
                    status_container.success(f"✅ ¡Descarga completada!")
                    db.guardar_csv("data/properties_expanded.csv")
                    stats = db.obtener_estadisticas()
                    
                    # Mostrar resumen final
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("✨ Nuevas propiedades", total_nuevas)
                    with col2:
                        st.metric("📊 Total en BD", stats['total_propiedades'])
                    with col3:
                        st.metric("💰 Precio promedio", stats.get('promedio_precio', 'N/A'))
                    
                    details_container.empty()
                    progress_container.progress(1.0)
                    
                    # Limpiar caché para recargar datos
                    st.cache_resource.clear()
                    st.rerun()
                
                st.session_state.scraper_running = False
                st.session_state.scraper_stop_flag = False
            except ImportError as ie:
                status_container.error(f"❌ Falta instalar: {ie}")
                st.session_state.scraper_running = False
            except Exception as e:
                status_container.error(f"❌ Error: {str(e)}")
                st.session_state.scraper_running = False

# DESHABILITADO - Sección de tareas programadas
# st.sidebar.markdown("## 🕐 Tareas Programadas")
# with st.sidebar.expander("Configurar Descarga Automática", expanded=False):
#     # [TODO: Sección de tareas programadas comentada - 100 líneas]

st.sidebar.markdown("---")

# NUEVA: Análisis de propiedades marcadas
st.sidebar.markdown("## 📊 Análisis de Preferencias")
with st.sidebar.expander("Ver Propiedades Marcadas", expanded=False):
    # Contar feedback del chat history
    positivos = [e for e in st.session_state.chat_history if e.get('rol') == 'feedback' and e.get('tipo') == 'positivo']
    negativos = [e for e in st.session_state.chat_history if e.get('rol') == 'feedback' and e.get('tipo') == 'negativo']
    
    # Mostrar resumen
    col_pos, col_neg = st.columns(2)
    with col_pos:
        st.metric("👍 Me Interesa", len(positivos))
    with col_neg:
        st.metric("👎 No Me Interesa", len(negativos))
    
    # Mostrar detalles de propiedades marcadas
    if positivos or negativos:
        st.markdown("### 👍 Propiedades de Interés")
        if positivos:
            for fb in positivos:
                # Buscar la propiedad en la BD
                prop_id = fb.get('propiedad_id')
                try:
                    # Obtener info de la propiedad desde el DataFrame
                    if not df_propiedades.empty:
                        prop_info = df_propiedades[df_propiedades['id'] == prop_id]
                        if not prop_info.empty:
                            prop = prop_info.iloc[0]
                            st.caption(f"🏠 **{prop.get('tipo', 'Propiedad')}** - {prop.get('zona', 'N/A')}")
                            st.caption(f"💰 {prop.get('precio', 'N/A')}")
                except:
                    st.caption(f"ID: {prop_id}")
                st.divider()
        else:
            st.info("Sin propiedades marcadas aún")
        
        st.markdown("### 👎 Propiedades Descartadas")
        if negativos:
            for fb in negativos:
                prop_id = fb.get('propiedad_id')
                try:
                    if not df_propiedades.empty:
                        prop_info = df_propiedades[df_propiedades['id'] == prop_id]
                        if not prop_info.empty:
                            prop = prop_info.iloc[0]
                            st.caption(f"🏠 **{prop.get('tipo', 'Propiedad')}** - {prop.get('zona', 'N/A')}")
                            st.caption(f"💰 {prop.get('precio', 'N/A')}")
                except:
                    st.caption(f"ID: {prop_id}")
                st.divider()
        else:
            st.info("Sin propiedades descartadas aún")

st.sidebar.markdown("---")

# Chat principal
st.subheader("💬 Búsqueda Inteligente", divider=False)

# Inicializar session state para búsqueda automática
if "search_query" not in st.session_state:
    st.session_state.search_query = ""
if "search_results" not in st.session_state:
    st.session_state.search_results = []
if "search_page" not in st.session_state:
    st.session_state.search_page = 0
if "last_input_time" not in st.session_state:
    st.session_state.last_input_time = 0

# Opción para ver todas las propiedades
col_all, col_search = st.columns([0.1, 1])
with col_all:
    if st.button("📋 Ver Todas", key="btn_all_props", width='stretch'):
        # Cargar todas las propiedades desde la BD
        from src.scrapers import PropertyDatabase
        db = PropertyDatabase()
        df_all = db.obtener_df()
        if not df_all.empty:
            props_all = df_all.to_dict('records')
            st.session_state.search_results = props_all
            st.session_state.search_query = "TODAS"
            st.session_state.search_page = 0
            st.rerun()  # Actualizar pantalla inmediatamente
        else:
            st.warning("No hay propiedades en la BD")

# Callback que se ejecuta cuando el usuario escribe
def on_search_input_change():
    st.session_state.last_input_time = time.time()
    st.session_state.search_page = 0

with col_search:
    perfil = st.text_input(
        "O describe tu familia y preferencias:",
        placeholder="Ej: Familia de 4 personas, buscan casa luminosa en Palermo con 3 habitaciones",
        key="user_input",
        on_change=on_search_input_change
    )

# Búsqueda automática con debounce (2 segundos) - SOLO si query != "TODAS"
if perfil and st.session_state.search_query != "TODAS":
    elapsed = time.time() - st.session_state.last_input_time
    
    # Si han pasado 2 segundos desde que dejó de escribir, ejecutar búsqueda
    if elapsed >= 2.0 and perfil != st.session_state.search_query:
        st.session_state.search_query = perfil
        st.session_state.search_page = 0
        
        # Buscar propiedades
        propiedades, error = buscar_propiedades(
            perfil,
            k=50  # Buscar 50 resultados iniciales para mejor ranking
        )
        
        if not error and propiedades:
            # Re-rankear resultados con scoring inteligente local
            propiedades_ranked = reranquear_propiedades_localmente(perfil, propiedades)
            st.session_state.search_results = propiedades_ranked
        elif error:
            st.session_state.search_results = []
            
    elif elapsed < 2.0 and perfil != st.session_state.search_query:
        # Mostrar placeholder mientras espera
        with st.spinner("⏳ Esperando para buscar..."):
            time.sleep(0.1)
        st.rerun()
elif perfil == "" and st.session_state.search_query != "TODAS":
    st.session_state.search_results = []
    st.session_state.search_query = ""

# Mostrar resultados con paginación
if st.session_state.search_results:
    # Paginación
    props_per_page = 5
    total_pages = (len(st.session_state.search_results) + props_per_page - 1) // props_per_page
    
    st.markdown("---")
    
    # Usar columnas iguales de 1:1:1
    pag_col1, pag_col2, pag_col3 = st.columns([1, 1, 1], gap="small")
    
    with pag_col1:
        if st.button("⬅️ Anterior", disabled=st.session_state.search_page == 0, width='stretch', key="btn_prev_page"):
            st.session_state.search_page -= 1
            st.rerun()
    
    with pag_col2:
        st.markdown(f"<div style='display: flex; justify-content: center; align-items: center; height: 48px;'><p style='text-align: center; margin: 0; font-size: 14px;'><b>Página {st.session_state.search_page + 1}/{total_pages}</b><br>({len(st.session_state.search_results)} resultados)</p></div>", unsafe_allow_html=True)
    
    with pag_col3:
        if st.button("Siguiente ➡️", disabled=st.session_state.search_page >= total_pages - 1, width='stretch', key="btn_next_page"):
            st.session_state.search_page += 1
            st.rerun()
    
    st.markdown("---")
    
    # Mostrar propiedades de la página actual
    start_idx = st.session_state.search_page * props_per_page
    end_idx = start_idx + props_per_page
    propiedades = st.session_state.search_results[start_idx:end_idx]
    
    st.success(f"✅ Encontré {len(st.session_state.search_results)} propiedad(es) relevante(s):")
    
    for i, prop in enumerate(propiedades, start=start_idx + 1):
        with st.expander(f"**{i}. {prop['tipo']} en {prop['zona']}** - {prop['precio']}", expanded=(i==start_idx+1)):
            
            # Layout principal: información a la izquierda y mapa a la derecha - SIMÉTRICOS
            col_left, col_right = st.columns([1, 1])
            
            with col_left:
                # Información básica compacta en 2 columnas
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Habitaciones", prop.get('habitaciones') or "N/A")
                    st.metric("Baños", prop.get('baños') or "N/A")
                with col2:
                    st.metric("M² Cubiertos", prop.get('metros_cubiertos') or "N/A")
                    pileta_text = "✅ Sí" if prop.get('pileta') else "❌ No"
                    st.metric("Pileta", pileta_text)
                
                # Detalles compactos en una sola línea
                if prop.get('direccion') or prop.get('estado') or prop.get('antiguedad'):
                    info_cols = st.columns(3)
                    if prop.get('direccion'):
                        with info_cols[0]:
                            st.caption(f"📍 {prop['direccion']}")
                    if prop.get('estado'):
                        with info_cols[1]:
                            st.caption(f"🏗️ {prop['estado']}")
                    if prop.get('antiguedad'):
                        with info_cols[2]:
                            st.caption(f"📅 {prop['antiguedad']} años")
                
                # Descripción compacta
                if prop.get('descripcion'):
                    st.caption(f"📝 {prop['descripcion'][:150]}...")
                
                # Amenities compactos
                if prop.get('amenities'):
                    st.caption(f"🏠 {prop['amenities'][:150]}...")
                
                # Palabras clave
                palabras_clave = prop.get('palabras_clave', [])
                if palabras_clave:
                    st.write(" ".join([f"`{p.capitalize()}`" for p in palabras_clave]))
                
                # Ubicación y links
                maps_url, coords, mapa = mostrar_mapa(prop.get('zona', ''))
                loc_cols = st.columns([1, 1])
                with loc_cols[0]:
                    st.caption(f"[🗺️ Maps]({maps_url})")
                with loc_cols[1]:
                    if prop.get('url'):
                        st.caption(f"[🔗 Portal]({prop['url']})")
            
            with col_right:
                # MAPA A LA DERECHA - ANCHO COMPLETO
                st.subheader("🗺️ Ubicación", divider=False)
                if coords:
                    map_data = {
                        'latitude': [coords['lat']],
                        'longitude': [coords['lng']]
                    }
                    st.map(map_data, zoom=15, width='stretch', height=300)
            
            # GALERÍA DE FOTOS EN LA PARTE INFERIOR - ANCHO COMPLETO
            if prop.get('fotos'):
                try:
                    import json
                    fotos = prop.get('fotos')
                    if isinstance(fotos, str):
                        fotos = json.loads(fotos)
                    
                    # FILTRAR: Excluir imágenes que no sean de propiedades
                    fotos_validas = [f for f in fotos if es_imagen_propiedad_valida(f)]
                    
                    if fotos_validas and len(fotos_validas) > 0:
                        st.markdown("### 📸 Galería")
                        
                        # Inicializar índice
                        gallery_key = f"gallery_{prop['id']}"
                        if gallery_key not in st.session_state:
                            st.session_state[gallery_key] = 0
                        
                        current_photo_idx = st.session_state[gallery_key]
                        
                        # Asegurar que el índice no excede las fotos válidas
                        if current_photo_idx >= len(fotos_validas):
                            current_photo_idx = 0
                            st.session_state[gallery_key] = 0
                        
                        # Mostrar foto sin espacios
                        st.image(fotos_validas[current_photo_idx], width='stretch')
                        
                        # Contador centrado
                        st.caption(f"📷 {current_photo_idx + 1}/{len(fotos_validas)}", unsafe_allow_html=False)
                        
                        # Botones de navegación centrados
                        nav_cols = st.columns([0.3, 0.1, 0.1, 0.3])
                        with nav_cols[1]:
                            if st.button("⬅️", key=f"prev_{prop['id']}", width='stretch'):
                                st.session_state[gallery_key] = (current_photo_idx - 1) % len(fotos_validas)
                                st.rerun()
                        with nav_cols[2]:
                            if st.button("➡️", key=f"next_{prop['id']}", width='stretch'):
                                st.session_state[gallery_key] = (current_photo_idx + 1) % len(fotos_validas)
                                st.rerun()
                except Exception as e:
                    pass
            elif prop.get('foto_portada'):
                # Mostrar foto portada si no hay galería
                try:
                    foto_portada = prop['foto_portada']
                    if foto_portada and es_imagen_propiedad_valida(foto_portada):
                        st.markdown("### 📸 Foto")
                        st.image(foto_portada, width='stretch')
                except:
                    pass
            
            # Feedback debajo del contenido (ancho completo)
            st.markdown("---")
            
            # Verificar si ya fue marcada
            prop_id = prop['id']
            ya_marcada_positivo = any(e.get('propiedad_id') == prop_id and e.get('tipo') == 'positivo' for e in st.session_state.chat_history if e.get('rol') == 'feedback')
            ya_marcada_negativo = any(e.get('propiedad_id') == prop_id and e.get('tipo') == 'negativo' for e in st.session_state.chat_history if e.get('rol') == 'feedback')
            # Si ya fue marcada en cualquier categoría, ambos botones se deshabilitan
            ya_marcada = ya_marcada_positivo or ya_marcada_negativo
            
            col_like, col_dislike = st.columns([1, 1])
            with col_like:
                if ya_marcada:
                    st.button("✅ Ya marcada" if ya_marcada_positivo else "✅ Ya tiene feedback", disabled=True, width='stretch', key=f"like_disabled_{prop['id']}")
                else:
                    if st.button("👍 Me interesa", key=f"like_{prop['id']}", width='stretch'):
                        timestamp = datetime.now().strftime("%H:%M:%S")
                        st.session_state.chat_history.append({
                            "rol": "feedback",
                            "tipo": "positivo",
                            "propiedad_id": prop['id'],
                            "timestamp": timestamp
                        })
                        # Guardar en BD
                        from src.scrapers import PropertyDatabase
                        db = PropertyDatabase()
                        db.guardar_feedback(prop['id'], "positivo", timestamp)
                        st.success("✓ Guardado")
                        st.rerun()
            with col_dislike:
                if ya_marcada:
                    st.button("✅ Ya marcada" if ya_marcada_negativo else "✅ Ya tiene feedback", disabled=True, width='stretch', key=f"dislike_disabled_{prop['id']}")
                else:
                    if st.button("👎 No es para mí", key=f"dislike_{prop['id']}", width='stretch'):
                        timestamp = datetime.now().strftime("%H:%M:%S")
                        st.session_state.chat_history.append({
                            "rol": "feedback",
                            "tipo": "negativo",
                            "propiedad_id": prop['id'],
                            "timestamp": timestamp
                        })
                        # Guardar en BD
                        from src.scrapers import PropertyDatabase
                        db = PropertyDatabase()
                        db.guardar_feedback(prop['id'], "negativo", timestamp)
                        st.info("✓ Guardado")
                        st.rerun()

# Mostrar historial compacto
if st.session_state.chat_history and len(st.session_state.chat_history) > 0:
    with st.expander(f"📋 Historial ({len(st.session_state.chat_history)} eventos)", expanded=False):
        for entrada in st.session_state.chat_history:
            if entrada['rol'] == 'usuario':
                st.caption(f"**Usuario ({entrada['timestamp']}):** {entrada['mensaje']}")
            elif entrada['rol'] == 'asistente':
                st.caption(f"**Asistente ({entrada['timestamp']}):** {entrada['mensaje']}")
            elif entrada['rol'] == 'feedback':
                emoji = "👍" if entrada['tipo'] == 'positivo' else "👎"
                st.caption(f"{emoji} Propiedad #{entrada['propiedad_id']}")
