#!pip install onnxruntime
#!pip install boto3

import os
import boto3
import joblib
import tempfile
import onnxruntime as ort
import numpy as np
import pandas as pd
import torch
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler


# Configura tu cliente S3 (si estás en local y no tienes IAM)
s3 = boto3.client('s3',
                  aws_access_key_id='AKIAWQYSU3LK2WICFH7E',
                  aws_secret_access_key='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',
                  region_name='us-east-1')  # Cambia según tu región

# Nombre del bucket y la ruta del archivo
bucket_name = 'proyectofinalmlops'
s3_key = 'entremamiento/scaler.pkl'
local_path = 'scaler.pkl'  # Nombre con el que se guardará localmente

# Descargar los archivos
s3.download_file(bucket_name, s3_key, local_path)
s3.download_file(bucket_name, 'entremamiento/modelo_lstm.onnx', 'modelo_lstm.onnx')
s3.download_file(bucket_name, 'datos/X_test.npy', 'X_test.npy')
s3.download_file(bucket_name, 'datos/y_test.npy', 'y_test.npy')

#cargar los archivos
scaler = joblib.load('scaler.pkl')
# Carga el scaler previamente guardado
#scaler = joblib.load("/content/sample_data/scaler.pkl")

#cargar el modelo 
session = ort.InferenceSession("modelo_lstm.onnx")
# Obtener nombres de entrada y salida
input_name = session.get_inputs()[0].name
output_name = session.get_outputs()[0].name

yy_test = np.load('y_test.npy')
XX_test = np.load('X_test.npy')

y_test = torch.tensor(yy_test)
X_test = torch.tensor(XX_test)

def pronostico(ultim_ventana):
  #ventana_escalada = scaler.transform(ultim_ventana) # no lo usamos por que la particion se realizo cuando ya estaba la data estandarizada
  entrada = ultim_ventana.reshape(1, ultim_ventana.shape[0], ultim_ventana.shape[1]).astype(np.float32)
  output = session.run(None, {"input": entrada})[0]
  pred = output[0, 0]
  predicciones_original = scaler.inverse_transform(np.array(pred).reshape(-1, 1))
  return float(predicciones_original[0][0])

ultima_ventana1 = np.array(X_test[0])
ultima_ventana2 = np.array(X_test[100])
ultima_ventana3 = np.array(X_test[500])
ultima_ventana4 = np.array(X_test[1000])
ultima_ventana5 = np.array(X_test[1200])
ultima_ventana6 = np.array(X_test[1450])
ultima_ventana7 = np.array(X_test[1479])

def test_prediccion():
  assert pronostico(ultima_ventana1) == 265.36865234375
  assert pronostico(ultima_ventana2) == 289.42669677734375
  assert pronostico(ultima_ventana3) == 277.4028015136719
  assert pronostico(ultima_ventana4) == 437.3785705566406
  assert pronostico(ultima_ventana5) == 400.95068359375
  assert pronostico(ultima_ventana6) == 476.4277648925781
  assert pronostico(ultima_ventana7) == 500.10400390625




