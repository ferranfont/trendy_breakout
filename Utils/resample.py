import sys
import os
import pandas as pd

# Añade la carpeta principal al path para poder importar chart_volume
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from chart_volume import plot_close_and_volume

# === CONFIGURACIÓN ===
media_period = 200
nombre_fichero = 'export_GC_2015_formatted.csv'

# Rutas correctas para DATA al mismo nivel que trendy_breakout
script_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.abspath(os.path.join(script_dir, '..', '..', 'DATA'))
ruta_completa = os.path.join(data_dir, nombre_fichero)
ruta_salida = os.path.join(data_dir, 'GC_1D_2015.csv')

# Chequeo de archivo
if not os.path.exists(ruta_completa):
    print(f"ERROR: No se encuentra el archivo de datos en:\n{ruta_completa}")
    print("¿Estás seguro de que el archivo está en la carpeta DATA?")
    exit()

# === CARGA Y FILTRO RÁPIDO ===
cols = ['Date', 'Open', 'High', 'Low', 'Close', 'Volumen']
df = pd.read_csv(ruta_completa, usecols=cols)
df.columns = [c.lower().replace('volumen', 'volume') for c in df.columns]

# Convertir columna de fecha a datetime y fijarla como índice
df['date'] = pd.to_datetime(df['date'], utc=True)
df = df.set_index('date')

# RESAMPLE A VELAS DIARIAS (OHLCV)
velas_diarias = df.resample('1D').agg({
    'open': 'first',
    'high': 'max',
    'low': 'min',
    'close': 'last',
    'volume': 'sum'
})

# EMA
velas_diarias['ema'] = velas_diarias['close'].ewm(span=media_period, adjust=False).mean().round(2)
velas_diarias['ema'] = velas_diarias['ema'].shift(1)

print('Fichero:', ruta_completa, 'importado')
print(f"Características del DataFrame diario: {velas_diarias.shape}")
print(velas_diarias.head(3))

# GRAFICAR
plot_close_and_volume(timeframe=1, df=velas_diarias.reset_index(), symbol="GC")

# GUARDAR CSV
velas_diarias.to_csv(ruta_salida, index=True)
print(f'Archivo guardado como {ruta_salida}')
