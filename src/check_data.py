#!/usr/bin/env python3
from scrapers import PropertyDatabase
import pandas as pd

db = PropertyDatabase('../data/properties.db')
df = db.obtener_df()

print(f"Total de propiedades en BD: {len(df)}")
if df.empty:
    print("❌ LA BD ESTÁ VACÍA")
else:
    print(f"✅ Columnas: {list(df.columns)}")
    print(f"✅ Primeras propiedades:")
    print(df[['id', 'zona', 'precio', 'descripcion']].head())
