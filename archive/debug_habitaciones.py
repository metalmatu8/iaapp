#!/usr/bin/env python3

from scrapers import PropertyDatabase
import pandas as pd

db = PropertyDatabase()
df = db.obtener_df()

print(f"Total propiedades: {len(df)}")
print(f"\nColumna 'habitaciones':")
print(df[['zona', 'habitaciones']].head(10))
print(f"\nNulos en habitaciones: {df['habitaciones'].isna().sum()}")
print(f"Valores únicos: {df['habitaciones'].unique()}")
print(f"Tipo: {df['habitaciones'].dtype}")

# Test filtro
df_test = df[df['habitaciones'] >= 1]
print(f"\nPropiedades con habitaciones >= 1: {len(df_test)}")
