def isla(df):
    """
    Marca 'short' cuando:
        - Hay cruce bajista (close cruza por debajo de la EMA)
        - Se activa alerta.
        - Marca la primera vela tras el cruce donde high < ema y low < low_cruce.
    Marca 'long' cuando:
        - Hay cruce alcista (close cruza por encima de la EMA)
        - Se activa alerta.
        - Marca la primera vela tras el cruce donde low > ema y high > high_cruce.
    """
    trigger = [None] * len(df)
    # Estados separados para las dos alertas
    alert_short = False
    low_cruce = None

    alert_long = False
    high_cruce = None

    for i in range(1, len(df)):
        # Cruce bajista: activa alerta short y guarda el low
        if (df['close'].iloc[i-1] > df['ema'].iloc[i-1]) and (df['close'].iloc[i] < df['ema'].iloc[i]):
            alert_short = True
            low_cruce = df['low'].iloc[i]
        # Cruce alcista: activa alerta long y guarda el high
        if (df['close'].iloc[i-1] < df['ema'].iloc[i-1]) and (df['close'].iloc[i] > df['ema'].iloc[i]):
            alert_long = True
            high_cruce = df['high'].iloc[i]

        # Señal SHORT (solo la primera tras cruce)
        if alert_short and (df['high'].iloc[i] < df['ema'].iloc[i]) and (df['low'].iloc[i] < low_cruce):
            trigger[i] = 'short'
            alert_short = False

        # Señal LONG (solo la primera tras cruce)
        if alert_long and (df['low'].iloc[i] > df['ema'].iloc[i]) and (df['high'].iloc[i] > high_cruce):
            trigger[i] = 'long'
            alert_long = False

        # Reset alerta SHORT si hay cruce alcista (o si vuelve a cerrar por encima)
        if df['close'].iloc[i] > df['ema'].iloc[i]:
            alert_short = False
            low_cruce = None
        # Reset alerta LONG si hay cruce bajista (o si vuelve a cerrar por debajo)
        if df['close'].iloc[i] < df['ema'].iloc[i]:
            alert_long = False
            high_cruce = None

    return trigger
