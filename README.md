# Agente RAG Inmobiliario

Este proyecto es un agente conversacional de recomendación inmobiliaria basado en IA, que utiliza la arquitectura RAG (Retrieval-Augmented Generation) para sugerir propiedades a familias según sus preferencias y perfil. Es 100% gratuito, de código abierto y fácil de usar, incluso para personas sin experiencia en programación.

## ¿Qué hace esta aplicación?
- Recibe una descripción de la familia y sus preferencias (zona, presupuesto, habitaciones, etc.).
- Busca en una base de datos de propiedades (CSV) usando búsqueda semántica y filtros.
- Devuelve las 3 mejores opciones explicadas en lenguaje natural.
- Interfaz web simple y amigable (Streamlit).

## Tecnologías utilizadas
- **Python 3.10+**
- **pandas**: manejo de datos
- **sentence-transformers**: generación de embeddings semánticos (modelo open-source)
- **chromadb**: vector store local para búsqueda semántica
- **streamlit**: interfaz web simple y gratuita

## Estructura del proyecto
```
├── app.py              # Código principal de la aplicación
├── properties.csv      # Base de datos de propiedades de ejemplo
└── README.md           # Este archivo
```

## Cómo instalar y ejecutar
1. **Clona este repositorio**
   ```
   git clone https://github.com/tuusuario/iaapp.git
   cd iaapp
   ```
2. **Crea un entorno virtual (opcional pero recomendado)**
   ```
   python -m venv .venv
   # En Windows:
   .venv\Scripts\activate
   # En Mac/Linux:
   source .venv/bin/activate
   ```
3. **Instala las dependencias**
   ```
   pip install -r requirements.txt
   # O instala manualmente:
   pip install pandas chromadb sentence-transformers streamlit
   ```
4. **Ejecuta la aplicación**
   ```
   streamlit run app.py
   ```
5. **Abre tu navegador** en la dirección que te indica Streamlit (por defecto http://localhost:8501)

## Cómo usar
1. Escribe una descripción de tu familia y preferencias en el campo de texto (ejemplo: `2 adultos, 2 niños, Palermo, pileta, 3 habitaciones, max 200000`).
2. Haz clic en "Buscar".
3. Verás las 3 propiedades más relevantes, con detalles y explicación.

## Personalización
- Puedes editar el archivo `properties.csv` para agregar, quitar o modificar propiedades.
- El modelo semántico es open-source y no requiere licencias.
- Si quieres agregar más filtros o mejorar la lógica, edita `app.py`.

## Ejemplo de entrada y salida
**Entrada:**
```
Familia: 2 adultos, 2 niños, buscan casa en Palermo, pileta, 3 habitaciones, max 250000
```
**Salida:**
- Casa en Palermo, 3 habitaciones, pileta, USD 250000, descripción y link.
- ...

## ¿Cómo funciona internamente?
1. Carga el CSV de propiedades y genera un texto descriptivo para cada una.
2. Usa `sentence-transformers` para crear embeddings semánticos de cada propiedad.
3. Al recibir una consulta, genera el embedding de la preferencia y busca las propiedades más similares en ChromaDB.
4. Muestra las 3 mejores opciones en la web.

## Requisitos mínimos
- Python 3.10 o superior
- 2GB RAM (recomendado)
- No requiere GPU ni servicios pagos

## Créditos y Licencia
- Inspirado en la arquitectura RAG y en proyectos de IA open-source.
- Licencia MIT: puedes usar, modificar y compartir libremente.

---

¿Dudas o sugerencias? Abre un issue o contacta al autor.
