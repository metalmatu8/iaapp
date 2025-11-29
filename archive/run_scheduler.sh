#!/bin/bash
# run_scheduler.sh - Ejecutar task scheduler en background (Linux/Mac)
# Uso: ./run_scheduler.sh

echo "======================================="
echo "  Task Scheduler - Scraping Automatico"
echo "======================================="
echo ""

# Verificar que Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python3 no está instalado"
    exit 1
fi

# Cambiar al directorio del script
cd "$(dirname "$0")"

echo "Iniciando Task Scheduler..."
echo "Log guardado en: scheduler.log"
echo ""
echo "Para detener el scheduler, presiona Ctrl+C"
echo ""

# Ejecutar el scheduler
python3 task_scheduler.py

# Si se cierra, mostrar mensaje
echo ""
echo "Task Scheduler detenido"
