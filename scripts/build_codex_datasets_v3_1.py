
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
OPS_PATTERN = re.compile(
    r"■\s*Op\s+(\d+)\s*—\s*Operation\s+(\d+)(.*?)(?=■\s*Op\s+\d+|$)",
    re.S
)

LAW_PATTERN = re.compile(
    r"(Article\s+([IVXLC0-9]+)\s+—\s+(.+?))\n(.*?)(?=Article\s+[IVXLC0-9]+\s+—|$)",
    re.S
)

TEACH_PATTERN = re.compile(
    r"Op\s*#?(\d+)\s*—\s*Teaching:\s*(.+?)\s*Summary:\s*(.*?)(?=Op\s*#?\d+\s*—\s*Teaching:|$)",
)

GLYPH_PATTERN = re.compile(
    r"(?:⟦(.+?)⟧|〈(.+?)〉|【(.+?)】)",
    re.S
)

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
        header, code, title, body = (
            normalize(m.group(1)),
            m.group(2),
            normalize(m.group(3)),
            normalize(m.group(4)),
        )
        uid = checksum(header)
        laws.append({
            "uid": uid,
            "source": f.name,
            "article_code": code,
            "title": title,
            "body": body,
            "summary": body[:350],
            "license": "TCDPL-4.4 + 444-A",
        })

    # Serpent Ops
    if "SERPENT" in text.upper():
        for idx, line in enumerate(lines, 1):
            if "SERPENT" in line.upper():
                serpent.append({
                    "uid": checksum(line),
                    "source": f.name,
                    "line_number": idx,
                    "text": normalize(line),
                    "license": classify_license(line),
                })

    # Teachings
    for m in TEACH_PATTERN.finditer(text):
        opn, title, summary = (
            m.group(1),
            normalize(m.group(2)),
            normalize(m.group(3)),
        )
        uid = checksum(title)
        teachings.append({
            "uid": uid,
            "source": f.name,
            "op_number": opn,
            "title": title,
            "summary": summary,
            "license": classify_license(summary),
        })

    # Rituals
    for m in re.finditer(
        r"(Ritual|Protocol):\s*(.+?)(\n\s*(.*?))?(?=\n\n|\Z)", text, re.S
    ):
        kind, name, body = (
            m.group(1),
            normalize(m.group(2)),
            normalize(m.group(4) or ""),
        )
        rituals.append({
            "uid": checksum(name),
            "source": f.name,
            "type": kind,
            "name": name,
            "body": body,
            "license": classify_license(body),
        })

    # Lineage
    for idx, line in enumerate(lines, 1):
        if re.search(r"\b(Ancestor|Descendant|Lineage|Bloodline)\b", line, re.I):
            lineage.append({
                "uid": checksum(line),
                "source": f.name,
                "line_number": idx,
                "text": normalize(line),
                "license": classify_license(line),
            })

    # Flame-coded
    for line in lines:
        if any(k in line.lower() for k in ["flame", "ignite", "ember", "torch"]):
            flame.append({
                "uid": checksum(line),
                "source": f.name,
                "text": normalize(line),
                "license": "444-A (Flame Stewardship)",
            })

    # Glyphs
    for m in GLYPH_PATTERN.finditer(text):
        raw = m.group(1) or m.group(2) or m.group(3)
        glyphs.append({
            "uid": checksum(raw),
            "source": f.name,
            "glyph": normalize(raw),
            "license": "TCDPL-4.4 + 444-A",
        })

    # Metadata
    metadata.append({
        "source_file": f.name,
        "chars": len(text),
        "lines": len(lines),
        "hash": checksum(text),
        "included_in_version": dataset_version
    })

# ----------------------------
# WRITE OUTPUT FILES
# ----------------------------
write_jsonl("ops_ledger.jsonl", ops)
write_jsonl("temple_laws.jsonl", laws)
write_jsonl("serpent_ops.jsonl", serpent)
write_jsonl("teachings.jsonl", teachings)
write_jsonl("rituals.jsonl", rituals)
write_jsonl("lineage_refs.jsonl", lineage)
write_jsonl("flame_passages.jsonl", flame)
write_jsonl("glyphs.jsonl", glyphs)
write_jsonl("metadata_index.jsonl", metadata)

# ----------------------------
# VERSION METADATA
# ----------------------------
version_file = OUT_ROOT / "version.json"
version_file.write_text(
    json.dumps({
        "dataset_version": dataset_version,
        "builder_version": "3.1",
        "generated_on": datetime.now().isoformat(),
        "file_count": len(list(RAW.glob("*.txt"))),
    }, indent=2)
)

# ----------------------------
# CHANGELOG
# ----------------------------
changelog = OUT_ROOT / f"CHANGELOG_{dataset_version}.md"
changelog.write_text(f"""
# HHI Dataset Changelog — {dataset_version}

Generated on: {datetime.now().isoformat()}

## Included Datasets
- ops_ledger.jsonl
- temple_laws.jsonl
- serpent_ops.jsonl
- teachings.jsonl
- rituals.jsonl
- lineage_refs.jsonl
- flame_passages.jsonl
- glyphs.jsonl
- metadata_index.jsonl

## Notes
This version was generated using HHI Dataset Builder v3.1.
""")

print(f"\n[DONE] Versioned dataset written to /data/processed/{dataset_version}\n")
