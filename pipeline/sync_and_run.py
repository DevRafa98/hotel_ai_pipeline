import os
from pipeline.storage_client import upload_doc
from pipeline import run_pipeline

def main():
    docs_dir = "docs"  # 👈 carpeta en el repo donde guardas tus .docx/.pdf/.txt

    if not os.path.exists(docs_dir):
        print("⚠️ No se encontró carpeta docs/")
        return

    print("📤 Subiendo documentos del repo a Supabase Storage...\n")
    for fname in os.listdir(docs_dir):
        path = os.path.join(docs_dir, fname)
        if os.path.isfile(path) and fname.endswith((".pdf", ".docx", ".txt")):
            upload_doc(path)

    print("\n🚀 Ejecutando pipeline...\n")
    run_pipeline.main()

if __name__ == "__main__":
    main()
