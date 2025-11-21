#!/usr/bin/env python3
"""Simular la búsqueda de la app con filtros"""

import chromadb
from sentence_transformers import SentenceTransformer
import pandas as pd
import sqlite3
import sys

if sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Cargar BD
conn = sqlite3.connect("properties.db")
df = pd.read_sql_query("SELECT * FROM propiedades", conn)
conn.close()

print(f"Propiedades en BD: {len(df)}\n")

# Conectar a ChromaDB
client = chromadb.PersistentClient(path="./chroma_data")
collection = client.get_collection("propiedades")

model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

# Simular búsqueda de app
queries = [
    ("departamento", None),
    ("palermo", None),
    ("departamento", "Palermo"),
]

for query, zona_filter in queries:
    print(f"Busqueda: '{query}' (zona: {zona_filter or 'Todas'})")
    print("-" * 70)
    
    # Pre-filtrado por metadatos
    df_filtrado = df.copy()
    if zona_filter:
        df_filtrado = df_filtrado[df_filtrado['zona'].str.lower() == zona_filter.lower()]
    
    if df_filtrado.empty:
        print("  No hay propiedades con ese filtro")
        print()
        continue
    
    # Búsqueda semántica
    query_emb = model.encode([query])
    results = collection.query(query_embeddings=query_emb.tolist(), n_results=min(3, len(df_filtrado)))
    
    # Filtrar resultados
    propiedades_recomendadas = []
    for result_id, prop_meta in zip(results['ids'][0], results['metadatas'][0]):
        if result_id in df_filtrado['id'].astype(str).values:
            propiedades_recomendadas.append(prop_meta)
    
    if not propiedades_recomendadas:
        print("  Sin resultados que cumplan filtros")
    else:
        for i, prop in enumerate(propiedades_recomendadas, 1):
            print(f"  {i}. {prop['zona']} - {prop['tipo']}: {prop['precio']}")
    print()
