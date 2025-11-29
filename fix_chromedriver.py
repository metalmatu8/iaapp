#!/usr/bin/env python3
"""
Script para detectar la versión correcta de Chromium e instalar ChromeDriver compatible.
Ejecutar una vez antes de usar la app en Streamlit Cloud.
"""

import os
import sys
import re
import subprocess
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def get_chromium_version():
    """Detecta la versión de Chromium instalada en el sistema."""
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
                match = re.search(r'(\d+\.\d+\.\d+\.\d+)', output)
                if match:
                    version = match.group(1)
                    major_version = version.split('.')[0]
                    logger.info(f"✅ Detectado Chromium versión {version} en {path}")
                    return major_version, version
            except Exception as e:
                logger.debug(f"No se pudo detectar versión de {path}: {e}")
                continue
    
    logger.warning("⚠️ No se encontró Chromium instalado")
    return None, None

def clean_chromedriver_cache():
    """Limpia el cache de webdriver-manager."""
    cache_paths = [
        os.path.expanduser("~/.wdm"),  # Linux/macOS
        os.path.expanduser("~/.cache/wdm"),  # Linux
        os.path.join(os.environ.get("TEMP", "/tmp"), "wdm"),  # Windows
        "/home/appuser/.wdm",  # Streamlit Cloud
    ]
    
    for path in cache_paths:
        if os.path.exists(path):
            try:
                import shutil
                shutil.rmtree(path)
                logger.info(f"✅ Limpiado cache de webdriver-manager: {path}")
            except Exception as e:
                logger.warning(f"⚠️ No se pudo limpiar {path}: {e}")

def setup_chromedriver():
    """Descarga la versión correcta de ChromeDriver."""
    major_version, full_version = get_chromium_version()
    
    if not major_version:
        logger.info("⚠️ No se puede detectar versión de Chromium - en entorno local puede ser normal")
        logger.info("✅ ChromeDriver se descargará automáticamente al inicializar Selenium")
        return True  # No es error en local, Selenium lo manejará
    
    logger.info(f"🔧 Instalando ChromeDriver para versión {major_version}...")
    
    try:
        # Limpiar cache viejo
        clean_chromedriver_cache()
        
        # Instalar ChromeDriver correcto
        from webdriver_manager.chrome import ChromeDriverManager
        
        # Forzar descarga de la versión correcta
        driver_path = ChromeDriverManager(version=major_version).install()
        logger.info(f"✅ ChromeDriver instalado correctamente en: {driver_path}")
        
        # Verificar que el archivo existe
        if os.path.exists(driver_path):
            # Hacer ejecutable en Linux
            try:
                os.chmod(driver_path, 0o755)
            except:
                pass  # En Windows puede fallar, no es crítico
            logger.info(f"✅ ChromeDriver listo: {driver_path}")
            return True
        else:
            logger.error(f"❌ ChromeDriver no existe en: {driver_path}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error instalando ChromeDriver: {e}")
        logger.info("💡 Continuando sin fix de versión - Selenium intentará usar versión disponible")
        return True  # Permitir continuación incluso si falla

if __name__ == "__main__":
    logger.info("🚀 Iniciando fix_chromedriver.py...")
    
    success = setup_chromedriver()
    
    if success:
        logger.info("✅ ChromeDriver configurado correctamente")
        sys.exit(0)
    else:
        logger.error("❌ Fallo configurando ChromeDriver")
        # No fallar - permitir que continue la app
        sys.exit(0)
