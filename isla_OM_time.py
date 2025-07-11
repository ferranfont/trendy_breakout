def order_managment(df, s=5, max_bars_in_trade=5):
    """
    Gestión de órdenes según trigger.
    Solo entra si la hora es > 10:45.
    Target: 
      - LONG: dos velas seguidas con high < ema.
      - SHORT: dos velas seguidas con low > ema.
    Stop inicial (s puntos), pero luego si pasan N velas y no hay beneficio, cierra con "time_out".
    """
    trades = []
    position = None
    entry_index = None
    entry_price = None
    below_ema_count = 0
    above_ema_count = 0
    stop = None
    bars_in_trade = 0

    from datetime import time
    entry_time_limit = time(10, 45)

    for i in range(len(df)):
        candle_time = df['date'].iloc[i].time() if hasattr(df['date'].iloc[i], 'time') else pd.to_datetime(df['date'].iloc[i]).time()
        # Entrada LONG
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
            bars_in_trade = 0

        # Entrada SHORT
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
            bars_in_trade = 0

        # ----------- LONG -----------
        if position == 'long':
            bars_in_trade += 1

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
                bars_in_trade = 0
                continue

            # Time-out STOP
            if bars_in_trade >= max_bars_in_trade:
                # Sale si el precio no está por encima del entry
                if df['close'].iloc[i] <= entry_price:
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
                        'exit_type': 'time_out',
                        'time_in_market': (df['date'].iloc[i] - df['date'].iloc[entry_index]).total_seconds() / 60
                    })
                    position = None
                    entry_index = None
                    entry_price = None
                    below_ema_count = 0
                    stop = None
                    bars_in_trade = 0
                    continue

        # ----------- SHORT -----------
        if position == 'short':
            bars_in_trade += 1

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
                bars_in_trade = 0
                continue

            # Time-out STOP
            if bars_in_trade >= max_bars_in_trade:
                # Sale si el precio no está por debajo del entry
                if df['close'].iloc[i] >= entry_price:
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
                        'exit_type': 'time_out',
                        'time_in_market': (df['date'].iloc[i] - df['date'].iloc[entry_index]).total_seconds() / 60
                    })
                    posit
