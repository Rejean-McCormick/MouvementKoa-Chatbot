import os, json

INPUT_DIR = "docs"
OUTPUT_FILE = "chunks.jsonl"
CHUNK_SIZE = 1000
OVERLAP = 100

def chunk_text(text, size=CHUNK_SIZE, overlap=OVERLAP):
    chunks = []
    start = 0
    length = len(text)
    while start < length:
        end = min(start + size, length)
        chunks.append(text[start:end])
        start += size - overlap
    return chunks

def read_file(path):
    raw = open(path, "rb").read()
    for enc in ("utf-8", "utf-8-sig", "utf-16", "latin-1"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="ignore")

def main():
    total = 0
    with open(OUTPUT_FILE, "w", encoding="utf-8") as out_f:
        # Parcours récursif de tous les fichiers sous INPUT_DIR
        for root, _, files in os.walk(INPUT_DIR):
            for fname in files:
                if not fname.lower().endswith(".md"):
                    continue
                path = os.path.join(root, fname)
                text = read_file(path)
                for i, chunk in enumerate(chunk_text(text)):
                    record = {
                        "id": f"{os.path.relpath(path, INPUT_DIR).replace(os.sep, '_')}_{i}",
                        "source": os.path.relpath(path, INPUT_DIR),
                        "text": chunk
                    }
                    out_f.write(json.dumps(record, ensure_ascii=False) + "\n")
                    total += 1
    print(f"✅ Généré {OUTPUT_FILE} avec {total} chunks")

if __name__ == "__main__":
    main()
