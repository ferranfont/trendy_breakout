import plotly.graph_objs as go
from plotly.subplots import make_subplots
import os
import pandas as pd

def plot_close_and_volume(timeframe, df, symbol, tracking_record=None):
    df = df.reset_index()
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

    # ---- Breakout points ----
    if 'breakout' in df.columns:
        puntos_breakout = df[df['breakout']]
        fig.add_trace(go.Scatter(
            x=puntos_breakout['date'],
            y=puntos_breakout['high'] + 2,
            mode='markers',
            marker=dict(color='green', size=5, symbol='circle'),
            name='Breakout',
            showlegend=False
        ), row=1, col=1)

    # ---- Breakdown points ----
    if 'breakdown' in df.columns:
        puntos_breakdown = df[df['breakdown']]
        fig.add_trace(go.Scatter(
            x=puntos_breakdown['date'],
            y=puntos_breakdown['low'] - 2,
            mode='markers',
            marker=dict(color='red', size=5, symbol='circle'),
            name='Breakdown',
            showlegend=False
        ), row=1, col=1)

    # ---- EMA line (optional) ----
    if 'ema' in df.columns:
        fig.add_trace(go.Scatter(
            x=df['date'],
            y=df['ema'],
            mode='lines',
            line=dict(color='blue', width=1),
            showlegend=True,
            name="EMA"
        ), row=1, col=1)

    # ---- DONCHIAN CHANNEL ----
    # Banda alta Donchian
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['donchian_high'],
        mode='lines',
        line=dict(color='orange', width=1, dash='dot'),
        name='Donchian High'
    ), row=1, col=1)

    # Banda baja Donchian
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['donchian_low'],
        mode='lines',
        line=dict(color='purple', width=1, dash='dot'),
        name='Donchian Low'
    ), row=1, col=1)


    # ---- TRADE LINES from tracking_record ----
    if tracking_record is not None and not tracking_record.empty:
        # Asegura que los tipos son correctos
        tracking_record = tracking_record.dropna(subset=['entry_time', 'exit_time', 'entry_price', 'exit_price'])
        tracking_record['entry_time'] = pd.to_datetime(tracking_record['entry_time'])
        tracking_record['exit_time'] = pd.to_datetime(tracking_record['exit_time'])
        for _, row in tracking_record.iterrows():
            color = 'seagreen' if row['label'] == 'long' else 'firebrick'
            # Línea discontinua
            fig.add_trace(go.Scatter(
                x=[row['entry_time'], row['exit_time']],
                y=[row['entry_price'], row['exit_price']],
                mode='lines',
                line=dict(color=color, width=2, dash='dot'),
                showlegend=False,
                hoverinfo='skip'
            ), row=1, col=1)
            # Cuadrado en la salida
            fig.add_trace(go.Scatter(
                x=[row['exit_time']],
                y=[row['exit_price']],
                mode='markers',
                marker=dict(color=color, size=9, symbol='square'),
                name=f"Exit {row['label'].capitalize()}",
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
        showlegend=False,
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

    config = {
        "displayModeBar": True,
        "scrollZoom": True
    }

    fig.write_html(html_path, config=config)
    print(f"✅ Gráfico Plotly guardado como HTML: '{html_path}'")

    import webbrowser
    webbrowser.open('file://' + os.path.realpath(html_path))
