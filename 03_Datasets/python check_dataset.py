import os
import pandas as pd
import json

# Path to your processed folder
processed_folder = r"C:\Users\amy\Documents\GitHub\Datasets_Core\datasets\H3CD-5\processed"

# List all files in the folder
files = os.listdir(processed_folder)
print("Files found in processed folder:", files)

# Find CSV and JSONL files automatically
csv_files = [f for f in files if f.lower().endswith(".csv")]
jsonl_files = [f for f in files if f.lower().endswith(".jsonl")]

# Load and check CSV files
for csv_file in csv_files:
    csv_path = os.path.join(processed_folder, csv_file)
    print(f"\n--- Checking CSV: {csv_file} ---")
    try:
        df = pd.read_csv(csv_path)
        print("Number of messages:", len(df))
        print("Columns:", df.columns.tolist())
        print("First 3 rows:\n", df.head(3))
        print("Missing values per column:\n", df.isnull().sum())
        # Check label consistency if columns exist
        for col in ["Tone", "Intent"]:
            if col in df.columns:
                print(f"Unique values in {col}:", df[col].unique())
    except Exception as e:
        print("Error loading CSV:", e)

# Load and check JSONL files
for jsonl_file in jsonl_files:
    jsonl_path = os.path.join(processed_folder, jsonl_file)
    print(f"\n--- Checking JSONL: {jsonl_file} ---")
    try:
        with open(jsonl_path, "r", encoding="utf-8") as f:
            json_lines = [json.loads(line) for line in f]
        print("Number of messages:", len(json_lines))
        print("First message:\n", json_lines[0] if json_lines else "No data")
    except Exception as e:
        print("Error loading JSONL:", e)
