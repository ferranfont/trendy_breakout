def order_managment_bb(df, s=6):
    """
    Gestión de órdenes según trigger.
    Solo entra si la hora está entre entry_time_limit y late_time_limit.
    Target: 
      - LONG: Take Profit en la banda BB superior (bb_upper).
      - SHORT: Take Profit en la banda BB inferior (bb_lower).
    Stop loss (s puntos). Si va 10 puntos a favor, mueve el stop a break even.
    """
    trades = []
    position = None
    entry_index = None
    entry_price = None
    stop = None  # El stop dinámico

    from datetime import time
    entry_time_limit = time(15, 30)
    late_time_limit = time(20, 30)

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
            stop = entry_price + s

        # ----------- LONG MANAGEMENT ----------- 
        if position == 'long':
            # MOVE STOP TO BREAK EVEN if price is 10+ in favor
            if stop < entry_price and df['high'].iloc[i] >= entry_price + 10:
                stop = entry_price

            # Stop loss
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

            # Target profit: precio toca o supera la BB superior
            if df['high'].iloc[i] >= df['bb_upper'].iloc[i]:
                exit_price = df['bb_upper'].iloc[i]
                pnl = exit_price - entry_price
                trades.append({
                    'entry_index': entry_index,
                    'entry_date': df['date'].iloc[entry_index],
                    'entry_price': entry_price,
                    'exit_index': i,
                    'exit_date': df['date'].iloc[i],
                    'exit_price': exit_price,
                    'side': 'long',
                    'pnl': pnl,
                    'pnl_S': pnl * 50,
                    'exit_type': 'bb_upper',
                    'time_in_market': (df['date'].iloc[i] - df['date'].iloc[entry_index]).total_seconds() / 60
                })
                position = None
                continue

        # ----------- SHORT MANAGEMENT -----------
        if position == 'short':
            # MOVE STOP TO BREAK EVEN if price is 10+ in favor
            if stop > entry_price and df['low'].iloc[i] <= entry_price - 10:
                stop = entry_price

            # Stop loss
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

            # Target profit: precio toca o perfora la BB inferior
            if df['low'].iloc[i] <= df['bb_lower'].iloc[i]:
                exit_price = df['bb_lower'].iloc[i]
                pnl = entry_price - exit_price
                trades.append({
                    'entry_index': entry_index,
                    'entry_date': df['date'].iloc[entry_index],
                    'entry_price': entry_price,
                    'exit_index': i,
                    'exit_date': df['date'].iloc[i],
                    'exit_price': exit_price,
                    'side': 'short',
                    'pnl': pnl,
                    'pnl_S': pnl * 50,
                    'exit_type': 'bb_lower',
                    'time_in_market': (df['date'].iloc[i] - df['date'].iloc[entry_index]).total_seconds() / 60
                })
                position = None
                continue

    return trades
