#  🧠 MLOPS_Model - Pronóstico de Serie de Tiempo para ETF SPY

Este proyecto implementa un pipeline de MLOps para el pronóstico de la serie de tiempo del ETF SPY utilizando modelos LSTM exportados a ONNX, con visualización interactiva en Streamlit y gestión de artefactos en AWS S3.

## ¿Cómo funciona?
1. El modelo LSTM es entrenado y exportado a ONNX.
2. Los artefactos y el modelo se almacenan en AWS S3.
3. La aplicación Streamlit descarga los artefactos y realiza la inferencia.
4. El usuario puede visualizar los resultados y métricas desde la interfaz web.

## 📁 Estructura del Proyecto

```
MLOPS_Model/
│
├── app/                         # Lógica principal de la aplicación
│   ├── app.py                   # Endpoint principal (API)
│   ├── app_v2.py                # Versión avanzada de la API
│   ├── model_loader.py          # Carga del modelo
│   └── predictor.py             # Función de predicción
│
├── config/
│   └── settings.py              # Configuraciones generales del proyecto
│
├── models/
│   └── model.pkl                # Modelo entrenado serializado
│
├── pruebas/
│   ├── test_1.py                # Scripts de prueba independientes
│   └── test_2.py
│
├── scripts/                     # Scripts de automatización
│   ├── deploy_to_ecs.py        # Despliegue en AWS ECS
│   ├── download_artifacts.py   # Descarga de artefactos
│   └── health_check.py         # Verificación de salud del servicio
│
├── tests/                       # Pruebas unitarias y de integración
│   ├── test_api.py
│   ├── test_integration.py
│   └── test_model.py
│
├── .github/workflows/
│   └── deploy.yml              # Automatización de CI/CD con GitHub Actions
│
├── Dockerfile                  # Imagen de contenedor para el servicio
├── docker-compose.yml          # Orquestación local
├── requirements.txt            # Dependencias del proyecto
├── README.md                   # Este documento
└── .git/                       # Carpeta de control de versiones Git
```

## Descripción

- **app/app.py**: Aplicación principal en Streamlit que descarga artefactos desde S3, realiza inferencia con un modelo LSTM en formato ONNX y muestra los resultados de pronóstico.
- **models/**: Contiene el modelo LSTM exportado a ONNX.
- **artifacts/**: Incluye los artefactos necesarios para la inferencia (scaler, X_test, y_test).
- **scripts/download_artifacts.py**: Script para descargar los artefactos desde AWS S3.
- **requirements.txt**: Lista de dependencias del proyecto.
- **Dockerfile**: Permite construir una imagen reproducible para despliegue.

## ⚙️ Requisitos

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

-Si corres el proyecto con Docker y pasas el .env con "--env-file .env", las variables estarán disponibles.

-Si corres localmente, asegúrate de cargar el .env (puedes usar "python-dotenv").

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

## Notas

- Colaborador: Asegúrate de que los archivos `scaler.pkl`, `X_test.npy`, `y_test.npy` y `modelo_lstm.onnx` estén presentes en las rutas correctas.
- No subas las credenciales de AWS a ningún repositorio público.

## Contribuciones
¡Las contribuciones son bienvenidas! Por favor abre un issue o pull request para sugerencias o mejoras.

---

**Autores:**  
- Jonathan Pacheco
- Julio Morales
- ICESI - MLOps Proyecto Final# Test CI/CD
