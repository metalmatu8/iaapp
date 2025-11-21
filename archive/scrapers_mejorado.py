#!/usr/bin/env python3
"""
scrapers_mejorado.py - Scrapers mejorados con extracción de datos completos
Extrae: precio, m², habitaciones, baños, amenities, ubicación, etc.
"""

import requests
from typing import List, Dict
import logging
from datetime import datetime
import re

logger = logging.getLogger(__name__)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
]


class ArgenpropScraperMejorado:
    """Scraper mejorado para Argenprop que extrae múltiples características."""
    
    AMENITIES_KEYWORDS = {
        "luminoso", "moderno", "nuevo", "reciclado", "renovado", "amplio", "espacioso",
        "doble circulación", "hall", "placard", "living", "cocina", "balcón", "terraza",
        "pileta", "piscina", "jardín", "patio", "cochera", "garaje", "aire acondicionado",
        "calefacción", "gas", "servicios", "crédito", "único", "oportunidad", "impecable",
        "excelente", "contra frente", "frente", "lateral", "dependencia"
    }
    
    @staticmethod
    def extraer_metros(texto):
        """Extrae metros cuadrados del texto."""
        if not texto:
            return None
        match = re.search(r'(\d+(?:\.\d+)?)\s*m[²2]', texto, re.IGNORECASE)
        if match:
            return float(match.group(1))
        return None
    
    @staticmethod
    def extraer_numero(texto, palabras_clave):
        """Extrae el primer número de un texto que contiene palabras clave."""
        if not texto:
            return None
        texto_lower = texto.lower()
        if any(palabra in texto_lower for palabra in palabras_clave):
            match = re.search(r'(\d+)', texto)
            if match:
                return int(match.group(1))
        return None
    
    @staticmethod
    def extraer_datos_tarjeta(card, zona, debug=False):
        """Extrae datos detallados de una tarjeta de Argenprop."""
        try:
            from selenium.webdriver.common.by import By
            
            # Título
            h2 = card.find_element(By.TAG_NAME, "h2").text.strip()
            if not h2:
                return None
            
            # URL
            href = card.get_attribute("href")
            if not href or href.startswith("javascript"):
                return None
            if href.startswith("/"):
                href = "https://www.argenprop.com" + href
            
            # Inicializar variables
            precio = "N/A"
            direccion = ""
            metros_cubiertos = None
            metros_descubiertos = None
            habitaciones = None
            banos = None
            toilettes = None
            orientacion = None
            antiguedad = None
            amenities = []
            
            # Recopilar todo el texto de la tarjeta
            textos = []
            
            # De párrafos
            try:
                for p in card.find_elements(By.TAG_NAME, "p"):
                    text = p.text.strip()
                    if text:
                        textos.append(text)
            except:
                pass
            
            # De spans
            try:
                for span in card.find_elements(By.TAG_NAME, "span"):
                    text = span.text.strip()
                    if text and text not in textos:
                        textos.append(text)
            except:
                pass
            
            # De divs
            try:
                for div in card.find_elements(By.TAG_NAME, "div"):
                    text = div.text.strip()
                    if text and 5 < len(text) < 100 and text not in textos:
                        textos.append(text)
            except:
                pass
            
            # Procesar textos extraídos
            for texto in textos:
                texto_lower = texto.lower()
                
                # Precio
                if "$" in texto or "usd" in texto_lower:
                    if precio == "N/A" or "$" in texto:
                        precio = texto
                
                # M² cubiertos y descubiertos
                metros = ArgenpropScraperMejorado.extraer_metros(texto)
                if metros:
                    if "descubie" in texto_lower or "desc" in texto_lower:
                        metros_descubiertos = metros
                    elif "cubie" in texto_lower or "cub" in texto_lower:
                        metros_cubiertos = metros
                    else:
                        # Por defecto, cubiertos
                        if not metros_cubiertos:
                            metros_cubiertos = metros
                
                # Habitaciones/Dormitorios/Ambientes
                if habitaciones is None:
                    hab = ArgenpropScraperMejorado.extraer_numero(
                        texto, ["dorm", "dormitorio", "ambientes", "ambiente"]
                    )
                    if hab:
                        habitaciones = hab
                
                # Baños
                if banos is None:
                    ban = ArgenpropScraperMejorado.extraer_numero(
                        texto, ["baño", "bano", "baños", "banos"]
                    )
                    if ban:
                        banos = ban
                
                # Toilettes
                if toilettes is None:
                    toil = ArgenpropScraperMejorado.extraer_numero(
                        texto, ["toilette", "toilettes", "wc"]
                    )
                    if toil:
                        toilettes = toil
                
                # Antigüedad
                if antiguedad is None:
                    match = re.search(r'(\d+)\s*año', texto, re.IGNORECASE)
                    if match:
                        antiguedad = int(match.group(1))
                
                # Orientación
                orientaciones = ["norte", "sur", "este", "oeste", "noreste", "noroeste", "sureste", "suroeste"]
                if not orientacion and any(word in texto_lower for word in orientaciones):
                    orientacion = texto
                
                # Amenities (características)
                for amenity_keyword in ArgenpropScraperMejorado.AMENITIES_KEYWORDS:
                    if amenity_keyword in texto_lower:
                        if texto not in amenities and len(texto) < 80:
                            amenities.append(texto)
                        break
                
                # Dirección
                if not direccion and 50 < len(texto) < 150:
                    if not any(x in texto_lower for x in ["$", "usd", "m²", "m2", "año"]):
                        if texto != h2:
                            direccion = texto
            
            # Armar descripción
            desc = f"{h2} - {direccion}" if direccion else h2
            
            # Armar amenities string
            amenities_str = " | ".join(amenities[:5]) if amenities else ""
            
            propiedad = {
                "id": href,
                "tipo": "Departamento",
                "zona": zona,
                "precio": precio,
                "descripcion": desc[:500],
                "url": href,
                "fuente": "Argenprop",
                "fecha_agregado": datetime.now().isoformat(),
                "amenities": amenities_str,
                "habitaciones": habitaciones,
                "baños": banos,
                "toilettes": toilettes,
                "pileta": None,
                "metros_cubiertos": metros_cubiertos,
                "metros_descubiertos": metros_descubiertos,
                "orientacion": orientacion,
                "antiguedad": antiguedad,
                "latitud": None,
                "longitud": None,
            }
            
            if debug:
                logger.info(f"✅ {h2} | {metros_cubiertos}m² | {habitaciones} dorm | {banos} baños")
            
            return propiedad
        
        except Exception as e:
            if debug:
                logger.error(f"Error extrayendo: {e}")
            return None
    
    @staticmethod
    def buscar_propiedades(zona: str = "Palermo", tipo: str = "Venta", limit: int = 10, debug: bool = False) -> List[Dict]:
        """Scraping mejorado de Argenprop."""
        if debug:
            logger.info(f"🔍 Buscando {tipo} en {zona}...")
        
        try:
            from selenium import webdriver
            from selenium.webdriver.common.by import By
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            import time
        except:
            logger.error("Selenium no disponible")
            return []
        
        tipo_text = "alquiler" if tipo.lower() == "alquiler" else "venta"
        zona_slug = zona.lower().replace(" ", "-").replace("é", "e").replace("á", "a").replace("ú", "u")
        url = f"https://www.argenprop.com/departamentos/{tipo_text}/{zona_slug}"
        
        propiedades = []
        driver = None
        
        try:
            # Configurar driver
            opts = Options()
            opts.add_argument("--headless")
            opts.add_argument("--no-sandbox")
            opts.add_argument("--disable-dev-shm-usage")
            opts.add_argument("--disable-gpu")
            opts.add_argument("--window-size=1920,1080")
            opts.add_argument("user-agent=" + USER_AGENTS[0])
            
            try:
                from webdriver_manager.chrome import ChromeDriverManager
                from selenium.webdriver.chrome.service import Service
                driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opts)
            except:
                driver = webdriver.Chrome(options=opts)
            
            if debug:
                logger.info(f"📍 {url}")
            
            driver.get(url)
            
            # Esperar a que carguen las tarjetas
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".card"))
                )
            except:
                pass
            
            time.sleep(2)  # Esperar a que cargue completamente
            
            # Extraer tarjetas
            cards = driver.find_elements(By.CSS_SELECTOR, ".card")
            if debug:
                logger.info(f"📊 Encontradas {len(cards)} tarjetas")
            
            for card in cards[:limit]:
                try:
                    prop = ArgenpropScraperMejorado.extraer_datos_tarjeta(card, zona, debug)
                    if prop:
                        propiedades.append(prop)
                except Exception as e:
                    if debug:
                        logger.error(f"Error procesando tarjeta: {e}")
                    continue
            
            if debug:
                logger.info(f"✅ Extraídas {len(propiedades)} propiedades")
        
        except Exception as e:
            logger.error(f"Error en scraper: {e}")
        
        finally:
            if driver:
                try:
                    driver.quit()
                except:
                    pass
        
        return propiedades
