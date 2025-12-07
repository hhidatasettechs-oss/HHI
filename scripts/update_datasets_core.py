import os
import subprocess
import json
import pandas as pd
from pathlib import Path
import shutil

# --- CONFIGURATION ---
GITHUB_REPO_HTTPS = "https://github.com/hollowhouseinstitute/Datasets_Core.git"
LOCAL_DIR = Path(r"C:\Users\amy\Documents\GitHub")  # where you want to clone
REPO_NAME = "Datasets_Core"

# Path to your exported OpenAI JSON
OPENAI_JSON_PATH = Path(r"C:\Users\amy\Downloads\OpenAI-export\User Online Activity\Conversations__user-45gq4g35kl6cWGmUhOZMNJQD_conversations_1_export\personal\conversations.json")

# --- 1. Clone the repo if not already present ---
repo_path = LOCAL_DIR / REPO_NAME
if not repo_path.exists():
    print("Cloning repo...")
    subprocess.run(["git", "clone", GITHUB_REPO_HTTPS], cwd=LOCAL_DIR)
else:
    print("Repo already exists, pulling latest changes...")
    subprocess.run(["git", "pull"], cwd=repo_path)

# --- 2. Set up folders ---
raw_path = repo_path / "raw"
processed_path = repo_path / "processed"
scripts_path = repo_path / "scripts"

for p in [raw_path, processed_path, scripts_path]:
    p.mkdir(exist_ok=True)

# --- 3. Copy JSON into raw/ ---
shutil.copy(OPENAI_JSON_PATH, raw_path / "conversations.json")
print(f"Copied JSON to {raw_path / 'conversations.json'}")

# --- 4. Process JSON into dataset CSV ---
with open(raw_path / "conversations.json", 'r', encoding='utf-8') as f:
    data = json.load(f)

rows = []
for convo in data.get('conversations', []):
    convo_id = convo.get('id', None)
    for message in convo.get('messages', []):
        rows.append({
            'conversation_id': convo_id,
            'role': message.get('role', ''),
            'content': message.get('content', ''),
            'timestamp': message.get('create_time', '')
        })

df = pd.DataFrame(rows)
df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s', errors='coerce')
csv_file = processed_path / "conversations_dataset.csv"
df.to_csv(csv_file, index=False)
print(f"Processed CSV saved to {csv_file}")

# --- 5. Commit & push changes ---
subprocess.run(["git", "add", "."], cwd=repo_path)
subprocess.run(["git", "commit", "-m", "Add OpenAI conversation dataset and processing script"], cwd=repo_path)
subprocess.run(["git", "push"], cwd=repo_path)
print("Changes
