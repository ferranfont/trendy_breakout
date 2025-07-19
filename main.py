# código que evalua si un producto es tendencial o mean-reversión enbase a su rendimiento al romper máximos y mínimos

import pandas as pd
from chart_volume import plot_close_and_volume
import plotly.graph_objects as go


symbol = 'GC'
timeframe = '1D'    

# === LECTURA DEL ARCHIVO DE VELAS DIARIAS ===
ruta_archivo = '../DATA/GC_1D_2015.csv'

# Cargar el CSV y parsear la columna 'date' como fecha
df = pd.read_csv(ruta_archivo, parse_dates=['date'])

# Asegurar que 'date' es índice tipo fecha
df = df.set_index('date')

print("Archivo cargado:")
print(df.head())
print(df.info())

# === GRAFICAR VELAS DIARIAS Y VOLUMEN ===
plot_close_and_volume(timeframe=timeframe, df=df, symbol=symbol)
print(f"Gráfico de {symbol} en timeframe {timeframe} generado.")

