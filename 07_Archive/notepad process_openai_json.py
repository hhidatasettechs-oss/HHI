import json
from pathlib import Path
import re

# ✅ This script is specifically wired for:
# datasets/H3CD-5/raw/*.json → datasets/H3CD-5/processed/*.txt

SCRIPTS_DIR = Path.cwd()
DATASET = SCRIPTS_DIR.parent
RAW = DATASET / "raw"
PROCESSED = DATASET / "processed"
PROCESSED.mkdir(exist_ok=True)

def clean_text(text):
    text = text.replace("\r\n", "\n").strip()
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text

for json_file in RAW.glob("*.json"):
    print(f"\n📥 Processing: {json_file.name}")

    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    conversations = data if isinstance(data, list) else [data]

    for convo in conversations:
        title = convo.get("title", "untitled")
        title = re.sub(r"[^\w\d\-_. ]", "_", title)

        convo_id = convo.get("id", "no_id")

        out_file = PROCESSED / f"{title}_{convo_id}.txt"

        messages_text = []

        mapping = convo.get("mapping", {})
        for node in mapping.values():
            msg = node.get("message")
            if not msg:
                continue

            role = msg.get("author", {}).get("role", "unknown")

            parts = msg.get("content", {}).get("parts", [])
            if parts:
                content = "\n".join(str(p) for p in parts)
                messages_text.append(f"[{role.upper()}]\n{content}\n")

        final_text = clean_text("\n".join(messages_text))

        if final_text.strip():
            out_file.write_text(final_text, encoding="utf-8")
            print("✅ saved:", out_file.name)

print("\n✅ OpenAI JSON processing complete for H3CD-5.")
