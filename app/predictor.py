# filepath: app/predictor.py
#     """Renderizar la barra lateral de Streamlit"""

import numpy as np
import onnxruntime as ort
import logging
from typing import Dict, Any, List
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

logger = logging.getLogger(__name__)

class ETFPredictor:
    """Clase para realizar predicciones con el modelo LSTM"""
    
    def __init__(self, model_session: ort.InferenceSession, scaler, test_data: Dict[str, np.ndarray]):
        """
        Inicializar el predictor
        
        Args:
            model_session: Sesión ONNX del modelo
            scaler: Scaler para normalización de datos
            test_data: Datos de prueba (X_test, y_test)
        """
        self.model_session = model_session
        self.scaler = scaler
        self.test_data = test_data
        
        # Obtener nombres de entrada y salida del modelo
        self.input_name = self.model_session.get_inputs()[0].name
        self.output_name = self.model_session.get_outputs()[0].name
        
        logger.info(f"Predictor initialized with input: {self.input_name}, output: {self.output_name}")
    
    def predict_single(self, input_window: np.ndarray) -> float:
        """
        Realizar una predicción individual
        
        Args:
            input_window: Ventana de datos de entrada
            
        Returns:
            float: Predicción individual
        """
        try:
            # Preparar entrada para el modelo
            entrada = input_window.reshape(1, input_window.shape[0], input_window.shape[1]).astype(np.float32)
            
            # Realizar predicción
            output = self.model_session.run(None, {self.input_name: entrada})[0]
            pred = output[0, 0]
            
            # Desnormalizar predicción
            prediccion_original = self.scaler.inverse_transform(np.array(pred).reshape(-1, 1))
            
            return float(prediccion_original[0][0])
            
        except Exception as e:
            logger.error(f"Error in single prediction: {e}")
            raise
    
    def predict(self, num_days: int) -> np.ndarray:
        """
        Realizar predicciones para múltiples días
        
        Args:
            num_days: Número de días a predecir
            
        Returns:
            np.ndarray: Array de predicciones
        """
        try:
            predictions = []
            
            # Usar la última ventana de datos de prueba como punto de partida
            current_window = self.test_data['X_test'][-1].copy()
            
            for day in range(num_days):
                # Realizar predicción
                pred = self.predict_single(current_window)
                predictions.append(pred)
                
                # Actualizar ventana deslizante
                # Normalizar la nueva predicción para agregarla a la ventana
                pred_normalized = self.scaler.transform(np.array([[pred]]))[0, 0]
                
                # Desplazar ventana y agregar nueva predicción
                current_window = np.roll(current_window, -1, axis=0)
                current_window[-1, 0] = pred_normalized
                
                if (day + 1) % 50 == 0:
                    logger.info(f"Generated {day + 1}/{num_days} predictions")
            
            return np.array(predictions)
            
        except Exception as e:
            logger.error(f"Error in multi-day prediction: {e}")
            raise
    
    def get_real_data(self) -> np.ndarray:
        """
        Obtener datos reales desnormalizados para visualización
        
        Returns:
            np.ndarray: Datos reales desnormalizados
        """
        try:
            real_data = self.scaler.inverse_transform(
                self.test_data['y_test'].reshape(-1, 1)
            ).flatten()
            return real_data
        except Exception as e:
            logger.error(f"Error getting real data: {e}")
            raise
    
    def evaluate_model(self) -> Dict[str, float]:
        """
        Evaluar el rendimiento del modelo en datos de prueba
        
        Returns:
            Dict[str, float]: Métricas de evaluación
        """
        try:
            # Generar predicciones para todos los datos de prueba
            y_pred = []
            
            for i in range(len(self.test_data['X_test'])):
                pred = self.predict_single(self.test_data['X_test'][i])
                y_pred.append(pred)
            
            y_pred = np.array(y_pred)
            
            # Obtener valores reales
            y_true = self.get_real_data()
            
            # Calcular métricas
            mse = mean_squared_error(y_true, y_pred)
            rmse = np.sqrt(mse)
            mae = mean_absolute_error(y_true, y_pred)
            r2 = r2_score(y_true, y_pred)
            
            metrics = {
                'mse': float(mse),
                'rmse': float(rmse),
                'mae': float(mae),
                'r2': float(r2),
                'predictions_count': len(y_pred)
            }
            
            logger.info(f"Model evaluation completed: R²={r2:.4f}, RMSE={rmse:.4f}")
            return metrics
            
        except Exception as e:
            logger.error(f"Error in model evaluation: {e}")
            raise
    
    def get_prediction_statistics(self, predictions: np.ndarray) -> Dict[str, float]:
        """
        Obtener estadísticas de las predicciones
        
        Args:
            predictions: Array de predicciones
            
        Returns:
            Dict[str, float]: Estadísticas de las predicciones
        """
        try:
            stats = {
                'min': float(predictions.min()),
                'max': float(predictions.max()),
                'mean': float(predictions.mean()),
                'std': float(predictions.std()),
                'median': float(np.median(predictions)),
                'q25': float(np.percentile(predictions, 25)),
                'q75': float(np.percentile(predictions, 75)),
                'trend': 'upward' if predictions[-1] > predictions[0] else 'downward',
                'volatility': float(predictions.std() / predictions.mean() * 100)  # CV%
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error calculating prediction statistics: {e}")
            raise
    
    def validate_predictions(self, predictions: np.ndarray, max_error_threshold: float = 51.84) -> Dict[str, Any]:
        """
        Validar que las predicciones están dentro de rangos aceptables
        
        Args:
            predictions: Array de predicciones
            max_error_threshold: Umbral máximo de error aceptable
            
        Returns:
            Dict[str, Any]: Resultados de validación
        """
        try:
            validation_results = {
                'valid': True,
                'checks': {},
                'errors': []
            }
            
            # Verificar valores NaN o infinitos
            has_invalid = np.any(np.isnan(predictions)) or np.any(np.isinf(predictions))
            validation_results['checks']['no_invalid_values'] = not has_invalid
            if has_invalid:
                validation_results['valid'] = False
                validation_results['errors'].append("Predictions contain NaN or infinite values")
            
            # Verificar valores negativos
            has_negative = np.any(predictions < 0)
            validation_results['checks']['no_negative_values'] = not has_negative
            if has_negative:
                validation_results['valid'] = False
                validation_results['errors'].append("Predictions contain negative values")
            
            # Verificar valores extremadamente altos
            has_extreme = np.any(predictions > 1000)
            validation_results['checks']['no_extreme_values'] = not has_extreme
            if has_extreme:
                validation_results['valid'] = False
                validation_results['errors'].append("Predictions contain extremely high values (>1000)")
            
            # Verificar variabilidad razonable
            volatility = predictions.std() / predictions.mean() * 100
            reasonable_volatility = volatility < 50  # Menos del 50% de CV
            validation_results['checks']['reasonable_volatility'] = reasonable_volatility
            validation_results['volatility'] = volatility
            if not reasonable_volatility:
                validation_results['errors'].append(f"Predictions show excessive volatility: {volatility:.2f}%")
            
            return validation_results
            
        except Exception as e:
            logger.error(f"Error in prediction validation: {e}")
            return {
                'valid': False,
                'checks': {},
                'errors': [f"Validation error: {str(e)}"]
            }