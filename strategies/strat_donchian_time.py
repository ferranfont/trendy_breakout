import pandas as pd
import os

def donchian_time_exit_system(df, return_summary=True):
    bars_hold = 2

    threshold = 2
    point_value = 50
    output_path = "outputs/tracking_record_donchian_time_exit.csv"

    trades = []
    in_position = False
    side = None
    entry_idx = None
    entry_price = None
    stop_loss = None
    favorable_counter = 0
    waiting_for_favorable = False

    for i in range(len(df)):
        row = df.iloc[i]
        date = df.index[i]

        # ---------- ENTRADA ----------
        if not in_position:
            if row['high'] >= row['donchian_high']:
                entry_idx = i
                entry_price = row['close']
                stop_loss = df.iloc[i]['low'] - threshold
                side = 'long'
                in_position = True
                favorable_counter = 0
                waiting_for_favorable = True
                trades.append({'action': 'open', 'date': date, 'side': side, 'entry_price': entry_price, 'stop_loss': stop_loss})
                continue

            if row['low'] <= row['donchian_low']:
                entry_idx = i
                entry_price = row['close']
                stop_loss = df.iloc[i]['high'] + threshold
                side = 'short'
                in_position = True
                favorable_counter = 0
                waiting_for_favorable = True
                trades.append({'action': 'open', 'date': date, 'side': side, 'entry_price': entry_price, 'stop_loss': stop_loss})
                continue

        # ---------- GESTIÓN ----------
        if in_position:
            # STOP LOSS — salida al nivel exacto
            if side == 'long' and row['low'] <= stop_loss:
                trades.append({'action': 'close', 'date': date, 'side': side, 'exit_price': stop_loss, 'stop_loss': stop_loss})
                in_position = False
                continue
            if side == 'short' and row['high'] >= stop_loss:
                trades.append({'action': 'close', 'date': date, 'side': side, 'exit_price': stop_loss, 'stop_loss': stop_loss})
                in_position = False
                continue

            # Esperar cruce favorable
            price = row['close']
            if waiting_for_favorable:
                if (side == 'long' and price > entry_price) or (side == 'short' and price < entry_price):
                    waiting_for_favorable = False
                    favorable_counter = 1
                continue

            # Contador de velas favorables
            if (side == 'long' and price > entry_price) or (side == 'short' and price < entry_price):
                favorable_counter += 1
            else:
                favorable_counter = 0

            if favorable_counter >= bars_hold:
                trades.append({'action': 'close', 'date': date, 'side': side, 'exit_price': price, 'stop_loss': stop_loss})
                in_position = False

    # Cierre forzado al final si queda abierta
    if in_position:
        last_row = df.iloc[-1]
        trades.append({'action': 'close', 'date': df.index[-1], 'side': side, 'exit_price': last_row['close'], 'stop_loss': stop_loss})

    # Crear tracking record
    records = []
    last_open = None
    for t in trades:
        if t['action'] == 'open':
            last_open = t
        elif t['action'] == 'close' and last_open:
            records.append({
                'entry_time': last_open['date'],
                'exit_time': t['date'],
                'entry_price': last_open['entry_price'],
                'exit_price': t['exit_price'],
                'side': last_open['side'],
                'initial_stop': last_open['stop_loss'],
                'final_stop': t['stop_loss']
            })
            last_open = None

    tracking_record = pd.DataFrame(records)

    if return_summary and not tracking_record.empty:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        tracking_record['profit_point'] = tracking_record.apply(
            lambda x: x['exit_price'] - x['entry_price'] if x['side'] == 'long' else x['entry_price'] - x['exit_price'], axis=1)
        tracking_record['profit_usd'] = tracking_record['profit_point'] * point_value
        tracking_record['time_in_market'] = (
            pd.to_datetime(tracking_record['exit_time']) - pd.to_datetime(tracking_record['entry_time'])
        ).dt.total_seconds() / 60
        tracking_record['label'] = tracking_record['side']

        tracking_record.to_csv(output_path, index=False)
        print(f"✅ Exportado a: {output_path}")
        print(tracking_record.head())
        print(f"🔹 TRADES: {len(tracking_record)}")
        print(f"🔹 WIN RATE: {len(tracking_record[tracking_record['profit_usd'] > 0]) / len(tracking_record) * 100:.2f}%")
        print(f"🔹 AVG TIME IN MARKET: {tracking_record['time_in_market'].mean():.2f} minutos")
        print(f"🔹 AVG PROFIT PER TRADE: {tracking_record['profit_usd'].mean():.2f} USD")
        print(f"🔹 MAX PROFIT: {tracking_record['profit_usd'].max():.2f} USD")
        print(f"🔹 MIN PROFIT: {tracking_record['profit_usd'].min():.2f} USD")

    return tracking_record
