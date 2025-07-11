# script que ejecuta una vela tendencial en la que se entra cuando tenemos una vela entera a favor de una media
import pandas as pd
import os
from chart_volume import plot_close_and_volume
from isla import isla
from isla_OM import order_managment

media_period = 30

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
    d['trigger'] = isla(d)

    trades = order_managment(df=d)
    trades_df = pd.DataFrame(trades)

    # Añade columna 'day' al DataFrame de trades para trazar luego si quieres
    if not trades_df.empty:
        trades_df['day'] = day

        # Evita duplicados: si mismo entry_date ya existe en el CSV final, no lo añadas
        if not trades_full.empty:
            trades_df = trades_df[~trades_df['entry_date'].isin(trades_full['entry_date'])]

        # Añade al csv acumulado
        trades_df.to_csv(csv_path, mode='a', index=False, header=not os.path.exists(csv_path) or trades_full.empty)
        print(f"✅ Añadido {len(trades_df)} trades al CSV outputs/trades_results.csv")
        
        # Añade a variable acumulada en memoria para el resumen final
        trades_full = pd.concat([trades_full, trades_df], ignore_index=True)

# ---- RESUMEN FINAL DE TODOS LOS DÍAS ----
if not trades_full.empty:
    print("\n========== RESUMEN DE OPERATIVA ==========")
    total_trades = len(trades_full)
    num_wins = ((trades_full['pnl'] > 0) & (trades_full['exit_type'] == 'target')).sum()
    num_lost = ((trades_full['pnl'] < 0) | (trades_full['exit_type'] == 'stop')).sum()
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

