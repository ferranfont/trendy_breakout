def order_managment(df, s=4):
    """
    Gestión de órdenes según trigger.
    Target: 
      - LONG: dos velas seguidas con high < ema.
      - SHORT: dos velas seguidas con low > ema.
    Stop loss (s puntos).
    Guarda pnl_S = pnl*50 y time_in_market (en minutos).
    Cuando va 5 puntos a favor, mueve stop a break even.
    """
    trades = []
    position = None
    entry_index = None
    entry_price = None
    below_ema_count = 0
    above_ema_count = 0
    stop = None  # El stop dinámico

    for i in range(len(df)):
        # Entrada LONG
        if position is None and df['trigger'].iloc[i] == 'long':
            position = 'long'
            entry_index = i
            entry_price = df['close'].iloc[i]
            below_ema_count = 0
            stop = entry_price - s  # Inicializa el stop normal

        # Entrada SHORT
        if position is None and df['trigger'].iloc[i] == 'short':
            position = 'short'
            entry_index = i
            entry_price = df['close'].iloc[i]
            above_ema_count = 0
            stop = entry_price + s  # Inicializa el stop normal

        # ----------- LONG -----------
        if position == 'long':
            # MOVE STOP TO BREAK EVEN if price is 5+ in favor
            if stop < entry_price and df['high'].iloc[i] >= entry_price + 20:
                stop = entry_price  # Break even

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
            if stop > entry_price and df['low'].iloc[i] <= entry_price - 20:
                stop = entry_price  # Break even

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
