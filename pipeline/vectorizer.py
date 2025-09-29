import os
from dotenv import load_dotenv
from supabase import create_client
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import SupabaseVectorStore
from .chunker import chunk_text  # 👈 import relativo

load_dotenv()

# =========
# Configuración
# =========
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not SUPABASE_URL or not SUPABASE_KEY or not OPENAI_API_KEY:
    raise RuntimeError("❌ Faltan variables de entorno: SUPABASE_URL, SUPABASE_KEY o OPENAI_API_KEY")

# Cliente Supabase
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Embeddings
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

# VectorStore conectado a la tabla knowledge_base
vectorstore = SupabaseVectorStore(
    client=supabase,
    table_name="knowledge_base",
    embedding=embeddings
)

# =========
# Guardar chunks (borrando primero los antiguos)
# =========
def save_chunks_to_supabase(doc_name: str, chunks: list[str]):
    """Elimina los chunks previos de un documento y guarda los nuevos en Supabase."""
    try:
        # 1. Eliminar registros antiguos
        supabase.table("knowledge_base").delete().eq("metadata->>source", doc_name).execute()
        print(f"🗑️ Eliminados chunks antiguos de {doc_name}")

        # 2. Crear embeddings para cada chunk
        vectors = embeddings.embed_documents(chunks)

        # 3. Insertar en Supabase directamente
        rows = [
            {
                "content": chunk,
                "embedding": vector,
                "metadata": {"source": doc_name, "chunk": i}
            }
            for i, (chunk, vector) in enumerate(zip(chunks, vectors), start=1)
        ]

        supabase.table("knowledge_base").insert(rows).execute()
        print(f"✅ Guardados {len(rows)} chunks de {doc_name} en Supabase")

    except Exception as e:
        print(f"⚠️ Error guardando {doc_name}: {e}")

# =========
# Ejemplo de uso
# =========
if __name__ == "__main__":
    sample_text = (
        "El Hotel Alda Centro Ponferrada está situado en el centro de la ciudad. "
        "Dispone de Wi-Fi gratuito y servicio de lavandería de autoservicio."
    )

    chunks = chunk_text(sample_text, chunk_size=50, overlap=10)
    save_chunks_to_supabase("ejemplo.txt", chunks)
