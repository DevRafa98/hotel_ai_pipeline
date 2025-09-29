import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET", "hotel_docs")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("❌ Faltan SUPABASE_URL o SUPABASE_KEY en el entorno.")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def upload_doc(local_path: str, remote_name: str | None = None):
    """Sube un archivo local al bucket, sobrescribiéndolo si ya existe."""
    if not os.path.exists(local_path):
        raise FileNotFoundError(f"⚠️ No existe el archivo local: {local_path}")

    # Si no damos nombre remoto, se usa el nombre del archivo local
    if remote_name is None:
        remote_name = os.path.basename(local_path)

    with open(local_path, "rb") as f:
        data = f.read()

    # 🔹 Intentar sobrescribir (use .upload para crear/replace)
    result = supabase.storage.from_(SUPABASE_BUCKET).upload(
        path=remote_name,
        file=data,
        file_options={"upsert": "true"}  # 👈 permite sobrescribir
    )

    print(f"✅ Subido {local_path} → {remote_name} en bucket {SUPABASE_BUCKET}")
    return result


if __name__ == "__main__":
    # 👇 Cambia esto por la ruta a tu doc local
    local_file = "/home/rafaelpg/Downloads/Alda Hotels Centro Ponferrada.docx"
    upload_doc(local_file)
