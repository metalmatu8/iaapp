#!/usr/bin/env python3
"""Debug diferentes URLs de Argenprop."""

import requests
from bs4 import BeautifulSoup

urls_to_try = [
    "https://www.argenprop.com/venta-departamento-palermo",
    "https://www.argenprop.com/venta-departamentos-palermo",
    "https://www.argenprop.com/departamentos-en-alquiler-palermo",
    "https://www.argenprop.com/buscar?location=palermo&transaction=buy&category=apartment",
]

ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

for url in urls_to_try:
    try:
        r = requests.get(url, headers={"User-Agent": ua}, timeout=10)
        print(f"\nURL: {url}")
        print(f"  Status: {r.status_code}")
        print(f"  Size: {len(r.text)} bytes")
        
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, "html.parser")
            # Buscar cualquier elemento que parezca una tarjeta
            articles = soup.find_all("article")
            divs_listing = soup.find_all("div", {"data-qa": "listing-item"})
            print(f"  Articles: {len(articles)}")
            print(f"  Data-qa listing-item: {len(divs_listing)}")
            
            # Si encontramos contenido, mostrar primeras líneas
            if articles or divs_listing:
                print("  *** ENCONTRADO CONTENIDO ***")
            break
    except Exception as e:
        print(f"\nURL: {url} - Error: {e}")
