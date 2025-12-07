import os
import shutil
from pathlib import Path

# === 1. SET YOUR SOURCE FOLDER ===
# This is where your downloaded dataset files currently are.
SOURCE = Path(r"C:\Users\amy\Downloads")  # <-- change if needed

# === 2. SET YOUR TARGET "MONEY" FOLDER ===
TARGET = Path(r"C:\Users\amy\Documents\HHI_Datasets_To_Sell")
TARGET.mkdir(exist_ok=True)

# === 3. DATASET DEFINITIONS ===
datasets = {
    "01_Relational_Loops": ["relational_loops_200.jsonl", "relational_loops_200.csv", "README.txt"],
    "02_Boundary_Scripts": ["boundary_scripts_150.jsonl", "boundary_scripts_150.csv", "README.txt"],
    "03_Emotional_Regulation": ["emotional_regulation_300.jsonl", "emotional_regulation_300.csv", "README.txt"],
    "04_Toxic_to_Healthy": ["toxic_to_healthy_300.jsonl", "toxic_to_healthy_300.csv", "README.txt"],
    "05_Repair_Dialogue_Pack": ["repair_dialogue_350.jsonl", "repair_dialogue_350.csv", "README.txt"]
import os
import shutil
from pathlib import Path

# === 1. SOURCE FOLDER (WHERE YOUR DOWNLOADED FILES ARE) ===
SOURCE = Path(r"C:\Users\amy\Downloads")  # change if your files are somewhere else

# === 2. TARGET "MONEY FOLDER" ===
TARGET = Path(r"C:\Users\amy\Documents\HHI\HHI_Datasets_To_Sell")
TARGET.mkdir(parents=True, exist_ok=True)

# === 3. EXPECTED DATASET FILES ===
datasets = {
    "01_Relational_Loops": [
        "relational_loops_200.jsonl",
        "relational_loops_200.csv",
        "README_relational_loops.txt"
    ],
    "02_Boundary_Scripts": [
        "boundary_scripts_150.jsonl",
        "boundary_scripts_150.csv",
        "README_boundary_scripts.txt"
    ],
    "03_Emotional_Regulation": [
        "emotional_regulation_300.jsonl",
        "emotional_regulation_300.csv",
        "README_emotional_regulation.txt"
    ],
    "04_Toxic_to_Healthy": [
        "toxic_to_healthy_300.jsonl",
        "toxic_to_healthy_300.csv",
        "README_toxic_to_healthy.txt"
    ],
    "05_Repair_Dialogue_Pack": [
        "repair_dialogue_350.jsonl",
        "repair_dialogue_350.csv",
        "README_repair_dialogue.txt"
    ]
}

# === 4. CREATE DIRECTORIES + MOVE FILES ===
for folder_name, file_list in datasets.items():
    dataset_folder = TARGET / folder_name
    dataset_folder.mkdir(exist_ok=True)

    print(f"\n=== Setting up {folder_name} ===")

    for file_name in file_list:
        src = SOURCE / file_name
        dst = dataset_folder / file_name

        if src.exists():
            shutil.copy(src, dst)
            print(f"Copied: {file_name}")
        else:
            print(f"WARNING: {file_name} not found in Downloads.")

print("\n✔ All dataset folders created and files moved (where found).")
print(f"✔ Your datasets are now located in: {TARGET}")
