import pandas as pd
import os

def donchian_trailing_system(df, output_path="outputs/tracking_record_donchian.csv", point_value=50, return_summary=True):
    """
    Estrategia long & short con trailing stop basada en Donchian:
    - LARGO: entra si el high >= donchian_high. Stop inicial: low - threshold.
      Trailing: si hay nuevo toque a banda superior, actualiza al low - threshold.
      Sale si close <= trailing_stop.
    - CORTO: entra si el low <= donchian_low. Stop inicial: high + threshold.
      Trailing: si hay nuevo toque a banda inferior, actualiza al high + threshold.
      Sale si close >= trailing_stop.
    - Solo una posición abierta a la vez.
    - Requiere columnas 'donchian_high' y 'donchian_low' ya calculadas en el df.
    Devuelve DataFrame con resumen, y guarda csv/printa stats si return_summary=True.
    """
    threshold = 2  # Fijo aquí

    trades = []
    in_position = False
    position_side = None  # 'long' o 'short'
    entry_idx = None
    entry_price = None
    trailing_stop = None

    for idx, row in df.iterrows():
        # ---------- ENTRADA LARGA ----------
        if not in_position and row['high'] >= row['donchian_high']:
            entry_idx = idx
            entry_price = row['close']
            trailing_stop = row['low'] - threshold
            trades.append({'action': 'open', 'date': idx, 'side': 'long', 'entry_price': entry_price, 'trailing_stop': trailing_stop})
            in_position = True
            position_side = 'long'
            continue

        # ---------- ENTRADA CORTA ----------
        if not in_position and row['low'] <= row['donchian_low']:
            entry_idx = idx
            entry_price = row['close']
            trailing_stop = row['high'] + threshold
            trades.append({'action': 'open', 'date': idx, 'side': 'short', 'entry_price': entry_price, 'trailing_stop': trailing_stop})
            in_position = True
            position_side = 'short'
            continue

        # ---------- GESTIÓN DE LARGOS ----------
        if in_position and position_side == 'long':
            # Trailing: nuevo toque, actualiza trailing_stop al low - threshold
            if row['high'] >= row['donchian_high']:
                trailing_stop = row['low'] - threshold
                trades.append({'action': 'trail', 'date': idx, 'side': 'long', 'trailing_stop': trailing_stop})
            # Salida: el close toca o cae por debajo del trailing stop
            if row['close'] <= trailing_stop:
                exit_idx = idx
                exit_price = row['close']
                trades.append({'action': 'close', 'date': idx, 'side': 'long', 'exit_price': exit_price, 'trailing_stop': trailing_stop})
                in_position = False
                entry_idx = None
                entry_price = None
                trailing_stop = None
                position_side = None

        # ---------- GESTIÓN DE CORTOS ----------
        if in_position and position_side == 'short':
            # Trailing: nuevo toque, actualiza trailing_stop al high + threshold
            if row['low'] <= row['donchian_low']:
                trailing_stop = row['high'] + threshold
                trades.append({'action': 'trail', 'date': idx, 'side': 'short', 'trailing_stop': trailing_stop})
            # Salida: el close toca o supera el trailing stop
            if row['close'] >= trailing_stop:
                exit_idx = idx
                exit_price = row['close']
                trades.append({'action': 'close', 'date': idx, 'side': 'short', 'exit_price': exit_price, 'trailing_stop': trailing_stop})
                in_position = False
                entry_idx = None
                entry_price = None
                trailing_stop = None
                position_side = None

    # Si queda abierta al final, la cerramos al último precio
    if in_position and entry_idx is not None:
        last_row = df.iloc[-1]
        trades.append({'action': 'close', 'date': last_row.name, 'side': position_side, 'exit_price': last_row['close'], 'trailing_stop': trailing_stop})

    # Empareja señales de entrada y salida (solo open y close)
    entries = []
    last_open = None
    for t in trades:
        if t['action'] == 'open':
            last_open = t
        if t['action'] == 'close' and last_open is not None and t['side'] == last_open['side']:
            entries.append({
                'entry_time': last_open['date'],
                'exit_time': t['date'],
                'entry_price': last_open['entry_price'],
                'exit_price': t['exit_price'],
                'side': t['side'],
                'initial_stop': last_open['trailing_stop'],
                'final_stop': t['trailing_stop']
            })
            last_open = None

    tracking_record = pd.DataFrame(entries)

    if return_summary and not tracking_record.empty:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        # Añade métricas al DataFrame
        tracking_record['profit_point'] = tracking_record.apply(
            lambda x: x['exit_price'] - x['entry_price'] if x['side'] == 'long' else x['entry_price'] - x['exit_price'], axis=1)
        tracking_record['profit_usd'] = tracking_record['profit_point'] * point_value
        tracking_record['time_in_market'] = (pd.to_datetime(tracking_record['exit_time']) - pd.to_datetime(tracking_record['entry_time'])).dt.days
        tracking_record['label'] = tracking_record['side']

        tracking_record.to_csv(output_path, index=False)
        print(f"✅ Resumen de estrategia Donchian exportado a: {output_path}")
        print(tracking_record.head(5))
        # Print resumen
        print(f"🔹 TOTAL PROFIT (USD): {tracking_record['profit_usd'].sum():,.2f}")
        print(f"🔹 TOTAL TRADES: {len(tracking_record)}")
        print(f"🔹 WIN RATE: {len(tracking_record[tracking_record['profit_usd'] > 0]) / len(tracking_record) * 100:.2f}%")
        print(f"🔹 AVERAGE TRADE DURATION: {tracking_record['time_in_market'].mean():.2f} days")
        print(f"🔹 AVERAGE PROFIT PER TRADE (USD): {tracking_record['profit_usd'].mean():,.2f}")
        print(f"🔹 AVERAGE PROFIT POINTS: {tracking_record['profit_point'].mean():.2f}")
        print(f"🔹 MAX PROFIT TRADE (USD): {tracking_record['profit_usd'].max():,.2f}")
        print(f"🔹 MIN PROFIT TRADE (USD): {tracking_record['profit_usd'].min():,.2f}")
        print(f"🔹 TOTAL PROFIT POINTS: {tracking_record['profit_point'].sum():,.2f}")
        print(f"🔹 TOTAL PROFIT USD: {tracking_record['profit_usd'].sum():,.2f}")

    return tracking_record
