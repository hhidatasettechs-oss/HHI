import json
import pandas as pd
import random
from pathlib import Path

# ------------------ CONFIG ------------------

# 🔴 CHANGE THIS PATH TO YOUR REAL OPENAI EXPORT FILE
OPENAI_EXPORT_PATH = Path(r"C:\Users\amy\Downloads\OpenAI-export\conversations.json")

BASE_DIR = Path(r"C:\Users\amy\Documents\GitHub\Datasets_Core")
OUTPUT_DIR = BASE_DIR / "draft_output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

SAMPLE_CSV = OUTPUT_DIR / "openai_chat_sample.csv"
SAMPLE_JSON = OUTPUT_DIR / "openai_chat_sample.json"

SAMPLE_SIZE = 50   # ✅ how many chat turns you want in the sample

# ------------------ LOAD EXPORT ------------------

with open(OPENAI_EXPORT_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

# ------------------ EXTRACT MESSAGES ------------------

rows = []

for convo in data:
    convo_id = convo.get("id", "unknown")
    messages = convo.get("mapping", {}).values()

    for msg in messages:
        content = msg.get("message")
        if not content:
            continue

        role = content.get("author", {}).get("role")
        parts = content.get("content", {}).get("parts")

        if role and parts:
            text = " ".join([str(p) for p in parts])

            # ✅ Basic anonymization
            text = text.replace("Amy", "[REDACTED_NAME]")
            text = text.replace("amy", "[REDACTED_NAME]")

            rows.append({
                "conversation_id": convo_id,
                "role": role,
                "text": text
            })

# ------------------ RANDOM SAMPLE ------------------

if len(rows) < SAMPLE_SIZE:
    sample_rows = rows
else:
    sample_rows = random.sample(rows, SAMPLE_SIZE)

df = pd.DataFrame(sample_rows)

# ------------------ SAVE OUTPUT ------------------

df.to_csv(SAMPLE_CSV, index=False)
df.to_json(SAMPLE_JSON, orient="records", indent=2)

# ------------------ DONE ------------------

print("\n✅ OPENAI CHAT SAMPLE DATASET CREATED")
print(f"📄 CSV: {SAMPLE_CSV}")
print(f"📄 JSON: {SAMPLE_JSON}")
print(f"📊 Sample Rows: {len(df)}")

