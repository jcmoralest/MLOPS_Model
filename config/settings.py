import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class Settings:
    """Configuración de la aplicación"""
    
    # AWS Configuration
    AWS_ACCESS_KEY_ID: str = os.getenv('AWS_ACCESS_KEY_ID', 'AKIAWQYSU3LK2WICFH7E')
    AWS_SECRET_ACCESS_KEY: str = os.getenv('AWS_SECRET_ACCESS_KEY', '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')
    AWS_REGION: str = os.getenv('AWS_REGION', 'us-east-1')
    S3_BUCKET: str = os.getenv('S3_BUCKET', 'proyectofinalmlops')
    
    # Model Configuration
    MODEL_VERSION: str = os.getenv('MODEL_VERSION', 'v1.0.0')
    MODEL_PATH: str = 'entremamiento/modelo_lstm.onnx'
    SCALER_PATH: str = 'entremamiento/scaler.pkl'
    
    # Data Configuration
    X_TEST_PATH: str = 'datos/X_test.npy'
    Y_TEST_PATH: str = 'datos/y_test.npy'
    
    # Application Configuration
    ENVIRONMENT: str = os.getenv('ENVIRONMENT', 'dev')
    DEBUG: bool = os.getenv('DEBUG', 'False').lower() == 'true'
    
    # Performance Configuration
    MAX_PREDICTION_DAYS: int = int(os.getenv('MAX_PREDICTION_DAYS', '365'))
    DEFAULT_PREDICTION_DAYS: int = int(os.getenv('DEFAULT_PREDICTION_DAYS', '200'))
    
    # Test Configuration
    MIN_R2_SCORE: float = float(os.getenv('MIN_R2_SCORE', '0.85'))
    MAX_RMSE: float = float(os.getenv('MAX_RMSE', '10.0'))
    
    def __post_init__(self):
        """Validar configuración después de la inicialización"""
        required_vars = ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY']
        missing_vars = [var for var in required_vars if not getattr(self, var)]
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {missing_vars}")
    
    @property
    def is_production(self) -> bool:
        """Verificar si estamos en producción"""
        return self.ENVIRONMENT.lower() == 'prod'
    
    @property
    def log_level(self) -> str:
        """Nivel de logging basado en el ambiente"""
        return 'DEBUG' if self.DEBUG else 'INFO'