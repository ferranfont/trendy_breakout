# 🧠 Trendy Breakout - Quantitative Strategy Framework

Este repositorio contiene un conjunto de herramientas y scripts para el desarrollo, simulación y evaluación de estrategias de trading basadas en rupturas de canales Donchian y breakout/breakdown simples. Está diseñado para analizar el comportamiento de instrumentos financieros con el fin de clasificarlos como tendenciales o mean-reverting.

---

## 📦 Instalación

```bash
pip install -r requirements.txt


🗂️ Estructura del Proyecto
/Utils
resample.py: Reagrupa los datos a velas diarias (u otro timeframe definido).

main.py: Script principal que ejecuta toda la lógica del sistema:

Carga de datos desde un .csv

Envío a quant_breaks.py para generar señales (breakout, breakdown)

Envío a módulos de estrategias para gestionar las órdenes

Generación de resúmenes de rendimiento y gráficas interactivas

/strategies
Contiene diferentes scripts de lógica de entrada/salida:

strat_break_OM.py: Estrategia basada en ruptura de máximos/mínimos. Incluye gestión de apertura, cierre y stop.

strat_donchian.py: Estrategia clásica Donchian (ruptura de canal superior/inferior).

strat_donchian_time.py: Variante con cierre por tiempo (bars_hold) una vez la operación entra en zona favorable, con stop fijo.

quant_donchian_channel.py: Genera el canal Donchian superior e inferior y las señales correspondientes.

/outputs
Contiene los resultados de las simulaciones:

tracking_record_*.csv: Tracking record completo de cada operación (entrada, salida, duración, beneficio).

equity_tracking_curve.html: Curva de equity interactiva generada con Plotly.

/charts
*_chart_*.html: Visualizaciones HTML de volumen y señales sobre los precios, generadas automáticamente para facilitar análisis visual.

📊 Métricas Generadas
Los scripts de resumen (summary_stats_*.py) generan automáticamente:

Total de operaciones y beneficio total

Win rate, media de duración de las operaciones

Expectancy y profit factor

Ratios financieros clave:

Sharpe Ratio

Sortino Ratio

Calmar Ratio

Volatilidad anualizada

Drawdown máximo

CAGR (%)

Además, se genera una curva de equity diaria (equity_tracking_curve.html) que distingue periodos de beneficio (verde) y pérdida (rojo).

📁 Archivos Clave
summary_stats_break.py: Resumen completo de estrategia de breakout simple.

summary_stats_donchian.py: Análisis detallado para estrategia Donchian.

chart_volume.py: Gráficos de señales con volumen para validación visual.

🚀 Objetivo
El propósito es identificar y etiquetar automáticamente productos financieros como tendenciales o mean-reverting según su comportamiento tras una ruptura, con herramientas cuantitativas robustas y visualizaciones automatizadas.