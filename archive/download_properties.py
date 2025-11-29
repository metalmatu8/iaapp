#!/usr/bin/env python
"""
download_properties.py - Script para descargar propiedades reales de internet
Ejecutar: python download_properties.py

Descarga propiedades de MercadoLibre y las almacena en CSV
"""

import sys
import time
from scrapers import MercadoLibreScraper, PropertyDatabase
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def descargar_propiedades_argentina():
    """
    Descarga propiedades de múltiples zonas de Buenos Aires
    Objetivo: Obtener cientos de miles de propiedades
    """
    
    print("=" * 70)
    print(" DESCARGADOR DE PROPIEDADES INMOBILIARIAS - ARGENTINA")
    print("=" * 70)
    print()
    
    # Zonas principales de Buenos Aires
    zonas = {
        "Capital Federal": [
            "Palermo", "Recoleta", "San Isidro", "Belgrano", "Flores",
            "Caballito", "La Boca", "San Telmo", "Villa Crespo", "Colegiales",
            "Almagro", "Balvanera", "Barracas", "Chacarita", "Constitución",
            "Retiro", "Núñez", "Parque Patricios", "Parque Chacabuco", "Villa Pueyrredón"
        ],
        "Gran Buenos Aires": [
            "San Justo", "Morón", "Ituzaingó", "Lanús", "Avellaneda",
            "Berazategui", "La Matanza", "Merlo", "Almágro", "Hurlingham"
        ]
    }
    
    db = PropertyDatabase("properties.csv")
    stats_inicio = db.obtener_estadisticas()
    
    print(f"Estado actual: {stats_inicio['total_propiedades']} propiedades\n")
    
    total_descargadas = 0
    total_nuevas = 0
    
    # Descargar por región
    for region, lista_zonas in zonas.items():
        print(f"\n{'='*70}")
        print(f"📍 REGIÓN: {region}")
        print(f"{'='*70}")
        
        for i, zona in enumerate(lista_zonas, 1):
            try:
                print(f"\n[{i}/{len(lista_zonas)}] Descargando {zona}...", end=" ")
                
                # Búsqueda 1: Casa
                props_casa = MercadoLibreScraper.buscar_propiedades(
                    f"casa {zona}", 
                    limit=50
                )
                nuevas_casa = db.agregar_propiedades(props_casa)
                
                # Búsqueda 2: Departamento
                props_depto = MercadoLibreScraper.buscar_propiedades(
                    f"departamento {zona}", 
                    limit=50
                )
                nuevas_depto = db.agregar_propiedades(props_depto)
                
                nuevas = nuevas_casa + nuevas_depto
                total_nuevas += nuevas
                total_descargadas += len(props_casa) + len(props_depto)
                
                print(f"✅ {nuevas} nuevas propiedades")
                
                # Respetar rate limits
                time.sleep(1)
            
            except Exception as e:
                print(f"❌ Error: {str(e)}")
                continue
    
    # Guardar y mostrar estadísticas
    print(f"\n{'='*70}")
    print("GUARDANDO DATOS...")
    print(f"{'='*70}")
    
    db.guardar("properties_expanded.csv")
    
    stats_final = db.obtener_estadisticas()
    
    print(f"""
✅ DESCARGA COMPLETADA

Estadísticas:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Total propiedades:    {stats_final['total_propiedades']}
  Nuevas propiedades:   {total_nuevas}
  Zonas únicas:         {stats_final['zonas']}
  Precio promedio:      ${stats_final['precio_promedio']:,.0f}
  Fuentes:              {', '.join(stats_final['fuentes'])}
  Archivo:              properties_expanded.csv
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Próximos pasos:
1. Reinicia la app: streamlit run app.py
2. Las nuevas propiedades estarán disponibles automáticamente
3. Repite esta descarga regularmente para mantener actualizado
    """)


def descargar_propiedades_personalizado(zonas: list, limite_por_zona: int = 50):
    """
    Descarga propiedades de zonas personalizadas
    
    Uso:
        python download_properties.py
    """
    
    db = PropertyDatabase("properties.csv")
    
    print(f"Descargando propiedades de: {', '.join(zonas)}")
    
    for zona in zonas:
        print(f"\n📍 {zona}...", end=" ")
        
        props = MercadoLibreScraper.buscar_propiedades(
            f"inmueble {zona}",
            limit=limite_por_zona
        )
        
        nuevas = db.agregar_propiedades(props)
        print(f"✅ {nuevas} nuevas")
        
        time.sleep(1)
    
    db.guardar("properties_expanded.csv")
    print("\n✅ Guardado en properties_expanded.csv")


if __name__ == "__main__":
    
    if len(sys.argv) > 1:
        # Uso personalizado: python download_properties.py Palermo Recoleta San-Isidro
        zonas = sys.argv[1:]
        descargar_propiedades_personalizado(zonas)
    else:
        # Descarga masiva de todo Buenos Aires
        descargar_propiedades_argentina()
