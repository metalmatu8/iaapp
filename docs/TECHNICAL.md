# 📚 Documentación Técnica - Agente RAG Inmobiliario

## Tabla de Contenidos
1. [Arquitectura General](#arquitectura-general)
2. [Pipeline RAG Detallado](#pipeline-rag-detallado)
3. [Módulos Core](#módulos-core)
4. [Integración LLM](#integración-llm)
5. [Tool Use y APIs](#tool-use-y-apis)
6. [Métricas y Evaluación](#métricas-y-evaluación)
7. [Despliegue](#despliegue)

---

## Arquitectura General

### Componentes Principales

```
┌─────────────────────────────────────────────────────────────────┐
│                     APLICACIÓN STREAMLIT                         │
│  (UI, gestión de sesiones, flujo conversacional)                 │
└────────┬────────────────────────────────────────┬────────────────┘
         │                                        │
         ▼                                        ▼
    ┌─────────────┐                     ┌──────────────────┐
    │   RAG Core  │                     │  LLM Integration │
    │ (Retrieval) │                     │  (Generación)    │
    └──────┬──────┘                     └────────┬─────────┘
           │                                     │
           ├─────────────────┬───────────────────┤
           │                 │                   │
           ▼                 ▼                   ▼
    ┌────────────┐   ┌──────────────┐   ┌──────────────┐
    │ ChromaDB   │   │   Config     │   │    Tools     │
    │Vector Store│   │ (Variables)  │   │ (APIs Ext.)  │
    └────────────┘   └──────────────┘   └──────────────┘
           │
           ▼
    ┌────────────────┐
    │ CSV Properties │
    │   + Embeddings │
    └────────────────┘
```

### Flujo de Datos

1. **Ingesta**: CSV → Pandas DataFrame
2. **Preprocesamiento**: Limpieza, normalización
3. **Embeddings**: Text → Vectores (sentence-transformers)
4. **Indexación**: Vectores → ChromaDB
5. **Query**: Usuario → Embedding
6. **Retrieval**: Top-k búsqueda + filtrado
7. **Generación**: Propiedades → LLM → Respuesta
8. **Output**: Streamlit → Usuario

---

## Pipeline RAG Detallado

### Paso 1: Carga de Propiedades

```python
df = pd.read_csv('properties.csv')
# Campos: id, tipo, zona, precio, habitaciones, baños, 
#         pileta, metros_cubiertos, metros_descubiertos,
#         descripcion, amenities, latitud, longitud, url
```

**Validaciones**:
- Campos obligatorios presentes
- Tipos de datos correctos (int, float, bool, str)
- Sin valores NaN en campos críticos

### Paso 2: Preprocesamiento de Texto

```python
# Combinación de campos textuales
texto = f"{tipo} en {zona}. {descripcion}. Amenities: {amenities}. M2 cub: {metros_cubiertos}"

# Normalización
texto = texto.lower()  # minúsculas
texto = texto.strip()   # eliminar espacios
```

### Paso 3: Generación de Embeddings

**Modelo**: `all-MiniLM-L6-v2` (sentence-transformers)
- Dimensionalidad: 384 vectores
- Entrenado en 215M pares de oraciones
- Tiempo: ~100ms por propiedad

```python
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')
embeddings = model.encode(textos)  # shape: (n_props, 384)
```

### Paso 4: Indexación en Vector Store

**ChromaDB**:
- Almacenamiento: Local (en memoria o disco)
- Similitud: Cosine distance
- Índice: HNSW (Hierarchical Navigable Small World)

```python
collection = chroma_client.create_collection("propiedades")
for prop in propiedades:
    collection.add(
        documents=[prop_texto],
        embeddings=[embedding],
        metadatas=[prop_metadata],
        ids=[str(prop_id)]
    )
```

### Paso 5: Retrieval Híbrido

**Algoritmo**:
1. Pre-filtrado por metadatos (exacto)
2. Búsqueda semántica (aproximada)
3. Reranking (opcional)

```python
def buscar_propiedades(query, zona=None, precio_max=None, ...):
    # 1. Filtrar por metadatos
    df_filtrado = filtrar_por_metadatos(df, zona, precio_max, ...)
    
    # 2. Generar embedding de query
    query_emb = model.encode([query])
    
    # 3. Búsqueda semántica
    results = collection.query(
        query_embeddings=query_emb,
        n_results=k,
        where_document={"$contains": zona} if zona else None
    )
    
    # 4. Reranking (opcional)
    propiedades_rerankeadas = reranking(results, query)
    
    return propiedades_rerankeadas
```

### Paso 6: Generación de Respuesta (LLM)

```python
# Construir prompt
contexto = "Propiedades encontradas:\n"
for prop in propiedades:
    contexto += f"- {prop['tipo']} en {prop['zona']}, USD {prop['precio']}\n"

prompt = f"""
Perfil del usuario: {perfil_usuario}

{contexto}

Explica por qué estas propiedades son adecuadas.
"""

# Generar con LLM
respuesta = llm.generate(prompt)
```

---

## Módulos Core

### `app.py` - Aplicación Principal

**Responsabilidades**:
- Interfaz Streamlit
- Gestión de sesiones y estado
- Orquestación de flujo conversacional
- Captura de feedback

**Principales funciones**:
- `cargar_sistema()`: Cache de modelo + vector store
- `filtrar_por_metadatos()`: Filtrado exacto
- `buscar_propiedades()`: Búsqueda RAG híbrida
- `formatear_propiedad()`: Presentación de resultados

### `config.py` - Configuración

**Gestiona**:
- LLM provider (OpenAI, Ollama, ninguno)
- Rutas de datos
- Parámetros de retrieval (k, threshold)
- Prompts del sistema
- APIs externas

**Variables clave**:
```python
LLM_PROVIDER = "ninguno"  # o "openai", "ollama"
K_RETRIEVAL = 3
EMBEDDINGS_MODEL = "all-MiniLM-L6-v2"
```

### `llm_integration.py` - Integración LLM

**Clases**:
- `LLMProvider`: Interfaz abstracta
- `OpenAIProvider`: Implementación GPT-4o/mini
- `OllamaProvider`: Implementación local Llama2/Mistral
- `MockProvider`: Testing

**Uso**:
```python
from llm_integration import obtener_llm_provider, generar_recomendacion

llm = obtener_llm_provider()
respuesta = generar_recomendacion(llm, perfil_usuario, propiedades)
```

### `tools.py` - Tool Use

**Clases**:
- `ToolExecutor`: Ejecuta herramientas
- `AgentTools`: Conjunto disponible

**Herramientas (Fase 3)**:
- `calcular_distancia_viaje()`: Google Maps
- `buscar_colegios()`: Proximidad de educación
- `verificar_zona_segura()`: Índices de seguridad
- `obtener_info_zona()`: Datos demográficos

---

## Integración LLM

### OpenAI GPT-4o

**Configuración**:
```bash
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-xxxxx
OPENAI_MODEL=gpt-4o-mini
```

**Costos aproximados**:
- Input: $0.15 / 1M tokens
- Output: $0.60 / 1M tokens
- ~100 tokens por recomendación

### Ollama (Local, Gratuito)

**Instalación**:
1. Descargar desde https://ollama.ai
2. `ollama run llama2` (descarga ~4GB)
3. Configurar en .env

**Ventajas**:
- Sin costo (offline)
- Sin límites de uso
- Control total de datos

**Desventajas**:
- Menor calidad que GPT-4
- Requiere GPU o CPU potente
- Latencia mayor (~10s)

---

## Tool Use y APIs

### Fase 3: Arquitectura Multi-Agente

```
User Query
    │
    ▼
LLM Agent
    │
    ├─→ Tool: calcular_distancia
    │   └─→ Google Maps API
    │       └─→ Tiempo de viaje
    │
    ├─→ Tool: buscar_colegios
    │   └─→ Google Places API
    │       └─→ Escuelas cercanas
    │
    └─→ Tool: verificar_seguridad
        └─→ Base de datos pública
            └─→ Índice de criminalidad
    │
    ▼
LLM sintetiza respuesta
    │
    ▼
Recomendación final con contexto completo
```

### Google Maps Integration

```python
import googlemaps

gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)

# Distancia
result = gmaps.distance_matrix(
    origins=["Palermo, Buenos Aires"],
    destinations=["Work Address"],
    modes=["driving", "transit"]
)

# Lugares cercanos
places = gmaps.places_nearby(
    location=(lat, lng),
    radius=2000,
    type='school'
)
```

---

## Métricas y Evaluación

### Métricas RAG

| Métrica | Fórmula | Target |
|---------|---------|--------|
| **Precision@3** | (# propiedades relevantes) / 3 | > 80% |
| **Recall@3** | (# props recuperadas) / (# props totales relevantes) | > 60% |
| **MRR** | 1 / (posición primera relevante) | > 0.7 |
| **NDCG@3** | Relevancia ponderada por posición | > 0.75 |

### Métricas LLM

| Métrica | Método |
|---------|--------|
| **BLEU Score** | Comparar con respuestas gold |
| **ROUGE** | Recall de n-gramas |
| **Coherencia** | Evaluación humana (1-5) |
| **Relevancia** | ¿Respuesta dirección a la pregunta? |

### Evaluación de Usuario

```python
# Feedback loop
feedback = {
    "query_id": "uuid",
    "usuario": "email",
    "propiedades_sugeridas": [1, 5, 7],
    "calificacion": 4,  # 1-5
    "timestamp": "2025-11-21T10:30:00Z"
}
```

---

## Despliegue

### Local
```bash
streamlit run app.py
```

### Docker
```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["streamlit", "run", "app.py"]
```

### Streamlit Cloud (Gratuito)
1. Push a GitHub
2. Conectar en https://share.streamlit.io
3. Configurar secrets (OPENAI_API_KEY, etc.)

### Producción
- Cloud: AWS EC2, DigitalOcean, GCP
- Orquestación: Kubernetes
- BD: PostgreSQL + pgvector
- Cache: Redis
- Monitoreo: Prometheus + Grafana

---

## Próximos Pasos

### MVP → Fase 2 (Multimodalidad)
- Incorporar CLIP para análisis de imágenes
- Scraping automatizado (Selenium/Scrapy)
- Base de datos relacional (PostgreSQL)

### Fase 3 (Agentes)
- LangChain agents con tool use
- Multi-turn reasoning
- Persistencia de memoria (conversación)

### Fase 4 (Producción)
- API REST (FastAPI)
- Integración WhatsApp (Twilio)
- Analytics y tracking
- A/B testing

---

**Versión**: 1.0 MVP  
**Última actualización**: Noviembre 2025
