#!/usr/bin/env python3
"""
normalizar_propiedades.py - Normaliza propiedades de BD a JSON y viceversa
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime
import re

class PropiedadNormalizer:
    """Normaliza propiedades para asegurar consistencia."""
    
    @staticmethod
    def normalizar_descripcion(texto_sucio: str) -> str:
        """Limpia y normaliza descripción."""
        if not texto_sucio:
            return ""
        
        # Limpiar espacios extra
        texto = re.sub(r'\s+', ' ', texto_sucio.strip())
        
        # Remover números iniciales sin sentido (ej: "30.003" que aparece en Argenprop)
        texto = re.sub(r'^[\d\.]+\s+', '', texto)
        
        # Remover duplicados de precio
        lines = texto.split()
        seen_price = False
        result = []
        for word in lines:
            if re.match(r'^\$|^USD', word):
                if not seen_price:
                    result.append(word)
                    seen_price = True
            elif word.lower() in ['expensas', 'impuestos']:
                if result and result[-1] not in ['expensas', 'impuestos']:
                    result.append(word)
            else:
                result.append(word)
        
        return ' '.join(result)[:300]
    
    @staticmethod
    def normalizar_zona(zona: str) -> str:
        """Normaliza nombre de zona."""
        if not zona:
            return ""
        
        # Capitalizar correctamente
        zona = zona.strip().title()
        
        # Reemplazos especiales
        replacements = {
            'Las Canitas': 'Las Cañitas',
            'La Boca': 'La Boca',
            'San Isidro': 'San Isidro',
            'Villa Crespo': 'Villa Crespo',
            'Lomas De Zamora': 'Lomas de Zamora',
        }
        
        for old, new in replacements.items():
            if zona.lower() == old.lower():
                return new
        
        return zona
    
    @staticmethod
    def normalizar_precio(precio_texto: str) -> dict:
        """Extrae y normaliza precio."""
        if not precio_texto or precio_texto == "N/A":
            return {"valor": 0, "moneda": "USD", "texto": precio_texto}
        
        # Buscar números
        numeros = re.findall(r'[\d,\.]+', precio_texto)
        
        # Buscar moneda
        moneda = "USD" if "USD" in precio_texto.upper() else "$" if "$" in precio_texto else "USD"
        
        valor = 0
        if numeros:
            # Tomar el primer número significativo
            num_str = numeros[0].replace('.', '').replace(',', '')
            try:
                valor = int(num_str)
            except:
                pass
        
        return {
            "valor": valor,
            "moneda": moneda,
            "texto": precio_texto
        }
    
    @staticmethod
    def normalizar_propiedad(prop: dict) -> dict:
        """Normaliza una propiedad completa."""
        return {
            "id": prop.get("id", "").strip(),
            "tipo": prop.get("tipo", "Propiedad").strip(),
            "zona": PropiedadNormalizer.normalizar_zona(prop.get("zona", "")),
            "precio": PropiedadNormalizer.normalizar_precio(prop.get("precio", "N/A")),
            "descripcion": PropiedadNormalizer.normalizar_descripcion(prop.get("descripcion", "")),
            "habitaciones": int(prop.get("habitaciones", 0)) if prop.get("habitaciones") else None,
            "baños": int(prop.get("baños", 0)) if prop.get("baños") else None,
            "pileta": bool(prop.get("pileta")) if prop.get("pileta") is not None else False,
            "metros_cubiertos": float(prop.get("metros_cubiertos", 0)) if prop.get("metros_cubiertos") else None,
            "metros_descubiertos": float(prop.get("metros_descubiertos", 0)) if prop.get("metros_descubiertos") else None,
            "amenities": prop.get("amenities", "").strip(),
            "latitud": float(prop.get("latitud")) if prop.get("latitud") else None,
            "longitud": float(prop.get("longitud")) if prop.get("longitud") else None,
            "url": prop.get("url", "").strip(),
            "fuente": prop.get("fuente", "Desconocida").strip(),
            "fecha_agregado": prop.get("fecha_agregado", datetime.now().isoformat())
        }
    
    @staticmethod
    def exportar_a_json(db_path: str, json_path: str = "propiedades.json") -> int:
        """Exporta BD a JSON normalizado."""
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM propiedades")
        rows = cursor.fetchall()
        
        propiedades = []
        for row in rows:
            prop_dict = dict(row)
            prop_normalizada = PropiedadNormalizer.normalizar_propiedad(prop_dict)
            propiedades.append(prop_normalizada)
        
        conn.close()
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(propiedades, f, ensure_ascii=False, indent=2)
        
        return len(propiedades)
    
    @staticmethod
    def importar_desde_json(json_path: str, db_path: str = "properties.db") -> int:
        """Importa JSON normalizado a BD (reemplazando)."""
        with open(json_path, 'r', encoding='utf-8') as f:
            propiedades = json.load(f)
        
        # Recrear tabla (limpiar primero)
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Borrar tabla
        cursor.execute("DROP TABLE IF EXISTS propiedades")
        
        # Crear tabla
        cursor.execute("""
            CREATE TABLE propiedades (
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
        
        # Insertar datos normalizados
        insertadas = 0
        for prop in propiedades:
            try:
                cursor.execute("""
                    INSERT INTO propiedades 
                    (id, tipo, zona, precio, precio_valor, precio_moneda, 
                     habitaciones, baños, pileta, metros_cubiertos, metros_descubiertos,
                     descripcion, amenities, latitud, longitud, url, fuente, fecha_agregado)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    prop["id"],
                    prop["tipo"],
                    prop["zona"],
                    prop["precio"]["texto"],
                    prop["precio"]["valor"],
                    prop["precio"]["moneda"],
                    prop["habitaciones"],
                    prop["baños"],
                    1 if prop["pileta"] else 0,
                    prop["metros_cubiertos"],
                    prop["metros_descubiertos"],
                    prop["descripcion"],
                    prop["amenities"],
                    prop["latitud"],
                    prop["longitud"],
                    prop["url"],
                    prop["fuente"],
                    prop["fecha_agregado"]
                ))
                insertadas += 1
            except Exception as e:
                print(f"Error insertando {prop.get('id', 'desconocido')}: {e}")
        
        conn.commit()
        conn.close()
        
        return insertadas

if __name__ == "__main__":
    # Exportar a JSON
    print("Exportando BD a JSON...")
    count = PropiedadNormalizer.exportar_a_json("properties.db", "propiedades.json")
    print(f"✓ {count} propiedades exportadas a propiedades.json")
    
    # Ver JSON
    print("\nMostrando primeras 2 propiedades normalizadas:")
    with open("propiedades.json", 'r', encoding='utf-8') as f:
        props = json.load(f)
        for i, prop in enumerate(props[:2], 1):
            print(f"\n--- Propiedad {i} ---")
            print(json.dumps(prop, ensure_ascii=False, indent=2))
    
    # Reimportar a BD
    print("\n\nReimportando desde JSON a BD...")
    count = PropiedadNormalizer.importar_desde_json("propiedades.json")
    print(f"✓ {count} propiedades reimportadas y normalizadas")
