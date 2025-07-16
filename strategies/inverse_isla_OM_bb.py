import pandas as pd

def order_managment_inverse_isla_bb(df, sl_points=6, tp_max_points=6):
    """
    Estrategia inversa:
      - Trigger 'short' => COMPRA limitada en bb_lower
      - Trigger 'long'  => VENTA limitada en bb_upper
      - TP en la media BB, o a 6 puntos max.
      - SL fijo a 6 puntos.
    """
    trades = []
    position = None
    entry_index = None
    entry_price = None
    trade_side = None
    tp_price = None
    sl_price = None
    pending_trigger = None

    for i in range(1, len(df)):
        # Detectar trigger y guardar para siguiente toque de banda
        if position is None:
            if df['trigger'].iloc[i] == 'short':
                pending_trigger = ('buy', i)   # Trigger short, buscar compra
            elif df['trigger'].iloc[i] == 'long':
                pending_trigger = ('sell', i)  # Trigger long, buscar venta

        # Entrada inversa
        if position is None and pending_trigger:
            side, trig_idx = pending_trigger
            # COMPRA: cuando trigger era 'short' y toca banda inferior
            if side == 'buy' and not pd.isna(df['bb_lower'].iloc[i]) and df['low'].iloc[i] <= df['bb_lower'].iloc[i]:
                entry_index = i
                entry_price = df['bb_lower'].iloc[i]
                trade_side = 'long'
                dist_to_ma = df['bb_ma'].iloc[i] - entry_price
                tp_price = entry_price + min(tp_max_points, dist_to_ma)
                sl_price = entry_price - sl_points
                position = True
                pending_trigger = None
            # VENTA: cuando trigger era 'long' y toca banda superior
            elif side == 'sell' and not pd.isna(df['bb_upper'].iloc[i]) and df['high'].iloc[i] >= df['bb_upper'].iloc[i]:
                entry_index = i
                entry_price = df['bb_upper'].iloc[i]
                trade_side = 'short'
                dist_to_ma = entry_price - df['bb_ma'].iloc[i]
                tp_price = entry_price - min(tp_max_points, dist_to_ma)
                sl_price = entry_price + sl_points
                position = True
                pending_trigger = None

        # GESTIÓN DE LA OPERACIÓN ABIERTA
        if position:
            # Take Profit
            if trade_side == 'long' and df['high'].iloc[i] >= tp_price:
                pnl = tp_price - entry_price
                trades.append({
                    'entry_index': entry_index,
                    'entry_date': df['date'].iloc[entry_index],
                    'entry_price': entry_price,
                    'exit_index': i,
                    'exit_date': df['date'].iloc[i],
                    'exit_price': tp_price,
                    'side': trade_side,
                    'pnl': pnl,
                    'pnl_S': pnl * 50,
                    'exit_type': 'target',
                    'time_in_market': (df['date'].iloc[i] - df['date'].iloc[entry_index]).total_seconds() / 60
                })
                position = None
                continue
            if trade_side == 'short' and df['low'].iloc[i] <= tp_price:
                pnl = entry_price - tp_price
                trades.append({
                    'entry_index': entry_index,
                    'entry_date': df['date'].iloc[entry_index],
                    'entry_price': entry_price,
                    'exit_index': i,
                    'exit_date': df['date'].iloc[i],
                    'exit_price': tp_price,
                    'side': trade_side,
                    'pnl': pnl,
                    'pnl_S': pnl * 50,
                    'exit_type': 'target',
                    'time_in_market': (df['date'].iloc[i] - df['date'].iloc[entry_index]).total_seconds() / 60
                })
                position = None
                continue

            # Stop Loss
            if trade_side == 'long' and df['low'].iloc[i] <= sl_price:
                pnl = sl_price - entry_price
                trades.append({
                    'entry_index': entry_index,
                    'entry_date': df['date'].iloc[entry_index],
                    'entry_price': entry_price,
                    'exit_index': i,
                    'exit_date': df['date'].iloc[i],
                    'exit_price': sl_price,
                    'side': trade_side,
                    'pnl': pnl,
                    'pnl_S': pnl * 50,
                    'exit_type': 'stop',
                    'time_in_market': (df['date'].iloc[i] - df['date'].iloc[entry_index]).total_seconds() / 60
                })
                position = None
                continue
            if trade_side == 'short' and df['high'].iloc[i] >= sl_price:
                pnl = entry_price - sl_price
                trades.append({
                    'entry_index': entry_index,
                    'entry_date': df['date'].iloc[entry_index],
                    'entry_price': entry_price,
                    'exit_index': i,
                    'exit_date': df['date'].iloc[i],
                    'exit_price': sl_price,
                    'side': trade_side,
                    'pnl': pnl,
                    'pnl_S': pnl * 50,
                    'exit_type': 'stop',
                    'time_in_market': (df['date'].iloc[i] - df['date'].iloc[entry_index]).total_seconds() / 60
                })
                position = None
                continue

    return trades
