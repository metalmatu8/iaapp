#!/usr/bin/env python3
"""
Ejemplo de uso del scraper mejorado de BuscadorProp
Descarga propiedades y las guarda en la BD
"""

import sys
sys.path.insert(0, 'src')

from scrapers import BuscadorPropScraper, PropertyDatabase
import time

print("=" * 80)
print("SCRAPER MEJORADO DE BUSCADORPROP - DEMO")
print("=" * 80)

# Configurar zona a buscar
zona = "Lomas de Zamora"
tipo = "casas"
limite = 5

print(f"\n🔍 Buscando {limite} {tipo} en venta en {zona}...")
print("⏳ Esto puede tomar algunos minutos...\n")

try:
    # Descargar propiedades
    propiedades = BuscadorPropScraper.buscar_propiedades(
        zona=zona,
        tipo=tipo,
        limit=limite,
        debug=True
    )
    
    print(f"\n✅ Se encontraron {len(propiedades)} propiedades")
    
    if propiedades:
        # Guardar en BD
        print("\n💾 Guardando en base de datos...")
        db = PropertyDatabase()
        agregadas = db.agregar_propiedades(propiedades)
        
        print(f"✅ {agregadas} propiedades guardadas en BD")
        
        # Mostrar resumen
        print("\n" + "=" * 80)
        print("RESUMEN DE PROPIEDADES DESCARGADAS")
        print("=" * 80)
        
        for idx, prop in enumerate(propiedades, 1):
            print(f"\n{idx}. {prop['tipo']}")
            print(f"   📍 {prop['direccion']}")
            print(f"   💰 {prop['precio']}")
            print(f"   🏠 {prop['habitaciones']} hab | {prop['baños']} baños")
            print(f"   📐 {prop['metros_cubiertos']}m² cubiertos | {prop['metros_descubiertos']}m² totales")
            print(f"   ℹ️  {prop['estado']}")
            fotos = prop.get('fotos', [])
            if isinstance(fotos, str):
                import json
                try:
                    fotos = json.loads(fotos)
                except:
                    fotos = []
            print(f"   📸 {len(fotos)} fotos")
        
        # Mostrar estadísticas de BD
        print("\n" + "=" * 80)
        print("ESTADÍSTICAS DE BASE DE DATOS")
        print("=" * 80)
        
        stats = db.obtener_estadisticas()
        print(f"Total de propiedades: {stats.get('total_propiedades', 0)}")
        print(f"Por zona:")
        for zona_stat, count in stats.get('propiedades_por_zona', {}).items():
            print(f"  - {zona_stat}: {count}")
        print(f"Por fuente:")
        for fuente, count in stats.get('propiedades_por_fuente', {}).items():
            print(f"  - {fuente}: {count}")
        
        # Exportar CSV
        print("\n💾 Exportando a CSV...")
        db.guardar_csv("properties_export.csv")
        print("✅ Archivo properties_export.csv creado")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("✅ DEMO COMPLETADA")
print("=" * 80)
