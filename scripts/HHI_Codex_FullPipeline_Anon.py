import os
import re
import json
import hashlib
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

# =========================================================
# CONFIG
# =========================================================

ROOT = Path(r"C:\Users\amy\Documents\HHI")
RAW_DIR = ROOT / "codex_raw"
OUT_ROOT = ROOT / "data" / "processed"
VERSIONS_DIR = OUT_ROOT / "versions"
LATEST_DIR = OUT_ROOT / "latest"

# Version folder format: v001, v002, v003, ...
VERSION_PREFIX = "v"

# OPS detection: matches entire blocks like:
# ■ Op 434 — Operation 434
# Glyph: ...
# ...
OPS_PATTERN = re.compile(
    r"■\s*Op\s+(\d+)\s*—\s*Operation\s+(\d+)(.*?)(?=^■\s*Op\s+\d+\s*—\s*Operation\s+\d+|\\Z)",
    re.S | re.M,
)

FIELD_PATTERN = re.compile(r"([A-Za-z ]+):\s*(.+)")

# =========================================================
# ANONYMIZATION CONFIG (HARD MODE "B")
# =========================================================
# You can extend these lists with your own entities if needed.

CUSTOM_NAMES = [
    "Amy",
    "Tez",
    "Montez",
    "Rex",
    "Brenda",
    "Floyd",
    "Eddie",
]

CUSTOM_LOCATIONS = [
    "Albuquerque",
    "Llano River",
    "Houston",
    "Lincoln",
    "Nebraska",
    "Texas",
    "New Mexico",
    "Kansas City",
]

# Patterns for IDs, contacts, dates, etc.
EMAIL_PATTERN = re.compile(
    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b", re.I
)
PHONE_PATTERN = re.compile(
    r"\b(?:\+?\d{1,3}[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})\b"
)
DATE_PATTERN = re.compile(
    r"\b(?:\d{4}-\d{2}-\d{2}|\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b"
)
# Rough month-name date pattern
MONTH_DATE_PATTERN = re.compile(
    r"\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|"
    r"Jul(?:y)?|Aug(?:ust)?|Sep(?:t(?:ember)?)?|Oct(?:ober)?|Nov(?:ember)?|"
    r"Dec(?:ember)?)(?:\s+\d{1,2})(?:,\s*\d{2,4})?\b",
    re.I,
)

# =========================================================
# UTILS
# =========================================================

def normalize_text(text: str) -> str:
    """Normalize whitespace & control chars, keep case."""
    text = text.replace("\r", "")
    text = text.replace("\u007f", "")
    # collapse multiple spaces and tabs
    text = re.sub(r"[ \t]+", " ", text)
    # normalize multiple blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def load_all_files(raw_dir: Path) -> List[Dict[str, Any]]:
    """Load all .txt/.md files as raw documents."""
    docs = []
    for p in raw_dir.rglob("*"):
        if p.is_file() and p.suffix.lower() in {".txt", ".md"}:
            try:
                raw = p.read_text(encoding="utf-8", errors="ignore")
            except Exception as e:
                print(f"[WARN] Could not read {p}: {e}")
                continue
            docs.append(
                {
                    "path": str(p),
                    "name": p.name,
                    "raw": raw,
                    "normalized": normalize_text(raw),
                }
            )
    return docs


def parse_ops_from_text(text: str) -> List[Dict[str, Any]]:
    """Extract OPS blocks & fields from a normalized text blob."""
    ops = []
    for m in OPS_PATTERN.finditer(text):
        op_id = m.group(1)
        op_number = m.group(2)
        block_raw = m.group(3)
        block_norm = normalize_text(block_raw)

        fields = {}
        for line in block_raw.splitlines():
            line = line.strip().lstrip("\u007f")
            fm = FIELD_PATTERN.match(line)
            if fm:
                label = fm.group(1).strip()
                value = fm.group(2).strip()
                key = label.lower().replace(" ", "_")
                fields[key] = value

        ops.append(
            {
                "op_id": op_id,
                "op_number": op_number,
                "block_raw": block_raw.strip(),
                "block_normalized": block_norm,
                **fields,
            }
        )
    return ops


# =========================================================
# HARD ANONYMIZATION
# =========================================================

