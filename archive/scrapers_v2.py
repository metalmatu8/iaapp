#!/usr/bin/env python3
"""
scrapers_v2.py - Scrapers mejorados para Argenprop y BuscadorProp
Extrae descripciones reales (títulos + direcciones)
"""

import requests
from typing import List, Dict
import logging
from datetime import datetime
import sqlite3
import pandas as pd
import random
from random import uniform
import time
import urllib.parse

logger = logging.getLogger(__name__)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0",
]


class ArgenpropScraper:
    @staticmethod
    def buscar_propiedades(zona: str = "Palermo", tipo: str = "Venta", limit: int = 10, debug: bool = False) -> List[Dict]:
        """Scraping de Argenprop usando Selenium."""
        if debug:
            logger.info(f"Argenprop: buscando {tipo} en {zona}...")
        
        return ArgenpropScraper.buscar_propiedades_selenium(zona=zona, tipo=tipo, limit=limit, debug=debug)

    @staticmethod
    def buscar_propiedades_selenium(zona: str = "Palermo", tipo: str = "Venta", limit: int = 10, debug: bool = False) -> List[Dict]:
        """Scraping de Argenprop - extrae h2 (título) + dirección."""
        try:
            from selenium import webdriver
            from selenium.webdriver.common.by import By
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
        except:
            logger.error("selenium no disponible")
            return []

        tipo_text = "alquiler" if tipo.lower() == "alquiler" else "venta"
        zona_slug = zona.lower().replace(" ", "-").replace("é", "e").replace("á", "a")
        base_url = f"https://www.argenprop.com/departamentos/{tipo_text}/{zona_slug}"
        
        opts = Options()
        opts.add_argument("--headless")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
        opts.add_argument("--disable-gpu")
        opts.add_argument("--window-size=1920,1080")
        opts.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0")
        
        out: List[Dict] = []
        driver = None
        try:
            try:
                from webdriver_manager.chrome import ChromeDriverManager
                from selenium.webdriver.chrome.service import Service
                driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opts)
            except:
                driver = webdriver.Chrome(options=opts)
            
            if debug:
                logger.info(f"Argenprop: {base_url}")
            
            driver.get(base_url)
            
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".card"))
                )
            except:
                pass
            
            cards = driver.find_elements(By.CSS_SELECTOR, ".card")
            if debug:
                logger.info(f"Encontradas {len(cards)} tarjetas")
            
            for card in cards[:limit]:
                try:
                    # URL
                    href = card.get_attribute("href")
                    if not href or href.startswith("javascript"):
                        continue
                    if href.startswith("/"):
                        href = "https://www.argenprop.com" + href
                    
                    # h2 = TÍTULO REAL
                    h2 = card.find_element(By.TAG_NAME, "h2").text.strip()
                    if not h2:
                        continue
                    
                    # Precio desde párrafos
                    precio = "N/A"
                    direccion = ""
                    for p in card.find_elements(By.TAG_NAME, "p"):
                        p_text = p.text.strip()
                        if "$" in p_text or "USD" in p_text:
                            precio = p_text
                        elif len(p_text) < 100 and len(p_text) > 5 and not ("$" in p_text):
                            direccion = p_text
                    
                    # Descripción = titulo + direccion
                    desc = f"{h2} - {direccion}" if direccion else h2
                    
                    out.append({
                        "id": href,
                        "tipo": "Departamento",
                        "zona": zona,
                        "precio": precio,
                        "descripcion": desc[:300],
                        "url": href,
                        "fuente": "Argenprop",
                        "fecha_agregado": datetime.now().isoformat(),
                        "amenities": "",
                        "habitaciones": None,
                        "baños": None,
                        "pileta": None,
                        "metros_cubiertos": None,
                        "metros_descubiertos": None,
                        "latitud": None,
                        "longitud": None,
                    })
                except:
                    continue
            
            if debug:
                logger.info(f"Extraídas {len(out)} propiedades")
        
        except Exception as e:
            logger.error(f"Argenprop error: {e}")
        
        finally:
            if driver:
                try:
                    driver.quit()
                except:
                    pass
        
        return out


