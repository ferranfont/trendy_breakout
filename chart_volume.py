import plotly.graph_objs as go
from plotly.subplots import make_subplots
import os

def plot_close_and_volume(timeframe, df, trades_df):
    symbol = 'ES'
    html_path = f'charts/close_vol_chart_{symbol}_{timeframe}.html'
    os.makedirs(os.path.dirname(html_path), exist_ok=True)

    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        row_heights=[0.80, 0.20],
        vertical_spacing=0.03,
    )

    # ---- Velas japonesas ----
    fig.add_trace(go.Candlestick(
        x=df['date'],
        open=df['open'],
        high=df['high'],
        low=df['low'],
        close=df['close'],
        name='OHLC',
        increasing_line_color='green',
        decreasing_line_color='red',
        increasing_line_width=1,
        decreasing_line_width=1,
        showlegend=False,
    ), row=1, col=1)

    # ---- Línea EMA (azul) ----
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['ema'],
        mode='lines',
        line=dict(color='blue', width=1),
        name='EMA',
        showlegend=True,
    ), row=1, col=1)

        # ---- Línea EMA (azul) ----
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['ema_slow'],
        mode='lines',
        #line=dict(color='green', width=1),
        line=dict(color='rgba(46,204,113,0.4)', width=1),
        name='EMA',
        showlegend=True,
    ), row=1, col=1)

    # ---- Puntos rojos bajo la vela si trigger=='short' ----
    short_mask = df['trigger'] == 'short'
    if short_mask.any():
        fig.add_trace(go.Scatter(
            x=df.loc[short_mask, 'date'],
            y=df.loc[short_mask, 'high']+0,
            mode='markers',
            marker=dict(color='red', size=10, symbol='circle'),
            name='Short Trigger',
            showlegend=True
        ), row=1, col=1)

    # ---- Puntos verdes bajo la vela si trigger=='long' ----
    long_mask = df['trigger'] == 'long'
    if long_mask.any():
        fig.add_trace(go.Scatter(
            x=df.loc[long_mask, 'date'],
            y=df.loc[long_mask, 'low'] + 0,
            mode='markers',
            marker=dict(color='green', size=10, symbol='circle'),
            name='Long Trigger',
            showlegend=True
        ), row=1, col=1)

    # ---- Añade operaciones de trades_df ----
    for _, row in trades_df.iterrows():
        color = 'grey' if row['side'] == 'long' else 'grey'
        # Línea discontínua de entrada a salida
        fig.add_trace(go.Scatter(
            x=[row['entry_date'], row['exit_date']],
            y=[row['entry_price'], row['exit_price']],
            mode='lines',
            line=dict(color=color, width=2, dash='dot'),
            showlegend=False,
            hoverinfo='skip'
        ), row=1, col=1)
        # Cuadrado en la salida
        fig.add_trace(go.Scatter(
            x=[row['exit_date']],
            y=[row['exit_price']],
            mode='markers',
            marker=dict(color=color,size=12,symbol='square'),
            name=f"Exit {row['side'].capitalize()}",
            showlegend=False
        ), row=1, col=1)

    # ---- Volumen ----
    fig.add_trace(go.Bar(
        x=df['date'],
        y=df['volume'],
        marker_color='royalblue',
        marker_line_color='blue',
        marker_line_width=0.4,
        opacity=0.95,
        name='Volumen'
    ), row=2, col=1)

    fig.update_layout(
        dragmode='pan',
        title=f'{symbol}_ETH_{timeframe}',
        width=1500,
        height=800,
        margin=dict(l=20, r=20, t=40, b=20),
        font=dict(size=12, color="black"),
        plot_bgcolor='rgba(255,255,255,1)',
        paper_bgcolor='rgba(255,255,255,1)',
        showlegend=True,
        template='plotly_white',
        xaxis=dict(
            type='date',
            showgrid=False,
            linecolor='gray',
            linewidth=1,
            range=[df['date'].min(), df['date'].max()]
        ),
        yaxis=dict(showgrid=True, linecolor='gray', linewidth=1),
        xaxis2=dict(
            type='date',
            tickangle=45,
            showgrid=False,
            linecolor='gray',
            linewidth=1,
            range=[df['date'].min(), df['date'].max()]
        ),
        yaxis2=dict(showgrid=True, linecolor='grey', linewidth=1),

        xaxis_rangeslider_visible=False,
        xaxis2_rangeslider_visible=False,
    )

    # Elimina barra de navegación Plotly
    config = {
        "displayModeBar": False,
        "scrollZoom": True
    }

    fig.write_html(html_path, config=config)
    print(f"✅ Gráfico Plotly guardado como HTML: '{html_path}'")

    import webbrowser
    webbrowser.open('file://' + os.path.realpath(html_path))
