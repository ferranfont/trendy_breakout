# script que ejecuta una vela tendencial en la que se entra cuando tenemos una vela entera a favor de una media
import pandas as pd
from dotenv import load_dotenv
from datetime import datetime
import webbrowser
import os

# ====================================================
# 📥 DESCARGA DE DATOS 
# ====================================================
directorio = '../DATA'
nombre_fichero = 'export_es_2015_formatted.csv'
ruta_completa = os.path.join(directorio, nombre_fichero)
print("\n======================== 🔍 df  ===========================")
df = pd.read_csv(ruta_completa)
print('Fichero:', ruta_completa, 'importado')
print(f"Características del Fichero Base: {df.shape}")

print(df.head())