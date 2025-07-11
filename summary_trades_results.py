import pandas as pd
import plotly.graph_objs as go
import os
import webbrowser
import numpy as np

# Cargar CSV de trades
csv_path = 'outputs/trades_results.csv'
trades_df = pd.read_csv(csv_path, parse_dates=['entry_date', 'exit_date'])

# ----------- RESUMEN DIARIO -----------
summary = (
    trades_df
    .groupby('day')
    .agg(
        n_trades = ('pnl', 'count'),
        pnl_sum = ('pnl', 'sum'),
        pnl_S_sum = ('pnl_S', 'sum'),
        avg_pnl = ('pnl', 'mean'),
        n_wins = ('pnl', lambda x: (x > 0).sum()),
        n_losses = ('pnl', lambda x: (x < 0).sum()),
        max_pnl = ('pnl', 'max'),
        min_pnl = ('pnl', 'min'),
        avg_time = ('time_in_market', 'mean')
    )
    .reset_index()
)
summary['day_result'] = summary['pnl_sum'].apply(lambda x: 'win' if x > 0 else ('loss' if x < 0 else 'neutral'))

# Guardar resumen diario en CSV
summary.to_csv('outputs/summary_by_day.csv', index=False)

# Asegúrate de estar ordenado por fecha
summary = summary.sort_values('day')
summary['equity_curve'] = summary['pnl_S_sum'].cumsum()

# Creamos columnas separadas para positivo y negativo
summary['equity_pos'] = summary['equity_curve'].where(summary['equity_curve'] >= 0, 0)
summary['equity_neg'] = summary['equity_curve'].where(summary['equity_curve'] < 0, 0)

# Gráfico de área: verde sobre 0, rojo bajo 0
fig = go.Figure()

# Área verde pálido (por encima de 0)
fig.add_trace(go.Scatter(
    x=summary['day'],
    y=summary['equity_pos'],
    mode='lines',
    fill='tozeroy',
    line=dict(color='rgba(46,204,113,1)', width=2),
    fillcolor='rgba(46,204,113,0.3)',
    name='Equity +'
))

# Área rojo pálido (por debajo de 0)
fig.add_trace(go.Scatter(
    x=summary['day'],
    y=summary['equity_neg'],
    mode='lines',
    fill='tozeroy',
    line=dict(color='rgba(231,76,60,1)', width=2),
    fillcolor='rgba(231,76,60,0.3)',
    name='Equity -'
))

fig.update_layout(
    title='Cumulative Equity Curve (Green above 0, Red below 0)',
    xaxis_title='Día',
    yaxis_title='Equity (€)',
    width=1200,
    height=600,
    template='plotly_white',
    margin=dict(l=30, r=30, t=60, b=30),
    font=dict(size=14),
    legend=dict(x=0.5, y=0.89)
)

# Guarda y abre en navegador
output_html = 'outputs/equity_curve.html'
fig.write_html(output_html, auto_open=False)
print(f"✅ Equity curve guardada en {output_html}")
webbrowser.open('file://' + os.path.realpath(output_html))
