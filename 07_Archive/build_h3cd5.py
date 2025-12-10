import os
import re
import json
import nltk
from pathlib import Path
from collections import Counter

# ============================================
# HHI Datasets Core — H3CD-5 Dataset Builder
# Raw Folder:
# C:\Users\amy\Documents\GitHub\Datasets_Core\datasets\H3CD-5\raw\Hollow_Books_Text
# ============================================

nltk.download('punkt', quiet=True)

RAW = Path(r"C:\Users\amy\Documents\GitHub\Datasets_Core\datasets\H3CD-5\raw\Hollow_Books_Text")
BASE = Path(r"C:\Users\amy\Documents\GitHub\Datasets_Core\datasets\H3CD-5")

OUT = BASE / "processed"
JSONL = BASE / "jsonl"
META = BASE / "meta"
ART = BASE / "artifacts"

# Make folders if needed
for d in [OUT, JSONL, META, ART]:
    d.mkdir(parents=True, exist_ok=True)

# Load all raw .txt / .md files
files = [p for p in RAW.iterdir() if p.suffix.lower() in [".txt", ".md"]]

def clean_text(t):
    t = t.replace("\r", "")
    t = re.sub(r"\s+", " ", t)
    return t.strip()

def split_sentences(t):
    return nltk.sent_tokenize(t)

def split_paragraphs(t):
    return [p.strip() for p in t.split("\n") if p.strip()]

def chunk_text(t, max_tokens=180):
    words = t.split()
    chunks = []
    current = []
    for w in words:
        current.append(w)
        if len(current) >= max_tokens:
            chunks.append(" ".join(current))
            current = []
    if current:
        chunks.append(" ".join(current))
    return chunks

def keyword_extract(t):
    words = re.findall(r"[A-Za-z]+", t.lower())
    freq = Counter(words)
    return freq.most_common(20)

dataset_master = []

print(f"Found {len(files)} raw files in Hollow_Books_Text")

for f in files:
    raw = f.read_text(encoding="utf-8", errors="ignore")
    if not raw.strip():
        continue

    clean = clean_text(raw)
    sentences = split_sentences(clean)
    paragraphs = split_paragraphs(raw)
    chunks = chunk_text(clean)
    keywords = keyword_extract(clean)

    meta = {
        "filename": f.name,
        "tokens": len(clean.split()),
        "sentence_count": len(sentences),
        "paragraphs": len(paragraphs),
        "chunks": len(chunks),
    }

    # Save clean version
    (OUT / f"{f.stem}_clean.txt").write_text(clean, encoding="utf-8")

    # Save per-file jsonl
    record = {
        "file": f.name,
        "text": clean,
        "sentences": sentences,
        "paragraphs": paragraphs,
        "chunks": chunks,
        "keywords": keywords,
        "meta": meta,
    }

    (JSONL / f"{f.stem}.jsonl").write_text(
        json.dumps(record, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    # Save metadata
    (META / f"{f.stem}_meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=4), encoding="utf-8"
    )

    dataset_master.append(record)

# Save master dataset
(ART / "H3CD5_master_dataset.jsonl").write_text(
    "\n".join([json.dumps(r, ensure_ascii=False) for r in dataset_master]),
    encoding="utf-8",
)

print("===========================================")
print("HHI H3CD-5 DATASET BUILD COMPLETE.")
print(f"Processed {len(dataset_master)} files.")
print("Outputs: processed/, jsonl/, meta/, artifacts/")
print("===========================================")

