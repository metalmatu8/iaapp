#!/usr/bin/env python3
"""Test búsqueda con propiedades completas"""

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
client = chromadb.PersistentClient(path="./chroma_data")
collection = client.get_collection("propiedades")
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

query = "palermo"
df_filtrado = filtrar_por_metadatos(df_propiedades)

query_emb = model.encode([query])
results = collection.query(query_embeddings=query_emb.tolist(), n_results=3)

propiedades_recomendadas = []
for result_id in results['ids'][0]:
    if result_id in df_filtrado['id'].astype(str).values:
        prop_row = df_filtrado[df_filtrado['id'].astype(str) == result_id].iloc[0]
        propiedades_recomendadas.append(prop_row.to_dict())

print(f"Resultados para '{query}': {len(propiedades_recomendadas)}\n")
for i, prop in enumerate(propiedades_recomendadas, 1):
    print(f"{i}. {prop['zona']} - {prop['tipo']}")
    print(f"   Precio: {prop.get('precio', 'N/A')}")
    print(f"   Habitaciones: {prop.get('habitaciones') or 'N/A'}")
    print(f"   Desc: {prop.get('descripcion', 'N/A')[:60]}...")
    print()
