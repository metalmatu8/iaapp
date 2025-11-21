#!/usr/bin/env python3

from scrapers import PropertyDatabase
import pandas as pd

db = PropertyDatabase()
df = db.obtener_df()

print('Primeras propiedades de obtener_df():')
print(df[['id', 'zona', 'tipo']].head(3))
print(f'\nTotal: {len(df)} propiedades')
print(f'Tipo de ID: {df["id"].dtype}')
print(f'\nPrimer ID completo:')
print(f'  {df["id"].iloc[0]}')
