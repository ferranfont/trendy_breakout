# código que evalua si un producto es tendencial o mean-reversión enbase a su rendimiento al romper máximos y mínimos

import pandas as pd
from chart_volume import plot_close_and_volume
from strat_break_OM import generate_trades_with_limits
from strat_break_OM import summarize_trades
import os
import plotly.graph_objects as go
from breaks import breaks


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


# === APLICAR BREAKOUTS ===
df = breaks(df)
print(df)

# === GRAFICAR VELAS DIARIAS Y VOLUMEN ===
plot_close_and_volume(timeframe=timeframe, df=df, symbol=symbol)
print(f"Gráfico de {symbol} en timeframe {timeframe} generado.")


# Supón que tu DataFrame se llama 'df' y tiene columnas ['date', 'breakout', 'breakdown']

trades_df = generate_trades_with_limits(df)
summary_df = summarize_trades(trades_df)
print(summary_df.head(50))
total_profit_usd = summary_df['profit_usd'].sum()
print(f"🔹 TOTAL PROFIT (USD): {total_profit_usd:,.2f}")


