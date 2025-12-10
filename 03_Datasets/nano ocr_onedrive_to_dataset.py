# file: tools/build_sale_ready_textds.py
import argparse
import datetime as dt
import hashlib
import json
import re
import sys
import unicodedata
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

DEFAULT_EXTS = (".txt", ".md")
SEED = 17

# --- PII regexes ---
PII_PATTERNS = {
    "email": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
    "phone": re.compile(r"(?:(?:\+?\d{1,3}[\s.-]?)?(?:\(?\d{3}\)?|\d{3})[\s.-]?\d{3}[\s.-]?\d{4})"),
    "ssn": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    "credit_card": re.compile(r"\b(?:\d[ -]*?){13,19}\b"),
    "ip": re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"),
    "url": re.compile(r"\bhttps?://[^\s)>\]]+\b", re.IGNORECASE),
}

CONTROL_CHARS = "".join(map(chr, list(range(0, 32)) + [127]))
CONTROL_TABLE = str.maketrans({c: " " for c in CONTROL_CHARS})

@dataclass
class Record:
    id: str
    source_path: str
    title: str
    text: str
    tokens_est: int
    hash: str
    tags: List[str]

# --- utils ---
def sha1_hex(s: str) -> str:
    return hashlib.sha1(s.encode("utf-8")).hexdigest()

def now_iso() -> str:
    return dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

def normalize_text(raw: str) -> str:
    t = unicodedata.normalize("NFC", raw).translate(CONTROL_TABLE).replace("\r", "")
    t = t.replace("’", "'").replace("“", '"').replace("”", '"').replace("–", "-").replace("—", "-")
    t = re.sub(r"[ \t]+", " ", t)
    t = re.sub(r"\n{3,}", "\n\n", t)
    return t.strip()

def redact_pii(text: str, keep_urls: bool) -> Tuple[str, Dict[str, int]]:
    counts: Dict[str, int] = {k: 0 for k in PII_PATTERNS}
    red = text
    for name, pat in PII_PATTERNS.items():
        if name == "url" and keep_urls:
            continue
        red, n = pat.subn(f"<{name.upper()}>", red)
        counts[name] += n
    return red, counts

def estimate_tokens(text: str) -> int:
    return len(re.findall(r"\S+", text))

def greedy_chunks(text: str, char_budget: int) -> List[str]:
    if char_budget <= 0 or len(text) <= char_budget:
        return [text]
    words = text.split()
    chunks, cur, cur_len = [], [], 0
    for w in words:
        add = len(w) + (1 if cur else 0)
        if cur and cur_len + add > char_budget:
            chunks.append(" ".join(cur)); cur, cur_len = [w], len(w)
        else:
            cur.append(w); cur_len += add
    if cur: chunks.append(" ".join(cur))
    return chunks

def read_text_file(p: Path) -> Optional[str]:
    try:
        return p.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return None  # why: keep pipeline resilient

def iter_files(root: Path, exts: Sequence[str], recursive: bool) -> Iterable[Path]:
    exts = tuple(e.lower() for e in exts)
    if recursive:
        yield from (p for p in root.rglob("*") if p.is_file() and p.suffix.lower() in exts)
    else:
        yield from (p for p in root.iterdir() if p.is_file() and p.suffix.lower() in exts)

def write_jsonl(path: Path, rows: Iterable[Dict]) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    n = 0
    with tmp.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n"); n += 1
    tmp.replace(path)
    return n

def write_checksums(dir_path: Path) -> None:
    for p in dir_path.glob("*.jsonl"):
        h = hashlib.sha256(p.read_bytes()).hexdigest()
        (p.with_suffix(p.suffix + ".sha256")).write_text(h + "  " + p.name, encoding="utf-8")

