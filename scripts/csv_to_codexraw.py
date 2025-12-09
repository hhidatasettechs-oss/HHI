import csv
import re
import json
from pathlib import Path

# =============================
# CONFIG
# =============================
ROOT = Path(r"C:\Users\amy\Documents\HHI")
CSV_DIR = ROOT / "csv_raw"       # where you put CSV files
OUT_DIR = ROOT / "codex_raw"     # where processed .txt goes for Codex pipeline

OUT_DIR.mkdir(parents=True, exist_ok=True)

# =============================
# ANON HARD MODE (same rules)
# =============================

CUSTOM_NAMES = ["Amy", "Tez", "Montez", "Rex", "Brenda", "Floyd", "Eddie"]
CUSTOM_LOCATIONS = ["Albuquerque", "Llano River", "Houston", "Lincoln",
                    "Nebraska", "Texas", "New Mexico", "Kansas City"]

EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b", re.I)
PHONE_PATTERN = re.compile(r"\b(?:\+?\d{1,3}[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})\b")
DATE_PATTERN = re.compile(r"\b(?:\d{4}-\d{2}-\d{2}|\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b")
MONTH_DATE_PATTERN = re.compile(
    r"\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|"
    r"Jul(?:y)?|Aug(?:ust)?|Sep(?:t(?:ember)?)?|Oct(?:ober)?|Nov(?:ember)?|"
    r"Dec(?:ember)?)(?:\s+\d{1,2})(?:,\s*\d{2,4})?\b", re.I
)

def anonymize(text: str, anon_map: dict) -> str:

    text = EMAIL_PATTERN.sub("CONTACT_EMAIL", text)
    text = PHONE_PATTERN.sub("CONTACT_PHONE", text)

    # Dates
    def date_repl(m):
        val = m.group(0)
        key = "DATE::" + val
        if key not in anon_map:
            anon_map[key] = f"DATE_{len(anon_map)+1:03d}"
        return anon_map[key]

    text = DATE_PATTERN.sub(date_repl, text)
    text = MONTH_DATE_PATTERN.sub(date_repl, text)

    # Names
    for name in CUSTOM_NAMES:
        pattern = re.compile(rf"\b{name}\b", re.I)
        key = "NAME::" + name
        if key not in anon_map:
            anon_map[key] = f"NAME_{len(anon_map)+1:03d}"
        text = pattern.sub(anon_map[key], text)

    # Locations
    for loc in CUSTOM_LOCATIONS:
        pattern = re.compile(rf"\b{re.escape(loc)}\b", re.I)
        key = "LOC::" + loc
        if key not in anon_map:
            anon_map[key] = f"LOC_{len(anon_map)+1:03d}"
        text = pattern.sub(anon_map[key], text)

    # Pronouns
    text = re.sub(r"\bI'm\b", "the subject is", text, flags=re.I)
    text = re.sub(r"\bI’ve\b", "the subject has", text, flags=re.I)
    text = re.sub(r"\bI'd\b", "the subject would", text, flags=re.I)
    text = re.sub(r"\bI\b", "the subject", text, flags=re.I)
    text = re.sub(r"\bmy\b", "the subject's", text, flags=re.I)
    text = re.sub(r"\bmine\b", "the subject's", text, flags=re.I)

    return text


# =============================
# MAIN CSV → TXT PROCESSOR
# =============================

def process_csv(path: Path):
    anon_map = {}
    blocks = []

    with path.open("r", encoding="utf-8", errors="ignore") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Turn row into text block
            block = " | ".join(f"{k}: {v}" for k, v in row.items())
            block = block.strip()
            if not block:
                continue

            # Anonymize
            block_anon = anonymize(block, anon_map)
            blocks.append(block_anon)

    # Output TXT file into codex_raw
    out_path = OUT_DIR / f"{path.stem}_converted.txt"
    out_path.write_text("\n\n".join(blocks), encoding="utf-8")

    print(f"[OK] Converted CSV → {out_path}")


def main():
    CSV_DIR.mkdir(parents=True, exist_ok=True)
    files = list(CSV_DIR.glob("*.csv"))

    if not files:
        print("[INFO] No CSV files found.")
        return

    for file in files:
        process_csv(file)

    print("[DONE] All CSV files converted into codex_raw TXT blocks.")


if __name__ == "__main__":
    main()

