def order_managment_A(df, s=4):
    """
    Gestión de órdenes según trigger.
    Solo entra si la hora está entre entry_time_limit y late_time_limit.
    Target: 
      - LONG: dos velas seguidas con high < ema.
      - SHORT: dos velas seguidas con low > ema.
    Stop loss (s puntos). Si va 10 puntos a favor, mueve el stop a break even.
    """
    trades = []
    position = None
    entry_index = None
    entry_price = None
    below_ema_count = 0
    above_ema_count = 0
    stop = None  # El stop dinámico

    from datetime import time
    entry_time_limit = time(1, 30)
    late_time_limit = time(7, 50)  # Por ejemplo, no entrar nuevas órdenes después de las 22:00

    for i in range(len(df)):
        candle_time = df['date'].iloc[i].time() if hasattr(df['date'].iloc[i], 'time') else pd.to_datetime(df['date'].iloc[i]).time()
        
        # ---- ENTRADA LONG SOLO ENTRE LOS DOS LÍMITES DE HORA ----
        if (
            position is None
            and df['trigger'].iloc[i] == 'long'
            and entry_time_limit < candle_time < late_time_limit
        ):
            position = 'long'
            entry_index = i
            entry_price = df['close'].iloc[i]
            below_ema_count = 0
            stop = entry_price - s

        # ---- ENTRADA SHORT SOLO ENTRE LOS DOS LÍMITES DE HORA ----
        if (
            position is None
            and df['trigger'].iloc[i] == 'short'
            and entry_time_limit < candle_time < late_time_limit
        ):
            position = 'short'
            entry_index = i
            entry_price = df['close'].iloc[i]
            above_ema_count = 0
            stop = entry_price + s

        # ----------- LONG ----------- (lógica idéntica a la tuya)
        if position == 'long':
            if stop < entry_price and df['high'].iloc[i] >= entry_price + 10:
                stop = entry_price
            if df['low'].iloc[i] <= stop:
                pnl = stop - entry_price
                trades.append({
                    'entry_index': entry_index,
                    'entry_date': df['date'].iloc[entry_index],
                    'entry_price': entry_price,
                    'exit_index': i,
                    'exit_date': df['date'].iloc[i],
                    'exit_price': stop,
                    'side': 'long',
                    'pnl': pnl,
                    'pnl_S': pnl * 50,
                    'exit_type': 'stop',
                    'time_in_market': (df['date'].iloc[i] - df['date'].iloc[entry_index]).total_seconds() / 60
                })
                position = None
                continue

            if df['high'].iloc[i] < df['ema'].iloc[i]:
                below_ema_count += 1
            else:
                below_ema_count = 0

            if below_ema_count == 2:
                pnl = df['close'].iloc[i] - entry_price
                trades.append({
                    'entry_index': entry_index,
                    'entry_date': df['date'].iloc[entry_index],
                    'entry_price': entry_price,
                    'exit_index': i,
                    'exit_date': df['date'].iloc[i],
                    'exit_price': df['close'].iloc[i],
                    'side': 'long',
                    'pnl': pnl,
                    'pnl_S': pnl * 50,
                    'exit_type': 'target',
                    'time_in_market': (df['date'].iloc[i] - df['date'].iloc[entry_index]).total_seconds() / 60
                })
                position = None
                continue

        # ----------- SHORT -----------
        if position == 'short':
            if stop > entry_price and df['low'].iloc[i] <= entry_price - 10:
                stop = entry_price
            if df['high'].iloc[i] >= stop:
                pnl = entry_price - stop
                trades.append({
                    'entry_index': entry_index,
                    'entry_date': df['date'].iloc[entry_index],
                    'entry_price': entry_price,
                    'exit_index': i,
                    'exit_date': df['date'].iloc[i],
                    'exit_price': stop,
                    'side': 'short',
                    'pnl': pnl,
                    'pnl_S': pnl * 50,
                    'exit_type': 'stop',
                    'time_in_market': (df['date'].iloc[i] - df['date'].iloc[entry_index]).total_seconds() / 60
                })
                position = None
                continue

            if df['low'].iloc[i] > df['ema'].iloc[i]:
                above_ema_count += 1
            else:
                above_ema_count = 0

            if above_ema_count == 2:
                pnl = entry_price - df['close'].iloc[i]
                trades.append({
                    'entry_index': entry_index,
                    'entry_date': df['date'].iloc[entry_index],
                    'entry_price': entry_price,
                    'exit_index': i,
                    'exit_date': df['date'].iloc[i],
                    'exit_price': df['close'].iloc[i],
                    'side': 'short',
                    'pnl': pnl,
                    'pnl_S': pnl * 50,
                    'exit_type': 'target',
                    'time_in_market': (df['date'].iloc[i] - df['date'].iloc[entry_index]).total_seconds() / 60
                })
                position = None
                continue

    return trades
