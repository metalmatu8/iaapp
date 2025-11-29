#!/usr/bin/env python3
"""Debug BuscadorProp extraction."""

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

url = "https://www.buscadorprop.com.ar/venta-palermo"
print(f"Cargando: {url}\n")

driver.get(url)
time.sleep(5)

# Intentar descargar loader
try:
    loader = driver.find_element(By.CSS_SELECTOR, ".loading-spinner")
    print(f"Loading spinner visible: {loader.is_displayed()}")
except:
    print("Loading spinner no encontrado")

# Scroll
actions = ActionChains(driver)
for _ in range(3):
    actions.scroll_by_amount(0, 500).perform()
    time.sleep(1)

# Buscar selectores
selectors = [
    ("a[data-test*='listing']", "a[data-test*='listing']"),
    ("a[class*='listing']", "a[class*='listing']"),
    ("div[class*='property']", "div[class*='property']"),
    ("div[class*='resultado']", "div[class*='resultado']"),
    ("article", "article"),
    (".card", ".card"),
    ("a[href*='propiedad']", "a[href*='propiedad']"),
    ("a[href*='inmueble']", "a[href*='inmueble']"),
]

for name, selector in selectors:
    elements = driver.find_elements(By.CSS_SELECTOR, selector)
    print(f"{name}: {len(elements)} elementos")
    if elements and len(elements) > 0:
        el = elements[0]
        href = el.get_attribute("href")
        text = el.text.strip()[:100]
        print(f"  1er elemento href: {href}")
        print(f"  1er elemento text: {text}")
        print(f"  1er elemento HTML: {el.get_attribute('outerHTML')[:300]}...")
        
        # Intentar extraer de forma similar a Argenprop
        lines = [l.strip() for l in text.split("\n") if l.strip() and len(l.strip()) > 3]
        print(f"  Líneas significativas: {lines[:3]}")
        print()

driver.quit()
