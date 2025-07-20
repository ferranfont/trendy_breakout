# código que evalua si un producto es tendencial o mean-reversión enbase a su rendimiento al romper máximos y mínimos

import pandas as pd
from chart_volume import plot_close_and_volume
from strategies.strat_break_OM import generate_trades_with_limits
from strategies.strat_break_OM import summarize_trades
from strategies.strat_donchian import donchian_trailing_system
from strategies.strat_donchian_time import donchian_time_exit_system
from quant_donchian_channel import add_donchian_channel
import os
import plotly.graph_objects as go
from quant_breaks import breaks

strat_num = 1
symbol = 'GC'
timeframe = '1D'   
donchian_period = 14


# === LECTURA DEL ARCHIVO DE VELAS DIARIAS ===
ruta_archivo = '../DATA/GC_1D_2015.csv'

# Cargar el CSV y parsear la columna 'date' como fecha
df = pd.read_csv(ruta_archivo, parse_dates=['date'])
df = df.set_index('date')


# === QUANT MODULE CALCULO BREAKOUTS ===
df = add_donchian_channel(df, window=donchian_period)
df = breaks(df)

print(df.head(3))

# === GESTION DE LAS ÓRDENES Y CREACIÓN DE UN SUMMARY ===
def normalize_trades(trades_df, strategy):
    # Estrategia breakout clásica: usa summarize_trades, pasa sea cual sea la estrategia a una normalización del output para poder ser usado en el resto del código
    if strategy == 1:
        # Ya está normalizado, porque summarize_trades devuelve el formato correcto
        return trades_df
    # Estrategia Donchian: su función devuelve el formato correcto
    elif strategy == 2:
        # Si alguna columna falta, la creas vacía (p.ej., 'label')
        if 'label' not in trades_df.columns:
            trades_df['label'] = 'long'
        return trades_df
    elif strategy == 3:
        # estrategia Donchian Time Exit
        # si ya está en formato con columnas necesarias, devuélvelo directamente
        return tracking_record
    else:
        raise ValueError("Unknown strategy")
# ============ MENÚ DE ESTRATEGIAS ==============
print("\n=================== ESTRATEGIAS DISPONIBLES ========================")
print("1. generate_trades_with_limits          # always in as oposite break reverse positon")
print("2. donchian_trailing_system             # dochian level breakout")
print("3. donchian_time_exit_system             # dochian level breakout")
print("\n")

if strat_num == 1:
    trades_df = generate_trades_with_limits(df)
    tracking_record = summarize_trades(trades_df)
    normalized_trades = normalize_trades(tracking_record, 1)
elif strat_num == 2:
    trades_df = donchian_trailing_system(df)
    normalized_trades = normalize_trades(trades_df, 2)
elif strat_num == 3:
    tracking_record = donchian_time_exit_system(df)
    normalized_trades = normalize_trades(tracking_record, 3)





# === GRAFICAR VELAS DIARIAS Y VOLUMEN ===
plot_close_and_volume(timeframe, df, symbol, tracking_record=normalized_trades)
print(f"Gráfico de {symbol} en timeframe {timeframe} generado.")

