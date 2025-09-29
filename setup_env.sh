#!/bin/bash
set -e

VENV=".venv"

echo "⚙️ Configurando entorno local..."

# 1. Crear venv si no existe
if [ ! -d "$VENV" ]; then
  echo "📦 Creando entorno virtual en $VENV..."
  python3 -m venv $VENV
else
  echo "✅ Entorno virtual ya existe en $VENV"
fi

# 2. Activar venv
echo "🔗 Activando entorno virtual..."
source $VENV/bin/activate

# 3. Instalar dependencias
echo "⬇️ Instalando dependencias..."
pip install --upgrade pip
pip install -r requirements.txt

echo "✅ Entorno listo. Para activarlo en otra terminal:"
echo "   source $VENV/bin/activate"
