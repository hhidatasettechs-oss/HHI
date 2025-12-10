import os
import json
import re
from pathlib import Path
from collections import Counter

ROOT = Path(r"C:\Users\amy\Downloads\Hollow_Books_Text")
OUT = ROOT / "datasets"
OUT.mkdir(exist_ok=True)

def read_text(path):
    try:
        return Path(path).read_text(encoding="utf-8", errors="ignore")
    except:
        return ""

def clean(t):
    t = t.replace("\r", "")
    t = re.sub(r"\s+", " ", t)
    return t.strip()

def sentences(t):
    return re.split(r'(?<=[.!?]) +', t)

def paragraphs(t):
    return [p.strip() for p in t.split("\n\n") if p.strip()]

def chunks(t, size=400):
    return [t[i:i+size] for i in range(0, len(t), size)]

def keywords(t, n=10):
    words = re.findall(r"[a-zA-Z]+", t.lower())
    stop = set("a an the and or of to in is be this that it as at on for with by from".split())
    words = [w for w in words if w not in stop]
    return [w for w, _ in Counter(words).most_common(n)]

def simple_summary(t):
    s = sentences(t)
    if len(s) <= 3:
        return t
    return s[0] + " " + s[-1]

def entity_extract(t):
    return list(set(re.findall(r"\b[A-Z][a-z]+(?: [A-Z][a-z]+)*\b", t)))

def write_jsonl(name, rows):
    path = OUT / name
    with open(path, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print("Wrote:", path)

files = [p for p in ROOT.iterdir() if p.suffix.lower() in [".txt", ".md"]]

raw_rows = []
clean_rows = []
line_rows = []
para_rows = []
sent_rows = []
chunk_rows = []
keyword_rows = []
summary_rows = []
meta_rows = []
narrative_rows = []
qa_rows = []
emotion_rows = []
token_rows = []
entity_rows = []
training_rows = []

for f in files:
    text = read_text(f)
    c = clean(text)

    raw_rows.append({"file": f.name, "text": text})
    clean_rows.append({"file": f.name, "text": c})

    for line in text.splitlines():
        if line.strip():
            line_rows.append({"file": f.name, "line": line.strip()})

    for p in paragraphs(text):
        para_rows.append({"file": f.name, "paragraph": p})

    for s in sentences(text):
        if s.strip():
            sent_rows.append({"file": f.name, "sentence": s.strip()})

    for ch in chunks(c):
        chunk_rows.append({"file": f.name, "chunk": ch})

    keyword_rows.append({"file": f.name, "keywords": keywords(c)})

    summary_rows.append({"file": f.name, "summary": simple_summary(c)})

    meta_rows.append({
        "file": f.name,
        "chars": len(text),
        "words": len(text.split()),
        "paragraphs": len(paragraphs(text))
    })

    s = sentences(c)
    intro = s[0] if s else ""
    body = " ".join(s[1:-1]) if len(s) > 2 else ""
    close = s[-1] if s else ""
    narrative_rows.append({
        "file": f.name,
        "intro": intro,
        "body": body,
        "closing": close
    })

    qa_rows.append({
        "file": f.name,
        "question": f"What is the main idea of {f.name}?",
        "answer": simple_summary(c)
    })

    emotion_rows.append({
        "file": f.name,
        "tone": "positive" if "love" in c.lower() else "neutral",
        "intensity": len(c) % 5
    })

    token_rows.append({
        "file": f.name,
        "token_count_estimate": len(c.split())
    })

    entity_rows.append({
        "file": f.name,
        "entities": entity_extract(c)
    })

    training_rows.append({
        "input": f"Summarize: {c[:300]}...",
        "output": simple_summary(c)
    })

write_jsonl("1_raw_text.jsonl", raw_rows)
write_jsonl("2_clean_text.jsonl", clean_rows)
write_jsonl("3_lines.jsonl", line_rows)
write_jsonl("4_paragraphs.jsonl", para_rows)
write_jsonl("5_sentences.jsonl", sent_rows)
write_jsonl("6_chunks.jsonl", chunk_rows)
write_jsonl("7_keywords.jsonl", keyword_rows)
write_jsonl("8_summaries.jsonl", summary_rows)
write_jsonl("9_metadata.jsonl", meta_rows)
write_jsonl("10_narrative_structure.jsonl", narrative_rows)
write_jsonl("11_qa_pairs.jsonl", qa_rows)
write_jsonl("12_emotion_tone.jsonl", emotion_rows)
write_jsonl("13_token_counts.jsonl", token_rows)
write_jsonl("14_entities.jsonl", entity_rows)
write_jsonl("15_training_pairs.jsonl", training_rows)

print("DONE — all 15 datasets created.")
