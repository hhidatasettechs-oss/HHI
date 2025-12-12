import os
import re
import json
from pathlib import Path
from datetime import datetime

# ---------------------------------------------------------
# CONFIG
# ---------------------------------------------------------

RAW_DIR = r"C:\Users\amy\Documents\HHI\codex_raw"
OUT_DIR = r"C:\Users\amy\Documents\HHI\processed"

OPS_PATTERN = re.compile(
    r"■\s*Op\s+(\d+)\s*—\s*Operation\s+(\d+)(.*?)(?=■\s*Op\s+\d+|$)",
    re.S
)

FIELD_PATTERN = re.compile(r"([A-Za-z ]+):\s*(.+)")

# ---------------------------------------------------------
# HELPERS
# ---------------------------------------------------------

def normalize(text: str) -> str:
    """Normalize weird characters, extra whitespace, etc."""
    text = text.replace("\u007f", "")
    text = text.replace("\r", "")
    return text.strip()

def parse_fields(block: str) -> dict:
    """Extract field:value pairs inside an OPS block."""
    fields = {}
    for line in block.splitlines():
        line = line.strip()
        m = FIELD_PATTERN.match(line)
        if m:
            label = m.group(1).strip()
            value = m.group(2).strip()
            key = label.lower().replace(" ", "_")
            fields[key] = value
    return fields

def load_all_text(raw_dir: str) -> str:
    """Read all .txt and .md files in codex_raw."""
    root = Path(raw_dir)
    buff = []
    for f in root.rglob("*"):
        if f.is_file() and f.suffix.lower() in [".txt", ".md"]:
            try:
                buff.append(f.read_text(encoding="utf-8", errors="ignore"))
            except:
                print(f"[WARN] Could not read: {f}")
    return "\n\n".join(buff)

# ---------------------------------------------------------
# MAIN PROCESSING
# ---------------------------------------------------------

def process_codex_raw():
    print(f"[INFO] Reading raw files from: {RAW_DIR}")

    text = load_all_text(RAW_DIR)
    text = normalize(text)

    print("[INFO] Extracting OPS blocks...")
    ops = []

    for match in OPS_PATTERN.finditer(text):
        op_id = match.group(1)
        op_number = match.group(2)
        block = normalize(match.group(3))

        fields = parse_fields(block)

        ops.append({
            "op_id": op_id,
            "op_number": op_number,
            "block": block,
            **fields
        })

    print(f"[OK] Found {len(ops)} OPS entries")

    # -----------------------------------------------------
    # WRITE OUTPUTS
    # -----------------------------------------------------

    os.makedirs(OUT_DIR, exist_ok=True)

    jsonl_path = os.path.join(OUT_DIR, "ops_ledger.jsonl")
    json_path = os.path.join(OUT_DIR, "ops_ledger.json")
    metadata_path = os.path.join(OUT_DIR, "metadata.json")

    # JSONL
    with open(jsonl_path, "w", encoding="utf-8") as f:
        for entry in ops:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    # JSON
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(ops, f, indent=4, ensure_ascii=False)

    # Metadata
    metadata = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "source_folder": RAW_DIR,
        "ops_count": len(ops),
        "files_processed": len(list(Path(RAW_DIR).rglob("*")))
    }

    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=4)

    print(f"[OK] Saved processed outputs to: {OUT_DIR}")
    print("[DONE]")


if __name__ == "__main__":
    process_codex_raw()
