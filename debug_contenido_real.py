#!/usr/bin/env python3
"""Debug - inspeccionar qué descripciones reales podemos extraer."""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time

def debug_argenprop():
    print("="*60)
    print("ARGENPROP - Inspeccionando contenido de tarjeta")
    print("="*60)
    
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
    
    driver.get("https://www.argenprop.com/departamentos/venta/palermo")
    time.sleep(5)
    
    # Obtener primera tarjeta
    cards = driver.find_elements(By.CSS_SELECTOR, ".card")
    if cards:
        card = cards[0]
        print(f"\nPrimera tarjeta encontrada")
        print(f"HTML completo (primeros 2000 chars):")
        html = card.get_attribute("outerHTML")
        print(html[:2000])
        
        print(f"\n\nContenido .text:")
        print(repr(card.text))
        
        print(f"\n\nElementos internos:")
        # Buscar divs, spans, etc
        for tag in ["h2", "h3", "p", "span", "div"]:
            elements = card.find_elements(By.TAG_NAME, tag)
            for i, el in enumerate(elements[:3]):
                text = el.text.strip()
                if text:
                    print(f"  {tag}[{i}]: {text[:80]}")
    
    driver.quit()

def debug_buscadorprop():
    print("\n\n" + "="*60)
    print("BUSCADORPROP - Inspeccionando contenido de propiedad")
    print("="*60)
    
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
    
    driver.get("https://www.buscadorprop.com.ar/venta-palermo")
    time.sleep(8)
    
    # Obtener primer link de propiedad
    links = driver.find_elements(By.CSS_SELECTOR, "a[href*='/propiedad/']")
    if links:
        link = links[0]
        print(f"\nPrimer link encontrado: {link.get_attribute('href')}")
        
        # Obtener elemento padre
        parent = link
        for _ in range(5):
            parent = parent.find_element(By.XPATH, "..")
            if len(parent.text) > 50:
                break
        
        print(f"\nTexto del contenedor:")
        print(repr(parent.text[:500]))
        
        print(f"\n\nHTML del contenedor (primeros 2000 chars):")
        html = parent.get_attribute("outerHTML")
        print(html[:2000])
        
        print(f"\n\nElementos internos:")
        for tag in ["h2", "h3", "p", "span", "strong"]:
            elements = parent.find_elements(By.TAG_NAME, tag)
            for i, el in enumerate(elements[:3]):
                text = el.text.strip()
                if text:
                    print(f"  {tag}[{i}]: {text[:80]}")
    
    driver.quit()

if __name__ == "__main__":
    debug_argenprop()
    debug_buscadorprop()
