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

## probar un cambio significativo en  una metrica significativa



# sabemos que el RMSE de train fue 12.21 y el respectivo RMSE de test fue: 25.92
#Como tope establecemos que el error en valor absoluto de cada una de los pronosticos no debe superar el valor 
#de dos veces el RMSE equivalente a 51.84

# from re import A
# Probamos que no existe un cambio significativo en alguna métrica definida dado el modelo que se tenga.
# para esta prueba vamos a calcular los ultimos 10 pronosticos del conjunto de prueba y garantizamos 
# que ninguno de estos supera la medida esablecida de 51.84

#### RMSE
def test_model(numeros):

  a = True
  Abs_error =[]

  for n in numeros:
    predicciones_invertidas_t = pronostico(np.array(X_test[n]))
    aerr = abs(scaler.inverse_transform(np.array(y_test[n]).reshape(-1, 1)).item()-predicciones_invertidas_t)
    Abs_error.append(aerr)
    if (aerr > 51.84):
      a = False
    
  return(a)
  print(Abs_error)
  
numeros = [1572, 1573, 1574, 1575, 1576, 1577, 1578, 1579, 1580, 1581]
assert test_model(numeros) == True
