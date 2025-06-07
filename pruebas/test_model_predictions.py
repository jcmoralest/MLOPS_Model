# tests/test_model_predictions.py

import os
import sys
import boto3
import joblib
import pytest
import numpy as np
import onnxruntime as ort
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.append(str(Path(__file__).parent.parent))

class TestModelPredictions:
    """Tests para verificar predicciones específicas del modelo"""
    
    @classmethod
    def setup_class(cls):
        """Configuración inicial - descargar archivos si es necesario"""
        # Verificar si los archivos ya existen
        artifacts_path = Path("artifacts")
        
        if not all([
            (artifacts_path / "scaler.pkl").exists(),
            (artifacts_path / "modelo_lstm.onnx").exists(),
            (artifacts_path / "X_test.npy").exists(),
            (artifacts_path / "y_test.npy").exists()
        ]):
            # Si no existen, usar el script de descarga
            import subprocess
            result = subprocess.run([sys.executable, "scripts/download_artifacts.py"], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                pytest.fail(f"Failed to download artifacts: {result.stderr}")
        
        # Cargar archivos
        cls.scaler = joblib.load(artifacts_path / "scaler.pkl")
        cls.session = ort.InferenceSession(str(artifacts_path / "modelo_lstm.onnx"))
        cls.X_test = np.load(artifacts_path / "X_test.npy")
        cls.y_test = np.load(artifacts_path / "y_test.npy")
    
    def pronostico(self, ultim_ventana):
        """Función auxiliar para hacer pronósticos"""
        entrada = ultim_ventana.reshape(1, ultim_ventana.shape[0], 
                                       ultim_ventana.shape[1]).astype(np.float32)
        output = self.session.run(None, {"input": entrada})[0]
        pred = output[0, 0]
        predicciones_original = self.scaler.inverse_transform(
            np.array(pred).reshape(-1, 1)
        )
        return float(predicciones_original[0][0])
    
    def test_specific_predictions(self):
        """Test 1: Verificar predicciones específicas"""
        test_cases = [
            (0, 265.36865234375),
            (100, 289.42669677734375),
            (500, 277.4028015136719),
            (1000, 437.3785705566406),
            (1200, 400.95068359375),
            (1450, 476.4277648925781),
            (1479, 500.10400390625)
        ]
        
        for idx, expected_value in test_cases:
            ultima_ventana = np.array(self.X_test[idx])
            prediction = self.pronostico(ultima_ventana)
            
            # Permitir pequeña tolerancia por diferencias de precisión
            assert abs(prediction - expected_value) < 0.001, \
                f"Prediction for index {idx} failed: {prediction} != {expected_value}"
            
            print(f"✅ Prediction {idx}: {prediction:.6f} (expected: {expected_value})")
    
    def test_model_error_threshold(self):
        """Test 2: Verificar que el error no supera el umbral"""
        # RMSE de train fue 12.21 y RMSE de test fue 25.92
        # Umbral establecido: 2 * RMSE = 51.84
        max_error_threshold = 51.84
        
        # Probar últimos 10 pronósticos
        indices = list(range(1572, 1582))
        errors = []
        
        for n in indices:
            if n < len(self.X_test):  # Verificar que el índice existe
                pred = self.pronostico(np.array(self.X_test[n]))
                real = self.scaler.inverse_transform(
                    np.array(self.y_test[n]).reshape(-1, 1)
                ).item()
                
                abs_error = abs(real - pred)
                errors.append(abs_error)
                
                assert abs_error <= max_error_threshold, \
                    f"Error at index {n} exceeds threshold: {abs_error:.2f} > {max_error_threshold}"
        
        avg_error = np.mean(errors)
        print(f"✅ All errors within threshold. Average error: {avg_error:.2f}")
        print(f"   Max error: {max(errors):.2f}, Threshold: {max_error_threshold}")

# Tests adicionales para mayor cobertura
class TestModelIntegrity:
    """Tests adicionales para verificar la integridad del modelo"""
    
    def test_model_files_exist(self):
        """Verificar que todos los archivos necesarios existen"""
        required_files = [
            "artifacts/scaler.pkl",
            "artifacts/modelo_lstm.onnx",
            "artifacts/X_test.npy",
            "artifacts/y_test.npy"
        ]
        
        for file_path in required_files:
            assert Path(file_path).exists(), f"Required file not found: {file_path}"
            assert Path(file_path).stat().st_size > 0, f"File is empty: {file_path}"
    
    def test_model_output_range(self):
        """Verificar que las predicciones están en un rango razonable"""
        # Cargar modelo si no está cargado
        if not hasattr(self, 'session'):
            TestModelPredictions.setup_class()
            self.session = TestModelPredictions.session
            self.X_test = TestModelPredictions.X_test
            self.scaler = TestModelPredictions.scaler
        
        # Hacer algunas predicciones aleatorias
        sample_indices = np.random.choice(len(self.X_test), size=10, replace=False)
        
        for idx in sample_indices:
            pred = TestModelPredictions().pronostico(np.array(self.X_test[idx]))
            
            # Verificar rango razonable para ETF SPY (entre $50 y $600)
            assert 50 <= pred <= 600, \
                f"Prediction out of reasonable range: {pred}"
            
            # Verificar que no es NaN o infinito
            assert not np.isnan(pred), "Prediction is NaN"
            assert not np.isinf(pred), "Prediction is infinite"