# --- core ---
def build_records(
    inputs: List[Path],
    keep_urls: bool,
    chunk_chars: int,
    tags: List[str],
) -> Tuple[List[Record], Dict[str, int], Dict[str, int]]:
    seen_hashes: set = set()
    pii_totals: Dict[str, int] = {k: 0 for k in PII_PATTERNS}
    drop_reasons: Dict[str, int] = {"empty": 0, "duplicate": 0}
    out: List[Record] = []

    for p in inputs:
        raw = read_text_file(p)
        if raw is None:
            continue
        norm = normalize_text(raw)
        if not norm:
            drop_reasons["empty"] += 1
            continue

        red, counts = redact_pii(norm, keep_urls=keep_urls)
        for k, v in counts.items():
            pii_totals[k] += v

        h = sha1_hex(red)
        if h in seen_hashes:
            drop_reasons["duplicate"] += 1
            continue
        seen_hashes.add(h)

        chunks = greedy_chunks(red, char_budget=chunk_chars)
        for idx, ch in enumerate(chunks):
            rid = sha1_hex(f"{h}:{idx}")
            out.append(Record(
                id=rid,
                source_path=str(p),
                title=p.stem if len(chunks) == 1 else f"{p.stem} [part {idx+1}/{len(chunks)}]",
                text=ch,
                tokens_est=estimate_tokens(ch),
                hash=sha1_hex(ch),
                tags=tags,
            ))
    return out, pii_totals, drop_reasons

def split_sets(n: int, split_str: str, seed: int = SEED) -> Tuple[List[int], List[int], List[int]]:
    parts = [int(x) for x in split_str.split(",")]
    assert len(parts) == 3 and sum(parts) == 100, "--split must be 'train,val,test' totaling 100"
    idxs = list(range(n))
    import random as _r
    _r.Random(seed).shuffle(idxs)
    t_cut = n * parts[0] // 100
    v_cut = t_cut + n * parts[1] // 100
    return idxs[:t_cut], idxs[t_cut:v_cut], idxs[v_cut:]

def validate_record(rec: Record) -> None:
    if not rec.id or not rec.text:
        raise ValueError("invalid record: missing id/text")
    if not isinstance(rec.tokens_est, int) or rec.tokens_est < 0:
        raise ValueError("invalid tokens_est")
    if not re.fullmatch(r"[0-9a-f]{40}", rec.hash):
        raise ValueError("invalid hash")

def export_dataset(out_dir: Path, recs: List[Record], split: str) -> Dict[str, int]:
    ds_dir = out_dir / "processed"
    ds_dir.mkdir(parents=True, exist_ok=True)

    train_idx, val_idx, test_idx = split_sets(len(recs), split)
    train = [recs[i] for i in train_idx]
    val = [recs[i] for i in val_idx]
    test = [recs[i] for i in test_idx]

    for r in recs:
        validate_record(r)

    n_train = write_jsonl(ds_dir / "train.jsonl", (asdict(r) for r in train))
    n_val   = write_jsonl(ds_dir / "val.jsonl",   (asdict(r) for r in val))
    n_test  = write_jsonl(ds_dir / "test.jsonl",  (asdict(r) for r in test))
    write_checksums(ds_dir)
    return {"train": n_train, "val": n_val, "test": n_test}