def anonymize_text_hard(text: str, anon_map: Dict[str, str]) -> str:
    """Apply hard anonymization to a text block."""
    # 1) Contacts (email, phone)
    text = EMAIL_PATTERN.sub("CONTACT_EMAIL", text)
    text = PHONE_PATTERN.sub("CONTACT_PHONE", text)

    # 2) Dates → DATE_###
    # tokenization via mapping; increment counters
    # We'll use anon_map to store stable replacements.
    def _date_repl(m):
        val = m.group(0)
        key = f"DATE::{val}"
        if key not in anon_map:
            idx = sum(k.startswith("DATE::") for k in anon_map) + 1
            anon_map[key] = f"DATE_{idx:03d}"
        return anon_map[key]

    text = DATE_PATTERN.sub(_date_repl, text)
    text = MONTH_DATE_PATTERN.sub(_date_repl, text)

    # 3) Custom names → NAME_###
    for name in CUSTOM_NAMES:
        pattern = re.compile(rf"\b{name}\b", re.I)
        key = f"NAME::{name}"
        if key not in anon_map:
            idx = sum(k.startswith("NAME::") for k in anon_map) + 1
            anon_map[key] = f"NAME_{idx:03d}"
        text = pattern.sub(anon_map[key], text)

    # 4) Custom locations → LOC_###
    for loc in CUSTOM_LOCATIONS:
        pattern = re.compile(rf"\b{re.escape(loc)}\b", re.I)
        key = f"LOC::{loc}"
        if key not in anon_map:
            idx = sum(k.startswith("LOC::") for k in anon_map) + 1
            anon_map[key] = f"LOC_{idx:03d}"
        text = pattern.sub(anon_map[key], text)

    # 5) Pronouns (hard mode) – very rough but effective
    # I / I'm / I've / I'd → "the subject"
    text = re.sub(r"\bI'm\b", "the subject is", text, flags=re.I)
    text = re.sub(r"\bI’ve\b", "the subject has", text, flags=re.I)
    text = re.sub(r"\bI'd\b", "the subject would", text, flags=re.I)
    text = re.sub(r"\bI\b", "the subject", text, flags=re.I)

    # my / mine → the subject's
    text = re.sub(r"\bmy\b", "the subject's", text, flags=re.I)
    text = re.sub(r"\bmine\b", "the subject's", text, flags=re.I)

    # family relations → RELATION_###
    relation_terms = [
        "mother", "father", "mom", "dad", "son", "daughter",
        "husband", "wife", "boyfriend", "girlfriend", "partner",
        "ex-husband", "ex-wife", "ex"
    ]
    for rel in relation_terms:
        pattern = re.compile(rf"\b{rel}\b", re.I)
        key = f"REL::{rel}"
        if key not in anon_map:
            idx = sum(k.startswith("REL::") for k in anon_map) + 1
            anon_map[key] = f"RELATION_{idx:03d}"
        text = pattern.sub(anon_map[key], text)

    return text


# =========================================================
# VERSIONING
# =========================================================

