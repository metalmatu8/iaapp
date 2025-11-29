#!/usr/bin/env python3
"""Script de debug para Zonaprop."""

import requests
from bs4 import BeautifulSoup
from random import uniform, choice
import time

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0",
]

url = "https://www.zonaprop.com.ar/venta-departamentos-palermo.html"

print("=" * 70)
print("DEBUG ZONAPROP")
print("=" * 70)
print(f"\nURL: {url}\n")

for attempt in range(3):
    print(f"\n[INTENTO {attempt + 1}/3]")
    ua = USER_AGENTS[attempt % len(USER_AGENTS)]
    headers = {
        "User-Agent": ua,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "es-AR,es;q=0.9",
        "Referer": "https://www.zonaprop.com.ar/",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }
    
    print(f"User-Agent: {ua[:60]}...")
    
    try:
        r = requests.get(url, headers=headers, timeout=10)
        print(f"Status: {r.status_code}")
        print(f"Content-Length: {len(r.text)} bytes")
        
        # Detectar bloqueos
        if "verificar que usted es un ser humano" in r.text.lower():
            print("❌ BLOQUEADO: Captcha detectado")
            print(f"   Contenido: {r.text[:200]}...")
            time.sleep(uniform(2, 5))
            continue
        
        if "cloudflare" in r.text.lower() and len(r.text) < 1000:
            print("❌ BLOQUEADO: Cloudflare Challenge")
            print(f"   Contenido: {r.text[:200]}...")
            time.sleep(uniform(2, 5))
            continue
        
        # Parse HTML
        soup = BeautifulSoup(r.text, "html.parser")
        
        # Buscar cards
        cards = soup.find_all("div", class_=lambda x: x and "card" in str(x).lower())
        print(f"   Cards encontradas (class*='card'): {len(cards)}")
        
        if not cards:
            cards = soup.find_all("div", {"data-qa": "listing-item"})
            print(f"   Cards encontradas (data-qa='listing-item'): {len(cards)}")
        
        if not cards:
            cards = soup.find_all("article")
            print(f"   Cards encontradas (article): {len(cards)}")
        
        if cards:
            print(f"✓ Total cards: {len(cards)}")
            for i, card in enumerate(cards[:2]):
                print(f"\n   Card {i+1}:")
                links = card.find_all("a", href=True)
                print(f"     - Links: {len(links)}")
                if links:
                    href = links[0].get("href", "")
                    print(f"     - Primer href: {href[:80]}...")
                text = card.text.strip()[:100]
                print(f"     - Texto: {text}...")
            break
        else:
            print("❌ No se encontraron cards")
            print(f"   Primer fragmento HTML:\n{r.text[:300]}...")
    
    except Exception as e:
        print(f"❌ Error: {type(e).__name__}: {e}")
        time.sleep(uniform(1, 2))

print("\n" + "=" * 70)
