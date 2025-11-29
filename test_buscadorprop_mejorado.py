#!/usr/bin/env python3
"""Script de prueba para el scraper mejorado de BuscadorProp"""

import sys
import os

# Configurar encoding para Windows
if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, 'src')

from scrapers import BuscadorPropScraper
import json

print("=" * 80)
print("PRUEBA DE SCRAPER MEJORADO DE BUSCADORPROP")
print("=" * 80)

# Probar con una búsqueda de prueba
zona = "lomas-de-zamora-temperley"
print(f"\nBuscando propiedades en {zona}...")

propiedades = BuscadorPropScraper.buscar_propiedades(
    zona="lomas de zamora",
    tipo="casas",
    limit=3,
    debug=True
)

print(f"\nSe encontraron {len(propiedades)} propiedades")

# Mostrar detalles de cada propiedad
for idx, prop in enumerate(propiedades, 1):
    print(f"\n{'='*80}")
    print(f"PROPIEDAD {idx}")
    print(f"{'='*80}")
    
    print(f"Tipo: {prop.get('tipo')}")
    print(f"Zona: {prop.get('zona')}")
    print(f"Precio: {prop.get('precio')}")
    print(f"Direccion: {prop.get('direccion', 'N/A')}")
    print(f"Descripcion: {prop.get('descripcion', 'N/A')[:100]}...")
    
    print(f"\nCARACTERISTICAS:")
    print(f"  - Habitaciones: {prop.get('habitaciones')}")
    print(f"  - Baños: {prop.get('baños')}")
    print(f"  - M2 Cubiertos: {prop.get('metros_cubiertos')}")
    print(f"  - M2 Total: {prop.get('metros_descubiertos')}")
    print(f"  - Antiguedad: {prop.get('antiguedad')} años")
    print(f"  - Estado: {prop.get('estado')}")
    
    print(f"\nFOTOS:")
    print(f"  - Portada: {'Si' if prop.get('foto_portada') else 'No'}")
    fotos = prop.get('fotos', [])
    if isinstance(fotos, str):
        try:
            fotos = json.loads(fotos)
        except:
            fotos = []
    print(f"  - Total de fotos: {len(fotos)}")
    if fotos:
        for i, foto in enumerate(fotos[:3], 1):
            print(f"    {i}. {foto[:60]}...")
    
    print(f"\nURL: {prop.get('url')}")
    print(f"Fuente: {prop.get('fuente')}")

print(f"\n{'='*80}")
print("PRUEBA COMPLETADA")
print(f"{'='*80}")
