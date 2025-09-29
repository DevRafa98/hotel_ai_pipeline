import os
import sys
import io
from docx import Document
from pypdf import PdfReader

from .chunker import chunk_text
from .vectorizer import save_chunks_to_supabase
from .upload_doc import upload_doc  # 👈 función que sube al bucket

# ==========
# Funciones auxiliares
# ==========
def read_doc(name: str, data: bytes) -> str:
    """Lee documentos de distintos formatos desde bytes."""
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

# ==========
# Pipeline principal
# ==========
def main(files=None):
    docs_dir = "docs"  # 👈 carpeta local donde guardas los docs

    print("🚀 Iniciando pipeline (subida + vectorización)...\n")

    if files:
        docs = files
    else:
        docs = [
            os.path.join(docs_dir, f)
            for f in os.listdir(docs_dir)
            if f.endswith((".pdf", ".docx", ".txt"))
        ]

    if not docs:
        print("⚠️ No se encontraron documentos en docs/")
        return

    for path in docs:
        fname = os.path.basename(path)

        # 1. Subir al bucket
        print(f"📂 Subiendo {fname} al bucket...")
        upload_doc(path)

        # 2. Leer contenido
        with open(path, "rb") as f:
            raw = f.read()

        text = read_doc(fname, raw)
        if not text.strip():
            print(f"⚠️ Documento vacío o ilegible: {fname}")
            continue

        # 3. Chunking
        chunks = chunk_text(text, chunk_size=500, overlap=50)
        print(f"   → {len(chunks)} chunks generados")

        # 4. Guardar embeddings en Supabase
        save_chunks_to_supabase(fname, chunks)

    print("\n✅ Pipeline completada.")

# ==========
# Entrada CLI
# ==========
if __name__ == "__main__":
    args = sys.argv[1:]
    main(files=args if args else None)
