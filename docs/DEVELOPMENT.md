# 🚀 Guía de Desarrollo - Roadmap y Próximas Fases

## Introducción

Este documento describe cómo extender el Agente RAG Inmobiliario de MVP (Fase 1) a un producto robusto en producción (Fases 2-4).

---

## Fase 2: Enriquecimiento de Datos y Multimodalidad (Q1 2025)

### 2.1 RAG Multimodal con Imágenes

**Objetivo**: Permitir búsquedas como "Cocinas con isla de mármol" analizando fotos de propiedades.

**Implementación**:

```python
# vision_integration.py
from PIL import Image
import clip
import torch

class VisionRAG:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model, self.preprocess = clip.load("ViT-B/32", device=self.device)
    
    def extraer_caracteristicas_imagen(self, ruta_imagen):
        """Genera embedding de imagen con CLIP"""
        image = Image.open(ruta_imagen)
        image_input = self.preprocess(image).unsqueeze(0).to(self.device)
        
        with torch.no_grad():
            image_features = self.model.encode_image(image_input)
        
        return image_features
    
    def buscar_por_descripcion_visual(self, query, propiedades):
        """Busca propiedades por descripción visual"""
        text = clip.tokenize([query]).to(self.device)
        
        with torch.no_grad():
            text_features = self.model.encode_text(text)
        
        # Calcular similitud con cada imagen
        # ...
        return propiedades_ordenadas
```

**Pasos**:
1. Instalar `pip install open-clip-torch pillow`
2. Descargar imágenes de propiedades
3. Generar embeddings CLIP para cada imagen
4. Indexar en ChromaDB con metadatos de imagen
5. Modificar `buscar_propiedades()` para incluir búsqueda visual

**Recursos**:
- CLIP Paper: https://arxiv.org/abs/2103.14030
- OpenAI CLIP: https://github.com/openai/CLIP

---

### 2.2 Scraping Automatizado

**Objetivo**: Mantener dataset actualizado desde portales inmobiliarios.

**Opción A: Selenium (para sitios con JavaScript)**

```python
# scrapers/zonaprop_scraper.py
from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd

class ZonapropScraper:
    def __init__(self):
        self.driver = webdriver.Chrome()
    
    def scraper_propiedades(self, criterios):
        """
        Scrapeа propiedades de Zonaprop
        
        criterios: {
            "zona": "Palermo",
            "tipo": "Casa",
            "precio_min": 200000,
            "precio_max": 500000
        }
        """
        url = self._construir_url(criterios)
        self.driver.get(url)
        
        propiedades = []
        elementos = self.driver.find_elements(By.CLASS_NAME, "property-card")
        
        for elem in elementos:
            prop = {
                "tipo": elem.find_element(By.CLASS_NAME, "prop-type").text,
                "zona": elem.find_element(By.CLASS_NAME, "prop-zone").text,
                "precio": int(elem.find_element(By.CLASS_NAME, "prop-price").text.replace("$", "")),
                "descripcion": elem.find_element(By.CLASS_NAME, "prop-desc").text,
                "url": elem.find_element(By.TAG_NAME, "a").get_attribute("href"),
                # ...
            }
            propiedades.append(prop)
        
        return pd.DataFrame(propiedades)
    
    def _construir_url(self, criterios):
        # Construir URL según filtros
        pass

# Uso
scraper = ZonapropScraper()
df = scraper.scraper_propiedades({"zona": "Palermo"})
df.to_csv("propiedades_actualizado.csv")
```

**Opción B: Requests + BeautifulSoup (APIs públicas)**

```python
# scrapers/mercadolibre_scraper.py
import requests
from bs4 import BeautifulSoup

class MercadoLibreScraper:
    def __init__(self):
        self.base_url = "https://api.mercadolibre.com/sites/MLA/search"
    
    def scraper_propiedades(self, query):
        """Scrapeа de MercadoLibre Inmuebles API"""
        params = {
            "q": query,
            "category": "MLA1459",  # Inmuebles
            "limit": 50
        }
        
        response = requests.get(self.base_url, params=params)
        datos = response.json()
        
        propiedades = []
        for item in datos['results']:
            prop = {
                "id": item['id'],
                "titulo": item['title'],
                "precio": item['price'],
                "url": item['permalink'],
                # ...
            }
            propiedades.append(prop)
        
        return pd.DataFrame(propiedades)
```

**Scheduler (ejecutar cada 6 horas)**:

```python
# scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
from scrapers.zonaprop_scraper import ZonapropScraper

scheduler = BackgroundScheduler()

def actualizar_dataset():
    scraper = ZonapropScraper()
    df = scraper.scraper_propiedades({"zona": "Palermo"})
    df.to_csv("properties.csv", mode='a', header=False)  # Append
    print(f"Dataset actualizado: {len(df)} propiedades nuevas")

scheduler.add_job(actualizar_dataset, 'interval', hours=6)
scheduler.start()
```

