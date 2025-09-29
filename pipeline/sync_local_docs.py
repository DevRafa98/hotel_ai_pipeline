import os
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
    raise RuntimeError("❌ Faltan SUPABASE_URL o SUPABASE_KEY en el .env")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Carpeta local a vigilar
LOCAL_DIR = os.path.expanduser("~/Downloads")

# ==================
# Helpers
# ==================
def file_hash(data: bytes) -> str:
    """Devuelve hash MD5 de bytes."""
    return hashlib.md5(data).hexdigest()

# ==================
# Funciones
# ==================
def upload_doc(local_path: str):
    """Reemplaza un documento en el bucket, lo sube y verifica con hash."""
    file_name = os.path.basename(local_path)

    # Leer archivo local
    with open(local_path, "rb") as f:
        local_data = f.read()

    local_md5 = file_hash(local_data)

    # 1. Borrar versión previa
    try:
        supabase.storage.from_(SUPABASE_BUCKET).remove([file_name])
        print(f"🗑️ Eliminado {file_name} previo en bucket {SUPABASE_BUCKET}")
    except Exception:
        print(f"⚠️ No existía {file_name}, se subirá como nuevo.")

    # 2. Subir archivo actualizado
    supabase.storage.from_(SUPABASE_BUCKET).upload(
        path=file_name,
        file=local_data,
        file_options={"content-type": "application/octet-stream"}
    )

    # 3. Descargar para verificar
    remote_data = supabase.storage.from_(SUPABASE_BUCKET).download(file_name)
    remote_md5 = file_hash(remote_data)

    print(f"📂 {file_name}")
    print(f"   Local MD5 :  {local_md5}")
    print(f"   Remote MD5: {remote_md5}")

    if local_md5 == remote_md5:
        print(f"   ✅ Subida verificada, coincide con la versión local")
    else:
        print(f"   ❌ ERROR: No coincide con la versión local")

def detect_changes():
    """Detecta archivos relevantes en ~/Downloads."""
    exts = (".txt", ".pdf", ".docx")
    return [
        os.path.join(LOCAL_DIR, f)
        for f in os.listdir(LOCAL_DIR)
        if f.endswith(exts)
    ]

def main():
    print("🚀 Sincronizando documentos desde ~/Downloads → Supabase Storage...\n")

    files = detect_changes()
    if not files:
        print("⚠️ No hay archivos para subir.")
        return

    for lf in files:
        print(f"📂 Detectado {lf} → subiendo...")
        upload_doc(lf)

if __name__ == "__main__":
    main()
