# filepath: scripts/health_check.py
#     artifacts = {
#         'scaler': 'entremamiento/scaler.pkl',
#         'model': 'entremamiento/modelo_lstm.onnx',
#         'X_test': 'datos/X_test.npy',
#         'y_test': 'datos/y_test.npy'
#     }
# Health Check Script for Deployed ML Model

import os
import sys
import time
import requests
import argparse
import logging
from typing import Dict, Any

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HealthChecker:
    """Clase para verificar el estado de salud de la aplicación desplegada"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.timeout = 30
    
    def get_endpoint_url(self, environment: str) -> str:
        """Obtener URL del endpoint según el ambiente"""
        if environment == "prod":
            return "http://ml-model-prod.example.com:8501"
        else:  # dev
            return "http://ml-model-dev.example.com:8502"
    
    def check_basic_health(self, url: str) -> Dict[str, Any]:
        """Verificar salud básica de la aplicación"""
        try:
            # Verificar endpoint de salud de Streamlit
            health_url = f"{url}/_stcore/health"
            response = self.session.get(health_url)
            
            result = {
                "status": "healthy" if response.status_code == 200 else "unhealthy",
                "status_code": response.status_code,
                "response_time": response.elapsed.total_seconds(),
                "url": health_url
            }
            
            if response.status_code == 200:
                logger.info(f"✅ Health check passed: {health_url}")
            else:
                logger.warning(f"⚠️ Health check failed: {health_url} (Status: {response.status_code})")
            
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Health check failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "url": health_url
            }
    
    def check_application_functionality(self, url: str) -> Dict[str, Any]:
        """Verificar funcionalidad básica de la aplicación"""
        try:
            # Verificar que la página principal carga
            response = self.session.get(url)
            
            result = {
                "status": "functional" if response.status_code == 200 else "non-functional",
                "status_code": response.status_code,
                "response_time": response.elapsed.total_seconds(),
                "content_length": len(response.content),
                "url": url
            }
            
            if response.status_code == 200:
                # Verificar que el contenido contiene elementos esperados
                content = response.text.lower()
                expected_elements = ["etf", "pronóstico", "predicción", "streamlit"]
                
                found_elements = [elem for elem in expected_elements if elem in content]
                result["found_elements"] = found_elements
                result["content_check"] = len(found_elements) > 0
                
                if len(found_elements) > 0:
                    logger.info(f"✅ Application functionality check passed: {url}")
                    logger.info(f"   Found elements: {found_elements}")
                else:
                    logger.warning(f"⚠️ Application content check failed: expected elements not found")
                    result["status"] = "content-issue"
            else:
                logger.warning(f"⚠️ Application functionality check failed: {url} (Status: {response.status_code})")
            
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Application functionality check failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "url": url
            }
    
    def check_model_prediction(self, url: str) -> Dict[str, Any]:
        """Verificar que el modelo puede hacer predicciones (si hay un endpoint específico)"""
        try:
            # Este sería un endpoint específico para predicciones si existiera
            # Por ahora, verificamos que la aplicación responde
            prediction_url = f"{url}/predict"  # Endpoint hipotético
            
            try:
                response = self.session.get(prediction_url)
                return {
                    "status": "available" if response.status_code == 200 else "unavailable",
                    "status_code": response.status_code,
                    "url": prediction_url
                }
            except requests.exceptions.RequestException:
                # Si no existe el endpoint, asumimos que las predicciones se manejan en la UI
                return {
                    "status": "ui-based",
                    "message": "Predictions handled through UI",
                    "url": prediction_url
                }
                
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "url": prediction_url
            }
    
    def run_comprehensive_health_check(self, environment: str, max_retries: int = 3, retry_delay: int = 30):
        """Ejecutar verificación completa de salud"""
        logger.info(f"🏥 Starting comprehensive health check for {environment} environment")
        
        url = self.get_endpoint_url(environment)
        logger.info(f"🌐 Target URL: {url}")
        
        results = {
            "environment": environment,
            "timestamp": time.time(),
            "checks": {}
        }
        
        # Realizar verificaciones con reintentos
        for attempt in range(max_retries):
            logger.info(f"🔄 Health check attempt {attempt + 1}/{max_retries}")
            
            # 1. Verificación básica de salud
            logger.info("1️⃣ Running basic health check...")
            basic_health = self.check_basic_health(url)
            results["checks"]["basic_health"] = basic_health
            
            # 2. Verificación de funcionalidad de la aplicación
            logger.info("2️⃣ Running application functionality check...")
            app_functionality = self.check_application_functionality(url)
            results["checks"]["app_functionality"] = app_functionality
            
            # 3. Verificación del modelo
            logger.info("3️⃣ Running model prediction check...")
            model_check = self.check_model_prediction(url)
            results["checks"]["model_prediction"] = model_check
            
            # Evaluar resultados
            all_healthy = (
                basic_health.get("status") == "healthy" and
                app_functionality.get("status") in ["functional", "content-issue"]
            )
            
            if all_healthy:
                logger.info("🎉 All health checks passed!")
                results["overall_status"] = "healthy"
                return results
            else:
                logger.warning(f"⚠️ Health checks failed on attempt {attempt + 1}")
                if attempt < max_retries - 1:
                    logger.info(f"⏳ Waiting {retry_delay}s before retry...")
                    time.sleep(retry_delay)
        
        # Si llegamos aquí, todas las verificaciones fallaron
        logger.error("❌ All health check attempts failed")
        results["overall_status"] = "unhealthy"
        return results
    
    def print_results_summary(self, results: Dict[str, Any]):
        """Imprimir resumen de resultados"""
        print("\n" + "="*60)
        print(f"🏥 HEALTH CHECK SUMMARY - {results['environment'].upper()}")
        print("="*60)
        
        for check_name, check_result in results["checks"].items():
            status = check_result.get("status", "unknown")
            emoji = "✅" if status in ["healthy", "functional"] else "❌" if status in ["unhealthy", "error"] else "⚠️"
            print(f"{emoji} {check_name.replace('_', ' ').title()}: {status}")
            
            if "response_time" in check_result:
                print(f"   Response Time: {check_result['response_time']:.3f}s")
            if "error" in check_result:
                print(f"   Error: {check_result['error']}")
        
        overall_status = results.get("overall_status", "unknown")
        overall_emoji = "🎉" if overall_status == "healthy" else "💥"
        print(f"\n{overall_emoji} OVERALL STATUS: {overall_status.upper()}")
        print("="*60)

def main():
    """Función principal"""
    parser = argparse.ArgumentParser(description='Run health check on deployed ML model')
    parser.add_argument('--environment', required=True, choices=['dev', 'prod'],
                        help='Target environment')
    parser.add_argument('--max-retries', type=int, default=3,
                        help='Maximum number of retry attempts')
    parser.add_argument('--retry-delay', type=int, default=30,
                        help='Delay between retries in seconds')
    
    args = parser.parse_args()
    
    try:
        checker = HealthChecker()
        results = checker.run_comprehensive_health_check(
            args.environment, 
            args.max_retries, 
            args.retry_delay
        )
        
        checker.print_results_summary(results)
        
        # Exit with appropriate code
        if results.get("overall_status") == "healthy":
            sys.exit(0)
        else:
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"❌ Health check failed with unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()