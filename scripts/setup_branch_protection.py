# scripts/setup_branch_protection.py

import os
import requests
import json
from typing import Dict, Any

class BranchProtectionSetup:
    """Configurar protección de ramas en GitHub"""
    
    def __init__(self, token: str, owner: str, repo: str):
        self.token = token
        self.owner = owner
        self.repo = repo
        self.headers = {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        self.base_url = f'https://api.github.com/repos/{owner}/{repo}'
    
    def get_protection_rules(self, branch: str) -> Dict[str, Any]:
        """Definir reglas de protección según la rama"""
        
        base_rules = {
            "required_status_checks": {
                "strict": True,  # Requiere que la rama esté actualizada
                "contexts": [
                    "Code Quality Check",
                    "Unit Tests",
                    "Security Check",
                    "Docker Build Test"
                ]
            },
            "enforce_admins": False,  # Los admins también deben seguir las reglas
            "required_pull_request_reviews": {
                "required_approving_review_count": 1,  # Mínimo 1 aprobación
                "dismiss_stale_reviews": True,  # Descartar reviews al hacer push
                "require_code_owner_reviews": False,
                "dismissal_restrictions": {}
            },
            "restrictions": None,  # Sin restricciones de quién puede hacer push
            "allow_force_pushes": False,
            "allow_deletions": False,
            "required_conversation_resolution": True  # Resolver conversaciones antes de merge
        }
        
        # Reglas específicas para producción
        if branch == "prod":
            base_rules["required_pull_request_reviews"]["required_approving_review_count"] = 2
            base_rules["required_status_checks"]["contexts"].extend([
                "Run Tests",
                "Build and Deploy"
            ])
        
        return base_rules
    
    def setup_branch_protection(self, branch: str):
        """Configurar protección para una rama específica"""
        
        url = f"{self.base_url}/branches/{branch}/protection"
        rules = self.get_protection_rules(branch)
        
        try:
            response = requests.put(url, headers=self.headers, json=rules)
            
            if response.status_code == 200:
                print(f"✅ Protección configurada exitosamente para la rama '{branch}'")
                return True
            else:
                print(f"❌ Error configurando protección para '{branch}': {response.status_code}")
                print(f"   Respuesta: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def setup_all_branches(self):
        """Configurar protección para todas las ramas principales"""
        
        branches = ["main", "dev", "prod"]
        
        print("🔒 Configurando protección de ramas...")
        print("=" * 50)
        
        for branch in branches:
            print(f"\n📌 Configurando rama: {branch}")
            self.setup_branch_protection(branch)
        
        print("\n" + "=" * 50)
        print("✅ Configuración completada!")
        
        # Mostrar resumen
        self.show_protection_summary()
    
    def show_protection_summary(self):
        """Mostrar resumen de la protección configurada"""
        
        print("\n📊 RESUMEN DE PROTECCIÓN DE RAMAS")
        print("=" * 50)
        
        summary = """
        🔸 Rama 'main':
           - Requiere PR para cualquier cambio
           - 1 aprobación mínima
           - Todos los tests deben pasar
           
        🔸 Rama 'dev':
           - Requiere PR para cualquier cambio
           - 1 aprobación mínima
           - Todos los tests deben pasar
           
        🔸 Rama 'prod':
           - Requiere PR para cualquier cambio
           - 2 aprobaciones mínimas
           - Todos los tests y deploy deben pasar
           - Reviews más estrictos
        """
        
        print(summary)

def main():
    """Función principal"""
    
    # Obtener configuración
    github_token = os.getenv('GITHUB_TOKEN')
    repo_owner = os.getenv('GITHUB_REPOSITORY_OWNER', 'tu-usuario')
    repo_name = os.getenv('GITHUB_REPOSITORY_NAME', 'ml-model-project')
    
    if not github_token:
        print("❌ Error: GITHUB_TOKEN no está configurado")
        print("   Genera un token en: https://github.com/settings/tokens")
        print("   Permisos necesarios: repo (full control)")
        return
    
    # Configurar protección
    setup = BranchProtectionSetup(github_token, repo_owner, repo_name)
    setup.setup_all_branches()

if __name__ == "__main__":
    main()