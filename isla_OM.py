def order_managment(df, s=5):
    """
    Gestión de órdenes según trigger.
    Solo entra si la hora es > 15:45.
    Target: 
      - LONG: dos velas seguidas con high < ema.
      - SHORT: dos velas seguidas con low > ema.
    Stop loss (s puntos). Si va 5 puntos a favor, mueve el stop a break even.
    """
    trades = []
    position = None
    entry_index = None
    entry_price = None
    below_ema_count = 0
    above_ema_count = 0
    stop = None  # El stop dinámico

    # Define hora límite en formato datetime.time
    from datetime import time
    entry_time_limit = time(15, 45)

    for i in range(len(df)):
        # Extrae la hora local de la vela actual
        candle_time = df['date'].iloc[i].time() if hasattr(df['date'].iloc[i], 'time') else pd.to_datetime(df['date'].iloc[i]).time()
        # Entrada LONG solo si hora > 15:45
        if (
            position is None
            and df['trigger'].iloc[i] == 'long'
            and candle_time > entry_time_limit
        ):
            position = 'long'
            entry_index = i
            entry_price = df['close'].iloc[i]
            below_ema_count = 0
            stop = entry_price - s

        # Entrada SHORT solo si hora > 15:45
        if (
            position is None
            and df['trigger'].iloc[i] == 'short'
            and candle_time > entry_time_limit
        ):
            position = 'short'
            entry_index = i
            entry_price = df['close'].iloc[i]
            above_ema_count = 0
            stop = entry_price + s

        # ----------- LONG -----------
        if position == 'long':
            # MOVE STOP TO BREAK EVEN if price is 5+ in favor
            if stop < entry_price and df['high'].iloc[i] >= entry_price + 25:
                stop = entry_price

            # Stop loss (dynamic)
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
                entry_index = None
                entry_price = None
                below_ema_count = 0
                stop = None
                continue

            # Target: 2 velas seguidas con high < ema
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
                entry_index = None
                entry_price = None
                below_ema_count = 0
                stop = None
                continue

        # ----------- SHORT -----------
        if position == 'short':
            # MOVE STOP TO BREAK EVEN if price is 5+ in favor
            if stop > entry_price and df['low'].iloc[i] <= entry_price - 25:
                stop = entry_price

            # Stop loss (dynamic)
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
                entry_index = None
                entry_price = None
                above_ema_count = 0
                stop = None
                continue

            # Target: 2 velas seguidas con low > ema
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
                entry_index = None
                entry_price = None
                above_ema_count = 0
                stop = None
                continue

    return trades