def write_manifest(out_dir: Path, name: str, license_str: str, counts: Dict[str, int],
                   pii_totals: Dict[str, int], drop_reasons: Dict[str, int], args: argparse.Namespace) -> None:
    manifest = {
        "name": name,
        "version": "1.0.0",
        "created_utc": now_iso(),
        "license": license_str,
        "schema": {
            "format": "jsonl",
            "record": {
                "id": "str", "source_path": "str", "title": "str", "text": "str",
                "tokens_est": "int", "hash": "hex(40)", "tags": "list[str]"
            }
        },
        "files": {"train": "processed/train.jsonl", "val": "processed/val.jsonl", "test": "processed/test.jsonl"},
        "counts": counts,
        "drops": drop_reasons,
        "pii_redactions": pii_totals,
        "build_args": vars(args),
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

def write_stats(out_dir: Path, recs: List[Record]) -> None:
    toks = [r.tokens_est for r in recs]
    stats = {"records": len(recs), "tokens_est": {}} if not toks else {
        "records": len(recs),
        "tokens_est": {"min": min(toks), "max": max(toks), "mean": round(sum(toks)/len(toks), 2),
                       "p50": sorted(toks)[len(toks)//2]}
    }
    (out_dir / "stats.json").write_text(json.dumps(stats, indent=2), encoding="utf-8")

def write_dataset_card(out_dir: Path, name: str, license_str: str, counts: Dict[str, int], keep_urls: bool) -> None:
    md = f"""# {name}

**Version:** 1.0.0  
**License:** {license_str}  
**Format:** JSONL (UTF-8)  
**Splits:** train / val / test

## Schema
- `id` (str), `source_path` (str), `title` (str), `text` (str), `tokens_est` (int), `hash` (hex40), `tags` (str[])

## Files
- `processed/train.jsonl` — {counts.get("train",0)} rows  
- `processed/val.jsonl` — {counts.get("val",0)} rows  
- `processed/test.jsonl` — {counts.get("test",0)} rows

## Notes
- PII redaction applied (emails/phones/SSNs/credit cards/IPs{", URLs kept" if keep_urls else ", URLs redacted"}).  
- Duplicates removed via SHA1 after cleaning.  
- Chunks are ~target char budget without splitting words.
"""
    (out_dir / "DATASET_CARD.md").write_text(md, encoding="utf-8")

# --- CLI ---
def parse_args() -> argparse.Namespace:
    default_in = Path(r"C:\Users\amy\Downloads\Hollow_Books_Text")
    default_out = default_in / "processed_datasets"
    ap = argparse.ArgumentParser(description="Convert raw text into sale-ready processed datasets.")
    ap.add_argument("--in", dest="inp", type=Path, default=default_in, help="Input folder with raw text files.")
    ap.add_argument("--out", dest="out", type=Path, default=default_out, help="Output folder.")
    ap.add_argument("--name", type=str, default="HollowBooks_Text", help="Dataset name.")
    ap.add_argument("--license", type=str, default="CC-BY-4.0", help="License string to embed.")
    ap.add_argument("--ext", type=str, default=",".join(DEFAULT_EXTS), help="Comma-separated extensions.")
    ap.add_argument("--recursive", action="store_true", help="Recurse into subfolders.")
    ap.add_argument("--chunk-chars", type=int, default=1200, help="Target max characters per record.")
    ap.add_argument("--split", type=str, default="90,5,5", help="Split percentages train,val,test.")
    ap.add_argument("--tags", type=str, default="", help="Comma-separated tags to include on each record.")
    ap.add_argument("--keep-urls", action="store_true", help="Do NOT redact URLs.")
    return ap.parse_args()

def main() -> None:
    args = parse_args()
    in_dir: Path = args.inp
    out_dir: Path = args.out
    name: str = args.name
    license_str: str = args.license
    exts = tuple(e.strip().lower() for e in args.ext.split(",") if e.strip())
    tags = [t.strip() for t in args.tags.split(",") if t.strip()]

    files = sorted(iter_files(in_dir, exts, args.recursive))
    if not files:
        print(f"[!] No files with {exts} in {in_dir}", file=sys.stderr)
        sys.exit(1)

    recs, pii_totals, drops = build_records(files, args.keep_urls, args.chunk_chars, tags)
    if not recs:
        print("[!] No usable records after processing.", file=sys.stderr)
        sys.exit(1)

    counts = export_dataset(out_dir, recs, args.split)
    write_manifest(out_dir, name, license_str, counts, pii_totals, drops, args)
    write_stats(out_dir, recs)
    write_dataset_card(out_dir, name, license_str, counts, args.keep_urls)

    print(f"[OK] {name} built at {out_dir}")
    print(f"  total records: {len(recs)} | train={counts['train']} val={counts['val']} test={counts['test']}")
    print(f"  drops: {drops}")
    print(f"  redactions: {pii_totals}")

if __name__ == "__main__":
    main()
