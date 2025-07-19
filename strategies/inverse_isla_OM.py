def order_managment_A_inverse_limit(df, atr_mult=2, n=2):
    """
    Estrategia inversa con orden limitada: 
      - Trigger 'short': deja orden limitada de compra en close - n (solo ejecuta si el low toca ese precio antes de cruzar la EMA por arriba)
      - Trigger 'long': deja orden limitada de venta en close + n (solo ejecuta si el high toca ese precio antes de cruzar la EMA por abajo)
    Stop y target: ATR multiplicador en el momento de entrada.
    """
    trades = []
    from datetime import time

    entry_time_limit = time(0, 10)
    late_time_limit = time(7, 50)
    i = 0
    while i < len(df):
        candle_time = df['date'].iloc[i].time()
        # ORDEN LIMITADA DE COMPRA SI TRIGGER ES 'short'
        if (
            df['trigger'].iloc[i] == 'short'
            and entry_time_limit < candle_time < late_time_limit
        ):
            entry_level = df['close'].iloc[i] - n
            atr_entry = df['atr'].iloc[i]
            triggered = False
            canceled = False
            for j in range(i+1, len(df)):
                # Si cruza la EMA por arriba antes de tocar el entry, cancelada
                if df['high'].iloc[j] > df['ema'].iloc[j]:
                    canceled = True
                    break
                # Si toca el entry_level, ejecuta el trade
                if df['low'].iloc[j] <= entry_level:
                    entry_index = j
                    entry_price = entry_level
                    stop = entry_price - atr_mult * atr_entry
                    target = entry_price + atr_mult * atr_entry
                    position = 'long'
                    below_ema_count = 0
                    triggered = True
                    break
            if triggered:
                # Ahora gestiona el trade abierto
                for k in range(entry_index+1, len(df)):
                    # Stop Loss
                    if df['low'].iloc[k] <= stop:
                        pnl = stop - entry_price
                        trades.append({
                            'entry_index': entry_index,
                            'entry_date': df['date'].iloc[entry_index],
                            'entry_price': entry_price,
                            'exit_index': k,
                            'exit_date': df['date'].iloc[k],
                            'exit_price': stop,
                            'side': 'long',
                            'pnl': pnl,
                            'pnl_S': pnl * 50,
                            'exit_type': 'stop',
                            'time_in_market': (df['date'].iloc[k] - df['date'].iloc[entry_index]).total_seconds() / 60,
                            'atr_entry': atr_entry
                        })
                        i = k
                        break
                    # Take Profit
                    if df['high'].iloc[k] >= target:
                        pnl = target - entry_price
                        trades.append({
                            'entry_index': entry_index,
                            'entry_date': df['date'].iloc[entry_index],
                            'entry_price': entry_price,
                            'exit_index': k,
                            'exit_date': df['date'].iloc[k],
                            'exit_price': target,
                            'side': 'long',
                            'pnl': pnl,
                            'pnl_S': pnl * 50,
                            'exit_type': 'target',
                            'time_in_market': (df['date'].iloc[k] - df['date'].iloc[entry_index]).total_seconds() / 60,
                            'atr_entry': atr_entry
                        })
                        i = k
                        break
                    # Cierre por dos velas bajo la EMA
                    if df['high'].iloc[k] < df['ema'].iloc[k]:
                        below_ema_count += 1
                    else:
                        below_ema_count = 0
                    if below_ema_count == 2:
                        pnl = df['close'].iloc[k] - entry_price
                        trades.append({
                            'entry_index': entry_index,
                            'entry_date': df['date'].iloc[entry_index],
                            'entry_price': entry_price,
                            'exit_index': k,
                            'exit_date': df['date'].iloc[k],
                            'exit_price': df['close'].iloc[k],
                            'side': 'long',
                            'pnl': pnl,
                            'pnl_S': pnl * 50,
                            'exit_type': 'ema_exit',
                            'time_in_market': (df['date'].iloc[k] - df['date'].iloc[entry_index]).total_seconds() / 60,
                            'atr_entry': atr_entry
                        })
                        i = k
                        break
        # ORDEN LIMITADA DE VENTA SI TRIGGER ES 'long'
        if (
            df['trigger'].iloc[i] == 'long'
            and entry_time_limit < candle_time < late_time_limit
        ):
            entry_level = df['close'].iloc[i] + n
            atr_entry = df['atr'].iloc[i]
            triggered = False
            canceled = False
            for j in range(i+1, len(df)):
                # Si cruza la EMA por abajo antes de tocar el entry, cancelada
                if df['low'].iloc[j] < df['ema'].iloc[j]:
                    canceled = True
                    break
                # Si toca el entry_level, ejecuta el trade
                if df['high'].iloc[j] >= entry_level:
                    entry_index = j
                    entry_price = entry_level
                    stop = entry_price + atr_mult * atr_entry
                    target = entry_price - atr_mult * atr_entry
                    position = 'short'
                    above_ema_count = 0
                    triggered = True
                    break
            if triggered:
                for k in range(entry_index+1, len(df)):
                    # Stop Loss
                    if df['high'].iloc[k] >= stop:
                        pnl = entry_price - stop
                        trades.append({
                            'entry_index': entry_index,
                            'entry_date': df['date'].iloc[entry_index],
                            'entry_price': entry_price,
                            'exit_index': k,
                            'exit_date': df['date'].iloc[k],
                            'exit_price': stop,
                            'side': 'short',
                            'pnl': pnl,
                            'pnl_S': pnl * 50,
                            'exit_type': 'stop',
                            'time_in_market': (df['date'].iloc[k] - df['date'].iloc[entry_index]).total_seconds() / 60,
                            'atr_entry': atr_entry
                        })
                        i = k
                        break
                    # Take Profit
                    if df['low'].iloc[k] <= target:
                        pnl = entry_price - target
                        trades.append({
                            'entry_index': entry_index,
                            'entry_date': df['date'].iloc[entry_index],
                            'entry_price': entry_price,
                            'exit_index': k,
                            'exit_date': df['date'].iloc[k],
                            'exit_price': target,
                            'side': 'short',
                            'pnl': pnl,
                            'pnl_S': pnl * 50,
                            'exit_type': 'target',
                            'time_in_market': (df['date'].iloc[k] - df['date'].iloc[entry_index]).total_seconds() / 60,
                            'atr_entry': atr_entry
                        })
                        i = k
                        break
                    # Cierre por dos velas sobre la EMA
                    if df['low'].iloc[k] > df['ema'].iloc[k]:
                        above_ema_count += 1
                    else:
                        above_ema_count = 0
                    if above_ema_count == 2:
                        pnl = entry_price - df['close'].iloc[k]
                        trades.append({
                            'entry_index': entry_index,
                            'entry_date': df['date'].iloc[entry_index],
                            'entry_price': entry_price,
                            'exit_index': k,
                            'exit_date': df['date'].iloc[k],
                            'exit_price': df['close'].iloc[k],
                            'side': 'short',
                            'pnl': pnl,
                            'pnl_S': pnl * 50,
                            'exit_type': 'ema_exit',
                            'time_in_market': (df['date'].iloc[k] - df['date'].iloc[entry_index]).total_seconds() / 60,
                            'atr_entry': atr_entry
                        })
                        i = k
                        break
        i += 1
    return trades
