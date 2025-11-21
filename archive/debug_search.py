#!/usr/bin/env python3
"""Debug búsquedas que no retornan nada"""

import chromadb
from sentence_transformers import SentenceTransformer
import pandas as pd
import sqlite3
import sys

if sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Cargar BD
conn = sqlite3.connect('properties.db')
df = pd.read_sql_query('SELECT id, zona FROM propiedades', conn)
conn.close()

print(f"Zonas en BD: {df['zona'].unique()}")
print(f"Total: {len(df)} propiedades\n")

# ChromaDB
client = chromadb.PersistentClient(path="./chroma_data")
collection = client.get_collection("propiedades")
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

# Probar búsquedas
for query in ['palermo', 'recoleta', 'Palermo', 'Recoleta']:
    query_emb = model.encode([query])
    results = collection.query(query_embeddings=query_emb.tolist(), n_results=5)
    
    print(f"Busqueda: '{query}'")
    print(f"  Resultados totales: {len(results['ids'][0])}")
    
    # Ver primeros 2
    for i, (rid, meta) in enumerate(zip(results['ids'][0][:2], results['metadatas'][0][:2])):
        in_df = rid in df['id'].astype(str).values
        print(f"    {i+1}. {meta['zona']} - Match BD: {in_df}")
        if i == 0:
            print(f"       ID ChromaDB: {rid[:50]}...")
            print(f"       ID en BD tipos: {set(df['id'].astype(str).str[:20].values)}")
    
    # Contar matches
    matches = sum(1 for rid in results['ids'][0] if rid in df['id'].astype(str).values)
    print(f"  Total que matchean BD: {matches}/{len(results['ids'][0])}")
    print()
