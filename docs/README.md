# 🏠 Agente RAG Inmobiliario

**Trabajo Final - Diplomatura en IA Generativa**  
Equipo 12: Francisco Areses, Gabriel Damasceno Rodrigues, Matias Frano, Pablo Ramundo, Daniel Biondi

## Descripción

Un agente conversacional inteligente que utiliza la arquitectura RAG (Retrieval-Augmented Generation) para recomendar propiedades inmobiliarias basado en preferencias del usuario. Combina búsqueda semántica, filtrado de metadatos y generación de lenguaje natural para ofrecer una experiencia de usuario superior a los filtros tradicionales.

**Repositorio**: https://github.com/metalmatu8/iaapp

## 🎯 Características MVP (Fase 1 - Entrega Actual)

- ✅ **RAG Semántico**: Búsqueda inteligente basada en embeddings de propiedades
- ✅ **Filtrado Híbrido**: Combinación de búsqueda semántica + filtros por precio, zona, habitaciones, pileta
- ✅ **Interfaz Web Interactiva**: Chat en Streamlit con UX amigable
- ✅ **Historial de Búsqueda**: Retiene conversación del usuario con feedback
- ✅ **Dataset de Ejemplo**: 10 propiedades de demostración en CSV
- ✅ **100% Gratuito**: Sin licencias, código abierto, funciona localmente

## 🛠️ Stack Tecnológico

| Componente | Tecnología | Razón |
|-----------|-----------|-------|
| **Lenguaje** | Python 3.10+ | Estándar para IA/ML |
| **Orquestación RAG** | LangChain (futuro) | Manejo robusto de pipelines RAG |
| **Vector Store** | ChromaDB | Local, sin dependencias, fácil de usar |
| **Embeddings** | sentence-transformers | Open-source, sin APIs |
| **Modelo LLM** | OpenAI GPT-4o / Ollama Llama2 | Configurable, gratuito con Ollama |
| **Frontend** | Streamlit | Desarrollo rápido, sin JavaScript |
| **Gestión de Datos** | pandas | Procesamiento de CSV/metadatos |

## 📋 Estructura del Proyecto

```
├── app.py                    # Aplicación principal (Streamlit)
├── config.py                 # Configuración centralizada
├── llm_integration.py        # Integración LLM (OpenAI/Ollama)
├── tools.py                  # Tool Use para APIs externas (Fase 3)
├── properties.csv            # Dataset de propiedades
├── requirements.txt          # Dependencias Python
├── .env.example              # Plantilla de variables de entorno
└── README.md                 # Este archivo
```

## 🚀 Instalación y Uso

### Paso 1: Clonar repositorio
```bash
git clone https://github.com/metalmatu8/iaapp.git
cd iaapp
```

### Paso 2: Crear entorno virtual (recomendado)
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Mac/Linux
python -m venv .venv
source .venv/bin/activate
```

### Paso 3: Instalar dependencias
```bash
pip install -r requirements.txt
```

### Paso 4: Configurar variables de entorno (opcional)
```bash
# Copiar plantilla
cp .env.example .env

# Editar .env y agregar tus APIs (OpenAI, Google Maps, etc.)
# Para MVP, dejar LLM_PROVIDER=ninguno
```

### Paso 5: Ejecutar aplicación
```bash
streamlit run app.py
```

La aplicación abrirá en `http://localhost:8501`

## 📖 Cómo Usar

1. **Describe tu búsqueda**: "Familia de 4 personas, buscan casa en Palermo con 3 habitaciones y pileta"
2. **Usa los filtros avanzados** (sidebar izquierdo):
   - Seleccionar zona
   - Establecer precio máximo
   - Configurar habitaciones mínimas
   - Indicar si necesita pileta
3. **Recibe recomendaciones**: El sistema muestra 3 propiedades más relevantes
4. **Proporciona feedback**: Marca "👍 Me interesa" o "👎 No es para mí" para entrenar el sistema

## 🔧 Configuración Avanzada

### Usar OpenAI GPT-4o
```bash
# En .env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-xxxxx
OPENAI_MODEL=gpt-4o-mini
```

### Usar Ollama (Local, Gratis)
1. Descargar Ollama desde https://ollama.ai
2. Ejecutar: `ollama run llama2` (descarga ~4GB)
3. Configurar en .env:
```bash
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2
```

### Agregar propiedades al dataset
Editar `properties.csv` con el siguiente formato:

```csv
id,tipo,zona,precio,habitaciones,baños,pileta,metros_cubiertos,metros_descubiertos,descripcion,amenities,latitud,longitud,url
11,Casa,San Telmo,280000,3,2,False,160,80,"Casa histórica renovada","Patio;Parrilla",-34.62,-58.38,https://...
```

## 📊 Flujo de Datos (Pipeline RAG)

