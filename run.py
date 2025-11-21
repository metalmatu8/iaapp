#!/usr/bin/env python3
"""
CÓMO EJECUTAR LA APLICACIÓN

Este proyecto usa Streamlit y está organizado en carpetas.

╔════════════════════════════════════════════════════════════════╗
║                    FORMAS DE EJECUTAR                         ║
╚════════════════════════════════════════════════════════════════╝

1️⃣  RECOMENDADO - Scripts de desarrollo rápido:
   Windows:  dev.bat
   Linux:    bash dev.sh

2️⃣  Desde el directorio src/:
   cd src
   streamlit run app.py

3️⃣  Desde la raíz (requiere estar en src/):
   streamlit run src/app.py

╔════════════════════════════════════════════════════════════════╗
║                     ESTRUCTURA DEL PROYECTO                   ║
╚════════════════════════════════════════════════════════════════╝

iaapp/
├── src/                # Código fuente (app.py, scrapers.py, etc.)
├── data/               # Base de datos y datos
├── tests/              # Tests
├── docs/               # Documentación
├── archive/            # Scripts antiguos
├── dev.bat / dev.sh    # Scripts de desarrollo
└── README.md           # Documentación completa

Para más información, lee: README.md o STRUCTURE.md

═══════════════════════════════════════════════════════════════════

Este archivo es solo una guía. Para ejecutar, usa uno de los
métodos descritos arriba.
"""

if __name__ == "__main__":
    import sys
    print(__doc__)
    sys.exit(0)

