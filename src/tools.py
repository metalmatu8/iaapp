"""
tools.py - Herramientas externas (Tool Use) para el Agente RAG
Fase 3: Integración con Google Maps, APIs de datos geoespaciales, etc.
"""

from typing import Dict, List, Tuple, Optional
from config import GOOGLE_MAPS_API_KEY
import logging

logger = logging.getLogger(__name__)


class ToolExecutor:
    """Ejecuta herramientas (tools) externas para mejorar recomendaciones"""
    
    def __init__(self):
        self.google_maps_available = bool(GOOGLE_MAPS_API_KEY)
    
    def calcular_distancia_viaje(self, origen: str, destino: str) -> Optional[Dict]:
        """
        Calcula tiempo de viaje de una propiedad a un destino (ej: trabajo, colegio)
        
        Requiere: GOOGLE_MAPS_API_KEY
        
        Args:
            origen: Dirección de origen (ej: "Palermo, Buenos Aires")
            destino: Dirección de destino (ej: "Torre de Catalinas, CABA")
        
        Returns:
            Dict con distancia, tiempo, modo de transporte
        """
        if not self.google_maps_available:
            logger.warning("Google Maps API no configurada. Saltando cálculo de distancia.")
            return None
        
        try:
            import googlemaps
            gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)
            
            # Consultar distancia
            result = gmaps.distance_matrix(
                origins=[origen],
                destinations=[destino],
                modes=["driving", "transit", "walking"],
                units="metric"
            )
            
            if result['status'] == 'OK':
                element = result['rows'][0]['elements'][0]
                return {
                    'distancia_km': element['distance']['value'] / 1000,
                    'tiempo_minutos': element['duration']['value'] / 60,
                    'status': 'OK'
                }
            else:
                return {'status': result['status']}
        
        except ImportError:
            logger.error("googlemaps no está instalado. Instala con: pip install googlemaps")
            return None
        except Exception as e:
            logger.error(f"Error calculando distancia: {str(e)}")
            return None
    
    def verificar_proximidad_colegios(self, ubicacion: str, radio_km: int = 2) -> Optional[List[Dict]]:
        """
        Busca colegios cercanos a una propiedad
        
        Requiere: GOOGLE_MAPS_API_KEY
        
        Args:
            ubicacion: Dirección o coordenadas de la propiedad
            radio_km: Radio de búsqueda en km
        
        Returns:
            Lista de colegios cercanos
        """
        if not self.google_maps_available:
            logger.warning("Google Maps API no configurada. Saltando búsqueda de colegios.")
            return None
        
        try:
            import googlemaps
            gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)
            
            # Geocodificar ubicación
            geocode_result = gmaps.geocode(address=ubicacion)
            if not geocode_result:
                return None
            
            lat = geocode_result[0]['geometry']['location']['lat']
            lng = geocode_result[0]['geometry']['location']['lng']
            
            # Buscar colegios cercanos
            places_result = gmaps.places_nearby(
                location=(lat, lng),
                radius=radio_km * 1000,
                type='school'
            )
            
            colegios = []
            for place in places_result.get('results', []):
                colegios.append({
                    'nombre': place['name'],
                    'distancia': place.get('vicinity', 'N/A'),
                    'rating': place.get('rating', 'N/A')
                })
            
            return colegios
        
        except ImportError:
            logger.error("googlemaps no está instalado.")
            return None
        except Exception as e:
            logger.error(f"Error buscando colegios: {str(e)}")
            return None
    
    def verificar_zona_segura(self, ubicacion: str) -> Optional[Dict]:
        """
        Verifica estadísticas de seguridad de una zona (implementación futura)
        Puede integrarse con APIs de estadísticas públicas o bases de datos de criminalidad
        
        Args:
            ubicacion: Dirección de la propiedad
        
        Returns:
            Score de seguridad y detalles
        """
        # TODO: Integrar con API de estadísticas de seguridad
        # Ej: datos públicos de Buenos Aires, CABA, etc.
        logger.info(f"Verificación de seguridad para {ubicacion}: Función en desarrollo")
        return None
    
    def obtener_info_zona(self, zona: str) -> Optional[Dict]:
        """
        Obtiene información demográfica y socioeconómica de una zona
        
        Args:
            zona: Nombre del barrio/zona
        
        Returns:
            Información de la zona (población, densidad, etc.)
        """
        # TODO: Integrar con APIs de datos socioeconómicos
        logger.info(f"Información de zona {zona}: Función en desarrollo")
        return None


class AgentTools:
    """Conjunto de herramientas disponibles para el Agente autónomo (Fase 3)"""
    
    def __init__(self):
        self.executor = ToolExecutor()
        self.tools = {
            "calcular_distancia": self.executor.calcular_distancia_viaje,
            "buscar_colegios": self.executor.verificar_proximidad_colegios,
            "verificar_seguridad": self.executor.verificar_zona_segura,
            "info_zona": self.executor.obtener_info_zona
        }
    
    def listar_herramientas(self) -> List[Dict]:
        """Retorna lista de herramientas disponibles (para LLM)"""
        return [
            {
                "nombre": "calcular_distancia",
                "descripcion": "Calcula tiempo de viaje de una propiedad a un destino",
                "parametros": ["origen", "destino"]
            },
            {
                "nombre": "buscar_colegios",
                "descripcion": "Encuentra colegios cercanos a una propiedad",
                "parametros": ["ubicacion", "radio_km"]
            },
            {
                "nombre": "verificar_seguridad",
                "descripcion": "Verifica índice de seguridad de una zona",
                "parametros": ["ubicacion"]
            },
            {
                "nombre": "info_zona",
                "descripcion": "Obtiene información demográfica de una zona",
                "parametros": ["zona"]
            }
        ]
    
    def ejecutar_tool(self, tool_name: str, **kwargs) -> Optional[Dict]:
        """Ejecuta una herramienta específica"""
        if tool_name not in self.tools:
            logger.error(f"Tool no encontrada: {tool_name}")
            return None
        
        try:
            return self.tools[tool_name](**kwargs)
        except Exception as e:
            logger.error(f"Error ejecutando tool {tool_name}: {str(e)}")
            return None
