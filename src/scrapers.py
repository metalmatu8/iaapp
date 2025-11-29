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
import os

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
    def buscar_propiedades(zona: str = "Palermo", tipo: str = "Venta", limit: int = 10, debug: bool = False, stop_flag=None) -> List[Dict]:
        """Scraping de Argenprop usando Selenium."""
        if debug:
            logger.info(f"Argenprop: buscando {tipo} en {zona}...")
        
        return ArgenpropScraper.buscar_propiedades_selenium(zona=zona, tipo=tipo, limit=limit, debug=debug, stop_flag=stop_flag)

    @staticmethod
    def buscar_propiedades_selenium(zona: str = "Palermo", tipo: str = "Venta", limit: int = 10, debug: bool = False, stop_flag=None) -> List[Dict]:
        """Scraping de Argenprop - extrae h2 (título) + dirección + datos mejorados."""
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
        url = f"https://www.argenprop.com/departamentos/{tipo_text}/{zona_slug}"
        
        propiedades = []
        driver = None
        
        try:
            # Verificar si ya se solicitó detener antes de iniciar
            if stop_flag is not None and hasattr(stop_flag, 'scraper_stop_flag') and stop_flag.scraper_stop_flag:
                return []
            
            opts = Options()
            opts.add_argument("--headless")
            opts.add_argument("--no-sandbox")
            opts.add_argument("--disable-dev-shm-usage")
            opts.add_argument("--disable-gpu")
            opts.add_argument("--window-size=1920,1080")
            opts.add_argument("user-agent=" + random.choice(USER_AGENTS))
            
            try:
                from webdriver_manager.chrome import ChromeDriverManager
                from selenium.webdriver.chrome.service import Service
                driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opts)
            except:
                driver = webdriver.Chrome(options=opts)
            
            if debug:
                logger.info(f"Argenprop: {url}")
            
            driver.get(url)
            
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".card"))
                )
            except:
                pass
            
            time.sleep(2)
            
            # Scroll para cargar más tarjetas
            for _ in range(3):
                # Verificar flag de stop entre scrolls
                if stop_flag is not None and hasattr(stop_flag, 'scraper_stop_flag') and stop_flag.scraper_stop_flag:
                    break
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(1)
            
            cards = driver.find_elements(By.CSS_SELECTOR, ".card")
            if debug:
                logger.info(f"Encontradas {len(cards)} tarjetas")
            
            for idx, card in enumerate(cards[:limit]):
                # Verificar flag de stop en cada iteración
                if stop_flag is not None and hasattr(stop_flag, 'scraper_stop_flag') and stop_flag.scraper_stop_flag:
                    if debug:
                        logger.info(f"Stop solicitado, deteniendo en tarjeta {idx}")
                    break
                
                try:
                    # Obtener URL del link
                    href = ""
                    try:
                        link = card.find_element(By.TAG_NAME, "a")
                        href = link.get_attribute("href")
                        if not href.startswith("http"):
                            href = "https://www.argenprop.com" + href
                    except:
                        continue
                    
                    # Usar función mejorada de extracción
                    prop = ArgenpropScraper.extraer_datos_propiedad(card, href, zona, debug)
                    if prop:
                        propiedades.append(prop)
                except Exception as e:
                    if debug:
                        logger.error(f"Error procesando tarjeta: {e}")
                    continue
            
            if debug:
                logger.info(f"✅ Extraídas {len(propiedades)} propiedades")
        
        except Exception as e:
            logger.error(f"Error Argenprop: {e}")
        
        finally:
            if driver:
                try:
                    driver.quit()
                except:
                    pass
        
        return propiedades

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
    def extraer_detalles_propiedad(url: str, debug: bool = False) -> Dict:
        """Extrae detalles completos de una página de propiedad individual en BuscadorProp."""
        try:
            from selenium import webdriver
            from selenium.webdriver.common.by import By
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
        except:
            logger.error("selenium no disponible para extraer detalles")
            return {}
        
        detalles = {
            "direccion": None,
            "ambientes": None,
            "dormitorios": None,
            "baños": None,
            "antiguedad": None,
            "estado": None,
            "superficie_total": None,
            "superficie_cubierta": None,
            "pisos": None,
            "fotos": [],
            "precio_completo": None,
        }
        
        opts = Options()
        opts.add_argument("--headless")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
        opts.add_argument("--disable-gpu")
        opts.add_argument("--window-size=1920,1080")
        opts.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0")
        
        # Detectar si Chromium está instalado en el sistema (Streamlit Cloud)
        chromium_paths = [
            "/usr/bin/chromium-browser",  # Streamlit Cloud
            "/usr/bin/chromium",
            "/snap/bin/chromium",
            "/Applications/Chromium.app/Contents/MacOS/Chromium",  # macOS
            "C:\\Program Files\\Chromium\\Application\\chrome.exe",  # Windows
        ]
        chromium_binary = None
        for path in chromium_paths:
            if os.path.exists(path):
                chromium_binary = path
                logger.debug(f"Detectado Chromium en: {chromium_binary}")
                break
        
        if chromium_binary:
            opts.binary_location = chromium_binary
        
        driver = None
        try:
            try:
                from webdriver_manager.chrome import ChromeDriverManager
                from selenium.webdriver.chrome.service import Service
                driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opts)
            except ModuleNotFoundError as module_error:
                # webdriver_manager no está instalado
                if "webdriver_manager" in str(module_error):
                    logger.debug(f"BuscadorProp: webdriver_manager no disponible, devolviendo detalles vacíos")
                    return detalles
                else:
                    logger.debug(f"BuscadorProp: Error de módulo para {url}, devolviendo detalles vacíos")
                    return detalles
            except Exception as driver_init_error:
                # Si falla la inicialización del driver, es probable que sea por dependencias del sistema
                error_msg = str(driver_init_error)
                if "127" in error_msg or "unexpectedly exited" in error_msg or "chromedriver" in error_msg.lower():
                    logger.debug(f"BuscadorProp: Chromedriver no disponible, devolviendo detalles vacíos")
                    return detalles
                else:
                    logger.debug(f"BuscadorProp: Error inicializando driver para {url}, devolviendo detalles vacíos")
                    return detalles
            
            driver.get(url)
            time.sleep(3)
            
            # Extraer dirección
            try:
                direccion = driver.find_element(By.CSS_SELECTOR, "h1, .property-address, [class*='direccion'], [class*='address']").text
                detalles["direccion"] = direccion
            except:
                pass
            
            # Extraer precio completo
            try:
                # Buscar elemento con "USD" o "$"
                for elem in driver.find_elements(By.XPATH, "//*[contains(text(), 'USD') or contains(text(), '$')]"):
                    text = elem.text.strip()
                    if any(char.isdigit() for char in text):
                        detalles["precio_completo"] = text
                        if debug:
                            logger.info(f"Precio extraído: {text}")
                        break
            except:
                pass
            
            # Extraer características (ambientes, dormitorios, baños, etc.)
            try:
                # Buscar en los textos de la página
                page_text = driver.find_element(By.TAG_NAME, "body").text.lower()
                
                # Ambientes
                if "ambiente" in page_text:
                    for elem in driver.find_elements(By.XPATH, "//*[contains(text(), 'ambiente') or contains(text(), 'Ambiente')]"):
                        text = elem.text.strip()
                        try:
                            # Extraer número antes de "ambiente"
                            num = int(text.split()[0])
                            detalles["ambientes"] = num
                            break
                        except:
                            pass
                
                # Dormitorios
                if "dormitorio" in page_text:
                    for elem in driver.find_elements(By.XPATH, "//*[contains(text(), 'dormitorio') or contains(text(), 'Dormitorio')]"):
                        text = elem.text.strip()
                        try:
                            num = int(text.split()[0])
                            detalles["dormitorios"] = num
                            break
                        except:
                            pass
                
                # Baños
                if "baño" in page_text:
                    for elem in driver.find_elements(By.XPATH, "//*[contains(text(), 'baño') or contains(text(), 'Baño')]"):
                        text = elem.text.strip()
                        try:
                            num = int(text.split()[0])
                            detalles["baños"] = num
                            break
                        except:
                            pass
                
                # Antigüedad
                if "año" in page_text and "antigüedad" in page_text:
                    for elem in driver.find_elements(By.XPATH, "//*[contains(text(), 'año') and contains(text(), 'ntiguedad')]"):
                        text = elem.text.strip()
                        try:
                            num = int(text.split()[0])
                            detalles["antiguedad"] = num
                            break
                        except:
                            pass
                
                # Estado
                estado_keywords = ["refaccionar", "buen estado", "excelente", "a reformar"]
                for keyword in estado_keywords:
                    if keyword in page_text:
                        detalles["estado"] = keyword.title()
                        break
                
                # Superficie total
                if "m2" in page_text or "m²" in page_text:
                    try:
                        # Buscar "210m2" o "210 m2"
                        import re
                        matches = re.findall(r'(\d+)\s*m[2²]', page_text)
                        if matches:
                            # El primer match suele ser superficie total
                            detalles["superficie_total"] = int(matches[0])
                            # El segundo match suele ser cubierta
                            if len(matches) > 1:
                                detalles["superficie_cubierta"] = int(matches[1])
                    except:
                        pass
                
                # Pisos
                if "piso" in page_text:
                    for elem in driver.find_elements(By.XPATH, "//*[contains(text(), 'piso') or contains(text(), 'Piso')]"):
                        text = elem.text.strip()
                        if text.lower().startswith(('1 ', '2 ', '3 ', '4 ', '5 ', '6 ')):
                            try:
                                num = int(text.split()[0])
                                detalles["pisos"] = num
                                break
                            except:
                                pass
            except Exception as e:
                if debug:
                    logger.info(f"Error extrayendo características: {e}")
            
            # Extraer fotos
            try:
                fotos = []
                
                # Esperar a que carguen las imágenes
                time.sleep(2)
                
                # Palabras clave para excluir (logos, iconos, etc)
                exclude_keywords = [
                    'logo', 'icon', 'placeholder', 'avatar', 'sprite', 'button',
                    'header', 'footer', 'nav', 'menu', 'banner', 'badge',
                    'mark', 'seal', 'watermark', 'instagram', 'facebook',
                    'youtube', 'twitter', 'social', 'share', 'arrow',
                    'chevron', 'check', 'close', 'spinner', 'loading',
                    'flag', 'star', 'rating', 'dot', 'circle', 'square',
                    'buscadorprop', 'zonaprop', 'logo', 'badge', 'seal',
                    'button', 'arrow', 'heart', 'share', 'favorite',
                    'tiktok', 'instagram', 'facebook', 'youtube', 'twitter',
                    'social', 'watermark', 'copyright', 'realtor'
                ]
                
                def is_valid_photo(src):
                    """Verifica si una URL es una foto válida de una propiedad (no logo/icon/banner)."""
                    if not src or len(src) < 50:
                        return False
                    
                    src_lower = src.lower()
                    
                    # Excluir si contiene palabras clave sospechosas
                    if any(kw in src_lower for kw in exclude_keywords):
                        return False
                    
                    # Excluir patrones típicos de logos/icons
                    if any(pattern in src_lower for pattern in ['favicon', 'icon-', '/logo/', '/brand/', '/mark/', '/seal/', 'default-image', 'no-image', 'placeholder']):
                        return False
                    
                    # Incluir solo imágenes válidas
                    if not any(ext in src_lower for ext in ['.jpg', '.jpeg', '.png', '.webp', '.gif']):
                        return False
                    
                    # Heurística: URLs de propiedades reales suelen tener patrones de dimensiones
                    # o IDs largos (¿w=800&h=600, /800x600/, etc.)
                    import re
                    size_pattern = r'(?:w|width|h|height|size)=?\d{2,4}|/\d{3,4}x\d{3,4}/'
                    id_pattern = r'/\d{6,}|id=\d{6,}|prop_\d+|image_\d+'
                    
                    if re.search(size_pattern, src_lower) or re.search(id_pattern, src_lower):
                        return True
                    
                    # Si la URL es muy larga y tiene slashes con muchos parámetros, probablemente sea una imagen real
                    if len(src) > 100 and src.count('/') > 4:
                        return True
                    
                    return False
                
                # Estrategia 1: Buscar en atributos data-src (lazy loading)
                for img in driver.find_elements(By.XPATH, "//img[@data-src]"):
                    src = img.get_attribute("data-src") or img.get_attribute("src")
                    if is_valid_photo(src) and src not in fotos:
                        fotos.append(src)
                
                # Estrategia 2: Buscar en tags picture o div con data-src
                if not fotos or len(fotos) < 3:
                    for picture in driver.find_elements(By.TAG_NAME, "picture"):
                        try:
                            img = picture.find_element(By.TAG_NAME, "img")
                            src = img.get_attribute("src") or img.get_attribute("data-src")
                            if is_valid_photo(src) and src not in fotos:
                                fotos.append(src)
                        except:
                            pass
                
                # Estrategia 3: Ejecutar JavaScript para obtener todas las imágenes
                try:
                    js_fotos = driver.execute_script("""
                        const excludeKeywords = ['logo', 'icon', 'placeholder', 'avatar', 'sprite', 'button',
                                                 'header', 'footer', 'nav', 'menu', 'banner', 'badge',
                                                 'mark', 'seal', 'watermark', 'instagram', 'facebook',
                                                 'youtube', 'twitter', 'social', 'share', 'arrow'];
                        return Array.from(document.querySelectorAll('img'))
                            .map(img => img.src || img.getAttribute('data-src'))
                            .filter(src => {
                                if (!src || src.length < 40) return false;
                                const lower = src.toLowerCase();
                                if (excludeKeywords.some(kw => lower.includes(kw))) return false;
                                return true;
                            })
                            .filter((src, idx, arr) => arr.indexOf(src) === idx);
                    """)
                    if js_fotos:
                        for f in js_fotos:
                            if f not in fotos:
                                fotos.append(f)
                except:
                    pass
                
                # Remover duplicados manteniendo orden
                fotos_unicas = []
                for foto in fotos:
                    if foto not in fotos_unicas:
                        fotos_unicas.append(foto)
                
                detalles["fotos"] = fotos_unicas[:10]  # Máximo 10 fotos
                if debug:
                    logger.info(f"Fotos extraídas: {len(fotos_unicas)}")
            except Exception as e:
                if debug:
                    logger.info(f"Error extrayendo fotos: {e}")
        
        except Exception as e:
            error_msg = str(e)
            if "127" in error_msg or "unexpectedly exited" in error_msg or "chromedriver" in error_msg.lower():
                logger.debug(f"BuscadorProp: Chromedriver no disponible para extraer detalles de {url}")
            else:
                logger.debug(f"Error extrayendo detalles de {url}: {type(e).__name__}: {e}")
        
        finally:
            if driver:
                try:
                    driver.quit()
                except:
                    pass
        
        return detalles
    
    @staticmethod
    def buscar_propiedades(zona: str = "Palermo", tipo: str = "venta", limit: int = 10, debug: bool = False, stop_flag=None) -> List[Dict]:
        """Scraping de BuscadorProp."""
        if debug:
            logger.info(f"BuscadorProp: buscando {tipo} en {zona}...")
        
        return BuscadorPropScraper.buscar_propiedades_selenium(zona=zona, tipo=tipo, limit=limit, debug=debug, stop_flag=stop_flag)

    @staticmethod
    def buscar_propiedades_selenium(zona: str = "Palermo", tipo: str = "venta", limit: int = 10, debug: bool = False, stop_flag=None) -> List[Dict]:
        """Scraping de BuscadorProp - extrae h2 (tipo) + dirección (span/p) + detalles + fotos."""
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
        
        # Verificar si ya se solicitó detener
        if stop_flag is not None and hasattr(stop_flag, 'scraper_stop_flag') and stop_flag.scraper_stop_flag:
            return []
        
        opts = Options()
        opts.add_argument("--headless")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
        opts.add_argument("--disable-gpu")
        opts.add_argument("--window-size=1920,1080")
        opts.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0")
        
        # Detectar si Chromium está instalado en el sistema (Streamlit Cloud)
        chromium_paths = [
            "/usr/bin/chromium-browser",  # Streamlit Cloud
            "/usr/bin/chromium",
            "/snap/bin/chromium",
            "/Applications/Chromium.app/Contents/MacOS/Chromium",  # macOS
            "C:\\Program Files\\Chromium\\Application\\chrome.exe",  # Windows
        ]
        chromium_binary = None
        for path in chromium_paths:
            if os.path.exists(path):
                chromium_binary = path
                logger.debug(f"Detectado Chromium en: {chromium_binary}")
                break
        
        if chromium_binary:
            opts.binary_location = chromium_binary
        
        out: List[Dict] = []
        driver = None
        try:
            try:
                from webdriver_manager.chrome import ChromeDriverManager
                from selenium.webdriver.chrome.service import Service
                driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opts)
            except ModuleNotFoundError as module_error:
                # webdriver_manager no está instalado
                if "webdriver_manager" in str(module_error):
                    logger.error(f"BuscadorProp error: webdriver_manager no instalado. {module_error}")
                    logger.warning(f"BuscadorProp: No se puede descargar propiedades de {zona} - falta instalar webdriver_manager")
                    return []
                else:
                    logger.error(f"BuscadorProp error de módulo: {module_error}")
                    return []
            except Exception as driver_init_error:
                # Si falla la inicialización del driver, es probable que sea por dependencias del sistema
                error_msg = str(driver_init_error)
                if "127" in error_msg or "unexpectedly exited" in error_msg or "chromedriver" in error_msg.lower():
                    logger.error(f"BuscadorProp error: Chromedriver no disponible en este entorno (falta Chromium). {error_msg}")
                    logger.warning(f"BuscadorProp: No se puede descargar propiedades de {zona} - entorno sin soporte para Selenium")
                    return []
                else:
                    logger.error(f"BuscadorProp error al inicializar driver: {type(driver_init_error).__name__}: {driver_init_error}")
                    return []
            
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
            
            for idx, link in enumerate(links[:limit]):
                # Verificar flag de stop en cada iteración
                if stop_flag is not None and hasattr(stop_flag, 'scraper_stop_flag') and stop_flag.scraper_stop_flag:
                    if debug:
                        logger.info(f"Stop solicitado en BuscadorProp, deteniendo en link {idx}")
                    break
                
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
                    
                    # Precio inicial (de la tarjeta)
                    precio = "N/A"
                    for line in parent.text.split("\n"):
                        if "$" in line or "USD" in line.upper():
                            precio = line.strip()
                            break
                    
                    # Extraer foto de la tarjeta (portada)
                    foto_portada = None
                    try:
                        img = parent.find_element(By.TAG_NAME, "img")
                        img_src = img.get_attribute("src") or img.get_attribute("data-src")
                        # Filtrar iconos y logos (no cargar URLs con palabras clave sospechosas)
                        if img_src and not any(keyword in img_src.lower() for keyword in ["icon", "logo", "star", "placeholder", "header", "footer", "nav", "button", "badge"]):
                            foto_portada = img_src
                    except:
                        pass
                    
                    # NUEVO: Extraer detalles completos de la página individual
                    detalles = BuscadorPropScraper.extraer_detalles_propiedad(href, debug=debug)
                    
                    # Usar precio completo si está disponible
                    if detalles.get("precio_completo"):
                        precio = detalles["precio_completo"]
                    
                    out.append({
                        "id": href,
                        "tipo": titulo or "Propiedad",
                        "zona": zona,
                        "precio": precio,
                        "descripcion": desc[:300],
                        "url": href,
                        "fuente": "BuscadorProp",
                        "fecha_agregado": datetime.now().isoformat(),
                        "amenities": "",
                        "habitaciones": detalles.get("dormitorios") or detalles.get("ambientes"),
                        "baños": detalles.get("baños"),
                        "pileta": None,
                        "metros_cubiertos": detalles.get("superficie_cubierta"),
                        "metros_descubiertos": detalles.get("superficie_total"),
                        "latitud": None,
                        "longitud": None,
                        "foto_portada": foto_portada,
                        "fotos": detalles.get("fotos", []),
                        "antiguedad": detalles.get("antiguedad"),
                        "estado": detalles.get("estado"),
                        "direccion": detalles.get("direccion"),
                    })
                    
                    time.sleep(random.uniform(1, 2))  # Delay entre propiedades
                except Exception as e:
                    if debug:
                        logger.info(f"Error procesando link {idx}: {e}")
                    continue
            
            if debug:
                logger.info(f"Extraídas {len(out)} propiedades")
        
        except Exception as e:
            error_msg = str(e)
            if "127" in error_msg or "unexpectedly exited" in error_msg or "chromedriver" in error_msg.lower():
                logger.error(f"BuscadorProp error: Chromedriver fallo (code 127 - dependencias del sistema): {e}")
                logger.warning(f"BuscadorProp: No se puede descargar propiedades - entorno sin soporte para Selenium")
            else:
                logger.error(f"BuscadorProp error: {e}")
        
        finally:
            if driver:
                try:
                    driver.quit()
                except:
                    pass
        
        return out


