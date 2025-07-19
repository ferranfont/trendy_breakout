import pandas as pd
import numpy as np
import empyrical as emp
import matplotlib.pyplot as plt

# Leer datos
df = pd.read_csv("outputs/trades_results.csv", parse_dates=["exit_date"])
df = df.sort_values("exit_date")

# Equity curve
initial_capital = 10000
equity_curve = df["pnl_S"].cumsum() + initial_capital
equity_curve.index = df["exit_date"]
equity_curve = equity_curve.asfreq("1min").ffill()

# Calcular retornos
returns = equity_curve.pct_change().dropna()

# Drawdown manual
rolling_max = equity_curve.cummax()
drawdown = equity_curve / rolling_max - 1
max_drawdown = drawdown.min()
drawdown_duration = (drawdown < 0).astype(int).groupby((drawdown == 0).astype(int).cumsum()).sum().max()

# Plot Equity
plt.figure(figsize=(10, 4))
equity_curve.plot(title="Equity Curve", ylabel="Capital")
plt.grid()
plt.tight_layout()
plt.show()

# Plot Drawdown
plt.figure(figsize=(10, 3))
drawdown.plot(title="Drawdown (%)", color="red")
plt.grid()
plt.tight_layout()
plt.show()

# Ratios
ratios = {
    "Total Return (%)": (equity_curve[-1] / equity_curve[0] - 1) * 100,
    "CAGR (%)": emp.annual_return(returns) * 100,
    "Sharpe Ratio": emp.sharpe_ratio(returns),
    "Sortino Ratio": emp.sortino_ratio(returns),
    "Calmar Ratio": emp.calmar_ratio(returns),
    "Volatility (%)": emp.annual_volatility(returns) * 100,
    "Max Drawdown (%)": max_drawdown * 100,
    "Drawdown Duration (bars)": drawdown_duration,
    "Win Rate (%)": (df[df["pnl_S"] > 0].shape[0] / df.shape[0]) * 100 if df.shape[0] > 0 else np.nan,
    "Avg Win ($)": df[df["pnl_S"] > 0]["pnl_S"].mean(),
    "Avg Loss ($)": df[df["pnl_S"] < 0]["pnl_S"].mean(),
    "Expectancy ($)": df["pnl_S"].mean()
}

# Mostrar tabla
ratios_df = pd.DataFrame(ratios, index=["Metrics"]).T
print("\n📊 TABLA DE RATIOS COMPLETA:")
print(ratios_df.round(2))