---

### 2.3 Base de Datos Relacional

**Migración de CSV → PostgreSQL**

```python
# database.py
import sqlalchemy as sa
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, Text
from sqlalchemy.orm import declarative_base, Session
from datetime import datetime

Base = declarative_base()

class Propiedad(Base):
    __tablename__ = "propiedades"
    
    id = Column(Integer, primary_key=True)
    tipo = Column(String(50))
    zona = Column(String(100))
    precio = Column(Float)
    habitaciones = Column(Integer)
    baños = Column(Integer)
    pileta = Column(Boolean)
    metros_cubiertos = Column(Float)
    metros_descubiertos = Column(Float)
    descripcion = Column(Text)
    amenities = Column(Text)
    latitud = Column(Float)
    longitud = Column(Float)
    url = Column(String(500))
    imagen_url = Column(String(500))
    embedding = Column(sa.LargeBinary)  # Vector binario
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Crear tabla
engine = create_engine("postgresql://user:password@localhost/iaapp_db")
Base.metadata.create_all(engine)

# Usar
session = Session(engine)
props = session.query(Propiedad).filter(Propiedad.zona == "Palermo").all()
```

**Ventajas**:
- Escalabilidad (millones de registros)
- Transacciones ACID
- Búsquedas complejas con SQL
- Integración con pgvector para similitud

---

## Fase 3: Agentes Autónomos y Tool Use (Q2 2025)

### 3.1 Arquitectura Multi-Agente con LangChain

```python
# agents.py
from langchain.agents import Tool, initialize_agent, AgentType
from langchain.chat_models import ChatOpenAI
from llm_integration import generar_recomendacion

# Definir herramientas
tools = [
    Tool(
        name="Search Properties",
        func=lambda query: buscar_propiedades(query),
        description="Busca propiedades inmobiliarias por criterios"
    ),
    Tool(
        name="Calculate Travel Time",
        func=lambda origin, dest: calcular_distancia(origin, dest),
        description="Calcula tiempo de viaje entre dos ubicaciones"
    ),
    Tool(
        name="Find Schools",
        func=lambda location: buscar_colegios(location),
        description="Encuentra colegios cercanos a una ubicación"
    ),
    Tool(
        name="Check Safety",
        func=lambda zone: verificar_seguridad(zone),
        description="Verifica índice de seguridad de una zona"
    )
]

# Inicializar agente
llm = ChatOpenAI(model_name="gpt-4", temperature=0)
agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.OPENAI_FUNCTIONS,
    verbose=True,
    max_iterations=10
)

# Ejecutar
respuesta = agent.run("""
    Busca casas en Palermo, verifica tiempo de viaje al trabajo (Av. Santa Fe 3000),
    busca colegios cercanos y verifica seguridad de la zona.
""")
```

**Flujo**:
1. Usuario hace pregunta compleja
2. Agente decide qué herramientas usar
3. Ejecuta herramientas en secuencia
4. Sintetiza respuesta final

---

### 3.2 Tool Use / Function Calling

**Con OpenAI Function Calling API**:

```python
# function_calling.py
from openai import OpenAI

client = OpenAI()

# Definir funciones disponibles
tools = [
    {
        "type": "function",
        "function": {
            "name": "search_properties",
            "description": "Busca propiedades según criterios",
            "parameters": {
                "type": "object",
                "properties": {
                    "zona": {"type": "string"},
                    "precio_max": {"type": "number"},
                    "habitaciones": {"type": "integer"}
                },
                "required": ["zona"]
            }
        }
    },
    # Más funciones...
]

# LLM decide automáticamente qué función usar
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Busca casas en Palermo"}],
    tools=tools,
    tool_choice="auto"
)

# Parsear respuesta
if response.choices[0].message.tool_calls:
    for tool_call in response.choices[0].message.tool_calls:
        tool_name = tool_call.function.name
        tool_args = json.loads(tool_call.function.arguments)
        
        # Ejecutar función
        if tool_name == "search_properties":
            resultado = search_properties(**tool_args)
```

---

## Fase 4: Experiencia de Usuario y Despliegue (Q3 2025)

### 4.1 API REST con FastAPI