class PropertyDatabase:
    def __init__(self, db_path: str = "data/properties.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Inicializa la BD."""
        try:
            # Asegurar que la carpeta data existe
            db_dir = os.path.dirname(self.db_path)
            if db_dir and not os.path.exists(db_dir):
                os.makedirs(db_dir, exist_ok=True)
            
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
                    toilettes INTEGER,
                    pileta INTEGER,
                    metros_cubiertos REAL,
                    metros_descubiertos REAL,
                    orientacion TEXT,
                    antiguedad INTEGER,
                    descripcion TEXT,
                    amenities TEXT,
                    latitud REAL,
                    longitud REAL,
                    url TEXT,
                    fuente TEXT,
                    fecha_agregado TEXT,
                    foto_portada TEXT,
                    fotos TEXT,
                    estado TEXT,
                    direccion TEXT
                )
            """)
            
            # Crear tabla de feedback
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    propiedad_id TEXT NOT NULL,
                    tipo TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    UNIQUE(propiedad_id, tipo),
                    FOREIGN KEY(propiedad_id) REFERENCES propiedades(id)
                )
            """)
            conn.commit()
            
            # Agregar columnas nuevas si no existen (migración)
            cursor.execute("PRAGMA table_info(propiedades)")
            columns = {row[1] for row in cursor.fetchall()}
            
            nuevas_columnas = {
                'foto_portada': 'TEXT',
                'fotos': 'TEXT',
                'estado': 'TEXT',
                'direccion': 'TEXT'
            }
            
            for col_name, col_type in nuevas_columnas.items():
                if col_name not in columns:
                    try:
                        cursor.execute(f"ALTER TABLE propiedades ADD COLUMN {col_name} {col_type}")
                        logger.info(f"Agregada columna {col_name} a la BD")
                    except Exception as e:
                        logger.warning(f"Columna {col_name} ya existe o error: {e}")
            
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
                    
                    # Convertir fotos a JSON si es una lista
                    fotos_json = ""
                    if isinstance(prop.get("fotos"), list) and prop.get("fotos"):
                        import json
                        fotos_json = json.dumps(prop.get("fotos"))
                    
                    cursor.execute("""
                        INSERT OR REPLACE INTO propiedades 
                        (id, tipo, zona, precio, precio_valor, precio_moneda,
                         habitaciones, baños, toilettes, pileta, metros_cubiertos, metros_descubiertos,
                         orientacion, antiguedad, descripcion, amenities, latitud, longitud, url, fuente, fecha_agregado,
                         foto_portada, fotos, estado, direccion)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        prop.get("id", str(datetime.now())),
                        prop.get("tipo", ""),
                        prop.get("zona", ""),
                        prop.get("precio", ""),
                        precio_valor,
                        precio_moneda,
                        prop.get("habitaciones"),
                        prop.get("baños"),
                        prop.get("toilettes"),
                        1 if prop.get("pileta") else 0,
                        prop.get("metros_cubiertos"),
                        prop.get("metros_descubiertos"),
                        prop.get("orientacion"),
                        prop.get("antiguedad"),
                        prop.get("descripcion", ""),
                        prop.get("amenities", ""),
                        prop.get("latitud"),
                        prop.get("longitud"),
                        url,
                        prop.get("fuente", ""),
                        prop.get("fecha_agregado", datetime.now().isoformat()),
                        prop.get("foto_portada", ""),
                        fotos_json,
                        prop.get("estado", ""),
                        prop.get("direccion", "")
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

    def guardar_csv(self, csv_path: str = "data/properties_expanded.csv") -> None:
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

    def guardar_feedback(self, propiedad_id: str, tipo: str, timestamp: str = None) -> bool:
        """Guarda feedback de una propiedad (positivo/negativo)."""
        try:
            if timestamp is None:
                timestamp = datetime.now().isoformat()
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # INSERT OR IGNORE para evitar duplicados (constraint UNIQUE)
            cursor.execute("""
                INSERT OR IGNORE INTO feedback (propiedad_id, tipo, timestamp)
                VALUES (?, ?, ?)
            """, (propiedad_id, tipo, timestamp))
            
            conn.commit()
            conn.close()
            logger.info(f"Feedback guardado: {propiedad_id} - {tipo}")
            return True
        except Exception as e:
            logger.error(f"Error guardando feedback: {e}")
            return False

    def obtener_feedback(self) -> List[Dict]:
        """Obtiene todo el feedback guardado."""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM feedback")
            feedback = [dict(row) for row in cursor.fetchall()]
            conn.close()
            return feedback
        except Exception as e:
            logger.error(f"Error obteniendo feedback: {e}")
            return []

    def obtener_feedback_por_tipo(self, tipo: str) -> List[Dict]:
        """Obtiene feedback de un tipo específico (positivo/negativo)."""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM feedback WHERE tipo = ?", (tipo,))
            feedback = [dict(row) for row in cursor.fetchall()]
            conn.close()
            return feedback
        except Exception as e:
            logger.error(f"Error obteniendo feedback: {e}")
            return []

