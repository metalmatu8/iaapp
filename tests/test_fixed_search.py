#!/usr/bin/env python3
"""Test búsqueda con filtro de habitaciones arreglado"""

import chromadb
from sentence_transformers import SentenceTransformer
import pandas as pd
from scrapers import PropertyDatabase

db = PropertyDatabase()
df_propiedades = db.obtener_df()
df_propiedades = df_propiedades[df_propiedades['id'].notna() & (df_propiedades['id'].astype(str).str.len() > 0)]
df_propiedades = df_propiedades.reset_index(drop=True)

def filtrar_por_metadatos(df, zona=None, precio_max=None, habitaciones_min=None, pileta=None):
    resultado = df.copy()
    
    if zona:
        resultado = resultado[resultado['zona'].str.lower() == zona.lower()]
    
    if precio_max:
        resultado = resultado[resultado['precio'] <= precio_max]
    
    if habitaciones_min and habitaciones_min > 0:
        resultado = resultado[resultado['habitaciones'].notna() & (resultado['habitaciones'] >= habitaciones_min)]
    
    if pileta is not None:
        resultado = resultado[resultado['pileta'] == pileta]
    
    return resultado

# Test
cliente = chromadb.PersistentClient(path="./chroma_data")
collection = cliente.get_collection("propiedades")
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

queries = [
    ("palermo", None, None, 0),
    ("recoleta", None, None, 0),
    ("departamento", "Palermo", None, 0),
]

for query, zona, precio, hab in queries:
    print(f"\nBusqueda: '{query}' (zona={zona}, precio={precio}, hab={hab})")
    print("-" * 70)
    
    df_filtrado = filtrar_por_metadatos(df_propiedades, zona=zona, precio_max=precio, habitaciones_min=hab)
    print(f"  Propiedades tras filtro: {len(df_filtrado)}")
    
    if df_filtrado.empty:
        print("  VACIO - Sin resultados")
        continue
    
    query_emb = model.encode([query])
    results = collection.query(query_embeddings=query_emb.tolist(), n_results=3)
    
    propiedades_recomendadas = []
    for result_id, prop_meta in zip(results['ids'][0], results['metadatas'][0]):
        if result_id in df_filtrado['id'].astype(str).values:
            propiedades_recomendadas.append(prop_meta)
    
    print(f"  Resultados: {len(propiedades_recomendadas)}")
    for i, prop in enumerate(propiedades_recomendadas, 1):
        print(f"    {i}. {prop['zona']} - {prop['tipo']}: {prop['precio']}")
