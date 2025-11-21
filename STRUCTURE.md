# 🏗️ Estructura del Proyecto

El proyecto está organizado en carpetas de forma profesional:

```
iaapp/
├── src/                          # 📝 Código fuente principal
│   ├── app.py                   # Aplicación principal Streamlit
│   ├── scrapers.py              # Scrapers (Argenprop, BuscadorProp, Georef, BD)
│   ├── config.py                # Configuración
│   └── tools.py                 # Utilidades
│
├── data/                         # 💾 Base de datos y datos
│   ├── properties.db            # Base de datos SQLite
│   ├── properties_expanded.csv   # Datos exportados a CSV
│   └── chroma_data/             # Vector store (ChromaDB)
│
├── tests/                        # ✅ Tests y validación
│   └── test_*.py                # Tests unitarios
│
├── docs/                         # 📚 Documentación
│   ├── README.md
│   ├── ARCHITECTURE_v2_3.md
│   └── *.md                      # Otros documentos
│
├── archive/                      # 🗂️ Archivos antiguos
│   ├── debug_*.py               # Scripts de debug
│   ├── *backup*.py              # Backups antiguos
│   └── *.py                      # Otros scripts legacy
│
├── run.py                        # 🚀 Punto de entrada
├── requirements.txt              # 📦 Dependencias
└── README.md                     # Documentación principal
```

## 🚀 Cómo Ejecutar

### Desde la raíz del proyecto:
```bash
# Opción 1: Usando el archivo run.py
streamlit run run.py

# Opción 2: Desde la carpeta src
cd src
streamlit run app.py
```

### Instalación de dependencias:
```bash
pip install -r requirements.txt
```

## 📁 Descripción de Carpetas

### `src/` - Código Fuente
- **app.py**: Aplicación principal de Streamlit
  - UI con búsqueda RAG
  - Descarga de propiedades
  - Gestión de BD
  
- **scrapers.py**: Módulo de scraping
  - `ArgenpropScraper`: Scraping de Argenprop
  - `BuscadorPropScraper`: Scraping de BuscadorProp
  - `GeorefAPI`: Integración con API Georef
  - `PropertyDatabase`: Gestión de BD SQLite

- **config.py**: Configuración del proyecto
  - Variables de entorno
  - Constantes

- **tools.py**: Utilidades
  - Funciones auxiliares
  - Helpers

### `data/` - Base de Datos
- **properties.db**: Base de datos SQLite con propiedades
- **properties_expanded.csv**: Exportación de propiedades a CSV
- **chroma_data/**: Vector store con embeddings

### `tests/` - Tests
- Tests unitarios de funcionalidad
- Validación de scrapers
- Tests de búsqueda RAG

### `docs/` - Documentación
- Documentación del proyecto
- Guías de uso
- Especificaciones técnicas

### `archive/` - Histórico
- Scripts de debug
- Versiones antiguas
- Backups

## 🔧 Configuración

Las rutas están configuradas para funcionar desde `src/`:
- Base de datos: `../data/properties.db`
- ChromaDB: `../data/chroma_data`
- CSV: `../data/properties_expanded.csv`

## 📝 Notas

- Todos los imports internos usan rutas relativas
- El archivo `run.py` facilita ejecutar desde la raíz
- Los datos se guardan en la carpeta `data/` para separar datos del código
