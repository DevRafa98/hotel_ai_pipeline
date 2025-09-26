import tiktoken

# =========
# Tokenizador (usamos el mismo que GPT-3.5/GPT-4 para consistencia)
# =========
ENCODER = tiktoken.get_encoding("cl100k_base")

def count_tokens(text: str) -> int:
    """Cuenta tokens en un texto."""
    return len(ENCODER.encode(text))


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50):
    """
    Divide un texto en chunks de `chunk_size` tokens con un solapamiento de `overlap`.
    
    Args:
        text (str): Texto a dividir
        chunk_size (int): Máximo de tokens por chunk
        overlap (int): Tokens solapados entre chunks
    
    Returns:
        list[str]: Lista de chunks de texto
    """
    tokens = ENCODER.encode(text)
    chunks = []

    start = 0
    while start < len(tokens):
        end = min(start + chunk_size, len(tokens))
        chunk = ENCODER.decode(tokens[start:end])
        chunks.append(chunk)
        start += chunk_size - overlap  # avance con solapamiento

    return chunks
