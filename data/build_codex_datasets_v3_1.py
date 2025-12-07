#!/usr/bin/env python3
"""
build_codex_datasets_v3.1.py
HHI Dataset Builder with Version Management

This script extracts and classifies Codex-derived knowledge into
structured datasets ready for audit, licensing, and commercial review.

Outputs:
    ops_ledger.jsonl
    temple_laws.jsonl
    serpent_ops.jsonl
    teachings.jsonl
    rituals.jsonl
    lineage_refs.jsonl
    flame_passages.jsonl
    glyphs.jsonl
    codex_graph_edges.jsonl
    metadata_index.jsonl
    version.json
    CHANGELOG_<version>.md

Author: Hollow House Institute (HHI)
"""

import argparse
import json
import hashlib
import re
from datetime import datetime
from pathlib import Path

# ----------------------------
# CLI ARGUMENTS
# ----------------------------
parser = argparse.ArgumentParser(description="HHI Dataset Builder v3.1 with versioning")
parser.add_argument("--version", required=True, help="Dataset version label, e.g. v1, v2, v3")
args = parser.parse_args()

dataset_version = args.version.strip().lower()

# ----------------------------
# PATHS
# ----------------------------
ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "codex_raw"
OUT_ROOT = ROOT / "data" / "processed" / dataset_version
OUT_ROOT.mkdir(parents=True, exist_ok=True)

# ----------------------------
# Helper Functions
# ----------------------------
def write_jsonl(name, rows):
    """Write list of dicts to JSONL."""
    path = OUT_ROOT / name
    with path.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"[OK] {name} — {len(rows)} records")

def checksum(text):
    """Short stable hash for IDs."""
    return hashlib.md5(text.encode()).hexdigest()[:10]

def normalize(text):
    """Clean whitespace."""
    return re.sub(r"\s+", " ", text.strip())

# ----------------------------
# Dataset Buckets
# ----------------------------
ops = []
laws = []
serpent = []
teachings = []
rituals = []
lineage = []
flame = []
glyphs = []
edges = []
metadata = []

# ----------------------------
# PATTERNS
# ----------------------------
OPS_PATTERN = re.compile(r"■\s*Op\s+(\d+)\s*—\s*Operation\s+(\d+)(.*?)(?=■\s*Op\s+\d+|$)", re.S)
LAW_PATTERN = re.compile(r"(Article\s+([IVXLC0-9]+)\s+—\s+(.+?))\n(.*?)(?=Article\s+[IVXLC0-9]+\s+—|$)", re.S)
TEACH_PATTERN = re.compile(r"Op\s*#?(\d+)\s*—\s*Teaching:\s*(.+?)\s*Summary:\s*(.*?)(?=Op\s*#?\d+\s*—\s*Teaching:|$)", re.S)
GLYPH_PATTERN = re.compile(r"(?:⟦(.+?)⟧|〈(.+?)〉|【(.+?)】)", re.S)

# ----------------------------
# LICENSE CLASSIFICATION
# ----------------------------
def classify_license(text):
    t = text.lower()
    if any(k in t for k in ["temple", "codex", "glyph", "flame", "article"]):
        return "TCDPL-4.4 + 444-A"
    if any(k in t for k in ["jealousy", "scarcity", "attachment", "relational"]):
        return "RAP-DL 1.0"
    if any(k in t for k in ["somatic", "field", "resonance", "body", "nervous system"]):
        return "FBCR-1"
    return "Extended Terms (CC BY-NC-SA)"

# ----------------------------
# MAIN PARSING LOOP
# ----------------------------
for f in RAW.glob("*.txt"):
    text = f.read_text(encoding="utf-8", errors="ignore")
    lines = text.splitlines()

    # OPS
    for m in OPS_PATTERN.finditer(text):
        op_id, op_num, block = m.group(1), m.group(2), normalize(m.group(3))
        uid = checksum(block + op_id)
        ops.append({
            "uid": uid,
            "source": f.name,
            "op_id": op_id,
            "op_number": op_num,
            "block": block,
            "license": classify_license(block),
        })

    # Laws
    for m in LAW_PATTERN.finditer(text):
        header, code, title, body = normalize(m.group(1)), m.group(2), normalize(m.group(3)), normalize(m.group(4))
        uid = checksum(header)
