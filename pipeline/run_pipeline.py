import io
import sys
from pypdf import PdfReader
from docx import Document

from .storage_client import list_docs, download_doc
from .chunker import chunk_text
from .vectorizer import save_chunks_to_supabase


def read_doc(name: str, data: bytes) -> str:
    """Lee documentos desde Supabase Storage."""
    if name.endswith(".txt"):
        return data.decode("utf-8", errors="replace")

    elif name.endswith(".pdf"):
        reader = PdfReader(io.BytesIO(data))
        return "\n".join([p.extract_text() or "" for p in reader.pages])

    elif name.endswith(".docx"):
        doc = Document(io.BytesIO(data))
        return "\n".join([p.text for p in doc.paragraphs])

    else:
        print(f"⚠️ Formato no soportado: {name}")
        return ""


def main(files=None):
    print("🚀 Iniciando pipeline desde Supabase Storage...\n")

    # Si se pasan archivos concretos → solo esos
    # Si no → todos los del bucket
    docs = files if files else list_docs()

    if not docs:
        print("⚠️ No se encontraron documentos en el bucket.")
        return

    for name in docs:
        print(f"📄 Procesando {name}")
        raw = download_doc(name)
        text = read_doc(name, raw)

        if not text.strip():
            print(f"⚠️ Documento vacío o ilegible: {name}")
            continue

        chunks = chunk_text(text, chunk_size=500, overlap=50)
        print(f"   → {len(chunks)} chunks generados")

        save_chunks_to_supabase(name, chunks)

    print("\n✅ Pipeline completada.")


if __name__ == "__main__":
    # Si ejecutas: python -m pipeline.run_pipeline file1.docx file2.pdf
    args = sys.argv[1:]
    main(files=args if args else None)
