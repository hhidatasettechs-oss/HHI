import json
from pathlib import Path
import re

INPUT = "ocr_output.jsonl"
OUTDIR = Path("datasets_out")
OUTDIR.mkdir(exist_ok=True)

def load_messages():
    data = []
    with open(INPUT, "r", encoding="utf-8") as f:
        for line in f:
            entry = json.loads(line)
            data.append(entry)
    return data

msgs = load_messages()

# 1 RAW
with open(OUTDIR/"1_raw.jsonl", "w", encoding="utf-8") as f:
    for m in msgs:
        f.write(json.dumps(m) + "\n")

# 2 CLEANED
ts_regex = r"\b\d{1,2}:\d{2}\s?(AM|PM|am|pm)?\b"
with open(OUTDIR/"2_clean.jsonl", "w", encoding="utf-8") as f:
    for m in msgs:
        clean = re.sub(ts_regex, "", m["text"])
        f.write(json.dumps({"filename": m["filename"], "text": clean.strip()}) + "\n")

# 3 SPEAKER (naive placeholder)
def guess_speaker(text):
    if text.startswith(("Amy:", "A:", "Me:")):
        return "Amy"
    if text.startswith(("He:", "Him:", "You:")):
        return "Other"
    return "Unknown"

with open(OUTDIR/"3_speaker.jsonl", "w", encoding="utf-8") as f:
    for m in msgs:
        speaker = guess_speaker(m["text"])
        f.write(json.dumps({"speaker": speaker, "text": m["text"]}) + "\n")

# 4 SENTENCE SPLIT
with open(OUTDIR/"4_sentences.jsonl", "w", encoding="utf-8") as f:
    for m in msgs:
        sentences = [s.strip() for s in re.split(r"[.!?]", m["text"]) if s.strip()]
        for s in sentences:
            f.write(json.dumps({"parent": m["filename"], "sentence": s}) + "\n")

# 5–15 PLACEHOLDERS FOR NOW (I’ll populate full models next)
for i in range(5, 16):
    (OUTDIR / f"{i}_placeholder.txt").write_text("Processing template\n")
