import os
import time
import hashlib
from supabase import create_client
from dotenv import load_dotenv

# ==================
# Configuración
# ==================
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET", "hotel_docs")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("❌ Faltan SUPABASE_URL o SUPABASE_KEY en el entorno.")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ==================
# Helpers
# ==================
def file_hash(data: bytes) -> str:
    """Devuelve hash MD5 de un archivo en memoria."""
    return hashlib.md5(data).hexdigest()

# ==================
# Funciones principales
# ==================
def list_docs():
    """Lista todos los documentos en el bucket."""
    files = supabase.storage.from_(SUPABASE_BUCKET).list()
    return [f["name"] for f in files]

def upload_doc(local_path: str, remote_name: str | None = None):
    """Sobrescribe un documento en el bucket (borra primero, luego sube, y verifica)."""
    if not os.path.exists(local_path):
        raise FileNotFoundError(f"⚠️ No existe el archivo local: {local_path}")

    if remote_name is None:
        remote_name = os.path.basename(local_path)

    # Leer archivo local
    with open(local_path, "rb") as f:
        local_data = f.read()

    # 1. Borrar versión previa
    try:
        supabase.storage.from_(SUPABASE_BUCKET).remove([remote_name])
        print(f"🗑️ Eliminado {remote_name} previo en bucket {SUPABASE_BUCKET}")
    except Exception:
        print(f"⚠️ No existía {remote_name}, se subirá como nuevo.")

    # 2. Subir archivo actualizado
    supabase.storage.from_(SUPABASE_BUCKET).upload(
        path=remote_name,
        file=local_data,
        file_options={"content-type": "application/octet-stream"}
    )

    # 3. Descargar de nuevo para verificar
    remote_data = supabase.storage.from_(SUPABASE_BUCKET).download(remote_name)

    # 4. Comparar hashes
    local_md5 = file_hash(local_data)
    remote_md5 = file_hash(remote_data)

    print(f"📥 Local hash:  {local_md5}")
    print(f"📥 Remote hash: {remote_md5}")

    if local_md5 == remote_md5:
        print(f"✅ Subida verificada: {remote_name} coincide con el archivo local")
    else:
        print(f"❌ ERROR: {remote_name} en Supabase NO coincide con la versión local")

def download_doc(filename: str) -> bytes:
    """Descarga un documento del bucket, evitando caché con cache buster."""
    bust = int(time.time())
    path = f"{filename}?bust={bust}"
    data = supabase.storage.from_(SUPABASE_BUCKET).download(path)
    print(f"📥 Descargado {filename} (tamaño: {len(data)} bytes)")
    return data

# ==================
# Test manual
# ==================
if __name__ == "__main__":
    print("📂 Archivos en el bucket:")
    for f in list_docs():
        print(" -", f)
        download_doc(f)
