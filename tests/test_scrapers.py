#!/usr/bin/env python3
"""Script de prueba para verificar que los scrapers funcionen correctamente."""

from scrapers import ZonapropScraper, ArgenpropScraper, PropertyDatabase
import sys

def test_scrapers():
    print("=" * 60)
    print("PRUEBA DE SCRAPERS CON FALLBACK")
    print("=" * 60)
    
    db = PropertyDatabase()
    total_agregadas = 0
    
    # Test Zonaprop
    print("\n[1] Probando Zonaprop (requests + fallback Selenium)...")
    try:
        props = ZonapropScraper.buscar_propiedades(zona="Palermo", tipo="venta", limit=5, debug=True)
        print(f"   ✓ Zonaprop devolvió: {len(props)} propiedades")
        if props:
            nuevas = db.agregar_propiedades(props)
            total_agregadas += nuevas
            print(f"   ✓ Agregadas {nuevas} propiedades nuevas a la BD")
            print(f"   Ejemplo: {props[0]['descripcion'][:80]}...")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Test Argenprop
    print("\n[2] Probando Argenprop (requests + fallback Selenium)...")
    try:
        props = ArgenpropScraper.buscar_propiedades(zona="Palermo", tipo="Venta", limit=5, debug=True)
        print(f"   ✓ Argenprop devolvió: {len(props)} propiedades")
        if props:
            nuevas = db.agregar_propiedades(props)
            total_agregadas += nuevas
            print(f"   ✓ Agregadas {nuevas} propiedades nuevas a la BD")
            print(f"   Ejemplo: {props[0]['descripcion'][:80]}...")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Estadísticas finales
    print("\n" + "=" * 60)
    stats = db.obtener_estadisticas()
    print(f"RESULTADO FINAL:")
    print(f"  - Total propiedades en BD: {stats['total_propiedades']}")
    print(f"  - Propiedades agregadas en esta ejecución: {total_agregadas}")
    fuentes = [f for f in stats['fuentes'] if f]
    print(f"  - Fuentes: {', '.join(fuentes) if fuentes else 'ninguna'}")
    zonas = [z for z in stats['zonas'] if z]
    print(f"  - Zonas: {', '.join(zonas) if zonas else 'ninguna'}")
    print("=" * 60)

if __name__ == "__main__":
    test_scrapers()
