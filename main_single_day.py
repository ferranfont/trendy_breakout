# script que ejecuta una vela tendencial en la que se entra cuando tenemos una vela entera a favor de una media
import pandas as pd
import os
from chart_volume import plot_close_and_volume
import ta
from isla import isla

# Importación de módulos de gestión de órdenes desde la carpeta strategies
from strategies.isla_OM import order_managment_A            # salida de stop por trailing stop o cantidad
from strategies.isla_OM_bb import order_managment_bb        # salida haciendo scalping en las bandas de bollinger
from strategies.isla_OM_time import order_managment         # salida por tiempo máximo en trade o cantidad
from strategies.inverse_isla_OM_bb import order_managment_inverse_isla_bb   # entrada a la contra en las bandas de bollinger
from strategies.inverse_isla_OM import order_managment_A_inverse_limit      # gestión de órdenes inversa


# ======= PARÁMETROS =======
fecha = '2022-11-02'
media_period = 200
slow_period = 100

# ======= LECTURA Y PREPROCESADO DEL CSV =======
directorio = '../DATA'
nombre_fichero = 'export_es_2015_formatted.csv'
ruta_completa = os.path.join(directorio, nombre_fichero)

print("\n======================== 🔍 df  ===========================")
cols = ['Date', 'Open', 'High', 'Low', 'Close', 'Volumen']
df = pd.read_csv(ruta_completa, usecols=cols)
df.columns = [c.lower().replace('volumen', 'volume') for c in df.columns]

# Filtro por fecha (solo filas del día)
df = df[df['date'].str.startswith(fecha)]
df['date'] = pd.to_datetime(df['date']).dt.tz_convert('UTC')

# ======= INDICADORES =======
print("\n============= GENERACIÓN DE MEDIAS Y BOLLINGER BAND  ================")
df['ema'] = df['close'].ewm(span=media_period, adjust=False).mean().round(2)
df['ema'] = df['ema'].shift(0)
df['ema_slow'] = df['close'].ewm(span=slow_period, adjust=False).mean().round(2)

bb = ta.volatility.BollingerBands(close=df['close'], window=slow_period, window_dev=2)
df['bb_upper'] = bb.bollinger_hband()
df['bb_lower'] = bb.bollinger_lband()
df['bb_ma'] = bb.bollinger_mavg()
df['atr'] = ta.volatility.AverageTrueRange(
    high=df['high'],
    low=df['low'],
    close=df['close'],
    window=14
).average_true_range().round(2)

print('Fichero:', ruta_completa, 'importado')
print(f"Características del DataFrame filtrado: {df.shape}")
print(df.tail())

# ======= GENERACIÓN DE SEÑALES =======
print("\n======================== SEÑALES  ==============================")
df['trigger'] = isla(df)
trigger_shorts = df[df['trigger'] == 'short']
print(trigger_shorts[['date', 'close', 'ema', 'high', 'low', 'trigger']])
print(f"Total de señales 'short' en el DataFrame: {len(trigger_shorts)}")

# ======= SELECCIÓN Y EJECUCIÓN DE ESTRATEGIA =======
print("\n=================== ESTRATEGIAS DISPONIBLES ========================")
print("1. order_managment_A_inverse_limit      # gestión de órdenes inversa")
print("2. order_managment_inverse_isla_bb      # entrada a la contra en las bandas de bollinger")
print("3. order_managment_bb                   # salida haciendo scalping en las bandas de bollinger")
print("4. order_managment_A                    # salida de stop por trailing stop o cantidad")
print("5. order_managment                      # salida por tiempo máximo en trade o cantidad")

opcion = int(input("\n¿Qué estrategia quieres ejecutar? (1-5): "))

if opcion == 1:
    trades = order_managment_A_inverse_limit(df=df)                # gestión de órdenes inversa
elif opcion == 2:
    trades = order_managment_inverse_isla_bb(df=df)                # entrada a la contra en las bandas de bollinger
elif opcion == 3:
    trades = order_managment_bb(df=df)                             # salida haciendo scalping en las bandas de bollinger
elif opcion == 4:
    trades = order_managment_A(df=df)                              # salida de stop por trailing stop o cantidad
elif opcion == 5:
    trades = order_managment(df, s=3, max_bars_in_trade=20)        # salida por tiempo máximo en trade o cantidad
else:
    raise ValueError("Opción inválida. Elige un número entre 1 y 5.")

trades_df = pd.DataFrame(trades)
print(trades_df.columns)
print(trades_df)
print(f"Total de trades: {len(trades_df)}")

# ======= GUARDAR CSV Y MOSTRAR RESUMEN =======
os.makedirs('outputs', exist_ok=True)
trades_df.to_csv('outputs/trades_results.csv', index=False)
print("✅ Archivo CSV guardado en outputs/trades_results.csv")

print("\n========== RESUMEN DE OPERATIVA ==========")
total_trades = len(trades_df)
num_wins = (trades_df['pnl'] > 0).sum()
num_lost = (trades_df['pnl'] < 0).sum()
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
