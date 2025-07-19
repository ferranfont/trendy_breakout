import pandas as pd
import os

def generate_trades_with_limits(df):
    position = None  # 'long', 'short', or None
    trades = []

    for idx, row in df.iterrows():
        price = row['close']

        # Señal de breakout: cerrar corto, abrir largo
        if row['breakout']:
            if position == 'short':
                trades.append({'date': idx, 'side': 'short', 'action': 'close', 'price': price})
            if position != 'long':
                trades.append({'date': idx, 'side': 'long', 'action': 'open', 'price': price})
                position = 'long'
        # Señal de breakdown: cerrar largo, abrir corto
        elif row['breakdown']:
            if position == 'long':
                trades.append({'date': idx, 'side': 'long', 'action': 'close', 'price': price})
            if position != 'short':
                trades.append({'date': idx, 'side': 'short', 'action': 'open', 'price': price})
                position = 'short'

    # Cierra posición abierta al final (opcional)
    if position is not None and len(trades) > 0 and trades[-1]['action'] == 'open':
        last_price = df.iloc[-1]['close']
        trades.append({'date': df.index[-1], 'side': position, 'action': 'close', 'price': last_price})

    trades_df = pd.DataFrame(trades)
    return trades_df

def summarize_trades(trades_df, output_path="outputs/summary_strat_break.csv"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Agrupa en pares de (open, close)
    summary = []
    entry = None

    for _, row in trades_df.iterrows():
        if row['action'] == 'open':
            entry = row
        elif row['action'] == 'close' and entry is not None and entry['side'] == row['side']:
            entry_time = entry['date']
            exit_time = row['date']
            entry_price = entry['price']
            exit_price = row['price']
            time_in_market = (exit_time - entry_time).days if hasattr(exit_time, 'days') else (exit_time - entry_time) / pd.Timedelta('1D')
            side = entry['side']
            label = "long" if side == "long" else "short"
            if side == 'long':
                profit_point = exit_price - entry_price
            else:  # short
                profit_point = entry_price - exit_price
            profit_usd = profit_point * 50

            summary.append({
                "entry_time": entry_time,
                "exit_time": exit_time,
                "entry_price": entry_price,
                "exit_price": exit_price,
                "time_in_market": time_in_market,
                "profit_point": profit_point,
                "profit_usd": profit_usd,
                "label": label
            })
            entry = None  # Reset para la siguiente trade

    summary_df = pd.DataFrame(summary)
    summary_df.to_csv(output_path, index=False)
    print(f"✅ Resumen de estrategia exportado a: {output_path}")
    return summary_df

# --- Uso desde main ---
# trades_df = generate_trades_with_limits(df)
# summary_df = summarize_trades(trades_df)
