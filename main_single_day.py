# script que ejecuta una vela tendencial en la que se entra cuando tenemos una vela entera a favor de una media
import pandas as pd
import os
from chart_volume import plot_close_and_volume
from isla import isla
from isla_OM import order_managment

#fecha = '2025-01-03'
fecha = '2022-08-15'
media_period = 200
slow_period = 100

# ========= DESCARGA Y FILTRO RÁPIDO =========
directorio = '../DATA'
nombre_fichero = 'export_es_2015_formatted.csv'
ruta_completa = os.path.join(directorio, nombre_fichero)

print("\n======================== 🔍 df  ===========================")
cols = ['Date', 'Open', 'High', 'Low', 'Close', 'Volumen']
df = pd.read_csv(ruta_completa, usecols=cols)
df.columns = [c.lower().replace('volumen', 'volume') for c in df.columns]

# Filtro rápido por fecha SOLO filas del día
df = df[df['date'].str.startswith(fecha)]

# Solo ahora parseas y conviertes
# Si tu columna date no tiene zona horaria, descomenta la siguiente línea:
# df['date'] = pd.to_datetime(df['date']).dt.tz_localize('Europe/Madrid').dt.tz_convert('UTC')
# Si ya tiene zona horaria:
df['date'] = pd.to_datetime(df['date']).dt.tz_convert('UTC')

print("\n================== GENERACIÓN DE MEDIAS  ==========================")
df['ema'] = df['close'].ewm(span=media_period, adjust=False).mean().round(2)
df['ema'] = df['ema'].shift(1)  # Desplazar la EMA para evitar el lookahead bias
df['ema_slow'] = df['close'].ewm(span=slow_period, adjust=False).mean().round(2) 

print('Fichero:', ruta_completa, 'importado')
print(f"Características del DataFrame filtrado: {df.shape}")
print(df.head())

print("\n======================== SEÑALES  ==============================")
df['trigger'] = isla(df)
trigger_shorts = df[df['trigger'] == 'short']
print(trigger_shorts[['date', 'close', 'ema', 'high', 'low', 'trigger']])
print(f"Total de señales 'short' en el DataFrame: {len(trigger_shorts)}")

print("\n======================== GESTIÓN DE ORDENES =====================")
#trades = order_managment(df=df)                             # salida de stop por trailig stop o cantidad
trades = order_managment(df, s=10, max_bars_in_trade=10)    # salida por tiempo máximo en trade o cantidad
trades_df = pd.DataFrame(trades)
print(trades_df)
print(f"Total de trades: {len(trades_df)}")       


# Guardar CSV
os.makedirs('outputs', exist_ok=True)
trades_df.to_csv('outputs/trades_results.csv', index=False)
print("✅ Archivo CSV guardado en outputs/trades_results.csv")

# ----- RESUMEN -----
print("\n========== RESUMEN DE OPERATIVA ==========")
total_trades = len(trades_df)
num_wins = ((trades_df['pnl'] > 0) & (trades_df['exit_type'] == 'target')).sum()
num_lost = ((trades_df['pnl'] < 0) | (trades_df['exit_type'] == 'stop')).sum()
avg_win = trades_df.loc[trades_df['pnl'] > 0, 'pnl'].mean()
avg_lost = trades_df.loc[trades_df['pnl'] < 0, 'pnl'].mean()
success_rate = 100 * num_wins / total_trades if total_trades > 0 else 0
failure_rate = 100 * num_lost / total_trades if total_trades > 0 else 0
total_pnl = trades_df['pnl'].sum()
total_pnl_S = trades_df['pnl_S'].sum()
avg_time = trades_df['time_in_market'].mean()

print(f"Total trades: {total_trades}")
print(f"Ganadoras: {num_wins}  ({success_rate:.2f}%)")
print(f"Perdedoras: {num_lost}  ({failure_rate:.2f}%)")
print(f"Average Win: {avg_win:.2f}")
print(f"Average Lost: {avg_lost:.2f}")
print(f"Total PnL: {total_pnl:.2f}")
print(f"Total PnL_S: {total_pnl_S:.2f}")
print(f"Tiempo medio en mercado (min): {avg_time:.1f}")

print(df.head())
print("\n======================== GRAFICACIÓN  ===========================")
plot_close_and_volume(timeframe=1, df=df, trades_df=trades_df) 