def add_donchian_channel(df, window=7):
    df['donchian_high'] = df['high'].rolling(window=window, min_periods=1).max()
    df['donchian_low'] = df['low'].rolling(window=window, min_periods=1).min()
    # Banda media opcional:
    df['donchian_mid'] = (df['donchian_high'] + df['donchian_low']) / 2
    return df


