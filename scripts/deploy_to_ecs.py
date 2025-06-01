# filepath: 'scripts/deploy_to_ecs.py'

import os
import sys
import json
import boto3
import argparse
import logging
from typing import Dict, Any

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ECSDeployer:
    """Clase para manejar despliegues a AWS ECS"""
    
    def __init__(self):
        self.ecs_client = boto3.client('ecs')
        self.logs_client = boto3.client('logs')
        
    def get_task_definition_config(self, environment: str, image: str) -> Dict[str, Any]:
        """Obtener configuración de task definition según el ambiente"""
        
        base_config = {
            "family": f"ml-model-app-{environment}",
            "networkMode": "awsvpc",
            "requiresCompatibilities": ["FARGATE"],
            "cpu": "1024",
            "memory": "2048",
            "executionRoleArn": f"arn:aws:iam::{os.getenv('AWS_ACCOUNT_ID')}:role/ecsTaskExecutionRole",
            "taskRoleArn": f"arn:aws:iam::{os.getenv('AWS_ACCOUNT_ID')}:role/ecsTaskRole",
        }
        
        # Configuración específica por ambiente
        if environment == "prod":
            port = 8501
            cluster = "ml-model-prod-cluster"
            service = "ml-model-prod-service"
            cpu = "2048"
            memory = "4096"
        else:  # dev
            port = 8502
            cluster = "ml-model-dev-cluster"
            service = "ml-model-dev-service"
            cpu = "1024"
            memory = "2048"
        
        base_config.update({
            "cpu": cpu,
            "memory": memory
        })
        
        # Configuración del contenedor
        container_definition = {
            "name": f"ml-model-app-{environment}",
            "image": image,
            "essential": True,
            "portMappings": [
                {
                    "containerPort": port,
                    "protocol": "tcp"
                }
            ],
            "environment": [
                {"name": "ENVIRONMENT", "value": environment},
                {"name": "AWS_DEFAULT_REGION", "value": "us-east-1"},
                {"name": "S3_BUCKET", "value": "proyectofinalmlops"}
            ],
            "secrets": [
                {
                    "name": "AWS_ACCESS_KEY_ID",
                    "valueFrom": f"arn:aws:secretsmanager:us-east-1:{os.getenv('AWS_ACCOUNT_ID')}:secret:ml-model-aws-credentials:AWS_ACCESS_KEY_ID::"
                },
                {
                    "name": "AWS_SECRET_ACCESS_KEY",
                    "valueFrom": f"arn:aws:secretsmanager:us-east-1:{os.getenv('AWS_ACCOUNT_ID')}:secret:ml-model-aws-credentials:AWS_SECRET_ACCESS_KEY::"
                }
            ],
            "logConfiguration": {
                "logDriver": "awslogs",
                "options": {
                    "awslogs-group": f"/ecs/ml-model-app-{environment}",
                    "awslogs-region": "us-east-1",
                    "awslogs-stream-prefix": "ecs"
                }
            },
            "healthCheck": {
                "command": [
                    "CMD-SHELL",
                    f"curl -f http://localhost:{port}/_stcore/health || exit 1"
                ],
                "interval": 30,
                "timeout": 5,
                "retries": 3,
                "startPeriod": 60
            }
        }
        
        base_config["containerDefinitions"] = [container_definition]
        
        return {
            "task_definition": base_config,
            "cluster": cluster,
            "service": service,
            "port": port
        }
    
    def create_log_group(self, log_group_name: str):
        """Crear grupo de logs si no existe"""
        try:
            self.logs_client.create_log_group(logGroupName=log_group_name)
            logger.info(f"✅ Created log group: {log_group_name}")
        except self.logs_client.exceptions.ResourceAlreadyExistsException:
            logger.info(f"📝 Log group already exists: {log_group_name}")
        except Exception as e:
            logger.error(f"❌ Failed to create log group {log_group_name}: {e}")
    
    def register_task_definition(self, task_def_config: Dict[str, Any]) -> str:
        """Registrar nueva task definition"""
        try:
            response = self.ecs_client.register_task_definition(**task_def_config)
            task_def_arn = response['taskDefinition']['taskDefinitionArn']
            logger.info(f"✅ Registered task definition: {task_def_arn}")
            return task_def_arn
        except Exception as e:
            logger.error(f"❌ Failed to register task definition: {e}")
            raise
    
    def update_service(self, cluster: str, service: str, task_definition: str):
        """Actualizar servicio ECS"""
        try:
            response = self.ecs_client.update_service(
                cluster=cluster,
                service=service,
                taskDefinition=task_definition,
                forceNewDeployment=True
            )
            logger.info(f"✅ Updated service: {service}")
            return response
        except Exception as e:
            logger.error(f"❌ Failed to update service {service}: {e}")
            raise
    
    def wait_for_deployment(self, cluster: str, service: str, timeout: int = 600):
        """Esperar a que el despliegue se complete"""
        try:
            logger.info(f"⏳ Waiting for deployment to complete (timeout: {timeout}s)...")
            waiter = self.ecs_client.get_waiter('services_stable')
            waiter.wait(
                cluster=cluster,
                services=[service],
                WaiterConfig={
                    'Delay': 15,
                    'MaxAttempts': timeout // 15
                }
            )
            logger.info("✅ Deployment completed successfully!")
        except Exception as e:
            logger.error(f"❌ Deployment failed or timed out: {e}")
            raise
    
    def deploy(self, environment: str, image: str):
        """Ejecutar despliegue completo"""
        logger.info(f"🚀 Starting deployment to {environment} environment")
        logger.info(f"📦 Image: {image}")
        
        # Obtener configuración
        config = self.get_task_definition_config(environment, image)
        
        # Crear log group
        log_group_name = f"/ecs/ml-model-app-{environment}"
        self.create_log_group(log_group_name)
        
        # Registrar task definition
        task_def_arn = self.register_task_definition(config["task_definition"])
        
        # Actualizar servicio
        self.update_service(config["cluster"], config["service"], task_def_arn)
        
        # Esperar a que el despliegue se complete
        self.wait_for_deployment(config["cluster"], config["service"])
        
        logger.info(f"🎉 Deployment to {environment} completed successfully!")
        logger.info(f"🌐 Service URL: http://ml-model-{environment}.example.com:{config['port']}")

def main():
    """Función principal"""
    parser = argparse.ArgumentParser(description='Deploy ML model to ECS')
    parser.add_argument('--environment', required=True, choices=['dev', 'prod'],
                        help='Target environment')
    parser.add_argument('--image', required=True,
                        help='Docker image URI')
    
    args = parser.parse_args()
    
    # Verificar variables de entorno requeridas
    required_vars = ['AWS_ACCOUNT_ID']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f"❌ Missing required environment variables: {missing_vars}")
        sys.exit(1)
    
    try:
        deployer = ECSDeployer()
        deployer.deploy(args.environment, args.image)
    except Exception as e:
        logger.error(f"❌ Deployment failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()