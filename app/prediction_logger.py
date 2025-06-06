# filepath: app/prediction_logger.py

import boto3
import logging
from datetime import datetime
from typing import Union, List

logger = logging.getLogger(__name__)

class PredictionLogger:
    """Clase para registrar predicciones en archivos TXT en S3"""
    
    def __init__(self, bucket_name: str, aws_access_key_id: str, aws_secret_access_key: str, region: str = 'us-east-1'):
        self.bucket_name = bucket_name
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region
        )
    
    def log_prediction(self, prediction: Union[float, List[float]], environment: str = 'dev'):
        """
        Registrar una predicción en el archivo correspondiente en S3
        
        Args:
            prediction: Predicción individual o lista de predicciones
            environment: 'dev' o 'prod'
        """
        try:
            # Nombre del archivo
            filename = f"predicciones_{environment}.txt"
            s3_key = f"predictions/{filename}"
            
            # Formatear la entrada del log
            timestamp = datetime.now().isoformat()
            if isinstance(prediction, list):
                prediction_str = f"[{', '.join(map(str, prediction))}]"
            else:
                prediction_str = str(prediction)
            
            log_entry = f"{timestamp} | Environment: {environment} | Prediction: {prediction_str}\n"
            
            # Intentar obtener el archivo existente
            try:
                response = self.s3_client.get_object(Bucket=self.bucket_name, Key=s3_key)
                existing_content = response['Body'].read().decode('utf-8')
            except self.s3_client.exceptions.NoSuchKey:
                # El archivo no existe, crear uno nuevo
                existing_content = ""
                logger.info(f"Creating new prediction log file: {s3_key}")
            
            # Agregar nueva entrada
            updated_content = existing_content + log_entry
            
            # Subir el archivo actualizado
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=updated_content.encode('utf-8'),
                ContentType='text/plain'
            )
            
            logger.info(f"✅ Prediction logged to S3: {s3_key}")
            
        except Exception as e:
            logger.error(f"❌ Failed to log prediction: {e}")
            # No lanzar excepción para no interrumpir las predicciones
    
    def get_prediction_history(self, environment: str = 'dev', limit: int = None) -> List[str]:
        """
        Obtener el historial de predicciones
        
        Args:
            environment: 'dev' o 'prod'
            limit: Número máximo de entradas a devolver (None = todas)
            
        Returns:
            Lista de entradas del log
        """
        try:
            filename = f"predicciones_{environment}.txt"
            s3_key = f"predictions/{filename}"
            
            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=s3_key)
            content = response['Body'].read().decode('utf-8')
            
            lines = content.strip().split('\n')
            
            if limit:
                return lines[-limit:]
            return lines
            
        except self.s3_client.exceptions.NoSuchKey:
            logger.warning(f"No prediction history found for {environment}")
            return []
        except Exception as e:
            logger.error(f"Error reading prediction history: {e}")
            return []
