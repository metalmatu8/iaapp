"""
scrapers.py - Scrapers para Argenprop y BuscadorProp con SQLite.
Usa Google Search para encontrar URLs correctas dinámicamente.
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

# User-Agents variados para evitar bloqueos
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0",
]

def buscar_url_google(query: str, debug: bool = False) -> str:
    """Busca en Google para encontrar la URL correcta."""
    try:
        # Construir URL de búsqueda Google
        search_url = f"https://www.google.com/search?q={urllib.parse.quote(query)}"
        headers = {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "es-AR,es;q=0.9",
        }
        
        if debug:
            logger.info(f"Buscando en Google: {query}")
        
        r = requests.get(search_url, headers=headers, timeout=10)
        if r.status_code == 200:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(r.text, "html.parser")
            # Buscar primer enlace de resultado
            for link in soup.find_all("a"):
                href = link.get("href", "")
                if href.startswith("/url?q="):
                    url = href.split("/url?q=")[1].split("&")[0]
                    if ("argenprop.com" in query and "argenprop.com" in url) or \
                       ("buscadorprop.com" in query and "buscadorprop.com" in url):
                        if debug:
                            logger.info(f"URL encontrada: {url}")
                        return url
    except Exception as e:
        if debug:
            logger.warning(f"Error en búsqueda Google: {e}")
    
    return ""



class ArgenpropScraper:
    @staticmethod
    def buscar_propiedades(zona: str = "Palermo", tipo: str = "Venta", limit: int = 10, debug: bool = False) -> List[Dict]:
        """Scraping de Argenprop usando Selenium con búsqueda dinámica de URL."""
        if debug:
            logger.info(f"Argenprop: buscando {tipo} en {zona}...")
        
        return ArgenpropScraper.buscar_propiedades_selenium(zona=zona, tipo=tipo, limit=limit, debug=debug)

    @staticmethod
    def buscar_propiedades_selenium(zona: str = "Palermo", tipo: str = "Venta", limit: int = 10, debug: bool = False) -> List[Dict]:
        """Scraping de Argenprop con Selenium - estructura correcta con .card"""
        try:
            from selenium import webdriver
            from selenium.webdriver.common.by import By
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
        except:
            logger.error("selenium no disponible")
            return []

        # URL correcta: /departamentos/tipo/zona
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
                logger.info(f"Argenprop Selenium: {base_url}")
            
            driver.get(base_url)
            
            # Esperar a que carguen tarjetas .card
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".card"))
                )
            except:
                if debug:
                    logger.warning("Timeout esperando .card, continuando...")
            
            # Buscar tarjetas - Argenprop usa .card
            cards = driver.find_elements(By.CSS_SELECTOR, ".card")
            
            if debug:
                logger.info(f"Argenprop: Encontradas {len(cards)} tarjetas")
            
            for i, card in enumerate(cards[:limit]):
                try:
                    # Extraer URL del atributo href del enlace principal
                    href = card.get_attribute("href")
                    if not href:
                        # Intentar buscar enlace dentro de la tarjeta
                        link = card.find_element(By.TAG_NAME, "a")
                        href = link.get_attribute("href")
                    
                    if not href or href.startswith("javascript"):
                        continue
                    
                    if href.startswith("/"):
                        href = "https://www.argenprop.com" + href
                    
                    # Extraer descripción del contenido de la tarjeta
                    all_text = card.text.strip()
                    
                    # Limpiar líneas triviales
                    lines = [
                        l.strip() for l in all_text.split("\n") 
                        if l.strip() and len(l.strip()) > 3 
                        and l.strip().lower() not in ["ver", "acceder", "cotizar", "consultar", "contactar"]
                    ]
                    
                    descripcion = " ".join(lines[:3])[:200] if lines else ""
                    
                    if not descripcion or len(descripcion) < 5:
                        continue
                    
                    # Buscar precio
                    precio = "N/A"
                    for line in lines:
                        if "$" in line or "USD" in line.upper():
                            precio = line
                            break
                    
                    out.append({
                        "id": href,
                        "tipo": "Departamento",
                        "zona": zona,
                        "precio": precio,
                        "descripcion": descripcion,
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
                except Exception as e:
                    if debug:
                        logger.debug(f"Error procesando card {i}: {e}")
                    continue
            
            if debug:
                logger.info(f"Argenprop: {len(out)} propiedades extraídas")
        
        except Exception as e:
            logger.error(f"Selenium Argenprop error: {e}")
        
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
        """Scraping de BuscadorProp usando Selenium."""
        if debug:
            logger.info(f"BuscadorProp: buscando {tipo} en {zona}...")
        
        return BuscadorPropScraper.buscar_propiedades_selenium(zona=zona, tipo=tipo, limit=limit, debug=debug)

    @staticmethod
    def buscar_propiedades_selenium(zona: str = "Palermo", tipo: str = "venta", limit: int = 10, debug: bool = False) -> List[Dict]:
        """Scraping de BuscadorProp con Selenium - busca links de propiedades reales."""
        try:
            from selenium import webdriver
            from selenium.webdriver.common.by import By
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
        except:
            logger.error("selenium no disponible")
            return []

        # URL estándar BuscadorProp: /tipo-zona
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
                logger.info(f"BuscadorProp Selenium: {base_url}")
            
            driver.get(base_url)
            
            # Esperar a que cargue completamente
            try:
                WebDriverWait(driver, 15).until(
                    EC.invisibility_of_element_located((By.CSS_SELECTOR, ".loading-spinner"))
                )
            except:
                if debug:
                    logger.warning("Timeout esperando carga")
                time.sleep(8)
            
            # Scroll para cargar más
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)
            
            # Buscar links de propiedades reales - patrón: /propiedad/ID-descripción
            property_links = driver.find_elements(By.CSS_SELECTOR, "a[href*='/propiedad/']")
            
            if debug:
                logger.info(f"BuscadorProp: Encontrados {len(property_links)} links de propiedades")
            
            for i, link in enumerate(property_links[:limit]):
                try:
                    href = link.get_attribute("href")
                    if not href:
                        continue
                    
                    if not href.startswith("http"):
                        href = "https://www.buscadorprop.com.ar" + href
                    
                    # Obtener texto del link y su contexto
                    link_text = link.text.strip()
                    
                    # Obtener el elemento padre (contenedor de la tarjeta)
                    parent = link
                    for _ in range(5):  # Subir hasta 5 niveles
                        parent = parent.find_element(By.XPATH, "..")
                        all_text = parent.text.strip()
                        if all_text and len(all_text) > 20:
                            break
                    
                    all_text = parent.text.strip()
                    
                    # Limpiar líneas triviales
                    lines = [
                        l.strip() for l in all_text.split("\n") 
                        if l.strip() and len(l.strip()) > 2 
                        and l.strip().lower() not in ["ver", "consultar", "contactar", "ver más", "✓", "✗"]
                    ]
                    
                    descripcion = " ".join(lines[:3])[:200] if lines else ""
                    
                    if not descripcion or len(descripcion) < 5:
                        # Usar link text como fallback
                        descripcion = link_text[:200]
                    
                    if not descripcion or len(descripcion) < 5:
                        continue
                    
                    # Buscar precio en las líneas
                    precio = "N/A"
                    for line in lines:
                        if "$" in line or "USD" in line.upper():
                            precio = line
                            break
                    
                    out.append({
                        "id": href,
                        "tipo": "Propiedad",
                        "zona": zona,
                        "precio": precio,
                        "descripcion": descripcion,
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
                except Exception as e:
                    if debug:
                        logger.debug(f"Error procesando link {i}: {e}")
                    continue
            
            if debug:
                logger.info(f"BuscadorProp: {len(out)} propiedades extraídas")
        
        except Exception as e:
            logger.error(f"Selenium BuscadorProp error: {e}")
        
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
        """Inicializa la base de datos SQLite con la tabla de propiedades."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS propiedades (
                    id TEXT PRIMARY KEY,
                    tipo TEXT,
                    zona TEXT,
                    precio TEXT,
                    habitaciones REAL,
                    baños REAL,
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
        """Agrega propiedades a la BD, evitando duplicados por URL."""
        if not nuevas_props:
            return 0
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Obtener URLs existentes
            cursor.execute("SELECT url FROM propiedades WHERE url IS NOT NULL")
            existentes = set(row[0] for row in cursor.fetchall())
            
            agregadas = 0
            for prop in nuevas_props:
                url = prop.get("url", "")
                if url and url in existentes:
                    continue
                
                try:
                    cursor.execute("""
                        INSERT OR REPLACE INTO propiedades 
                        (id, tipo, zona, precio, habitaciones, baños, pileta, 
                         metros_cubiertos, metros_descubiertos, descripcion, amenities,
                         latitud, longitud, url, fuente, fecha_agregado)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        prop.get("id", str(datetime.now())),
                        prop.get("tipo", ""),
                        prop.get("zona", ""),
                        prop.get("precio", ""),
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
                    logger.debug(f"Error agregando propiedad: {e}")
                    continue
            
            conn.commit()
            conn.close()
            logger.info(f"Agregadas {agregadas} propiedades a BD")
            return agregadas
        except Exception as e:
            logger.error(f"Error en agregar_propiedades: {e}")
            return 0

    def obtener_todas(self) -> List[Dict]:
        """Obtiene todas las propiedades como lista de dicts."""
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
        """Obtiene propiedades como DataFrame de pandas."""
        try:
            conn = sqlite3.connect(self.db_path)
            df = pd.read_sql_query("SELECT * FROM propiedades", conn)
            conn.close()
            return df
        except Exception as e:
            logger.error(f"Error leyendo DF: {e}")
            return pd.DataFrame()

    def guardar_csv(self, csv_path: str = "properties_expanded.csv") -> None:
        """Exporta la BD a un archivo CSV."""
        try:
            df = self.obtener_df()
            if not df.empty:
                df.to_csv(csv_path, index=False)
                logger.info(f"BD exportada a {csv_path}")
        except Exception as e:
            logger.error(f"Error guardando CSV: {e}")

    def obtener_estadisticas(self) -> Dict:
        """Devuelve estadísticas básicas de la base de datos."""
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
