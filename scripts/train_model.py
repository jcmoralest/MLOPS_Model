import os
import numpy as np
import joblib

# Simulación de entrenamiento de modelo LSTM y generación de artefactos
# En un caso real, aquí iría el código de entrenamiento con tus datos

def fake_train_and_export():
    # Simula datos y modelo
    scaler = {"mean": 0.5, "std": 0.1}
    X_test = np.random.rand(100, 10)
    y_test = np.random.rand(100)
    # Simula un modelo ONNX (en la práctica, exporta tu modelo real)
    onnx_model_content = b"fake-onnx-model-content"

    # Rutas de guardado
    artifacts_path = os.getenv("ARTIFACTS_PATH", "artifacts")
    models_path = os.getenv("MODEL_PATH", "models")
    os.makedirs(artifacts_path, exist_ok=True)
    os.makedirs(models_path, exist_ok=True)

    # Guardar scaler
    joblib.dump(scaler, os.path.join(artifacts_path, "scaler.pkl"))
    # Guardar X_test y y_test
    np.save(os.path.join(artifacts_path, "X_test.npy"), X_test)
    np.save(os.path.join(artifacts_path, "y_test.npy"), y_test)
    # Guardar modelo ONNX simulado
    with open(os.path.join(models_path, "modelo_lstm.onnx"), "wb") as f:
        f.write(onnx_model_content)

    print("Modelo y artefactos guardados correctamente.")

if __name__ == "__main__":
    fake_train_and_export()