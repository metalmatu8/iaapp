#!/bin/bash
# Script de setup para Streamlit Cloud
# Se ejecuta automáticamente al iniciar la app

echo "🚀 Iniciando setup de Streamlit Cloud..."

# Detectar Chromium
echo "🔍 Detectando Chromium..."
if command -v chromium &> /dev/null; then
    CHROMIUM_VERSION=$(chromium --version 2>/dev/null || echo "unknown")
    echo "✅ Encontrado Chromium: $CHROMIUM_VERSION"
else
    echo "⚠️ Chromium no encontrado en PATH"
fi

# Limpiar cache de webdriver-manager si existe
echo "🧹 Limpiando cache de webdriver-manager..."
rm -rf ~/.wdm 2>/dev/null || true
rm -rf ~/.cache/wdm 2>/dev/null || true

echo "✅ Setup completado"
