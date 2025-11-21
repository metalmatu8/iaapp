#!/usr/bin/env python3
"""Script de prueba para verificar carga de datos paso a paso"""

import sys
import time

print("1️⃣  Importando módulos...")
try:
    import pandas as pd
    from sentence_transformers import SentenceTransformer
    import chromadb
    print("   ✅ Módulos importados")
except Exception as e:
    print(f"   ❌ Error: {e}")
    sys.exit(1)

print("\n2️⃣  Conectando a BD SQLite...")
try:
    from scrapers import PropertyDatabase
    db = PropertyDatabase('../data/properties.db')
    df = db.obtener_df()
    print(f"   ✅ BD conectada - {len(df)} propiedades")
except Exception as e:
    print(f"   ❌ Error: {e}")
    sys.exit(1)

print("\n3️⃣  Preparando embeddings...")
try:
    def make_text(row):
        desc = row.get('descripcion', '') if isinstance(row, dict) else row['descripcion']
        return f"{row['tipo']} en {row['zona']}. {desc}"
    
    df['text'] = df.apply(make_text, axis=1)
    print(f"   ✅ Textos preparados para {len(df)} propiedades")
except Exception as e:
    print(f"   ❌ Error: {e}")
    sys.exit(1)

print("\n4️⃣  Cargando modelo de embeddings (esto toma tiempo)...")
try:
    model = SentenceTransformer('all-MiniLM-L6-v2')
    print("   ✅ Modelo cargado")
except Exception as e:
    print(f"   ❌ Error: {e}")
    sys.exit(1)

print("\n5️⃣  Generando embeddings (ESPERA, esto puede tomar 1-2 minutos)...")
try:
    start = time.time()
    embeddings = model.encode(df['text'].tolist())
    elapsed = time.time() - start
    print(f"   ✅ {len(embeddings)} embeddings generados en {elapsed:.1f}s")
except Exception as e:
    print(f"   ❌ Error: {e}")
    sys.exit(1)

print("\n6️⃣  Creando/Actualizando ChromaDB...")
try:
    chroma_client = chromadb.PersistentClient(path="../data/chroma_data")
    
    # Eliminar colección anterior si existe
    try:
        chroma_client.delete_collection("propiedades")
        print("   📝 Colección anterior eliminada")
    except:
        pass
    
    collection = chroma_client.create_collection("propiedades")
    print(f"   ✅ Colección creada")
except Exception as e:
    print(f"   ❌ Error: {e}")
    sys.exit(1)

print("\n7️⃣  Agregando propiedades a ChromaDB...")
try:
    count = 0
    for i, row in df.iterrows():
        row_id = str(row['id']).strip() if row['id'] else None
        if not row_id or row_id == "nan" or row_id == "None":
            continue
        
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
            count += 1
        except Exception as e:
            print(f"      ⚠️  Error en fila {i}: {e}")
            continue
        
        if (i + 1) % 50 == 0:
            print(f"      📊 {i + 1}/{len(df)} propiedades agregadas...")
    
    print(f"   ✅ {count} propiedades agregadas a ChromaDB")
except Exception as e:
    print(f"   ❌ Error: {e}")
    sys.exit(1)

print("\n8️⃣  Verificando ChromaDB...")
try:
    final_count = collection.count()
    print(f"   ✅ ChromaDB tiene {final_count} documentos")
except Exception as e:
    print(f"   ❌ Error: {e}")
    sys.exit(1)

print("\n" + "="*60)
print("✅ TODO LISTO - La app debería funcionar correctamente")
print("="*60)
