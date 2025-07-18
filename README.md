Instalación:

pip install -r requirements.txt

script que analiza la entrada al mercado con una vela cuyo cuerpo está por encima/debajo de mercado, pero que todo el cuerpo no toca la media.

main_single_day.py analiza la entrada para un dia concreto
main.py hace lo mismo que el código anterior pero iterando en todo el vector de fechas disponibles.



isla.py  busca las velas y les asigna un puntito verde o rojo

CARPETA: strategies, cotiene las estrategias:

isla_OM.py hace la gestión de entrada de órdenes y genera el fichero tracking_record llamado trades_results.csv
isla_OM_time.py gestiona la entrada de órdenes, pero añade una salida por tiempo tras un número de velas determinado
isla_OM_bb.py acepta que el ES no es un producto tendencial y por lo tanto, intenta cerrar en las bandas de bollinger con un pequeño beneficio
inverse_isla_OM_bb.py es una estrategia que al admintir que el ES no es tendencial, opera a la contra en las bandas de bollinger


summary_trades_results.py agrupa los resultados por dia y saca ratios, genera también el fichero csv llamado summary_by_day.csv



Conclusiones: En espacios temporales de 1 minuto o similar, es muy difícil que la entrada de una señal buena. En estos casos el sistema es perdedor.
Asimismo, ninguna de las variantes, una salida por tiempo, o un scalping al tocar las bandas de bollinger tampoco dan buenos resultados. Por lo tanto, se ha buscado entrar a la contra, es decir, entrar con la señal de la vela aislada (algo que en teoría tiene poca relevancia) a la contra usando la banda de bollinger


En la carpeta outputs se genera el summary_by_day.csv analizable con el equity acumulado