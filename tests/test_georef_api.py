#!/usr/bin/env python3
"""
Obtener provincias y localidades de Argentina desde APIs públicas
"""

import requests
import json

# API del INDEC (Instituto Nacional de Estadística y Censos) - Argentina
# Alternativa: API de Georef

def obtener_provincias_georef():
    """Obtener provincias desde la API Georef (Argentina)"""
    try:
        url = "https://apis.datos.gob.ar/georef/api/provincias"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            provincias = [p['nombre'] for p in data.get('provincias', [])]
            return provincias
    except Exception as e:
        print(f"Error Georef provincias: {e}")
    return []

def obtener_municipios_georef(provincia_id=None):
    """Obtener municipios/localidades desde la API Georef"""
    try:
        url = "https://apis.datos.gob.ar/georef/api/municipios"
        params = {}
        if provincia_id:
            params['provincia'] = provincia_id
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            municipios = [m['nombre'] for m in data.get('municipios', [])]
            return municipios
    except Exception as e:
        print(f"Error Georef municipios: {e}")
    return []

def obtener_datos_completos_georef():
    """Obtener todas las provincias y sus municipios"""
    try:
        print("Obteniendo provincias...")
        url = "https://apis.datos.gob.ar/georef/api/provincias?max=24"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            resultado = {}
            for prov in data.get('provincias', [])[:5]:  # Primeras 5 para test
                print(f"  Obteniendo municipios de {prov['nombre']}...")
                resultado[prov['nombre']] = obtener_municipios_georef(prov['id'])
            return resultado
    except Exception as e:
        print(f"Error: {e}")
    return {}

if __name__ == "__main__":
    print("=== Test API Georef (Argentina) ===\n")
    
    # Obtener provincias
    provincias = obtener_provincias_georef()
    print(f"Provincias encontradas: {len(provincias)}")
    print(f"Primeras 5: {provincias[:5]}\n")
    
    # Obtener datos completos
    datos = obtener_datos_completos_georef()
    print(f"\nProvincias con datos: {len(datos)}")
    for prov, munis in datos.items():
        print(f"  {prov}: {len(munis)} municipios")
        print(f"    Primeros 3: {munis[:3]}")
