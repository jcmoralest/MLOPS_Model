# config/settings.py

import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class Settings:
    """Configuración centralizada de la aplicación"""
    
    # AWS Configuration
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    AWS_REGION = os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
    S3_BUCKET = os.getenv('S3_BUCKET_NAME', 'proyectofinalmlops')
    
    # Model Configuration
    MODEL_VERSION = os.getenv('MODEL_VERSION', 'v1.0.0')
    MIN_R2_SCORE = float(os.getenv('MIN_R2_SCORE', '0.85'))
    MAX_RMSE = float(os.getenv('MAX_RMSE', '10.0'))
    
    # Paths
    ARTIFACTS_PATH = Path(os.getenv('ARTIFACTS_PATH', './artifacts'))
    MODEL_PATH = Path(os.getenv('MODEL_PATH', './models'))
    
    # Environment
    ENVIRONMENT = os.getenv('ENVIRONMENT', 'dev')
    
    # ECS Configuration
    ECS_CLUSTER_DEV = os.getenv('ECS_CLUSTER_DEV', 'ml-model-dev-cluster')
    ECS_CLUSTER_PROD = os.getenv('ECS_CLUSTER_PROD', 'ml-model-prod-cluster')
    ECS_SERVICE_DEV = os.getenv('ECS_SERVICE_DEV', 'ml-model-dev-service')
    ECS_SERVICE_PROD = os.getenv('ECS_SERVICE_PROD', 'ml-model-prod-service')
    
    # Endpoints (actualizar con tus endpoints reales de AWS)
    # Estos serían los endpoints del Application Load Balancer (ALB)
    ENDPOINT_DEV = os.getenv('ENDPOINT_DEV', 'http://ml-dev-alb-123456789.us-east-1.elb.amazonaws.com')
    ENDPOINT_PROD = os.getenv('ENDPOINT_PROD', 'http://ml-prod-alb-987654321.us-east-1.elb.amazonaws.com')
    
    # Ports
    PORT_DEV = int(os.getenv('PORT_DEV', '8502'))
    PORT_PROD = int(os.getenv('PORT_PROD', '8501'))
    
    @classmethod
    def get_endpoint(cls, environment: str) -> str:
        """Obtener endpoint según el ambiente"""
        if environment == 'prod':
            return cls.ENDPOINT_PROD
        return cls.ENDPOINT_DEV
    
    @classmethod
    def get_port(cls, environment: str) -> int:
        """Obtener puerto según el ambiente"""
        if environment == 'prod':
            return cls.PORT_PROD
        return cls.PORT_DEV
    
    @classmethod
    def validate(cls):
        """Validar que todas las configuraciones requeridas estén presentes"""
        required = [
            'AWS_ACCESS_KEY_ID',
            'AWS_SECRET_ACCESS_KEY',
            'S3_BUCKET'
        ]
        
        missing = []
        for var in required:
            if not getattr(cls, var):
                missing.append(var)
        
        if missing:
            raise ValueError(f"Missing required configuration: {', '.join(missing)}")
        
        return True