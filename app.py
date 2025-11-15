
import pandas as pd
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
import streamlit as st

# 1. Cargar propiedades

# 1-4. Cargar y preparar datos, embeddings y vector store, cacheado
@st.cache_resource(show_spinner=True)
def cargar_sistema():
    df = pd.read_csv('properties.csv')
    def make_text(row):
        return f"{row['tipo']} en {row['zona']}. {row['descripcion']}. Amenities: {row['amenities']}. M2 cub: {row['metros_cubiertos']}, M2 desc: {row['metros_descubiertos']}"
    df['text'] = df.apply(make_text, axis=1)
    model = SentenceTransformer('all-MiniLM-L6-v2')
    embeddings = model.encode(df['text'].tolist())
    chroma_client = chromadb.Client(Settings(anonymized_telemetry=False))
    if 'propiedades' in [c.name for c in chroma_client.list_collections()]:
        chroma_client.delete_collection('propiedades')
    collection = chroma_client.create_collection("propiedades")
    for i, row in df.iterrows():
        collection.add(
            documents=[row['text']],
            embeddings=[embeddings[i]],
            metadatas=[row.to_dict()],
            ids=[str(row['id'])]
        )
    return model, collection

model, collection = cargar_sistema()

# 5. Interfaz simple con Streamlit
st.title("Buscador de Propiedades Inteligente")
perfil = st.text_input("Describe tu familia y preferencias (ej: 2 adultos, 2 niños, Palermo, pileta, 3 habitaciones, max 300000):")
if st.button("Buscar"):
    perfil_emb = model.encode([perfil])
    results = collection.query(query_embeddings=perfil_emb, n_results=3)
    for prop in results['metadatas'][0]:
        st.write(f"**{prop['tipo']} en {prop['zona']}**")
        st.write(f"Habitaciones: {prop['habitaciones']}, Baños: {prop['baños']}, Pileta: {prop['pileta']}")
        st.write(f"Metros cubiertos: {prop['metros_cubiertos']}, Descubiertos: {prop['metros_descubiertos']}")
        st.write(f"Precio: USD {prop['precio']}")
        st.write(f"Descripción: {prop['descripcion']}")
        st.write(f"[Ver propiedad]({prop['url']})")
        st.write("---")
