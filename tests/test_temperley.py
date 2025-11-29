#!/usr/bin/env python3
"""Test final: buscar Temperley debe retornar propiedades de Temperley"""

import chromadb
from sentence_transformers import SentenceTransformer
import pandas as pd
from scrapers import PropertyDatabase

db = PropertyDatabase()
df = db.obtener_df()
df = df[df['id'].notna() & (df['id'].astype(str).str.len() > 0)]

print(f"Total propiedades en BD: {len(df)}")
print(f"Zonas: {df['zona'].unique()}")

client = chromadb.PersistentClient(path="./chroma_data")
collection = client.get_collection("propiedades")
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

# Test búsqueda de Temperley
query = "temperley"
query_emb = model.encode([query])
results = collection.query(query_embeddings=query_emb.tolist(), n_results=5)

print(f"\nBúsqueda: '{query}'")
print("-" * 70)

zonas_encontradas = {}
for result_id, metadata in zip(results['ids'][0], results['metadatas'][0]):
    zona = metadata['zona']
    zonas_encontradas[zona] = zonas_encontradas.get(zona, 0) + 1
    print(f"  - {zona}: {metadata['tipo']} - {metadata['precio']}")

print(f"\nZonas encontradas:")
for zona, cnt in zonas_encontradas.items():
    print(f"  {zona}: {cnt}")

if 'Temperley' in zonas_encontradas:
    print("\n✅ CORRECTO: Temperley encontrada en búsqueda de 'temperley'")
else:
    print("\n❌ ERROR: Temperley NO encontrada en búsqueda de 'temperley'")