class BuscadorPropScraper:
    @staticmethod
    def buscar_propiedades(zona: str = "Palermo", tipo: str = "venta", limit: int = 10, debug: bool = False) -> List[Dict]:
        """Scraping de BuscadorProp."""
        if debug:
            logger.info(f"BuscadorProp: buscando {tipo} en {zona}...")
        
        return BuscadorPropScraper.buscar_propiedades_selenium(zona=zona, tipo=tipo, limit=limit, debug=debug)

    @staticmethod
    def buscar_propiedades_selenium(zona: str = "Palermo", tipo: str = "venta", limit: int = 10, debug: bool = False) -> List[Dict]:
        """Scraping de BuscadorProp - extrae h2 (tipo) + dirección (span/p)."""
        try:
            from selenium import webdriver
            from selenium.webdriver.common.by import By
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
        except:
            logger.error("selenium no disponible")
            return []

        zona_slug = zona.lower().replace(" ", "-").replace("é", "e").replace("á", "a")
        base_url = f"https://www.buscadorprop.com.ar/{tipo}-{zona_slug}"
        
        opts = Options()
        opts.add_argument("--headless")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
        opts.add_argument("--disable-gpu")
        opts.add_argument("--window-size=1920,1080")
        opts.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0")
        
        out: List[Dict] = []
        driver = None
        try:
            try:
                from webdriver_manager.chrome import ChromeDriverManager
                from selenium.webdriver.chrome.service import Service
                driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opts)
            except:
                driver = webdriver.Chrome(options=opts)
            
            if debug:
                logger.info(f"BuscadorProp: {base_url}")
            
            driver.get(base_url)
            
            try:
                WebDriverWait(driver, 15).until(
                    EC.invisibility_of_element_located((By.CSS_SELECTOR, ".loading-spinner"))
                )
            except:
                time.sleep(8)
            
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)
            
            links = driver.find_elements(By.CSS_SELECTOR, "a[href*='/propiedad/']")
            if debug:
                logger.info(f"Encontrados {len(links)} links")
            
            for link in links[:limit]:
                try:
                    href = link.get_attribute("href")
                    if not href:
                        continue
                    if not href.startswith("http"):
                        href = "https://www.buscadorprop.com.ar" + href
                    
                    # Obtener contenedor
                    parent = link
                    for _ in range(5):
                        parent = parent.find_element(By.XPATH, "..")
                        if len(parent.text.strip()) > 20:
                            break
                    
                    # h2 = tipo de propiedad
                    titulo = ""
                    try:
                        titulo = parent.find_element(By.TAG_NAME, "h2").text.strip()
                    except:
                        pass
                    
                    # Dirección: buscar span con comas o "Buenos Aires"
                    direccion = ""
                    for span in parent.find_elements(By.TAG_NAME, "span"):
                        span_text = span.text.strip()
                        if len(span_text) > 10 and len(span_text) < 150 and ("," in span_text or "Buenos Aires" in span_text):
                            direccion = span_text
                            break
                    
                    # Descripción
                    desc = f"{titulo} - {direccion}" if (titulo and direccion) else titulo
                    if not desc or len(desc) < 10:
                        continue
                    
                    # Precio
                    precio = "N/A"
                    for line in parent.text.split("\n"):
                        if "$" in line or "USD" in line.upper():
                            precio = line.strip()
                            break
                    
                    out.append({
                        "id": href,
                        "tipo": "Propiedad",
                        "zona": zona,
                        "precio": precio,
                        "descripcion": desc[:300],
                        "url": href,
                        "fuente": "BuscadorProp",
                        "fecha_agregado": datetime.now().isoformat(),
                        "amenities": "",
                        "habitaciones": None,
                        "baños": None,
                        "pileta": None,
                        "metros_cubiertos": None,
                        "metros_descubiertos": None,
                        "latitud": None,
                        "longitud": None,
                    })
                except:
                    continue
            
            if debug:
                logger.info(f"Extraídas {len(out)} propiedades")
        
        except Exception as e:
            logger.error(f"BuscadorProp error: {e}")
        
        finally:
            if driver:
                try:
                    driver.quit()
                except:
                    pass
        
        return out


