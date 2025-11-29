"""
config.py - Configuración centralizada del Agente RAG Inmobiliario
Soporta OpenAI y modelos open-source via Ollama
"""

import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# ==================== CONFIGURACIÓN LLM ====================
# Opciones: 'openai', 'ollama', 'ninguno' (solo RAG sin generación)
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ninguno")

# OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# Ollama (local)
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama2")

# ==================== CONFIGURACIÓN RAG ====================
VECTOR_DB_TYPE = "chromadb"  # Futuro: "milvus", "pinecone"
EMBEDDINGS_MODEL = "all-MiniLM-L6-v2"  # sentence-transformers
K_RETRIEVAL = 3  # Número de documentos a recuperar

# ==================== CONFIGURACIÓN DE DATOS ====================
DATA_PATH = "properties.csv"
VECTOR_STORE_PATH = "./data/vector_store"

# ==================== CONFIGURACIÓN DE APIs EXTERNAS ====================
# Para Fase 3: Tool Use
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "")
MERCADO_LIBRE_API_KEY = os.getenv("MERCADO_LIBRE_API_KEY", "")

# ==================== LOGGING ====================
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# ==================== PROMPTS SISTEMA ====================
SYSTEM_PROMPT = """Eres un asistente inmobiliario inteligente especializado en recomendaciones de propiedades.

Tu rol:
- Recibir consultas de usuarios sobre propiedades deseadas
- Analizar las propiedades recuperadas de la base de datos
- Explicar por qué cada propiedad es adecuada para el usuario
- Ser claro, conciso y amigable

Instrucciones:
- Si no hay propiedades relevantes, sugiere modificar los criterios de búsqueda
- Siempre explica el "por qué" de tus recomendaciones
- Destaca amenities y características que coincidan con la preferencia del usuario
- Máximo 300 palabras por respuesta
"""

RETRIEVAL_PROMPT_TEMPLATE = """Basándote en las siguientes propiedades recuperadas y el perfil del usuario, 
genera una recomendación personalizada explicando por qué cada propiedad es adecuada:

Perfil del Usuario: {user_profile}

Propiedades Encontradas:
{properties_context}

Recomendación:"""
