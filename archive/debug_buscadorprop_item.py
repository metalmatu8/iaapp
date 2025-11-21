#!/usr/bin/env python3
"""Debug detallado de items de BuscadorProp."""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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

driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
time.sleep(3)

# Buscar items
items = driver.find_elements(By.CSS_SELECTOR, "div[class*='item']")
print(f"Encontrados {len(items)} items\n")

if items:
    item = items[0]
    print("=== PRIMER ITEM ===")
    print(f"HTML (primeros 1000 chars):\n{item.get_attribute('outerHTML')[:1000]}\n")
    print(f"Text: {item.text}\n")
    
    # Buscar links dentro
    links = item.find_elements(By.TAG_NAME, "a")
    print(f"Links dentro del item: {len(links)}")
    for i, link in enumerate(links[:3]):
        href = link.get_attribute("href")
        text = link.text.strip()
        print(f"  Link {i}: href='{href}' text='{text}'")
    
    # Buscar span/div con texto
    print("\nElementos con texto:")
    for elem_type in ["span", "div", "p"]:
        elems = item.find_elements(By.TAG_NAME, elem_type)
        for e in elems[:3]:
            text = e.text.strip()
            if text and len(text) > 0:
                print(f"  {elem_type}: {text[:80]}")

driver.quit()
