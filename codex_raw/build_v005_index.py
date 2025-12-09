import json
import os

RAW_ROOT = r"C:\Users\amy\Documents\HHI\codex_raw"
CONFIG_PATH = os.path.join(RAW_ROOT, "v005_config.json")

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def count_jsonl(path):
    count = 0
    with open(path, "r", encoding="utf-8") as f:
        for _ in f:
            count += 1
    return count

def main():
    config = load_json(CONFIG_PATH)

    raw_root = config["raw_root"]
    files = config["files"]
    index_files = config["index_files"]

    anon_map_path = os.path.join(raw_root, files["anonymization_map"])
    metadata_path = os.path.join(raw_root, files["metadata"])
    blocks_path = os.path.join(raw_root, files["blocks_anon"])
    ops_path = os.path.join(raw_root, files["ops_ledger_anon"])

    print("=== HHI v005 RAW INDEX ===")
    print(f"RAW_ROOT: {raw_root}")
    print(f"Config:   {CONFIG_PATH}")

    metadata = load_json(metadata_path)
    anon_map = load_json(anon_map_path)

    print(f"\nVersion in metadata.json: {metadata.get('version')}")
    print(f"OPS count (metadata):     {metadata.get('ops_count')}")
    print(f"Block count (metadata):   {metadata.get('block_count')}")
    print(f"Anonymization entries:    {len(anon_map)}")

    print("\nCounting JSONL lines (this may take a bit)...")
    block_lines = count_jsonl(blocks_path)
    ops_lines = count_jsonl(ops_path)

    print(f"blocks_anon.jsonl:      {block_lines} lines")
    print(f"ops_ledger_anon.jsonl:  {ops_lines} lines")

    block_index_path = os.path.join(raw_root, index_files["block_index"])
    ops_index_path = os.path.join(raw_root, index_files["ops_index"])

    with open(block_index_path, "w", encoding="utf-8") as f_block:
        json.dump(
            {
                "version": "v005",
                "source": files["blocks_anon"],
                "line_count": block_lines
            },
            f_block,
            ensure_ascii=False,
            indent=2
        )

    with open(ops_index_path, "w", encoding="utf-8") as f_ops:
        json.dump(
            {
                "version": "v005",
                "source": files["ops_ledger_anon"],
                "line_count": ops_lines
            },
            f_ops,
            ensure_ascii=False,
            indent=2
        )

    print("\nIndex stubs written:")
    print(f"- {block_index_path}")
    print(f"- {ops_index_path}")
    print("\nv005 is now ACTIVE as raw material state.")

if __name__ == "__main__":
    main()