```
┌─────────────────┐
│ CSV Propiedades │
└────────┬────────┘
         │
         ▼
┌──────────────────────┐
│ Preprocessing Data   │ (normalización, limpieza)
└────────┬─────────────┘
         │
         ▼
┌──────────────────────┐
│ Generar Embeddings   │ (sentence-transformers)
└────────┬─────────────┘
         │
         ▼
┌──────────────────────┐
│ Vector Store         │ (ChromaDB)
│ (búsqueda semántica) │
└────────┬─────────────┘
         │
         ▼
┌──────────────────────┐
│ Query Usuario        │
└────────┬─────────────┘
         │
         ▼
┌──────────────────────────────┐
│ Retrieval Híbrido:           │
│ 1. Pre-filtrar metadatos     │
│ 2. Búsqueda semántica (top-k)│
│ 3. Reranking                 │
└────────┬─────────────────────┘
         │
         ▼
┌──────────────────────┐
│ LLM (Generación)     │ (opcional)
│ Respuesta explicada  │
└────────┬─────────────┘
         │
         ▼
┌──────────────────────┐
│ Respuesta Usuario    │
│ + Historial + Foto   │
└──────────────────────┘
```

## 🗺️ Roadmap (Fases Futuras)

### Fase 2: Enriquecimiento de Datos y Multimodalidad (Q1 2025)
- [ ] **RAG Multimodal**: Análisis de imágenes con CLIP/GPT-4 Vision
  - Usuario busca: "Cocinas con isla de mármol"
  - Sistema analiza fotos y detecta estas características
- [ ] **Scraping Automatizado**: Scrappers para Argenprop, MercadoLibre, Zonaprop
  - Dataset actualizado en tiempo real
  - Base de datos dinámica (PostgreSQL)
- [ ] **Indexación Avanzada**: FAISS/Milvus para datasets grandes (100k+ propiedades)

### Fase 3: Agentes Autónomos y Tool Use (Q2 2025)
- [ ] **Arquitectura Multi-Agente**:
  - Agente Buscador (retrieval especializado)
  - Agente Financiero (calcula hipotecas, costos)
  - Agente Evaluador (detecta trampas en descripciones)
  - Agente de Viajes (Google Maps + transporte público)
  
- [ ] **Integration de APIs Externas**:
  - Google Maps: Cálculo de tiempos de viaje reales
  - Google Places: Proximidad a colegios, hospitales, parques
  - Datos públicos: Seguridad por zona, demografía
  - APIs financieras: Tasas de hipoteca actualizadas

- [ ] **Tool Use / Function Calling**:
  - LLM decide qué herramientas usar automáticamente
  - Ejemplo: "Busca propiedades y calcula tiempo a trabajo"

### Fase 4: Experiencia de Usuario y Despliegue (Q3 2025)
- [ ] **Interfaz WhatsApp** (Twilio API):
  - Interacción natural vía chat de WhatsApp
  - Donde ocurren recomendaciones inmobiliarias reales
  
- [ ] **Feedback Loop**:
  - Mano arriba/abajo en respuestas
  - Re-entrenamiento de embeddings
  - Personalización por usuario
  
- [ ] **Despliegue en Producción**:
  - Docker + Kubernetes
  - CI/CD con GitHub Actions
  - Monitoreo y logging con Datadog/New Relic
  - Escalabilidad (100k+ usuarios concurrentes)

- [ ] **Analytics y Métricas**:
  - CTR de propiedades (click-through rate)
  - Tasa de conversión (consulta → venta)
  - NPS (Net Promoter Score)
  - A/B testing de ranking

## 📈 Métricas de Evaluación (MVP)

| Métrica | Objetivo | Estado |
|---------|----------|--------|
| Relevancia semántica | Top-1 Accuracy > 70% | En evaluación |
| Velocidad de respuesta | < 2s promedio | ✅ Cumple |
| Cobertura de búsqueda | Mín. 3 resultados en 80% de queries | ✅ Cumple |
| Satisfacción usuario | NPS > 50 | En evaluación |
| Costos operacionales | $0 (open-source) | ✅ Cumple |

## 🔐 Privacidad y Seguridad

- ✅ Sin almacenamiento de datos personales (MVP)
- ✅ Ejecutable localmente (zero cloud dependency)
- ✅ Datos de propiedades en CSV (auditable, transparente)
- 🔜 Encriptación en Fase 2
- 🔜 GDPR compliance en Fase 4

## ⚠️ Limitaciones Actuales (MVP)

- Dataset limitado a 10 propiedades de ejemplo
- Sin análisis de imágenes (multimodalidad)
- Sin cálculo de tiempos reales de viaje
- Sin persistencia de usuario (estadeless)
- LLM opcional (usar Ollama o no usar)

## 🤝 Contribuciones

Este proyecto es open-source. Si quieres contribuir:
1. Fork el repositorio
2. Crea un branch (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -m "Agregar X"`)
4. Push al branch (`git push origin feature/nueva-funcionalidad`)
5. Abre Pull Request

## 📞 Contacto y Soporte

- **Issues**: https://github.com/metalmatu8/iaapp/issues
- **Equipo**: Contactar a través de Issues en GitHub

## 📄 Licencia

Este proyecto está bajo licencia **MIT**. Eres libre de usar, modificar y distribuir el código.

---

**Última actualización**: Noviembre 2025  
**Versión**: MVP 1.0
