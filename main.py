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

# Normaliza la columna de fecha para que siempre tenga zona horaria UTC, evita warnings futuros
df['date'] = pd.to_datetime(df['date'], utc=True)  # ESTO ES LO CORRECTO Y RÁPIDO

# Crea columna solo fecha y lista única
df['only_date'] = df['date'].dt.date
unique_dates = df['only_date'].unique().tolist()
print(f"Total días a procesar: {len(unique_dates)}")

# ============ MENÚ DE ESTRATEGIAS ==============
print("\n=================== ESTRATEGIAS DISPONIBLES ========================")
print("1. order_managment_A_inverse_limit      # gestión de órdenes inversa")
print("2. order_managment_inverse_isla_bb      # entrada a la contra en las bandas de bollinger")
print("3. order_managment_bb                   # salida haciendo scalping en las bandas de bollinger")
print("4. order_managment_A                    # salida de stop por trailing stop o cantidad")
print("5. order_managment                      # salida por tiempo máximo en trade o cantidad")

while True:
    try:
        opcion = int(input("\n¿Qué estrategia quieres ejecutar? (1-5): "))
        if opcion in range(1, 6):
            break
        else:
            print("❌ Debes elegir un número del 1 al 5.")
    except ValueError:
        print("❌ Introduce un número válido del 1 al 5.")

# CSV FINAL DE TRADES
csv_path = 'outputs/trades_results.csv'
os.makedirs('outputs', exist_ok=True)
# Si ya existe, carga para evitar duplicados, si no, crea vacío
if os.path.exists(csv_path):
    trades_full = pd.read_csv(csv_path, parse_dates=['entry_date','exit_date'])
else:
    trades_full = pd.DataFrame()

# ---- Bucle rápido por lista de fechas ----
for day in unique_dates:
    d = df[df['only_date'] == day].copy()

    if len(d) < 50:
        continue

    d['ema'] = d['close'].ewm(span=media_period, adjust=False).mean().round(2)
    d['ema'] = d['ema'].shift(1)
    d['ema_slow'] = d['close'].ewm(span=slow_period, adjust=False).mean().round(2)
    d['trigger'] = isla(d)

    bb = ta.volatility.BollingerBands(close=d['close'], window=20, window_dev=2)
    d['bb_upper'] = bb.bollinger_hband()
    d['bb_lower'] = bb.bollinger_lband()
    d['bb_ma']    = bb.bollinger_mavg()

    d['atr'] = ta.volatility.AverageTrueRange(
        high=d['high'],
        low=d['low'],
        close=d['close'],
        window=14
    ).average_true_range().round(2)

    # ====================== ESTRATEGIAS ====================
    if opcion == 1:
        trades = order_managment_A_inverse_limit(df=d)                # gestión de órdenes inversa
    elif opcion == 2:
        trades = order_managment_inverse_isla_bb(df=d)                # entrada a la contra en las bandas de bollinger
    elif opcion == 3:
        trades = order_managment_bb(df=d)                             # salida haciendo scalping en las bandas de bollinger
    elif opcion == 4:
        trades = order_managment_A(df=d)                              # salida de stop por trailing stop o cantidad
    elif opcion == 5:
        trades = order_managment(d, s=4, max_bars_in_trade=3)         # salida por tiempo o cantidad

    trades_df = pd.DataFrame(trades)

    # Añade columna 'day' al DataFrame de trades para trazar luego si quieres
    if not trades_df.empty:
        trades_df['day'] = day
        # Evita duplicados: si mismo entry_date y exit_date ya existe en el CSV final, no lo añadas
        if not trades_full.empty:
            trades_df = trades_df[~trades_df['entry_date'].isin(trades_full['entry_date'])]
        # Añade a variable acumulada en memoria para el resumen final
        trades_full = pd.concat([trades_full, trades_df], ignore_index=True)
        # Añade al csv acumulado
        trades_df.to_csv(csv_path, mode='a', index=False, header=not os.path.exists(csv_path) or trades_full.empty)
        print(f"✅ Añadido {len(trades_df)} trades al CSV outputs/trades_results.csv")

# ==== LIMPIEZA Y CONTROL DE COLUMNAS PARA RESUMEN FINAL ====
if not trades_full.empty:
    print("\n========== RESUMEN DE OPERATIVA ==========")
    print("Columnas en trades_full:", trades_full.columns.tolist())
    if 'pnl' not in trades_full.columns:
        print("¡¡ERROR!! No existe la columna 'pnl' en trades_full")
        print(trades_full.head())
        exit(1)
    # Si hay columnas de tipo 'Unnamed', elimínalas
    trades_full = trades_full.loc[:, ~trades_full.columns.str.contains('^Unnamed')]

    total_trades = len(trades_full)
    num_wins = (trades_full['pnl'] > 0).sum()
    num_lost = (trades_full['pnl'] < 0).sum()
    avg_win = trades_full.loc[trades_full['pnl'] > 0, 'pnl'].mean()
    avg_lost = trades_full.loc[trades_full['pnl'] < 0, 'pnl'].mean()
    success_rate = 100 * num_wins / total_trades if total_trades > 0 else 0
    failure_rate = 100 * num_lost / total_trades if total_trades > 0 else 0
    total_pnl = trades_full['pnl'].sum()
    total_pnl_S = trades_full['pnl_S'].sum()
    avg_time = trades_full['time_in_market'].mean()

    print(f"Total trades: {total_trades}")
    print(f"Ganadoras: {num_wins}  ({success_rate:.2f}%)")
    print(f"Perdedoras: {num_lost}  ({failure_rate:.2f}%)")
    print(f"Average Win: {avg_win:.2f}")
    print(f"Average Lost: {avg_lost:.2f}")
    print(f"Total PnL: {total_pnl:.2f}")
    print(f"Total PnL_S: {total_pnl_S:.2f}")
    print(f"Tiempo medio en mercado (min): {avg_time:.1f}")
else:
    print("No se generaron trades en ningún día.")
