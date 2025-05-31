import os
import sys
import boto3
import logging
from pathlib import Path

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_s3_client():
    """Crear cliente S3"""
    return boto3.client(
        's3',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        region_name=os.getenv('AWS_REGION', 'us-east-1')
    )

def download_file_from_s3(s3_client, bucket, s3_key, local_path):
    """Descargar archivo desde S3"""
    try:
        # Crear directorio si no existe
        local_path = Path(local_path)
        local_path.parent.mkdir(parents=True, exist_ok=True)
        
        s3_client.download_file(bucket, s3_key, str(local_path))
        logger.info(f"✅ Downloaded {s3_key} -> {local_path}")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to download {s3_key}: {e}")
        return False

def main():
    """Función principal para descargar artefactos"""
    logger.info("🚀 Starting artifact download process...")
    
    # Configuración
    bucket_name = os.getenv('S3_BUCKET', 'proyectofinalmlops')
    
    # Verificar variables de entorno
    required_vars = ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f"❌ Missing required environment variables: {missing_vars}")
        sys.exit(1)
    
    # Crear cliente S3
    try:
        s3_client = create_s3_client()
        logger.info("✅ S3 client created successfully")
    except Exception as e:
        logger.error(f"❌ Failed to create S3 client: {e}")
        sys.exit(1)
    
    # Lista de archivos a descargar
    files_to_download = [
        {
            's3_key': 'entremamiento/scaler.pkl',
            'local_path': 'artifacts/scaler.pkl'
        },
        {
            's3_key': 'entremamiento/modelo_lstm.onnx',
            'local_path': 'artifacts/modelo_lstm.onnx'
        },
        {
            's3_key': 'datos/X_test.npy',
            'local_path': 'artifacts/X_test.npy'
        },
        {
            's3_key': 'datos/y_test.npy',
            'local_path': 'artifacts/y_test.npy'
        }
    ]
    
    # Descargar archivos
    success_count = 0
    total_files = len(files_to_download)
    
    for file_info in files_to_download:
        if download_file_from_s3(
            s3_client, 
            bucket_name, 
            file_info['s3_key'], 
            file_info['local_path']
        ):
            success_count += 1
    
    # Resumen
    logger.info(f"📊 Download Summary: {success_count}/{total_files} files downloaded successfully")
    
    if success_count == total_files:
        logger.info("🎉 All artifacts downloaded successfully!")
        sys.exit(0)
    else:
        logger.error(f"❌ Failed to download {total_files - success_count} files")
        sys.exit(1)

if __name__ == "__main__":
    main()