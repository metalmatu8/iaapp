#!/usr/bin/env python3
"""
Script para inicializar la base de datos con estructura vacía pero funcional.
Úsalo cuando borre la BD y quieras empezar de cero.
"""

import os
import sys
import sqlite3
from datetime import datetime

def init_database():
    """Crea la estructura de BD vacía pero lista para usar."""
    
    # Crear carpeta data si no existe
    os.makedirs("data", exist_ok=True)
    
    db_path = "data/properties.db"
    
    # Crear/conectar a BD
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Crear tabla propiedades con todas las columnas
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
    
    conn.commit()
    conn.close()
    
    print(f"✅ Base de datos inicializada en {db_path}")
    print("   La tabla 'propiedades' está lista para recibir datos")
    print("\n📋 Próximos pasos:")
    print("   1. Ejecuta: python -m streamlit run app.py")
    print("   2. En la app, ve a 'Descargar de Internet'")
    print("   3. Selecciona un portal (Argenprop, BuscadorProp, etc)")
    print("   4. Selecciona una zona y cantidad")
    print("   5. ¡Descarga tus primeras propiedades!")

if __name__ == "__main__":
    init_database()