def compute_content_hash(ops: List[Dict[str, Any]], blocks: List[Dict[str, Any]]) -> str:
    """Compute a stable hash from OPS + blocks to detect changes."""
    # Sort for stability
    ops_sorted = sorted(ops, key=lambda d: (d.get("op_id"), d.get("op_number")))
    blocks_sorted = sorted(blocks, key=lambda d: (d.get("source"), d.get("index")))
    payload = json.dumps(
        {"ops": ops_sorted, "blocks": blocks_sorted}, ensure_ascii=False, sort_keys=True
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def list_versions() -> List[str]:
    if not VERSIONS_DIR.exists():
        return []
    versions = []
    for p in VERSIONS_DIR.iterdir():
        if p.is_dir() and p.name.startswith(VERSION_PREFIX):
            suffix = p.name[len(VERSION_PREFIX):]
            if suffix.isdigit():
                versions.append(p.name)
    versions.sort()
    return versions


def get_latest_version() -> str:
    versions = list_versions()
    return versions[-1] if versions else None


def get_next_version_name(latest: str | None) -> str:
    if latest is None:
        return f"{VERSION_PREFIX}001"
    num = int(latest[len(VERSION_PREFIX):])
    return f"{VERSION_PREFIX}{num+1:03d}"


def load_prev_hash(latest: str | None) -> str | None:
    if latest is None:
        return None
    meta_path = VERSIONS_DIR / latest / "metadata.json"
    if not meta_path.exists():
        return None
    try:
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        return meta.get("content_hash")
    except Exception:
        return None


# =========================================================
# MAIN PIPELINE
# =========================================================

def main():
    print(f"[INFO] ROOT      : {ROOT}")
    print(f"[INFO] RAW_DIR   : {RAW_DIR}")
    print(f"[INFO] OUT_ROOT  : {OUT_ROOT}")

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    VERSIONS_DIR.mkdir(parents=True, exist_ok=True)

    # 1) Load all docs
    docs = load_all_files(RAW_DIR)
    print(f"[INFO] Loaded {len(docs)} docs from codex_raw")

    # 2) Build OPS + blocks
    all_ops: List[Dict[str, Any]] = []
    all_blocks: List[Dict[str, Any]] = []
    anon_map: Dict[str, str] = {}

    block_idx = 0
    for doc in docs:
        text_norm = doc["normalized"]

        # OPS from this doc
        ops = parse_ops_from_text(text_norm)
        for op in ops:
            # anonymize block
            anon_block = anonymize_text_hard(op["block_normalized"], anon_map)
            op_anon = dict(op)
            op_anon["block_anon"] = anon_block
            all_ops.append(op_anon)

        # generic blocks: split by double newline
        chunks = [c.strip() for c in text_norm.split("\n\n") if c.strip()]
        for c in chunks:
            anon_c = anonymize_text_hard(c, anon_map)
            all_blocks.append(
                {
                    "source": doc["name"],
                    "path": doc["path"],
                    "index": block_idx,
                    "text": c,
                    "text_anon": anon_c,
                }
            )
            block_idx += 1

    print(f"[INFO] OPS entries     : {len(all_ops)}")
    print(f"[INFO] Generic blocks  : {len(all_blocks)}")
    print(f"[INFO] Anon map size   : {len(anon_map)} keys")

    # 3) Compute hash & decide version
    content_hash = compute_content_hash(all_ops, all_blocks)
    latest = get_latest_version()
    prev_hash = load_prev_hash(latest)

    if prev_hash == content_hash and latest is not None:
        print(f"[INFO] No content change detected. Reusing latest version: {latest}")
        version_name = latest
    else:
        version_name = get_next_version_name(latest)
        print(f"[INFO] New content detected. Creating version: {version_name}")

    version_dir = VERSIONS_DIR / version_name
    version_dir.mkdir(parents=True, exist_ok=True)

    # 4) Write datasets into version folder
    ops_jsonl = version_dir / "ops_ledger_anon.jsonl"
    blocks_jsonl = version_dir / "blocks_anon.jsonl"
    anon_map_path = version_dir / "anonymization_map.json"
    meta_path = version_dir / "metadata.json"

    # ops JSONL
    with ops_jsonl.open("w", encoding="utf-8") as f:
        for op in all_ops:
            f.write(json.dumps(op, ensure_ascii=False) + "\n")

    # blocks JSONL
    with blocks_jsonl.open("w", encoding="utf-8") as f:
        for b in all_blocks:
            f.write(json.dumps(b, ensure_ascii=False) + "\n")

    # anonymization map
    with anon_map_path.open("w", encoding="utf-8") as f:
        json.dump(anon_map, f, indent=4, ensure_ascii=False)

    # metadata
    metadata = {
        "version": version_name,
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "root": str(ROOT),
        "raw_dir": str(RAW_DIR),
        "ops_count": len(all_ops),
        "block_count": len(all_blocks),
        "content_hash": content_hash,
    }
    with meta_path.open("w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=4, ensure_ascii=False)

    print(f"[OK] Wrote version data to {version_dir}")

    # 5) Update latest/
    if LATEST_DIR.exists():
        shutil.rmtree(LATEST_DIR)
    shutil.copytree(version_dir, LATEST_DIR)
    print(f"[OK] Updated 'latest' -> {LATEST_DIR}")

    print("[DONE] HHI Codex FullPipeline (anon, versioned, normalized) complete.")


if __name__ == "__main__":
    main()
