#!/usr/bin/env python3
"""Test de búsqueda RAG con ejemplos simples"""

import chromadb
from sentence_transformers import SentenceTransformer
import sys

# Codificación UTF-8 para Windows
if sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

client = chromadb.PersistentClient(path="./chroma_data")

try:
    collection = client.get_collection("propiedades")
    total = collection.count()
    print(f"ChromaDB encontrado: {total} documentos\n")
    
    model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    
    # Pruebas de búsqueda
    pruebas = [
        ("departamento", 3),
        ("palermo", 3),
        ("recoleta", 3),
        ("departamento 2 ambientes", 2),
    ]
    
    print("=" * 70)
    print("TEST DE BUSQUEDA RAG")
    print("=" * 70)
    
    for query, n in pruebas:
        print(f"\nBusqueda: '{query}'")
        print("-" * 70)
        
        query_emb = model.encode([query])
        results = collection.query(query_embeddings=query_emb.tolist(), n_results=n)
        
        if results['ids'] and results['ids'][0]:
            for i, (doc_id, metadata) in enumerate(zip(results['ids'][0], results['metadatas'][0]), 1):
                print(f"{i}. {metadata['zona']} - {metadata['tipo']}")
                print(f"   Precio: {metadata['precio']}")
        else:
            print("   [SIN RESULTADOS]")
    
    print("\n" + "=" * 70)
    print("TEST COMPLETADO EXITOSAMENTE")
    print("=" * 70)
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
