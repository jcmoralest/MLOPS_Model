# filepath: app/app.py
import os
import boto3
import torch
import joblib
import tempfile
import numpy as np
import pandas as pd
import seaborn as sns
import streamlit as st
import onnxruntime as ort
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import timedelta
from sklearn.preprocessing import MinMaxScaler
import sys
import logging
from pathlib import Path

from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# python -m pip install --upgrade pip
# pip install streamlit matplotlib pandas onnxruntime boto3 joblib  torch datetime sklearn
# pip install datetime
# pip install scikit-learn
# pip install onnxruntime


## para ejecutar es este desde la terminal
# streamlit run app.py


#tempfile

# Configura tu cliente S3 (si estás en local y no tienes IAM)
s3 = boto3.client(
    's3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
)

# Nombre del bucket y la ruta del archivo
bucket_name = 'proyectofinalmlops'
s3_key = 'entremamiento/scaler.pkl'

# Update paths to use environment variables
MODEL_PATH = os.getenv('MODEL_PATH', './models')
ARTIFACTS_PATH = os.getenv('ARTIFACTS_PATH', './artifacts')

# Update file paths
local_path = os.path.join(ARTIFACTS_PATH, 'scaler.pkl')
model_path = os.path.join(MODEL_PATH, 'modelo_lstm.onnx')
x_test_path = os.path.join(ARTIFACTS_PATH, 'X_test.npy')
y_test_path = os.path.join(ARTIFACTS_PATH, 'y_test.npy')


# Descargar los archivos
s3.download_file(bucket_name, s3_key, local_path)
s3.download_file(bucket_name, 'entremamiento/modelo_lstm.onnx', model_path)
s3.download_file(bucket_name, 'datos/X_test.npy', x_test_path)
s3.download_file(bucket_name, 'datos/y_test.npy', y_test_path)

#cargar los archivos
scaler = joblib.load(local_path)
#cargar el modelo 
session = ort.InferenceSession(model_path)
# Obtener nombres de entrada y salida
input_name = session.get_inputs()[0].name
output_name = session.get_outputs()[0].name

#cargamos los archivos
yy_test = np.load('y_test.npy')
XX_test = np.load('X_test.npy')
y_test = torch.tensor(yy_test)
X_test = torch.tensor(XX_test)

ventana_escalada = X_test[X_test.shape[0]-1].detach().numpy()
entrada = ventana_escalada.reshape(1, ventana_escalada.shape[0], ventana_escalada.shape[1]).astype(np.float32)

predicciones = []

for _ in range(200):
    output = session.run(None, {"input": entrada})[0]
    pred = output[0, 0]  # último valor de la secuencia predicha
    predicciones.append(pred)
    # Agregar la predicción a la ventana y eliminar el primer valor
    entrada = np.append(entrada[:, 1:, :], [[[pred]]], axis=1)

# invertir el scalado 
pronostico_np  = scaler.inverse_transform(np.array(predicciones).reshape(-1, 1))

#datos reales
datos_reales_np = scaler.inverse_transform(np.array(y_test).reshape(-1, 1))

# Creamos un eje de tiempo para el pronóstico (continuando los datos reales)
x_reales = np.arange(len(datos_reales_np))
x_pronostico = np.arange(len(datos_reales_np), len(datos_reales_np) + len(pronostico_np))

# Título de la app
st.title("Pronóstico de Serie de ETF SPY")

## grafico 2
# st.subheader("Serie de Tiempo + Pronóstico (200 días)")
#fig, ax = plt.subplots(figsize=(12, 6))
#ax.plot(x_reales, datos_reales_np, label="Datos reales")
#ax.plot(x_pronostico, pronostico_np, label="Pronóstico", linestyle="--", color="orange")
#ax.set_xlabel("Fecha")
#ax.set_ylabel("Valor")
#ax.set_title("Pronóstico de ETF")
#ax.legend()
#ax.grid(True)
#st.pyplot(fig)



# Estilo profesional con seaborn
sns.set(style="whitegrid")
# Crear figura
fig, ax = plt.subplots(figsize=(14, 7))
# Graficar datos reales
ax.plot(x_reales, datos_reales_np, label="Datos reales", linewidth=2.5, color="#1f77b4")
# Graficar pronóstico
ax.plot(x_pronostico, pronostico_np, label="Pronóstico (200 días)", linewidth=2.5, linestyle="--", color="#ff7f0e")
# Formato de fecha (si tus datos son fechas)
ax.xaxis.set_major_locator(mdates.AutoDateLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
plt.xticks(rotation=45)
# Etiquetas y título
ax.set_title("Pronóstico de Valor del ETF", fontsize=20, weight='bold', pad=20)
ax.set_xlabel("Fecha", fontsize=14)
ax.set_ylabel("Precio de Cierre", fontsize=14)
# Leyenda y grilla
ax.legend(fontsize=12, loc='upper left', frameon=True)
ax.grid(True, linestyle='--', linewidth=0.5)
# Remover bordes innecesarios
sns.despine()
# Margen y presentación
plt.tight_layout()
# Mostrar en Streamlit
st.pyplot(fig)