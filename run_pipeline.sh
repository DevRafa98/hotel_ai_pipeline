#!/bin/bash
set -e

VENV=".venv"

echo "⚙️ Iniciando pipeline completo..."

# 1. Crear venv si no existe
if [ ! -d "$VENV" ]; then
  echo "📦 Creando entorno virtual en $VENV..."
  python3 -m venv $VENV
fi

# 2. Activar venv
echo "🔗 Activando entorno virtual..."
source $VENV/bin/activate

# 3. Instalar dependencias si hace falta
echo "⬇️ Instalando dependencias..."
pip install --upgrade pip
pip install -r requirements.txt

# 4. Cargar variables de entorno
if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
  echo "🔑 Variables de entorno cargadas desde .env"
else
  echo "⚠️ No se encontró .env, asegúrate de tener SUPABASE_URL, SUPABASE_KEY y OPENAI_API_KEY"
  exit 1
fi

# 5. Sincronizar documentos locales → bucket
echo "📤 Sincronizando documentos..."
python -m pipeline.sync_local_docs

# 6. Ejecutar pipeline de vectorización
echo "🧩 Ejecutando vectorización en Supabase..."
python -m pipeline.run_pipeline

echo "✅ Pipeline completada."
