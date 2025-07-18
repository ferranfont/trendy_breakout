import pandas as pd
import os
from chart_volume import plot_close_and_volume

# === CONFIGURACIÓN ===
media_period = 200             # Periodo de la EMA
directorio = '../DATA'
nombre_fichero = 'export_GC_2015_formatted.csv'
ruta_completa = os.path.join(directorio, nombre_fichero)

# === CARGA Y FILTRO RÁPIDO ===
cols = ['Date', 'Open', 'High', 'Low', 'Close', 'Volumen']
df = pd.read_csv(ruta_completa, usecols=cols)
df.columns = [c.lower().replace('volumen', 'volume') for c in df.columns]

# Convertir columna de fecha a datetime y fijarla como índice (fundamental para resample)
df['date'] = pd.to_datetime(df['date'], utc=True)
df = df.set_index('date')

# === RESAMPLE A VELAS DIARIAS (OHLCV) ===
velas_diarias = df.resample('1D').agg({
    'open': 'first',
    'high': 'max',
    'low': 'min',
    'close': 'last',
    'volume': 'sum'
})

# === CÁLCULO DE MEDIA MÓVIL EXPONENCIAL (EMA) ===
velas_diarias['ema'] = velas_diarias['close'].ewm(span=media_period, adjust=False).mean().round(2)
velas_diarias['ema'] = velas_diarias['ema'].shift(1)  # Evita lookahead bias


print('Fichero:', ruta_completa, 'importado')
print(f"Características del DataFrame diario: {velas_diarias.shape}")
print(velas_diarias.head(3))

# === GRAFICAR ===
plot_close_and_volume(timeframe=1, df=velas_diarias.reset_index())

# === GUARDAR EL DATAFRAME DIARIO EN CSV ===
velas_diarias.to_csv('../DATA/GC_1D_2015.csv', index=True)
print('Archivo guardado como ../DATA/GC_1D_2015.csv')