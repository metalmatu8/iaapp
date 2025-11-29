#!/usr/bin/env python3
"""
task_scheduler.py - Ejecutor de tareas programadas para scraping automático
Ejecuta las tareas configuradas en scheduled_tasks.json
"""

import json
import os
import logging
from datetime import datetime, time as dt_time
import time
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class TaskScheduler:
    """Ejecuta tareas programadas de scraping"""
    
    def __init__(self, config_file="scheduled_tasks.json"):
        self.config_file = config_file
        self.running = True
        self.tasks = self.cargar_tareas()
    
    def cargar_tareas(self):
        """Carga las tareas desde el archivo JSON"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    tareas = json.load(f)
                logger.info(f"✅ Cargadas {len(tareas)} tareas")
                return tareas
            else:
                logger.info("No hay tareas configuradas")
                return []
        except Exception as e:
            logger.error(f"Error cargando tareas: {e}")
            return []
    
    def ejecutar_tarea(self, tarea):
        """Ejecuta una tarea de scraping"""
        try:
            logger.info(f"🚀 Ejecutando tarea: {tarea['zona']} @ {tarea['hora']}")
            
            from scrapers import ArgenpropScraper, BuscadorPropScraper, PropertyDatabase
            
            db = PropertyDatabase()
            
            # Obtener scraper
            if tarea['portal'] == 'Argenprop':
                props = ArgenpropScraper.buscar_propiedades(
                    zona=tarea['zona'],
                    tipo=tarea['tipo'],
                    limit=tarea['props'],
                    debug=False
                )
            else:  # BuscadorProp
                props = BuscadorPropScraper.buscar_propiedades(
                    zona=tarea['zona'],
                    tipo=tarea['tipo'].lower(),
                    limit=tarea['props'],
                    debug=False
                )
            
            # Agregar a BD
            nuevas = db.agregar_propiedades(props)
            db.guardar_csv("properties_expanded.csv")
            
            logger.info(f"✅ Tarea completada: {nuevas} propiedades agregadas")
            
            # Regenerar ChromaDB
            try:
                from regenerar_chromadb import regenerar_chroma
                regenerar_chroma()
                logger.info("✅ ChromaDB regenerado")
            except Exception as e:
                logger.warning(f"No se pudo regenerar ChromaDB: {e}")
            
            return True
        
        except Exception as e:
            logger.error(f"❌ Error ejecutando tarea: {e}")
            return False
    
    def verificar_tareas_pendientes(self):
        """Verifica si hay tareas que ejecutar"""
        ahora = datetime.now()
        hora_actual = ahora.strftime("%H:%M")
        
        for tarea in self.tasks:
            if not tarea.get('habilitada', True):
                continue
            
            hora_tarea = tarea.get('hora', '00:00')
            
            # Comparar horas (formato HH:MM)
            if hora_tarea == hora_actual:
                logger.info(f"⏰ Hora de ejecutar tarea: {tarea['zona']}")
                self.ejecutar_tarea(tarea)
                
                # Esperar para evitar ejecutar múltiples veces en el mismo minuto
                time.sleep(61)
    
    def iniciar_scheduler(self, intervalo_verificacion=30):
        """Inicia el loop del scheduler"""
        logger.info(f"🚀 Scheduler iniciado. Verificando cada {intervalo_verificacion} segundos")
        
        try:
            while self.running:
                # Recargar tareas cada iteración
                self.tasks = self.cargar_tareas()
                self.verificar_tareas_pendientes()
                time.sleep(intervalo_verificacion)
        
        except KeyboardInterrupt:
            logger.info("⏹️ Scheduler detenido por usuario")
        except Exception as e:
            logger.error(f"❌ Error en scheduler: {e}")
        finally:
            self.running = False
            logger.info("Scheduler finalizado")


def main():
    """Función principal"""
    scheduler = TaskScheduler()
    scheduler.iniciar_scheduler(intervalo_verificacion=30)


if __name__ == "__main__":
    main()
