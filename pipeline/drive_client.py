import os
import io
import json
from dotenv import load_dotenv
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from pypdf import PdfReader

load_dotenv()

# =========
# Configuración desde .env
# =========
FOLDER_ID = os.getenv("GOOGLE_DRIVE_FOLDER_ID")
SERVICE_ACCOUNT_JSON = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")

if not FOLDER_ID or not SERVICE_ACCOUNT_JSON:
    raise RuntimeError("❌ Falta GOOGLE_DRIVE_FOLDER_ID o GOOGLE_SERVICE_ACCOUNT_JSON en el entorno.")


# =========
# Autenticación con Service Account
# =========
def get_drive_client() -> GoogleDrive:
    gauth = GoogleAuth()
    gauth.settings["client_config_backend"] = "service"
    gauth.settings["service_config"] = {
        "client_json_dict": json.loads(SERVICE_ACCOUNT_JSON)
    }
    gauth.ServiceAuth()
    return GoogleDrive(gauth)


# =========
# Leer archivo de Google Drive a texto
# =========
def file_to_text(file_obj) -> str:
    """Convierte un archivo de Drive a texto según su tipo."""
    content = ""

    # Descargar el contenido en memoria
    file_data = io.BytesIO()
    file_obj.GetContentFile(file_data)

    # TXT
    if file_obj["title"].endswith(".txt"):
        content = file_data.getvalue().decode("utf-8", errors="replace")

    # PDF
    elif file_obj["title"].endswith(".pdf"):
        reader = PdfReader(file_data)
        for page in reader.pages:
            content += page.extract_text() or ""

    # (Se puede ampliar a DOCX más adelante)

    return content.strip()


# =========
# Descargar todos los docs de la carpeta
# =========
def fetch_docs_from_drive():
    """Descarga todos los docs de la carpeta y devuelve {nombre: texto}."""
    drive = get_drive_client()

    query = f"'{FOLDER_ID}' in parents and trashed=false"
    file_list = drive.ListFile({"q": query}).GetList()

    docs = {}
    for f in file_list:
        print(f"📂 Descargando: {f['title']}")
        try:
            docs[f["title"]] = file_to_text(f)
        except Exception as e:
            print(f"⚠️ Error procesando {f['title']}: {e}")

    return docs


if __name__ == "__main__":
    docs = fetch_docs_from_drive()
    for name, text in docs.items():
        preview = text[:200].replace("\n", " ")
        print(f"✅ {name}: {len(text)} caracteres (preview: {preview}...)")
