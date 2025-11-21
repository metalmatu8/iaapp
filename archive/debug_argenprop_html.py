#!/usr/bin/env python3
"""Debug Argenprop para ver estructura HTML."""

import requests
from bs4 import BeautifulSoup

url = "https://www.argenprop.com/venta-departamento-en-palermo"
ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

try:
    r = requests.get(url, headers={"User-Agent": ua}, timeout=10)
    print(f"Status: {r.status_code}")
    print(f"Content length: {len(r.text)}")
    
    soup = BeautifulSoup(r.text, "html.parser")
    
    # Buscar tarjetas
    cards = soup.find_all("article")
    print(f"\n<article> encontradas: {len(cards)}")
    
    if not cards:
        cards = soup.find_all("div", {"data-qa": "listing-item"})
        print(f"<div data-qa='listing-item'> encontradas: {len(cards)}")
    
    if not cards:
        # Buscar divs con clase que contenga 'card'
        cards = soup.find_all("div", class_=lambda x: x and "card" in str(x).lower())
        print(f"<div class='*card*'> encontradas: {len(cards)}")
    
    # Inspeccionar primera tarjeta
    if cards:
        print("\n" + "="*70)
        print(f"ESTRUCTURA DE PRIMERA TARJETA:")
        print("="*70)
        card = cards[0]
        print(f"HTML (primeros 500 chars):\n{str(card)[:500]}\n")
        
        # Buscar elementos comunes
        print("\nELEMENTOS ENCONTRADOS:")
        for tag in ["h1", "h2", "h3", "h4", "span", "p", "a"]:
            elems = card.find_all(tag)
            if elems:
                print(f"\n  {tag}: {len(elems)} encontrados")
                for i, elem in enumerate(elems[:3]):
                    text = elem.get_text(strip=True)[:60]
                    cls = elem.get("class", [])
                    print(f"    [{i}] {text}... (class={cls})")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
