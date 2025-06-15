#!/bin/bash
# debug_github_actions.sh

echo "🔍 Diagnosticando GitHub Actions..."
echo "================================="

# 1. Verificar estructura de directorios
echo "1. Verificando estructura de directorios:"
if [ -d ".github" ]; then
    echo "✅ Directorio .github existe"
else
    echo "❌ Directorio .github NO existe"
    echo "   Creando..."
    mkdir -p .github/workflows
fi

if [ -d ".github/workflows" ]; then
    echo "✅ Directorio .github/workflows existe"
else
    echo "❌ Directorio .github/workflows NO existe"
    echo "   Creando..."
    mkdir -p .github/workflows
fi

# 2. Listar archivos en workflows
echo ""
echo "2. Archivos en .github/workflows:"
ls -la .github/workflows/ 2>/dev/null || echo "❌ No se puede listar el directorio"

# 3. Verificar rama actual
echo ""
echo "3. Información de Git:"
echo "   Rama actual: $(git branch --show-current)"
echo "   Ramas locales:"
git branch

# 4. Verificar si hay cambios sin commit
echo ""
echo "4. Estado de Git:"
git status --short

# 5. Crear workflow de prueba simple
echo ""
echo "5. Creando workflow de prueba simple..."
cat > .github/workflows/test-simple.yml << 'EOF'
name: Test Simple

on:
  push:
  pull_request:
  workflow_dispatch:

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Test
        run: echo "GitHub Actions está funcionando!"
EOF

echo "✅ Workflow de prueba creado"

# 6. Verificar sintaxis YAML (si yamllint está instalado)
if command -v yamllint &> /dev/null; then
    echo ""
    echo "6. Verificando sintaxis YAML:"
    yamllint .github/workflows/*.yml || echo "⚠️ Hay problemas de sintaxis"
else
    echo ""
    echo "6. yamllint no está instalado, no se puede verificar sintaxis"
fi

echo ""
echo "================================="
echo "📋 Próximos pasos:"
echo ""
echo "1. Agregar y hacer commit de los cambios:"
echo "   git add .github/workflows/"
echo "   git commit -m 'fix: add GitHub Actions workflows'"
echo "   git push origin $(git branch --show-current)"
echo ""
echo "2. Si estás en una rama diferente a main/master/dev/prod:"
echo "   git checkout -b main"
echo "   git push -u origin main"
echo ""
echo "3. Verificar en GitHub:"
echo "   - Ve a la pestaña Actions en tu repositorio"
echo "   - Deberías ver el workflow 'Test Simple'"
echo "   - Puedes ejecutarlo manualmente con 'Run workflow'"