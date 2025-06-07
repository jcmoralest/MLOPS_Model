# scripts/verify_cicd_setup.py
# Script para verificar que todo esté configurado correctamente para CI/CD

import os
import sys
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple

class CICDVerifier:
    """Verificador de configuración CI/CD"""
    
    def __init__(self):
        self.checks_passed = 0
        self.checks_failed = 0
        self.warnings = []
    
    def print_header(self, title: str):
        """Imprimir encabezado de sección"""
        print(f"\n{'='*60}")
        print(f"  {title}")
        print(f"{'='*60}")
    
    def check_result(self, check_name: str, passed: bool, details: str = ""):
        """Registrar resultado de verificación"""
        if passed:
            print(f"✅ {check_name}")
            self.checks_passed += 1
        else:
            print(f"❌ {check_name}")
            if details:
                print(f"   → {details}")
            self.checks_failed += 1
    
    def check_files_exist(self) -> None:
        """Verificar que existen todos los archivos necesarios"""
        self.print_header("VERIFICANDO ARCHIVOS NECESARIOS")
        
        required_files = {
            # Workflows
            ".github/workflows/deploy.yml": "Pipeline principal de CI/CD",
            ".github/workflows/pr-tests.yml": "Pipeline para Pull Requests",
            
            # Scripts
            "scripts/download_artifacts.py": "Script para descargar artefactos",
            "scripts/deploy_to_ecs.py": "Script de despliegue a ECS",
            "scripts/health_check.py": "Script de health check",
            "scripts/generate_test_report.py": "Generador de reportes",
            
            # Tests
            "pruebas/test_1.py": "Test de predicciones específicas",
            "pruebas/test_2.py": "Test de umbral de error",
            "tests/test_model.py": "Tests del modelo con pytest",
            
            # Configuración
            "requirements.txt": "Dependencias de Python",
            "Dockerfile": "Imagen Docker",
            "pytest.ini": "Configuración de pytest",
            ".env": "variables de entorno"
        }
        
        for file_path, description in required_files.items():
            exists = Path(file_path).exists()
            self.check_result(f"{file_path} - {description}", exists)
    
    def check_environment_variables(self) -> None:
        """Verificar variables de entorno"""
        self.print_header("VERIFICANDO VARIABLES DE ENTORNO")
        
        required_env_vars = [
            "AWS_ACCESS_KEY_ID",
            "AWS_SECRET_ACCESS_KEY",
            "S3_BUCKET_NAME"
        ]
        
        optional_env_vars = [
            "AWS_ACCOUNT_ID",
            "GITHUB_TOKEN",
            "ENVIRONMENT"
        ]
        
        for var in required_env_vars:
            value = os.getenv(var)
            self.check_result(
                f"Variable requerida: {var}",
                value is not None,
                "No configurada" if not value else ""
            )
        
        print("\n📌 Variables opcionales:")
        for var in optional_env_vars:
            value = os.getenv(var)
            if value:
                print(f"  ✓ {var} está configurada")
            else:
                print(f"  ⚬ {var} no está configurada (opcional)")
                self.warnings.append(f"{var} no está configurada")
    
    def check_python_dependencies(self) -> None:
        """Verificar dependencias de Python"""
        self.print_header("VERIFICANDO DEPENDENCIAS DE PYTHON")
        
        critical_packages = [
            "streamlit",
            "boto3",
            "onnxruntime",
            "pytest",
            "numpy",
            "pandas",
            "matplotlib",
            "plotly"
        ]
        
        try:
            import pkg_resources
            installed_packages = {pkg.key for pkg in pkg_resources.working_set}
            
            for package in critical_packages:
                installed = package.lower() in installed_packages
                self.check_result(f"Paquete: {package}", installed)
                
        except Exception as e:
            print(f"⚠️  Error verificando paquetes: {e}")
            self.warnings.append("No se pudieron verificar todos los paquetes")
    
    def check_aws_connectivity(self) -> None:
        """Verificar conectividad con AWS"""
        self.print_header("VERIFICANDO CONECTIVIDAD AWS")
        
        try:
            import boto3
            
            # Verificar S3
            try:
                s3 = boto3.client('s3')
                bucket_name = os.getenv('S3_BUCKET_NAME', 'proyectofinalmlops')
                
                # Intentar listar objetos (no necesita permisos especiales)
                response = s3.list_objects_v2(Bucket=bucket_name, MaxKeys=1)
                self.check_result("Conexión a S3", True)
                
            except Exception as e:
                self.check_result(
                    "Conexión a S3", 
                    False, 
                    f"Error: {str(e)[:50]}..."
                )
            
        except ImportError:
            self.check_result("Conexión a AWS", False, "boto3 no está instalado")
    
    def check_docker(self) -> None:
        """Verificar Docker"""
        self.print_header("VERIFICANDO DOCKER")
        
        try:
            # Verificar que Docker está instalado
            result = subprocess.run(
                ["docker", "--version"], 
                capture_output=True, 
                text=True
            )
            docker_installed = result.returncode == 0
            self.check_result(
                "Docker instalado", 
                docker_installed,
                result.stderr if not docker_installed else ""
            )
            
            if docker_installed:
                # Verificar que Docker está corriendo
                result = subprocess.run(
                    ["docker", "info"], 
                    capture_output=True, 
                    text=True
                )
                docker_running = result.returncode == 0
                self.check_result(
                    "Docker daemon corriendo", 
                    docker_running
                )
                
        except FileNotFoundError:
            self.check_result("Docker instalado", False, "Docker no encontrado en PATH")
    
    def check_github_setup(self) -> None:
        """Verificar configuración de GitHub"""
        self.print_header("VERIFICANDO CONFIGURACIÓN DE GITHUB")
        
        try:
            # Verificar que es un repositorio git
            result = subprocess.run(
                ["git", "rev-parse", "--git-dir"],
                capture_output=True,
                text=True
            )
            is_git_repo = result.returncode == 0
            self.check_result("Repositorio Git inicializado", is_git_repo)
            
            if is_git_repo:
                # Verificar remoto
                result = subprocess.run(
                    ["git", "remote", "get-url", "origin"],
                    capture_output=True,
                    text=True
                )
                has_remote = result.returncode == 0
                self.check_result(
                    "Remote 'origin' configurado",
                    has_remote,
                    "No hay remote configurado" if not has_remote else ""
                )
                
                # Verificar rama actual
                result = subprocess.run(
                    ["git", "branch", "--show-current"],
                    capture_output=True,
                    text=True
                )
                current_branch = result.stdout.strip()
                print(f"\n📌 Rama actual: {current_branch}")
                
        except FileNotFoundError:
            self.check_result("Git instalado", False, "Git no encontrado en PATH")
    
    def run_sample_tests(self) -> None:
        """Ejecutar pruebas de muestra"""
        self.print_header("EJECUTANDO PRUEBAS DE MUESTRA")
        
        print("⚠️  Esta sección requiere que los artefactos estén descargados")
        print("   Ejecutando: python scripts/download_artifacts.py")
        
        try:
            # Intentar descargar artefactos
            result = subprocess.run(
                [sys.executable, "scripts/download_artifacts.py"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                print("✅ Artefactos descargados exitosamente")
                
                # Ejecutar un test simple
                print("\n🧪 Ejecutando test de verificación...")
                test_result = subprocess.run(
                    [sys.executable, "-m", "pytest", "tests/", "-v", "-k", "test_model_files_exist"],
                    capture_output=True,
                    text=True
                )
                
                self.check_result(
                    "Test de verificación",
                    test_result.returncode == 0,
                    "Ver logs para detalles" if test_result.returncode != 0 else ""
                )
            else:
                self.check_result(
                    "Descarga de artefactos",
                    False,
                    "No se pudieron descargar los artefactos"
                )
                
        except subprocess.TimeoutExpired:
            self.check_result("Descarga de artefactos", False, "Timeout")
        except Exception as e:
            self.check_result("Pruebas de muestra", False, str(e))
    
    def print_summary(self) -> None:
        """Imprimir resumen final"""
        self.print_header("RESUMEN DE VERIFICACIÓN")
        
        total_checks = self.checks_passed + self.checks_failed
        
        print(f"\n📊 Resultados:")
        print(f"   ✅ Verificaciones exitosas: {self.checks_passed}/{total_checks}")
        print(f"   ❌ Verificaciones fallidas: {self.checks_failed}/{total_checks}")
        
        if self.warnings:
            print(f"\n⚠️  Advertencias ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"   - {warning}")
        
        print(f"\n{'='*60}")
        
        if self.checks_failed == 0:
            print("🎉 ¡TODO LISTO! El proyecto está configurado correctamente para CI/CD")
        else:
            print("❗ Hay problemas que necesitan ser resueltos antes de usar CI/CD")
            print("\n📝 Próximos pasos:")
            print("   1. Revisar las verificaciones fallidas arriba")
            print("   2. Configurar las variables de entorno faltantes")
            print("   3. Instalar las dependencias necesarias")
            print("   4. Ejecutar este script nuevamente")
        
        print(f"{'='*60}\n")

def main():
    """Función principal"""
    print("🔍 VERIFICADOR DE CONFIGURACIÓN CI/CD")
    print("="*60)
    print("Este script verificará que todo esté configurado correctamente")
    print("para ejecutar el pipeline de CI/CD.")
    
    verifier = CICDVerifier()
    
    # Ejecutar todas las verificaciones
    verifier.check_files_exist()
    verifier.check_environment_variables()
    verifier.check_python_dependencies()
    verifier.check_aws_connectivity()
    verifier.check_docker()
    verifier.check_github_setup()
    
    # Preguntar si ejecutar tests
    print("\n" + "="*60)
    response = input("¿Deseas ejecutar las pruebas de muestra? (s/n): ")
    if response.lower() == 's':
        verifier.run_sample_tests()
    
    # Mostrar resumen
    verifier.print_summary()
    
    # Retornar código de salida
    return 0 if verifier.checks_failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())