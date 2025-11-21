#!/usr/bin/env python3
"""Test script for new Argenprop y BuscadorProp scrapers with Google Search."""

from scrapers import ArgenpropScraper, BuscadorPropScraper, PropertyDatabase
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def test_argenprop():
    """Test Argenprop Scraper."""
    logger.info("=" * 60)
    logger.info("TESTING ARGENPROP")
    logger.info("=" * 60)
    
    try:
        props = ArgenpropScraper.buscar_propiedades(
            zona="Palermo",
            tipo="Venta",
            limit=5,
            debug=True
        )
        
        logger.info(f"\n✅ Argenprop: {len(props)} propiedades encontradas")
        
        if props:
            logger.info("\nPrimera propiedad:")
            p = props[0]
            logger.info(f"  Zona: {p.get('zona')}")
            logger.info(f"  Precio: {p.get('precio')}")
            logger.info(f"  Descripción: {p.get('descripcion')[:80]}...")
            logger.info(f"  URL: {p.get('url')}")
        
        return len(props)
    except Exception as e:
        logger.error(f"❌ Argenprop Error: {e}")
        import traceback
        traceback.print_exc()
        return 0

def test_buscadorprop():
    """Test BuscadorProp Scraper."""
    logger.info("\n" + "=" * 60)
    logger.info("TESTING BUSCADORPROP")
    logger.info("=" * 60)
    
    try:
        props = BuscadorPropScraper.buscar_propiedades(
            zona="Palermo",
            tipo="venta",
            limit=5,
            debug=True
        )
        
        logger.info(f"\n✅ BuscadorProp: {len(props)} propiedades encontradas")
        
        if props:
            logger.info("\nPrimera propiedad:")
            p = props[0]
            logger.info(f"  Zona: {p.get('zona')}")
            logger.info(f"  Precio: {p.get('precio')}")
            logger.info(f"  Descripción: {p.get('descripcion')[:80]}...")
            logger.info(f"  URL: {p.get('url')}")
        
        return len(props)
    except Exception as e:
        logger.error(f"❌ BuscadorProp Error: {e}")
        import traceback
        traceback.print_exc()
        return 0

def test_database():
    """Test database integration."""
    logger.info("\n" + "=" * 60)
    logger.info("TESTING DATABASE")
    logger.info("=" * 60)
    
    try:
        db = PropertyDatabase()
        
        # Agregue propiedades de prueba desde Argenprop
        props_arg = ArgenpropScraper.buscar_propiedades(zona="Recoleta", limit=3, debug=False)
        props_buscador = BuscadorPropScraper.buscar_propiedades(zona="Belgrano", limit=3, debug=False)
        
        total_props = props_arg + props_buscador
        
        if total_props:
            nuevas = db.agregar_propiedades(total_props)
            logger.info(f"\n✅ Agregadas {nuevas} propiedades a BD")
            
            stats = db.obtener_estadisticas()
            logger.info(f"  Total en BD: {stats['total_propiedades']}")
            logger.info(f"  Fuentes: {stats['fuentes']}")
            logger.info(f"  Zonas: {stats['zonas']}")
        else:
            logger.warning("⚠️ No hay propiedades para agregar")
    
    except Exception as e:
        logger.error(f"❌ Database Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    argenprop_count = test_argenprop()
    buscadorprop_count = test_buscadorprop()
    
    logger.info("\n" + "=" * 60)
    logger.info("SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Argenprop: {argenprop_count} propiedades")
    logger.info(f"BuscadorProp: {buscadorprop_count} propiedades")
    logger.info(f"Total: {argenprop_count + buscadorprop_count} propiedades")
    
    if argenprop_count > 0 or buscadorprop_count > 0:
        logger.info("\n✅ Scraping exitoso - probando BD...")
        test_database()
    else:
        logger.error("\n❌ Ningún scraper devolvió propiedades")
