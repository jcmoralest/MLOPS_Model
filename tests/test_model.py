# filepath: tests/test_model.py
# -*- coding: utf-8 -*-
# tests/test_model.py

import pytest
import numpy as np
import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.append(str(Path(__file__).parent.parent))

from app.model_loader import ModelLoader
from app.predictor import ETFPredictor
from config.settings import Settings

class TestMLModel:
    """Tests para el modelo de ML"""
    
    @classmethod
    def setup_class(cls):
        """Configuración inicial para las pruebas"""
        cls.settings = Settings()
        cls.model_loader = ModelLoader(cls.settings)
        
        # Cargar artefactos
        artifacts = cls.model_loader.load_all_artifacts()
        cls.predictor = ETFPredictor(
            model_session=artifacts['model'],
            scaler=artifacts['scaler'],
            test_data=artifacts['test_data']
        )
    
    def test_model_responds_with_defined_input(self):
        """Test: El modelo responde con datos de entrada definidos"""
        # Preparar datos de entrada de prueba
        test_input = np.random.random((1, 60, 1)).astype(np.float32)
        
        # Realizar predicción
        result = self.predictor.model_session.run(
            None, 
            {self.predictor.input_name: test_input}
        )
        
        # Verificaciones
        assert result is not None, "El modelo no devolvió resultados"
        assert len(result) > 0, "El resultado está vacío"
        assert isinstance(result[0], np.ndarray), "El resultado no es un array numpy"
        assert result[0].shape == (1, 1), f"Forma inesperada del resultado: {result[0].shape}"
        
        print(f"✅ Test 1 PASSED: El modelo responde correctamente")
        print(f"   Forma del resultado: {result[0].shape}")
        print(f"   Valor predicho: {result[0][0, 0]}")
    
    def test_model_performance_metrics(self):
        """Test: El modelo mantiene métricas de rendimiento aceptables"""
        # Evaluar el modelo
        metrics = self.predictor.evaluate_model()
        
        # Verificaciones de métricas
        assert 'r2' in metrics, "Métrica R² no encontrada"
        assert 'rmse' in metrics, "Métrica RMSE no encontrada"
        assert 'mae' in metrics, "Métrica MAE no encontrada"
        assert 'mse' in metrics, "Métrica MSE no encontrada"
        
        # Verificar umbrales de rendimiento
        min_r2 = self.settings.MIN_R2_SCORE
        max_rmse = self.settings.MAX_RMSE
        
        assert metrics['r2'] >= min_r2, \
            f"R² score too low: {metrics['r2']:.4f} < {min_r2}"
        
        assert metrics['rmse'] <= max_rmse, \
            f"RMSE too high: {metrics['rmse']:.4f} > {max_rmse}"
        
        assert metrics['mae'] >= 0, "MAE debe ser no negativo"
        assert metrics['mse'] >= 0, "MSE debe ser no negativo"
        
        print(f"✅ Test 2 PASSED: Métricas de rendimiento aceptables")
        print(f"   R² Score: {metrics['r2']:.4f} (mín: {min_r2})")
        print(f"   RMSE: {metrics['rmse']:.4f} (máx: {max_rmse})")
        print(f"   MAE: {metrics['mae']:.4f}")
        print(f"   MSE: {metrics['mse']:.4f}")
    
    def test_prediction_consistency(self):
        """Test: Las predicciones son consistentes y realistas"""
        # Generar predicciones
        predictions = self.predictor.predict(30)  # 30 días
        
        # Verificaciones básicas
        assert len(predictions) == 30, f"Número incorrecto de predicciones: {len(predictions)}"
        assert all(isinstance(p, (int, float, np.number)) for p in predictions), \
            "Las predicciones contienen valores no numéricos"
        assert all(not np.isnan(p) for p in predictions), \
            "Las predicciones contienen valores NaN"
        assert all(not np.isinf(p) for p in predictions), \
            "Las predicciones contienen valores infinitos"
        
        # Verificar rango razonable (precios de ETF típicamente entre $50-$500)
        assert all(p > 0 for p in predictions), \
            "Las predicciones contienen valores negativos"
        assert all(p < 1000 for p in predictions), \
            "Las predicciones contienen valores extremadamente altos"
        
        print(f"✅ Test 3 PASSED: Predicciones consistentes y realistas")
        print(f"   Rango de predicciones: ${predictions.min():.2f} - ${predictions.max():.2f}")
        print(f"   Promedio: ${predictions.mean():.2f}")
    
    def test_data_integrity(self):
        """Test: Integridad de los datos cargados"""
        # Verificar datos de prueba
        X_test = self.predictor.test_data['X_test']
        y_test = self.predictor.test_data['y_test']
        
        # Verificaciones de forma
        assert X_test.ndim == 3, f"X_test debe tener 3 dimensiones, tiene {X_test.ndim}"
        assert y_test.ndim == 1, f"y_test debe tener 1 dimensión, tiene {y_test.ndim}"
        assert X_test.shape[0] == y_test.shape[0], \
            f"Inconsistencia en número de muestras: X_test={X_test.shape[0]}, y_test={y_test.shape[0]}"
        
        # Verificar que no hay valores faltantes
        assert not np.any(np.isnan(X_test)), "X_test contiene valores NaN"
        assert not np.any(np.isnan(y_test)), "y_test contiene valores NaN"
        
        # Verificar scaler
        real_data = self.predictor.get_real_data()
        assert len(real_data) > 0, "Los datos reales están vacíos"
        assert not np.any(np.isnan(real_data)), "Los datos reales contienen NaN"
        
        print(f"✅ Test 4 PASSED: Integridad de datos verificada")
        print(f"   Forma X_test: {X_test.shape}")
        print(f"   Forma y_test: {y_test.shape}")
        print(f"   Datos reales: {len(real_data)} valores")

if __name__ == "__main__":
    # Ejecutar tests directamente
    test_instance = TestMLModel()
    test_instance.setup_class()
    
    print("🧪 Ejecutando pruebas del modelo ML...")
    print("=" * 50)
    
    try:
        test_instance.test_model_responds_with_defined_input()
        test_instance.test_model_performance_metrics()
        test_instance.test_prediction_consistency()
        test_instance.test_data_integrity()
        
        print("=" * 50)
        print("🎉 Todas las pruebas pasaron exitosamente!")
        
    except AssertionError as e:
        print(f"❌ Test falló: {e}")
        exit(1)
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        exit(1)