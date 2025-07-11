Instalación:

pip install -r requirements.txt

script que analiza la entrada al mercado con una vela cuyo cuerpo está por encima/debajo de mercado, pero que todo el cuerpo no toca la media.

main_single_day.py analiza la entrada para un dia concreto
main.py hace lo mismo que el código anterior pero iterando en todo el vector de fechas disponibles.

isla.py  busca las velas y les asigna un puntito verde o rojo
isla_OM.py hacela gestión de entrada de órdenes y genera el fichero tracking_record llamado trades_results.csv

summary_trades_results.py agrupa los resultados por dia y saca ratios, genera también el fichero csv llamado summary_by_day.csv

