import os, json, datetime

base = os.path.expanduser(r"C:\Users\amy\Documents\HHI\Identity_Protection")
os.makedirs(base, exist_ok=True)

local_seed_file = "hhi_protected_assets.jsonl"
dest_seed_file = os.path.join(base, "hhi_protected_assets.jsonl")

with open(local_seed_file, "r", encoding="utf-8") as src, open(dest_seed_file, "w", encoding="utf-8") as dst:
    for line in src:
        dst.write(line)

manifest_path = os.path.join(base, "manifest.txt")
with open(manifest_path, "w", encoding="utf-8") as f:
    f.write("HHI DIGITAL LIKENESS RIGHTS PROTOCOL INSTALLED\n")
    f.write("Install Time: " + str(datetime.datetime.now()) + "\n")
    f.write("Seeds: 14\n")

print("HHI Identity Protection Install Complete.")