class PropertyDatabase:
    def __init__(self, db_path: str = "properties.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Inicializa la BD."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS propiedades (
                    id TEXT PRIMARY KEY,
                    tipo TEXT,
                    zona TEXT,
                    precio TEXT,
                    precio_valor INTEGER,
                    precio_moneda TEXT,
                    habitaciones INTEGER,
                    baños INTEGER,
                    pileta INTEGER,
                    metros_cubiertos REAL,
                    metros_descubiertos REAL,
                    descripcion TEXT,
                    amenities TEXT,
                    latitud REAL,
                    longitud REAL,
                    url TEXT,
                    fuente TEXT,
                    fecha_agregado TEXT
                )
            """)
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Error inicializando BD: {e}")

    def agregar_propiedades(self, nuevas_props: List[Dict]) -> int:
        """Agrega propiedades evitando duplicados por URL."""
        if not nuevas_props:
            return 0
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT url FROM propiedades WHERE url IS NOT NULL")
            existentes = set(row[0] for row in cursor.fetchall())
            
            agregadas = 0
            for prop in nuevas_props:
                url = prop.get("url", "")
                if url and url in existentes:
                    continue
                
                try:
                    # Extraer precio valor y moneda
                    precio_texto = prop.get("precio", "N/A")
                    precio_valor = 0
                    precio_moneda = "USD"
                    
                    if "$" in precio_texto:
                        precio_moneda = "$"
                    elif "USD" in precio_texto.upper():
                        precio_moneda = "USD"
                    
                    import re
                    numeros = re.findall(r'[\d,\.]+', precio_texto)
                    if numeros:
                        num_str = numeros[0].replace('.', '').replace(',', '')
                        try:
                            precio_valor = int(num_str)
                        except:
                            pass
                    
                    cursor.execute("""
                        INSERT OR REPLACE INTO propiedades 
                        (id, tipo, zona, precio, precio_valor, precio_moneda,
                         habitaciones, baños, pileta, metros_cubiertos, metros_descubiertos,
                         descripcion, amenities, latitud, longitud, url, fuente, fecha_agregado)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        prop.get("id", str(datetime.now())),
                        prop.get("tipo", ""),
                        prop.get("zona", ""),
                        prop.get("precio", ""),
                        precio_valor,
                        precio_moneda,
                        prop.get("habitaciones"),
                        prop.get("baños"),
                        1 if prop.get("pileta") else 0,
                        prop.get("metros_cubiertos"),
                        prop.get("metros_descubiertos"),
                        prop.get("descripcion", ""),
                        prop.get("amenities", ""),
                        prop.get("latitud"),
                        prop.get("longitud"),
                        url,
                        prop.get("fuente", ""),
                        prop.get("fecha_agregado", datetime.now().isoformat())
                    ))
                    agregadas += 1
                except Exception as e:
                    logger.debug(f"Error agregando: {e}")
                    continue
            
            conn.commit()
            conn.close()
            logger.info(f"Agregadas {agregadas} propiedades a BD")
            return agregadas
        except Exception as e:
            logger.error(f"Error en agregar_propiedades: {e}")
            return 0

    def obtener_todas(self) -> List[Dict]:
        """Obtiene todas las propiedades."""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM propiedades")
            props = [dict(row) for row in cursor.fetchall()]
            conn.close()
            return props
        except Exception as e:
            logger.error(f"Error obteniendo propiedades: {e}")
            return []

    def obtener_df(self) -> pd.DataFrame:
        """Obtiene propiedades como DataFrame."""
        try:
            conn = sqlite3.connect(self.db_path)
            df = pd.read_sql_query("SELECT * FROM propiedades", conn)
            conn.close()
            return df
        except Exception as e:
            logger.error(f"Error leyendo DF: {e}")
            return pd.DataFrame()

    def guardar_csv(self, csv_path: str = "properties_expanded.csv") -> None:
        """Exporta a CSV."""
        try:
            df = self.obtener_df()
            if not df.empty:
                df.to_csv(csv_path, index=False)
                logger.info(f"BD exportada a {csv_path}")
        except Exception as e:
            logger.error(f"Error guardando CSV: {e}")

    def obtener_estadisticas(self) -> Dict:
        """Estadísticas de la BD."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM propiedades")
            total = cursor.fetchone()[0]
            
            cursor.execute("SELECT DISTINCT fuente FROM propiedades")
            fuentes = [row[0] for row in cursor.fetchall()]
            
            cursor.execute("SELECT DISTINCT zona FROM propiedades")
            zonas = [row[0] for row in cursor.fetchall()]
            
            conn.close()
            return {
                "total_propiedades": total,
                "fuentes": fuentes,
                "zonas": zonas,
            }
        except Exception as e:
            logger.error(f"Error en estadísticas: {e}")
            return {"total_propiedades": 0, "fuentes": [], "zonas": []}
