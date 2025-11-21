#!/usr/bin/env python3
"""Debug script to inspect Argenprop and BuscadorProp HTML structure."""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time

def inspect_argenprop():
    """Inspect Argenprop HTML structure."""
    print("=" * 60)
    print("INSPECTING ARGENPROP")
    print("=" * 60)
    
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
    
    # Probar URL correcta según usuario
    url = "https://www.argenprop.com/departamentos/alquiler/palermo"
    print(f"Cargando: {url}\n")
    
    driver.get(url)
    time.sleep(5)  # Esperar a que cargue
    
    # Buscar diferentes selectores
    selectors = [
        ("article", "article"),
        ("[data-qa='listing-item']", "[data-qa='listing-item']"),
        (".card", ".card"),
        ("div[class*='property']", "div[class*='property']"),
        ("div[class*='listing']", "div[class*='listing']"),
        ("div[data-id]", "div[data-id]"),
    ]
    
    for name, selector in selectors:
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            print(f"✓ {name}: {len(elements)} elementos encontrados")
            if elements and len(elements) > 0:
                print(f"  Primer elemento HTML (primeros 200 chars):")
                print(f"  {elements[0].get_attribute('outerHTML')[:200]}...\n")
        except:
            print(f"✗ {name}: No encontrado\n")
    
    # Mostrar título y URL actual
    print(f"Título de página: {driver.title}")
    print(f"URL actual: {driver.current_url}")
    
    driver.quit()

def inspect_buscadorprop():
    """Inspect BuscadorProp HTML structure."""
    print("\n" + "=" * 60)
    print("INSPECTING BUSCADORPROP")
    print("=" * 60)
    
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
    
    # URL correcta según usuario
    url = "https://www.buscadorprop.com.ar/casas-venta-lomas-de-zamora-temperley"
    print(f"Cargando: {url}\n")
    
    driver.get(url)
    time.sleep(5)  # Esperar a que cargue
    
    # Buscar diferentes selectores
    selectors = [
        ("article", "article"),
        (".property", ".property"),
        ("[class*='property']", "[class*='property']"),
        (".card", ".card"),
        ("div[data-qa]", "div[data-qa]"),
        (".listing", ".listing"),
    ]
    
    for name, selector in selectors:
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            print(f"✓ {name}: {len(elements)} elementos encontrados")
            if elements and len(elements) > 0:
                print(f"  Primer elemento HTML (primeros 200 chars):")
                print(f"  {elements[0].get_attribute('outerHTML')[:200]}...\n")
        except:
            print(f"✗ {name}: No encontrado\n")
    
    # Mostrar título y URL actual
    print(f"Título de página: {driver.title}")
    print(f"URL actual: {driver.current_url}")
    
    driver.quit()

if __name__ == "__main__":
    inspect_argenprop()
    inspect_buscadorprop()
    print("\n" + "=" * 60)
    print("DEBUG COMPLETE")
    print("=" * 60)
