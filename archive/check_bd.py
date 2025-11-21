#!/usr/bin/env python3
"""Ver qué propiedades hay en BD ahora"""

import sqlite3

conn = sqlite3.connect('properties.db')
cursor = conn.cursor()

cursor.execute("""
    SELECT zona, COUNT(*) as cnt
    FROM propiedades
    GROUP BY zona
    ORDER BY cnt DESC
""")

print("Propiedades por zona:")
for zona, cnt in cursor.fetchall():
    print(f"  {zona}: {cnt}")

cursor.execute("""
    SELECT zona, fuente, COUNT(*) as cnt
    FROM propiedades
    GROUP BY zona, fuente
    ORDER BY zona, fuente
""")

print("\nDetalle por zona y fuente:")
for zona, fuente, cnt in cursor.fetchall():
    print(f"  {zona} ({fuente}): {cnt}")

conn.close()
