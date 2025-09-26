import os
from dotenv import load_dotenv
from openai import OpenAI
from supabase import create_client, Client

load_dotenv()

# =========
# Configuración
# =========
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not OPENAI_API_KEY or not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("❌ Faltan variables de entorno: OPENAI_API_KEY, SUPABASE_URL o SUPABASE_KEY")

# Clientes
client = OpenAI(api_key=OPENAI_API_KEY)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


# =========
# Función: generar embedding
# =========
def embed_text(text: str) -> list[float]:
    """Genera embedding para un texto usando OpenAI."""
    response = client.embeddings.create(
        model="text-embedding-3-large",
        input=text
    )
    return response.data[0].embedding


# =========
# Función: guardar en Supabase
# =========
def save_chunks_to_supabase(doc_name: str, chunks: list[str]):
    """Guarda cada chunk de un documento en la tabla 'knowledge_base'."""
    rows = []
    for i, chunk in enumerate(chunks, 1):
        try:
            embedding = embed_text(chunk)
            row = {
                "content": chunk,
                "embedding": embedding,
                "metadata": {
                    "source": doc_name,
                    "chunk": i
                }
            }
            rows.append(row)
        except Exception as e:
            print(f"⚠️ Error procesando chunk {i} de {doc_name}: {e}")

    if rows:
        supabase.table("knowledge_base").insert(rows).execute()
        print(f"✅ Guardados {len(rows)} chunks de {doc_name} en Supabase")
    else:
        print(f"⚠️ No se guardó nada de {doc_name}")
