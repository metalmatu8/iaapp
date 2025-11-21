#!/usr/bin/env python3
"""Debug BuscadorProp - buscar estructura real de propiedades."""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
import time

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

url = "https://www.buscadorprop.com.ar/casas-venta-lomas-de-zamora-temperley"
print(f"Cargando URL de usuario: {url}\n")

driver.get(url)
time.sleep(8)

# Buscar cualquier elemento con texto que parezca propiedad
print("Buscando divs con clases 'listing' o 'item':")
all_divs = driver.find_elements(By.CSS_SELECTOR, "div")
print(f"Total divs: {len(all_divs)}")

# Buscar por data attributes
print("\nBuscando elementos con data-attributes:")
elements = driver.find_elements(By.CSS_SELECTOR, "[data-id], [data-item], [data-property]")
print(f"Con data-* attributes: {len(elements)}")

# Buscar por clase listing
print("\nBuscando por clase 'listing':")
listing_divs = driver.find_elements(By.CSS_SELECTOR, "div[class*='listing']")
print(f"divs con 'listing' en clase: {len(listing_divs)}")
if listing_divs:
    print(f"1er listing HTML (primeros 500 chars):")
    print(listing_divs[0].get_attribute("outerHTML")[:500])

# Buscar sección principal
print("\nBuscando sección principal de listado:")
section = driver.find_element(By.CSS_SELECTOR, "section.listing")
print(f"Sección encontrada: {section is not None}")
print(f"Sección HTML (primeros 500 chars):")
print(section.get_attribute("outerHTML")[:500])

# Dentro de sección, buscar items
print("\nBuscando items dentro de sección:")
items = section.find_elements(By.CSS_SELECTOR, "*")
print(f"Total elementos dentro de sección: {len(items)}")

# Buscar por clase específica de BuscadorProp
print("\nBuscando por patrones de BuscadorProp:")
for cls in ["item", "propiedad", "resultado", "tarjeta", "card", "property"]:
    els = driver.find_elements(By.CSS_SELECTOR, f"div[class*='{cls}']")
    if els:
        print(f"  div[class*='{cls}']: {len(els)}")

# Obtener texto de sección para ver qué hay
print("\nTexto de sección de listing (primeros 500 chars):")
print(section.text[:500])

driver.quit()
