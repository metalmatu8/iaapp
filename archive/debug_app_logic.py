#!/usr/bin/env python3
"""Simular exactamente lo que hace app.py cuando buscas 'palermo'"""

import chromadb
from sentence_transformers import SentenceTransformer
import pandas as pd
import sqlite3
from scrapers import PropertyDatabase

# Cargar como lo hace app.py
db = PropertyDatabase()
df_propiedades = db.obtener_df()

# Filtrar como lo hace app.py
df_propiedades = df_propiedades[df_propiedades['id'].notna() & (df_propiedades['id'].astype(str).str.len() > 0)]
df_propiedades = df_propiedades.reset_index(drop=True)

print(f"Total propiedades en df_propiedades: {len(df_propiedades)}")
print(f"Zonas únicas: {df_propiedades['zona'].unique()}\n")

# Simular búsqueda
query = "palermo"
zona_filter = None  # Sin filtro de zona
precio_max_filter = None
habitaciones_min = 1
pileta_filter = None

# Pre-filtrado por metadatos (como lo hace app.py)
df_filtrado = df_propiedades.copy()

if zona_filter:
    df_filtrado = df_filtrado[df_filtrado['zona'].str.lower() == zona_filter.lower()]

if precio_max_filter:
    df_filtrado = df_filtrado[df_filtrado['precio'] <= precio_max_filter]

if habitaciones_min:
    df_filtrado = df_filtrado[df_filtrado['habitaciones'] >= habitaciones_min]

if pileta_filter is not None:
    df_filtrado = df_filtrado[df_filtrado['pileta'] == pileta_filter]

print(f"Propiedades después de filtrado: {len(df_filtrado)}")
print(f"Primeros IDs en df_filtrado:")
for i, id_val in enumerate(df_filtrado['id'].head(3)):
    print(f"  {i+1}. {id_val[:60]}...")

if df_filtrado.empty:
    print("\nERROR: df_filtrado está vacío!")
else:
    # Búsqueda semántica
    client = chromadb.PersistentClient(path="./chroma_data")
    collection = client.get_collection("propiedades")
    model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    
    query_emb = model.encode([query])
    results = collection.query(query_embeddings=query_emb.tolist(), n_results=min(3, len(df_filtrado)))
    
    print(f"\nResultados de ChromaDB: {len(results['ids'][0])} propiedades")
    
    # Filtrar por BD
    propiedades_recomendadas = []
    for result_id, prop_meta in zip(results['ids'][0], results['metadatas'][0]):
        print(f"\nComparando ID de ChromaDB:")
        print(f"  ChromaDB: {result_id[:60]}...")
        print(f"  ¿En df_filtrado? {result_id in df_filtrado['id'].astype(str).values}")
        
        if result_id in df_filtrado['id'].astype(str).values:
            propiedades_recomendadas.append(prop_meta)
    
    print(f"\nTotal que matchean df_filtrado: {len(propiedades_recomendadas)}")
    if propiedades_recomendadas:
        for i, prop in enumerate(propiedades_recomendadas, 1):
            print(f"  {i}. {prop['zona']} - {prop['tipo']}")
