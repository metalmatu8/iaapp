@echo off
REM Script para iniciar desarrollo rápido en Windows

echo.
echo 🚀 Iniciando IAApp en modo desarrollo...
echo.

REM Activar entorno virtual
if exist ".venv" (
    call .venv\Scripts\activate.bat
) else (
    echo ⚠️  Entorno virtual no encontrado. Creando...
    python -m venv .venv
    call .venv\Scripts\activate.bat
)

REM Instalar dependencias si no existen
python -c "import streamlit" >nul 2>&1
if errorlevel 1 (
    echo 📦 Instalando dependencias...
    pip install -r requirements.txt
)

REM Ejecutar la app
echo.
echo ✅ Iniciando Streamlit...
echo.
streamlit run src/app.py
