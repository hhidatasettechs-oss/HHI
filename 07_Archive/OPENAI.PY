import json, re
import pandas as pd
from nltk.tokenize import sent_tokenize

# ---------- LOAD ----------
with open("conversation.json", "r", encoding="utf-8") as f:
    convo = json.load(f)

if isinstance(convo, dict):
    convo = convo.get("messages") or [convo]


# ---------- ANONYMIZATION MAP ----------
name_pattern = re.compile(r"\b([A-Z][a-z]+)\b")
email_pattern = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
phone_pattern = re.compile(r"\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b")
location_words = ["Texas","Rio Grande","Kings","Houston","Austin","Corpus"]

def anonymize(text):
    if not isinstance(text,str):
        return text
    
    t = text

    # emails
    t = email_pattern.sub("CONTACT_EMAIL", t)

    # phones
    t = phone_pattern.sub("CONTACT_PHONE", t)

    # locations
    for loc in location_words:
        t = re.sub(rf"\b{loc}\b", "LOC_001", t, flags=re.IGNORECASE)

    # names (simple, can be upgraded)
    t = name_pattern.sub("PERSON_XXX", t)

    return t


# ---------- 1. RAW ANONYMIZED ----------
raw_a = []
for m in convo:
    m2 = m.copy()
    m2["text"] = anonymize(m.get("text", ""))
    raw_a.append(m2)

pd.DataFrame(raw_a).to_json("1_raw_anonymized.jsonl", orient="records", lines=True)


# ---------- 2. CLEAN ----------
def clean(t):
    if not isinstance(t,str): return t
    t = re.sub(r"\s+"," ",t)
    t = t.replace("\u200b","")
    return t.strip()

cleaned = []
for m in raw_a:
    m2 = m.copy()
    m2["clean_text"] = clean(m["text"])
    cleaned.append(m2)

pd.DataFrame(cleaned).to_json("2_clean_anonymized.jsonl", orient="records", lines=True)


# ---------- 3. SPEAKER ANONYMIZED ----------
speaker_map = {}
next_id = 1

speakers = []
for m in cleaned:
    sp = m.get("speaker") or m.get("author") or "unknown"
    if sp not in speaker_map:
        speaker_map[sp] = f"SPEAKER_{next_id:03d}"
        next_id += 1
    m3 = m.copy()
    m3["speaker"] = speaker_map[sp]
    speakers.append(m3)

pd.DataFrame(speakers).to_json("3_speaker_anonymized.jsonl", orient="records", lines=True)


# ---------- 4. SENTENCE SPLIT ----------
sent_rows = []
for m in speakers:
    sents = sent_tokenize(m["clean_text"])
    for s in sents:
        row = m.copy()
        row["sentence"] = s
        sent_rows.append(row)

pd.DataFrame(sent_rows).to_json("4_sentences_anonymized.jsonl", orient="records", lines=True)


# ---------- 5. CONTEXT WINDOWS ----------
windows = []
for i in range(len(speakers)):
    w = {
        "turn_id": i,
        "context_1": speakers[i]["clean_text"],
        "context_2": speakers[i-1]["clean_text"] if i>=1 else "",
        "context_3": speakers[i-2]["clean_text"] if i>=2 else "",
        "speaker": speakers[i]["speaker"]
    }
    windows.append(w)

pd.DataFrame(windows).to_json("5_windows_anonymized.jsonl", orient="records", lines=True)


# ---------- 6. AFFECTIVE LABEL SCAFFOLD ----------
affect = []
for m in speakers:
    affect.append({
        "speaker": m["speaker"],
        "text": m["clean_text"],
        "body_sensation": "",
        "affective_state": "",
        "activation_code": "",
        "trigger_theme": ""
    })

pd.DataFrame(affect).to_json("6_affect_scaffold_anonymized.jsonl", orient="records", lines=True)


print("ANONYMIZED DATASETS READY.")
