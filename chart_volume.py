import plotly.graph_objs as go
from plotly.subplots import make_subplots
import os

def plot_close_and_volume(timeframe, df, symbol):
    df = df.reset_index()
    html_path = f'charts/close_vol_chart_{symbol}_{timeframe}.html'
    os.makedirs(os.path.dirname(html_path), exist_ok=True)

    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        row_heights=[0.80, 0.20],
        vertical_spacing=0.03,
    )

    # ---- Velas japonesas con borde negro ----
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

    # Línea EMA real (opcional, naranja)
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['ema'],
        mode='lines',
        line=dict(color='blue', width=1),
        showlegend=True,
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

        # ==== Esta línea elimina el navegador intermedio ====
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
