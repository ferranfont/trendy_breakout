# summary_with_ratios_and_equity.py

import pandas as pd
import numpy as np
import plotly.graph_objs as go
import os
import webbrowser
import empyrical as emp
import matplotlib.pyplot as plt

# -------- CONFIG --------
input_csv = "outputs/tracking_record.csv"
initial_capital = 10000
output_html = "outputs/equity_tracking_curve.html"

# -------- LOAD & PROCESS DATA --------
df = pd.read_csv(input_csv, parse_dates=["entry_time", "exit_time"])
df = df.sort_values("exit_time")

df['equity'] = df['profit_usd'].cumsum() + initial_capital
equity_curve = pd.Series(df['equity'].values, index=df['exit_time']).asfreq("1D").ffill()
returns = equity_curve.pct_change().dropna()

# -------- RATIOS --------
ratios = {
    "Total Return (%)": (equity_curve.iloc[-1] / equity_curve.iloc[0] - 1) * 100,
    "CAGR (%)": emp.annual_return(returns) * 100,
    "Sharpe Ratio": emp.sharpe_ratio(returns),
    "Sortino Ratio": emp.sortino_ratio(returns),
    "Calmar Ratio": emp.calmar_ratio(returns),
    "Max Drawdown (%)": emp.max_drawdown(returns) * 100,
    "Volatility (%)": emp.annual_volatility(returns) * 100,
    "Win Rate (%)": (df['profit_usd'] > 0).sum() / len(df) * 100,
    "Avg Win ($)": df[df['profit_usd'] > 0]['profit_usd'].mean(),
    "Avg Loss ($)": df[df['profit_usd'] < 0]['profit_usd'].mean(),
    "Expectancy ($)": df['profit_usd'].mean(),
    "Average Time per Trade (days)": df['time_in_market'].mean()
}

# -------- PRINT RATIOS --------
print("\n📊 RATIO SUMMARY:")
print(pd.DataFrame(ratios, index=["Metrics"]).T.round(2))

# -------- EQUITY CURVE --------
df['day'] = df['exit_time'].dt.date
summary = df.groupby('day').agg(pnl_sum=('profit_usd', 'sum')).reset_index()
summary['equity'] = summary['pnl_sum'].cumsum() + initial_capital
summary['equity_pos'] = summary['equity'].where(summary['equity'] >= initial_capital, np.nan)
summary['equity_neg'] = summary['equity'].where(summary['equity'] < initial_capital, np.nan)

fig = go.Figure()

fig.add_trace(go.Scatter(
    x=summary['day'], y=summary['equity_pos'],
    mode='lines', fill='tozeroy',
    line=dict(color='rgba(46,204,113,1)', width=2),
    fillcolor='rgba(46,204,113,0.3)', name='Equity +'
))

fig.add_trace(go.Scatter(
    x=summary['day'], y=summary['equity_neg'],
    mode='lines', fill='tozeroy',
    line=dict(color='rgba(231,76,60,1)', width=2),
    fillcolor='rgba(231,76,60,0.3)', name='Equity -'
))

fig.update_layout(
    title='✅ Cumulative Equity Curve (Green = Gain, Red = Loss)',
    xaxis_title='Date',
    yaxis_title='Equity ($)',
    width=1400, height=800,
    template='plotly_white',
    font=dict(size=14),
    margin=dict(l=30, r=30, t=60, b=30)
)

# -------- SAVE & OPEN HTML --------
fig.write_html(output_html, auto_open=False)
print(f"\n📈 Equity curve saved to: {output_html}")
webbrowser.open('file://' + os.path.realpath(output_html))
