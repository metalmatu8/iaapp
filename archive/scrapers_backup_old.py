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


class GeorefAPI:
    """API de Georef para obtener provincias y localidades de Argentina"""
    BASE_URL = "https://apis.datos.gob.ar/georef/api"
    
    @staticmethod
    def obtener_provincias() -> List[Dict]:
        """Obtener todas las provincias de Argentina"""
        try:
            url = f"{GeorefAPI.BASE_URL}/provincias?max=24"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return [{"id": p["id"], "nombre": p["nombre"]} for p in data.get("provincias", [])]
        except Exception as e:
            logger.error(f"Error obteniendo provincias de Georef: {e}")
        return []
    
    @staticmethod
    def obtener_municipios(provincia_id: str = None) -> List[Dict]:
        """Obtener municipios/localidades de una provincia"""
        try:
            url = f"{GeorefAPI.BASE_URL}/municipios"
            params = {"max": 100}
            if provincia_id:
                params["provincia"] = provincia_id
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return [{"id": m["id"], "nombre": m["nombre"]} for m in data.get("municipios", [])]
        except Exception as e:
            logger.error(f"Error obteniendo municipios de Georef: {e}")
        return []
    
    @staticmethod
    def obtener_todo() -> Dict:
        """Obtener provincias y sus municipios"""
        resultado = {"provincias": [], "municipios_por_provincia": {}}
        provincias = GeorefAPI.obtener_provincias()
        resultado["provincias"] = provincias
        
        for prov in provincias[:5]:  # Primeras 5 para performance
            municipios = GeorefAPI.obtener_municipios(prov["id"])
            resultado["municipios_por_provincia"][prov["nombre"]] = municipios
        
        return resultado


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
    @staticmethod
    def extraer_datos_propiedad(card, href, zona, debug=False):
        """Extrae datos detallados de una tarjeta de propiedad en Argenprop."""
        try:
            from selenium.webdriver.common.by import By
            
            # Título
            h2 = card.find_element(By.TAG_NAME, "h2").text.strip()
            if not h2:
                return None
            
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
            amenities_list = []
            
            # Extraer información de párrafos y elementos
            elementos_texto = []
            try:
                for p in card.find_elements(By.TAG_NAME, "p"):
                    p_text = p.text.strip()
                    if p_text:
                        elementos_texto.append(p_text)
            except:
                pass
            
            # Extraer información de spans, divs, etc
            try:
                for span in card.find_elements(By.TAG_NAME, "span"):
                    span_text = span.text.strip()
                    if span_text and span_text not in elementos_texto:
                        elementos_texto.append(span_text)
            except:
                pass
            
            # Procesar texto extraído
            for text in elementos_texto:
                text_lower = text.lower()
                
                # Precio
                if "$" in text or "usd" in text_lower:
                    precio = text
                
                # Metros cubiertos (70 m² cubie., 70m2, etc)
                elif "m²" in text or "m2" in text:
                    try:
                        import re
                        match = re.search(r'(\d+(?:\.\d+)?)\s*m[²2]', text, re.IGNORECASE)
                        if match:
                            valor = float(match.group(1))
                            if "descubie" in text_lower or "desc" in text_lower:
                                metros_descubiertos = valor
                            else:
                                metros_cubiertos = valor
                    except:
                        pass
                
                # Habitaciones/Dormitorios
                elif any(word in text_lower for word in ["dorm", "dormitorio", "ambientes"]):
                    try:
                        import re
                        match = re.search(r'(\d+)', text)
                        if match:
                            habitaciones = int(match.group(1))
                    except:
                        pass
                
                # Baños
                elif "baño" in text_lower or "bano" in text_lower:
                    try:
                        import re
                        match = re.search(r'(\d+)', text)
                        if match:
                            banos = int(match.group(1))
                    except:
                        pass
                
                # Toilettes
                elif "toilette" in text_lower:
                    try:
                        import re
                        match = re.search(r'(\d+)', text)
                        if match:
                            toilettes = int(match.group(1))
                    except:
                        pass
                
                # Antigüedad
                elif "año" in text_lower or "antigüedad" in text_lower:
                    try:
                        import re
                        match = re.search(r'(\d+)\s*año', text, re.IGNORECASE)
                        if match:
                            antiguedad = int(match.group(1))
                    except:
                        pass
                
                # Orientación
                elif any(word in text_lower for word in ["norte", "sur", "este", "oeste", "noreste", "noroeste", "sureste", "suroeste"]):
                    orientacion = text
                
                # Características (luminoso, moderno, etc)
                elif len(text) < 50 and len(text) > 3:
                    palabras_clave_caracteristicas = [
                        "luminoso", "moderno", "nuevo", "reciclado", "renovado", "amplio", "espacioso",
                        "doble circulación", "hall", "placard", "living", "cocina", "balcón", "terraza",
                        "pileta", "piscina", "jardín", "patio", "cochera", "garaje", "aire acondicionado",
                        "calefacción", "gas", "servicios", "crédito", "único", "oportunidad", "impecable",
                        "excelente", "contra frente", "frente", "lateral"
                    ]
                    for caracteristica in palabras_clave_caracteristicas:
                        if caracteristica in text_lower:
                            if text not in amenities_list:
                                amenities_list.append(text)
                            break
                
                # Dirección (si no coincide con otros patrones y es texto medio)
                elif 50 < len(text) < 200 and not any(x in text_lower for x in ["$", "usd", "m²", "m2"]):
                    if not direccion and text != h2:
                        direccion = text
            
            # Descripción completa
            desc = f"{h2} - {direccion}" if direccion else h2
            
            # Amenities concatenados
            amenities_str = " | ".join(amenities_list) if amenities_list else ""
            
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
                logger.info(f"Propiedad extraída: {h2} - {metros_cubiertos}m² - {habitaciones} dorm")
            
            return propiedad
        
        except Exception as e:
            if debug:
                logger.error(f"Error extrayendo datos: {e}")
            return None
    


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
