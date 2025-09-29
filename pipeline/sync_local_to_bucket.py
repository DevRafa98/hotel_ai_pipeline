import os
import time
from supabase import create_client
from dotenv import load_dotenv
from pipeline import run_pipeline  

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET", "hotel_docs")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("❌ Faltan SUPABASE_URL o SUPABASE_KEY en el entorno.")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

LOCAL_FILE = os.path.expanduser("~/Descargas/Alda Hotels Centro Ponferrada.docx")

def get_remote_timestamp(filename: str) -> float | None:
    """Devuelve timestamp remoto del archivo en Supabase (o None si no existe)."""
    files = supabase.storage.from_(SUPABASE_BUCKET).list()
    for f in files:
        if f["name"] == filename:
            return time.mktime(time.strptime(f["updated_at"].split(".")[0], "%Y-%m-%dT%H:%M:%S"))
    return None

def upload_doc(local_path: str):
    remote_name = os.path.basename(local_path)
    with open(local_path, "rb") as f:
        data = f.read()
    supabase.storage.from_(SUPABASE_BUCKET).upload(
        path=remote_name,
        file=data,
        file_options={"upsert": "true"}
    )
    print(f"✅ Subido {local_path} → {remote_name} en bucket {SUPABASE_BUCKET}")

def main():
    if not os.path.exists(LOCAL_FILE):
        print(f"⚠️ No existe el archivo local: {LOCAL_FILE}")
        return

    local_ts = os.path.getmtime(LOCAL_FILE)
    remote_ts = get_remote_timestamp(os.path.basename(LOCAL_FILE))

    if remote_ts is None or local_ts > remote_ts:
        print("📂 Se detectaron cambios en el documento → subiendo...")
        upload_doc(LOCAL_FILE)
    else:
        print("✅ No hay cambios en el documento, no se sube.")

    print("🚀 Ejecutando pipeline...")
    run_pipeline.main()

if __name__ == "__main__":
    main()
