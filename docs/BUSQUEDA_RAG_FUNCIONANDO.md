# ✓ BÚSQUEDA RAG FUNCIONANDO

## Problema Identificado y Resuelto

**Problema**: "cuando busco departamento o palermo no encuentra nada"

**Root Cause**: ChromaDB usaba almacenamiento en memoria
- Cada instancia de `chromadb.Client()` creaba una nueva colección en memoria
- Los embeddings de `regenerar_chromadb.py` se guardaban pero luego se perdían
- `app.py` creaba una colección vacía cada vez

**Solución Implementada**:

### 1. ChromaDB Persistente
```python
# Antes (en memoria)
client = chromadb.Client(Settings(...))

# Ahora (persistente)
client = chromadb.PersistentClient(path="./chroma_data")
```

**Cambios**:
- `regenerar_chromadb.py`: Usa `PersistentClient` para guardar embeddings
- `app.py`: Usa `PersistentClient` para recuperar embeddings existentes

### 2. Correcciones en Búsqueda
**Bug en `app.py`**:
```python
# Antes (quebrado)
query_emb = model.encode([query])
results = collection.query(query_embeddings=query_emb, ...)  # ❌ array, no lista
for prop_meta in results['metadatas'][0]:  # ❌ ID no está en metadata
    if int(prop_meta['id']) in df_filtrado['id'].values:

# Ahora (funciona)
query_emb = model.encode([query])
results = collection.query(query_embeddings=query_emb.tolist(), ...)  # ✓ convertir a lista
for result_id, prop_meta in zip(results['ids'][0], results['metadatas'][0]):  # ✓ usar ID de results
    if result_id in df_filtrado['id'].astype(str).values:
```

**Cambios**:
- Convertir embeddings a `.tolist()` para ChromaDB
- Usar `results['ids'][0]` en lugar de buscar 'id' en metadata
- Comparar strings (no integers)

## Verificación

### ✓ Test de RAG Search
```bash
$ python test_rag_search.py
Busqueda: 'departamento'
1. Palermo - Propiedad: USD 145.000
2. Recoleta - Departamento: USD 135.000 + $190.000 expensas
3. Recoleta - Departamento: USD 152.000 + $220.000 expensas

Busqueda: 'palermo'
1. Palermo - Propiedad: USD 145.000
2. Palermo - Propiedad: USD 29.000
3. Palermo - Propiedad: USD 170.000

TEST COMPLETADO EXITOSAMENTE ✓
```

### ✓ Test de App Search (con filtros)
```bash
$ python test_app_search.py
Busqueda: 'departamento' (zona: Todas)
  1. Palermo - Propiedad: USD 145.000
  2. Recoleta - Departamento: USD 135.000 + $190.000 expensas
  3. Recoleta - Departamento: USD 152.000 + $220.000 expensas

Busqueda: 'palermo' (zona: Todas)
  1. Palermo - Propiedad: USD 145.000
  2. Palermo - Propiedad: USD 29.000
  3. Palermo - Propiedad: USD 170.000

Busqueda: 'departamento' (zona: Palermo)
  1. Palermo - Propiedad: USD 145.000
```

### ✓ App Streamlit Running
```
Local URL: http://localhost:8502
Cargadas 16 propiedades de BD SQLite
Colección existente encontrada con 16 documentos ✓
```

## Archivos Modificados

1. **regenerar_chromadb.py**
   - Cambiar a `PersistentClient(path="./chroma_data")`
   - ChromaDB ahora persiste en disco

2. **app.py**
   - Cambiar a `PersistentClient(path="./chroma_data")`
   - Convertir embeddings a `.tolist()`
   - Usar `results['ids'][0]` para comparar propiedades
   - Remover import innecesario `Settings`

3. **test_app_search.py** (nuevo)
   - Test para simular búsqueda con filtros
   - Valida que la lógica de app.py funciona

## Acceso a la App

**URL Local**: http://localhost:8502

**Prueba rápida**:
- Ingresa: "departamento" → retorna 3 propiedades ✓
- Ingresa: "palermo" → retorna 3 propiedades de Palermo ✓
- Usa filtro de zona + búsqueda → combina ambos filtros ✓

**Estado Final**: ✅ Sistema funcionando correctamente
