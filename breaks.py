# Calcula el breakout (close actual > high anterior)

def breaks(df):
    """
    Añade columna 'breakout': True si el close rompe el high de la vela anterior.
    Filtra filas NaN para comparar solo días hábiles.
    """
    df = df.copy()
    df = df[df['close'].notna()]   # Filtra festivos y días sin datos
    df['breakout'] = df['close'] > df['high'].shift(1)
    df['breakdown'] = df['close'] < df['low'].shift(1)
    return df
