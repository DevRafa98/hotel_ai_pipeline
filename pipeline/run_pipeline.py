import sys
from drive_client import fetch_docs_from_drive
from chunker import chunk_text
from vectorizer import save_chunks_to_supabase


def main():
    print("🚀 Iniciando pipeline de vectorización...\n")

    # 1. Descargar docs desde Google Drive
    docs = fetch_docs_from_drive()
    if not docs:
        print("⚠️ No se encontraron documentos en la carpeta de Drive.")
        sys.exit(0)

    # 2. Procesar cada documento
    for doc_name, text in docs.items():
        print(f"\n📄 Procesando documento: {doc_name}")

        # 2.1 Crear chunks
        chunks = chunk_text(text, chunk_size=500, overlap=50)
        print(f"   → Generados {len(chunks)} chunks para {doc_name}")

        # 2.2 Guardar en Supabase
        save_chunks_to_supabase(doc_name, chunks)

    print("\n✅ Pipeline completado. Documentos vectorizados en Supabase.")


if __name__ == "__main__":
    main()
