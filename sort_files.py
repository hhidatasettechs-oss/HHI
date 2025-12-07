import os
import shutil
from pathlib import Path

ROOT = Path(r"C:\Users\amy")
OUT = ROOT / "_Organized_Files"
OUT.mkdir(exist_ok=True)

PROTECT = [
    r"C:\Users\amy\Documents\GitHub",
    r"C:\Users\amy\Documents\Hollow_House",
    r"C:\Users\amy\Documents\Master_Ledgers",
]

CATEGORIES = {
    "images": [".jpg", ".jpeg", ".png", ".gif"],
    "docs": [".docx", ".doc", ".pptx", ".ppt"],
    "pdf": [".pdf"],
    "text": [".txt", ".md", ".rtf"],
    "data": [".csv", ".xlsx", ".json", ".jsonl"],
    "audio": [".mp3", ".wav", ".m4a"],
    "video": [".mp4", ".mov", ".avi"],
    "code": [".py", ".js", ".html", ".css"],
    "archives": [".zip", ".rar", ".7z"],
    "other": []
}

def get_category(ext):
    for cat, ext_list in CATEGORIES.items():
        if ext.lower() in ext_list:
            return cat
    return "other"

moved = 0
skipped = 0

for dirpath, dirs, files in os.walk(ROOT):
    if any(p.lower() in dirpath.lower() for p in PROTECT):
        continue

    for filename in files:
        file_path = Path(dirpath) / filename

        if filename.startswith("~$") or file_path.suffix == "":
            skipped += 1
            continue

        ext = file_path.suffix.lower()
        category = get_category(ext)

        cat_folder = OUT / category
        cat_folder.mkdir(exist_ok=True)

        new_path = cat_folder / filename

        try:
            shutil.move(str(file_path), str(new_path))
            print(f"MOVED: {file_path} -> {new_path}")
            moved += 1
        except Exception as e:
            print(f"SKIPPED: {file_path} ({e})")
            skipped += 1

print("\n----------- DONE -----------")
print(f"Moved: {moved}")
print(f"Skipped: {skipped}")
print(f"Output folder: {OUT}")
print("-----------------------------")
