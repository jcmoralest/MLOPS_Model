# Pronóstico de Serie de Tiempo para ETF SPY

Este proyecto implementa un pipeline de MLOps para el pronóstico de la serie de tiempo del ETF SPY utilizando modelos LSTM exportados a ONNX, con visualización interactiva en Streamlit y gestión de artefactos en AWS S3.

## Estructura del Proyecto

```
MLOPS_Model/
├── app/
│   └── app.py
├── config/
├── models/
│   └── modelo_lstm.onnx
├── artifacts/
│   ├── scaler.pkl
│   ├── X_test.npy
│   └── y_test.npy
├── scripts/
│   └── download_artifacts.py
├── requirements.txt
└── Dockerfile
```

## Descripción

- **app/app.py**: Aplicación principal en Streamlit que descarga artefactos desde S3, realiza inferencia con un modelo LSTM en formato ONNX y muestra los resultados de pronóstico.
- **models/**: Contiene el modelo LSTM exportado a ONNX.
- **artifacts/**: Incluye los artefactos necesarios para la inferencia (scaler, X_test, y_test).
- **scripts/download_artifacts.py**: Script para descargar los artefactos desde AWS S3.
- **requirements.txt**: Lista de dependencias del proyecto.
- **Dockerfile**: Permite construir una imagen reproducible para despliegue.

## Requisitos

- Python 3.9+
- AWS credentials con permisos de lectura en el bucket S3 configurado
- Docker (opcional, para despliegue en contenedor)

## Instalación

1. Clona el repositorio y navega al directorio del proyecto:

    ```bash
    git clone https://github.com/jcmoralest/MLOPS_Model/tree/Dev
    cd MLOPS_Model
    ```

2. Instala las dependencias:

    ```bash
    pip install -r requirements.txt
    ```

3. Configura tus credenciales de AWS como variables de entorno o en un archivo `.env`:

    ```
    AWS_ACCESS_KEY_ID=TU_ACCESS_KEY
    AWS_SECRET_ACCESS_KEY=TU_SECRET_KEY
    AWS_DEFAULT_REGION=us-east-1
    S3_BUCKET_NAME=proyectofinalmlops
    ```

4. Descarga los artefactos desde S3 (opcional si ya están en `artifacts/` y `models/`):

    ```bash
    python scripts/download_artifacts.py
    ```

## Ejecución local

Desde la raíz del proyecto, ejecuta:

```bash
streamlit run app/app.py
```

## Uso con Docker

1. Construye la imagen:

    ```bash
    docker build -t mlops-spy-app .
    ```

2. Ejecuta el contenedor:

    ```bash
    docker run -p 8501:8501 --env-file .env mlops-spy-app
    ```

## Visualización

La aplicación mostrará una gráfica interactiva con los datos reales y el pronóstico de los próximos 200 días para el ETF SPY.

## Archivos Vacíos Detectados

- `models/model.pkl` 



---

**Autores:**  
Jhonata Pacheco
Julio Morales
ICESI - MLOps Proyecto Final