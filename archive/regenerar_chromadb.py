#!/usr/bin/env python3
"""Regenera ChromaDB con las propiedades normalizadas de la BD"""

import chromadb
import sqlite3
from sentence_transformers import SentenceTransformer

def main():
    # Conectar a ChromaDB con almacenamiento persistente
    import os
    persist_dir = "./chroma_data"
    if not os.path.exists(persist_dir):
        os.makedirs(persist_dir)
    
    client = chromadb.PersistentClient(path=persist_dir)
    
    # Eliminar colección antigua si existe
    try:
        client.delete_collection("propiedades")
        print("✓ Colección antigua eliminada")
    except Exception as e:
        print(f"  (No había colección previa)")
    
    # Cargar propiedades de BD SQLite
    conn = sqlite3.connect("properties.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, zona, tipo, precio, descripcion, url
        FROM propiedades
        ORDER BY fecha_agregado DESC
    """)
    propiedades = cursor.fetchall()
    conn.close()
    
    if not propiedades:
        print("❌ No hay propiedades en la BD")
        return
    
    print(f"\n✓ Cargadas {len(propiedades)} propiedades de BD")
    
    # Crear colección y cargar embeddings
    collection = client.get_or_create_collection("propiedades")
    model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    
    ids = []
    documents = []
    metadatas = []
    
    for prop in propiedades:
        prop_id, zona, tipo, precio, descripcion, url = prop
        
        # Documento para embedding: descripción + zona + tipo
        doc_text = f"{descripcion} {zona} {tipo}".strip()
        
        ids.append(str(prop_id))
        documents.append(doc_text)
        metadatas.append({
            "zona": zona,
            "tipo": tipo,
            "precio": precio,
            "url": url
        })
    
    # Agregar a ChromaDB
    print("Generando embeddings...")
    collection.add(
        ids=ids,
        documents=documents,
        metadatas=metadatas
    )
    
    print(f"✓ {len(ids)} embeddings generados e indexados\n")
    
    # Test de búsqueda
    print("=" * 70)
    print("TEST: Búsqueda RAG")
    print("=" * 70)
    
    consultas = [
        "departamento de 2 ambientes en Palermo",
        "departamento barato menos de 100000",
        "propiedad en Recoleta"
    ]
    
    for query in consultas:
        print(f"\n🔍 '{query}'")
        print("-" * 70)
        
        results = collection.query(
            query_texts=[query],
            n_results=3
        )
        
        if results['ids'] and results['ids'][0]:
            for i, (doc, metadata) in enumerate(zip(results['documents'][0], results['metadatas'][0]), 1):
                print(f"\n{i}. {metadata['zona']} - {metadata['tipo']}")
                print(f"   Precio: {metadata['precio']}")
                print(f"   Desc: {doc[:100]}...")
        else:
            print("   Sin resultados")
    
    print("\n" + "=" * 70)
    print("✓ ChromaDB regenerado y listo para búsqueda RAG\n")

if __name__ == "__main__":
    main()