```python
# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import uvicorn

app = FastAPI(title="Agente RAG Inmobiliario API")

class BusquedaRequest(BaseModel):
    perfil_usuario: str
    zona: Optional[str] = None
    precio_max: Optional[float] = None
    habitaciones_min: Optional[int] = None

class PropiedadResponse(BaseModel):
    id: int
    tipo: str
    zona: str
    precio: float
    descripcion: str
    url: str

@app.post("/api/buscar", response_model=List[PropiedadResponse])
async def buscar(request: BusquedaRequest):
    """Endpoint para búsqueda de propiedades"""
    try:
        propiedades, error = buscar_propiedades(
            request.perfil_usuario,
            request.zona,
            request.precio_max,
            request.habitaciones_min
        )
        if error:
            raise HTTPException(status_code=400, detail=error)
        return propiedades
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/feedback")
async def registrar_feedback(propiedad_id: int, tipo: str):
    """Registra feedback de usuario"""
    # Guardar en DB para re-entrenamiento
    pass

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

**Ejecutar**:
```bash
pip install fastapi uvicorn
uvicorn main:app --reload
# Acceder a http://localhost:8000/docs para Swagger UI
```

---

### 4.2 Integración WhatsApp (Twilio)

```python
# whatsapp_integration.py
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
from flask import Flask, request

app = Flask(__name__)
twilio_client = Client("account_sid", "auth_token")

@app.route("/whatsapp", methods=['POST'])
def whatsapp_webhook():
    """Webhook para WhatsApp Business API"""
    
    incoming_msg = request.form.get('Body')
    sender = request.form.get('From')
    
    # Procesar con RAG
    propiedades, error = buscar_propiedades(incoming_msg)
    
    # Generar respuesta
    if error:
        respuesta = error
    else:
        respuesta = f"Encontré {len(propiedades)} propiedades:\n"
        for prop in propiedades:
            respuesta += f"• {prop['tipo']} en {prop['zona']} - USD {prop['precio']}\n"
    
    # Enviar respuesta
    resp = MessagingResponse()
    resp.message(respuesta)
    
    return str(resp)

if __name__ == "__main__":
    app.run(debug=False, port=5000)
```

**Flujo**:
1. Usuario envía mensaje WhatsApp
2. Twilio webhook recibe mensaje
3. Procesar con RAG
4. Enviar respuesta de vuelta

---

### 4.3 Docker y Kubernetes

**Dockerfile**:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

**docker-compose.yml**:

```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8501:8501"
    environment:
      - LLM_PROVIDER=ollama
      - OLLAMA_BASE_URL=http://ollama:11434
    depends_on:
      - ollama
      - postgres
  
  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama:/root/.ollama
  
  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=iaapp_db
      - POSTGRES_PASSWORD=password
    ports:
      - "5432:5432"
    volumes:
      - postgres:/var/lib/postgresql/data

volumes:
  ollama:
  postgres:
```

**Ejecutar**:
```bash
docker-compose up -d
```

---

### 4.4 Monitoring y Analytics

```python
# monitoring.py
from prometheus_client import Counter, Histogram, start_http_server
import logging

# Métricas
search_counter = Counter('searches_total', 'Total searches', ['zone'])
feedback_counter = Counter('feedbacks_total', 'Total feedbacks', ['type'])
latency_histogram = Histogram('search_latency_seconds', 'Search latency')

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

@latency_histogram.time()
def buscar_con_metricas(query):
    propiedades, error = buscar_propiedades(query)
    search_counter.labels(zone=query.get('zona')).inc()
    return propiedades, error

# Iniciar Prometheus
if __name__ == "__main__":
    start_http_server(8000)
    # Ahora métricas disponibles en http://localhost:8000
```

---

## Checklist de Implementación

### Fase 2
- [ ] Instalar CLIP y descargar modelo
- [ ] Integrar búsqueda visual en `app.py`
- [ ] Crear scrapers para Zonaprop/MercadoLibre
- [ ] Migrar a PostgreSQL
- [ ] Agregar pgvector para búsqueda semántica en BD

### Fase 3
- [ ] Integrar LangChain
- [ ] Implementar multi-agente
- [ ] Configurar function calling
- [ ] Tests de tool use

### Fase 4
- [ ] API FastAPI
- [ ] Integración Twilio WhatsApp
- [ ] Docker + Kubernetes
- [ ] Monitoring con Prometheus
- [ ] CI/CD con GitHub Actions

---

## Testing y Validación

```python
# tests/test_rag.py
import pytest
from app import buscar_propiedades

def test_busqueda_basica():
    props, error = buscar_propiedades("Casa en Palermo")
    assert error is None
    assert len(props) > 0

def test_filtrado_precio():
    props, error = buscar_propiedades(
        "Casa",
        precio_max=250000
    )
    assert all(p['precio'] <= 250000 for p in props)

def test_filtrado_zona():
    props, error = buscar_propiedades(
        "Casa",
        zona="Palermo"
    )
    assert all(p['zona'] == "Palermo" for p in props)

# Ejecutar tests
pytest tests/
```

---

**Próxima revisión**: Q1 2025
