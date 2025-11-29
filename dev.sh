#!/bin/bash
# Script para iniciar desarrollo rápido en Linux/Mac

echo "🚀 Iniciando IAApp en modo desarrollo..."

# Activar entorno virtual
if [ -d ".venv" ]; then
    source .venv/bin/activate
else
    echo "⚠️  Entorno virtual no encontrado. Creando..."
    python -m venv .venv
    source .venv/bin/activate
fi

# Instalar dependencias si no existen
if ! python -c "import streamlit" 2>/dev/null; then
    echo "📦 Instalando dependencias..."
    pip install -r requirements.txt
fi

# Ejecutar la app
echo "✅ Iniciando Streamlit..."
streamlit run src/app.py
