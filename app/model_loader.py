# filepath: app/model_loader.py

import os
import boto3
import joblib
import numpy as np
import onnxruntime as ort
import logging
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger(__name__)

class ModelLoader:
    """Clase para cargar modelos y artefactos desde S3"""
    
    def __init__(self, settings):
        self.settings = settings
        self.s3_client = self._create_s3_client()
        self.artifacts_dir = Path("artifacts")
        self.artifacts_dir.mkdir(exist_ok=True)
        
    def _create_s3_client(self):
        """Crear cliente S3"""
        return boto3.client(
            's3',
            aws_access_key_id=self.settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=self.settings.AWS_SECRET_ACCESS_KEY,
            region_name=self.settings.AWS_REGION
        )
    
    def download_file_from_s3(self, s3_key: str, local_path: str) -> bool:
        """Descargar archivo desde S3"""
        try:
            full_local_path = self.artifacts_dir / local_path
            self.s3_client.download_file(
                self.settings.S3_BUCKET, 
                s3_key, 
                str(full_local_path)
            )
            logger.info(f"Downloaded {s3_key} to {full_local_path}")
            return True
        except Exception as e:
            logger.error(f"Error downloading {s3_key}: {e}")
            return False
    
    def load_scaler(self) -> Any:
        """Cargar el scaler"""
        scaler_path = self.artifacts_dir / "scaler.pkl"
        if not scaler_path.exists():
            if not self.download_file_from_s3("entremamiento/scaler.pkl", "scaler.pkl"):
                raise Exception("Failed to download scaler")
        
        return joblib.load(scaler_path)
    
    def load_model(self) -> ort.InferenceSession:
        """Cargar el modelo ONNX"""
        model_path = self.artifacts_dir / "modelo_lstm.onnx"
        if not model_path.exists():
            if not self.download_file_from_s3("entremamiento/modelo_lstm.onnx", "modelo_lstm.onnx"):
                raise Exception("Failed to download model")
        
        return ort.InferenceSession(str(model_path))
    
    def load_test_data(self) -> Dict[str, np.ndarray]:
        """Cargar datos de prueba"""
        x_test_path = self.artifacts_dir / "X_test.npy"
        y_test_path = self.artifacts_dir / "y_test.npy"
        
        if not x_test_path.exists():
            if not self.download_file_from_s3("datos/X_test.npy", "X_test.npy"):
                raise Exception("Failed to download X_test")
        
        if not y_test_path.exists():
            if not self.download_file_from_s3("datos/y_test.npy", "y_test.npy"):
                raise Exception("Failed to download y_test")
        
        return {
            'X_test': np.load(x_test_path),
            'y_test': np.load(y_test_path)
        }
    
    def load_all_artifacts(self) -> Dict[str, Any]:
        """Cargar todos los artefactos necesarios"""
        logger.info("Loading all artifacts...")
        
        artifacts = {
            'scaler': self.load_scaler(),
            'model': self.load_model(),
            'test_data': self.load_test_data()
        }
        
        logger.info("All artifacts loaded successfully")
        return artifacts