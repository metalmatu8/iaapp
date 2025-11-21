@echo off
REM run_scheduler.bat - Ejecutar task scheduler en background (Windows)
REM Uso: run_scheduler.bat

echo =======================================
echo  Task Scheduler - Scraping Automatico
echo =======================================
echo.

REM Verificar que Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no está instalado o no está en PATH
    pause
    exit /b 1
)

REM Cambiar al directorio actual
cd /d "%~dp0"

echo Iniciando Task Scheduler...
echo Log guardado en: scheduler.log
echo.
echo Para detener el scheduler, presiona Ctrl+C
echo.

REM Ejecutar el scheduler
python task_scheduler.py

REM Si se cierra, mostrar mensaje
echo.
echo Task Scheduler detenido
pause
