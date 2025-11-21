#!/usr/bin/env python3
"""Debug - encontrar estructura real de propiedades en BuscadorProp."""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json

opts = Options()
opts.add_argument("--window-size=1920,1080")
opts.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0")

driver = None
try:
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium.webdriver.chrome.service import Service
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opts)
except:
    driver = webdriver.Chrome(options=opts)

url = "https://www.buscadorprop.com.ar/venta-palermo"
print(f"Cargando: {url}\n")

driver.get(url)

# Esperar loader
try:
    WebDriverWait(driver, 15).until(
        EC.invisibility_of_element_located((By.CSS_SELECTOR, ".loading-spinner"))
    )
except:
    time.sleep(8)

# Script para encontrar donde está la data
script = """
    // Buscar donde está el listado de propiedades
    const section = document.querySelector('section.listing');
    console.log('Sección encontrada:', section ? 'sí' : 'no');
    
    // Buscar todos los elementos con patrón propiedad
    const byLink = document.querySelectorAll('a[href*="-propiedad-"]');
    console.log('Links con "-propiedad-":', byLink.length);
    if (byLink.length > 0) {
        console.log('Primer link:', byLink[0].href);
        console.log('Parent:', byLink[0].parentElement.className);
    }
    
    // Buscar elementos que contengan precio
    const allDivs = document.querySelectorAll('div');
    let priceCount = 0;
    for (let div of allDivs) {
        if (div.textContent.match(/\$.*\d+/) || div.textContent.match(/USD/)) {
            priceCount++;
            if (priceCount === 1) {
                console.log('Div con precio:', div.className, div.textContent.substring(0, 100));
            }
        }
    }
    console.log('Divs con precio:', priceCount);
    
    // Buscar elementos con data-attributes
    const withData = document.querySelectorAll('[data-*]');
    console.log('Elementos con data-*:', withData.length);
    
    return 'Script ejecutado';
"""

try:
    result = driver.execute_script(script)
    print(result)
except Exception as e:
    print(f"Error: {e}")

# Obtener el HTML de la sección de listado
print("\n=== HTML DE SECCIÓN LISTING ===")
try:
    section = driver.find_element(By.CSS_SELECTOR, "section.listing")
    html = section.get_attribute("outerHTML")
    # Buscar primeros links con href 
    import re
    links = re.findall(r'href="([^"]*propiedad[^"]*)"', html)
    print(f"Found {len(links)} property links")
    if links:
        for link in links[:3]:
            print(f"  - {link}")
except Exception as e:
    print(f"Error: {e}")

driver.quit()
