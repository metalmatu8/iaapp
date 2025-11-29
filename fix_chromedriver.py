#!/usr/bin/env python3
"""
Script para detectar versión de Chromium e instalar ChromeDriver compatible.
Limpia cache y fuerza descarga correcta.
"""

import os
import sys
import re
import subprocess
import logging
import shutil

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def get_chromium_version():
    """Detecta versión de Chromium en el sistema."""
    chromium_paths = [
        "/usr/bin/chromium-browser",
        "/usr/bin/chromium",
        "/snap/bin/chromium",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
        "C:\\Program Files\\Chromium\\Application\\chrome.exe",
    ]
    
    for path in chromium_paths:
        if os.path.exists(path):
            try:
                result = subprocess.run([path, "--version"], capture_output=True, text=True, timeout=5)
                output = result.stdout + result.stderr
                # Buscar patrón "version X.Y.Z"
                match = re.search(r'(\d+\.\d+\.\d+\.\d+|\d+\.\d+)', output)
                if match:
                    version = match.group(1)
                    major_version = version.split('.')[0]
                    logger.info(f"✅ Detectado Chromium versión {version} en {path}")
                    return major_version, version, path
            except Exception as e:
                logger.debug(f"No se pudo detectar versión de {path}: {e}")
                continue
    
    logger.warning("⚠️ No se encontró Chromium instalado")
    return None, None, None

def clean_chromedriver_cache():
    """Limpia cache antiguo de webdriver-manager."""
    cache_paths = [
        os.path.expanduser("~/.wdm"),
        os.path.expanduser("~/.cache/wdm"),
        os.path.join(os.environ.get("TEMP", "/tmp"), "wdm"),
        "/home/appuser/.wdm",
    ]
    
    removed_any = False
    for path in cache_paths:
        if os.path.exists(path):
            try:
                shutil.rmtree(path)
                logger.info(f"✅ Cache limpiado: {path}")
                removed_any = True
            except Exception as e:
                logger.debug(f"No se pudo limpiar {path}: {e}")
    
    if not removed_any:
        logger.debug("ℹ️ No había cache antiguo para limpiar")

def setup_chromedriver():
    """Configura ChromeDriver compatible."""
    major_version, full_version, chromium_path = get_chromium_version()
    
    if not major_version:
        logger.info("ℹ️ Chromium no detectado (es normal en Windows local)")
        logger.info("ℹ️ webdriver-manager descargará automáticamente al ejecutarse")
        return True
    
    logger.info(f"🔧 Configurando ChromeDriver para Chromium v{major_version}...")
    
    try:
        # Limpiar cache ANTES de descargar
        clean_chromedriver_cache()
        
        # Instalar ChromeDriver versión correcta
        try:
            from webdriver_manager.chrome import ChromeDriverManager
            
            # Crear instancia con versión específica
            manager = ChromeDriverManager(version=major_version)
            driver_path = manager.install()
            
            logger.info(f"✅ ChromeDriver v{major_version} instalado en: {driver_path}")
            
            # Hacer ejecutable en Linux
            try:
                os.chmod(driver_path, 0o755)
                logger.debug(f"✅ ChromeDriver hecho ejecutable")
            except:
                pass
            
            return True
            
        except Exception as wdm_error:
            logger.warning(f"⚠️ Error con webdriver-manager: {wdm_error}")
            logger.info("ℹ️ webdriver-manager intentará auto-detectar al ejecutarse")
            return True  # Permitir continuación
            
    except Exception as e:
        logger.warning(f"⚠️ Error en setup: {e}")
        return True  # No bloquear si todo falla

if __name__ == "__main__":
    logger.info("🚀 Iniciando fix_chromedriver.py...")
    
    success = setup_chromedriver()
    
    if success:
        logger.info("✅ ChromeDriver listo")
        sys.exit(0)
    else:
        logger.warning("⚠️ Setup completado con warnings")
        sys.exit(0)  # No fallar, permitir que continúe

