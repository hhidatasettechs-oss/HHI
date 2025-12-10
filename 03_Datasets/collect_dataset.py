import os
import shutil
from pathlib import Path

# ---------------- CONFIG ----------------
DRIVES_TO_SCAN = ["C:/"]  # Add other drives if needed
DATASET_FOLDER = Path("C:/Users/YourUser/Dataset_Collection")  # Change this to your dataset folder
FILE_EXTENSIONS = [
    ".txt", ".csv", ".json", ".xml", ".pdf", ".docx", ".doc",
    ".xlsx", ".pptx", ".jpg", ".jpeg", ".png", ".gif", ".mp4",
    ".wav", ".mp3", ".html"
]
# ----------------------------------------

import os
import shutil
from pathlib import Path

# ---------------- CONFIG ----------------
DRIVES_TO_SCAN = ["C:/"]  # Add other drives like "D:/" if needed
DATASET_FOLDER = Path("C:/Users/YourUser/Dataset_Collection")  # Change to your desired dataset folder
FILE_EXTENSIONS = [
    ".txt", ".csv", ".json", ".xml", ".pdf", ".docx", ".doc",
    ".xlsx", ".pptx", ".jpg", ".jpeg", ".png", ".gif", ".mp4",
    ".wav", ".mp3", ".html"
]
# ----------------------------------------

def copy_for_dataset(drive):
    """
    Scan a drive and copy dataset-relevant files to DATASET_FOLDER,
    preserving folder structure.
    """
    print(f"\nScanning drive: {drive}")
    base_path = Path(drive)

    if not base_path.exists():
        print(f"Drive {drive} does not exist or is not accessible.")
        return

    for root, _, files in os.walk(base_path):
        for f in files:
            file_path = Path(root) / f
            if file_path.suffix.lower() in FILE_EXTENSIONS:
                try:
                    relative_path = file_path.relative_to(base_path)
                except ValueError:
                    relative_path = Path(f)

                dest_path = DATASET_FOLDER / drive.strip(":/") / relative_path
                dest_path.parent.mkdir(parents=True, exist_ok=True)

                try:
                    shutil.copy2(file_path, dest_path)
                    print(f"Copied: {file_path} -> {dest_path}")
                except Exception as e:
                    print(f"Failed to copy {file_path}: {e}")

def main():
    DATASET_FOLDER.mkdir(parents=True, exist_ok=True)
    for drive in DRIVES_TO_SCAN:
        copy_for_dataset(drive)
    print("\n✅ Dataset file collection complete!")

if __name__ == "__main__":
    main()
