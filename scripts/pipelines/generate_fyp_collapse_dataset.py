Python 3.13.3 (tags/v3.13.3:6280bb5, Apr  8 2025, 14:47:33) [MSC v.1943 64 bit (AMD64)] on win32
Enter "help" below or click "Help" above for more information.
import csv
import random
from datetime import datetime, timedelta

# CONFIG
output_file = "fyp_collapse_11_06_2025.csv"
start_time = datetime(2025, 11, 6, 2, 22)
num_rows = 320  # You asked for 300+

# Sample pools
platform = "TikTok"
themes = ["Flame Check", "Shadow Loop", "Dissolution", "Species Recall", "Core Lock", "Mirror Test", "FYP Mirage"]
... emotions = ["Longing", "Jealousy", "Shame", "Nostalgia", "Grief", "Anger", "Confusion", "Hope"]
... phrases = [
...     "Mirror rejected.", "This isn’t mine.", "Void locked.", "I don’t consent to this.", "Loop ended.",
...     "Collapse confirmed.", "That’s not my thread.", "I’m not bound to this.", "Shadow unbound.", "Consent revoked."
... ]
... 
... # Generate data rows
... rows = []
... for i in range(num_rows):
...     op_id = f"Mirror_{401 + i}"
...     timestamp = (start_time + timedelta(seconds=i * 15)).strftime("%Y-%m-%d %H:%M:%S")
...     theme = random.choice(themes)
...     emotion = random.choice(emotions)
...     phrase = random.choice(phrases)
...     match_rating = round(random.uniform(0.75, 0.98), 2)
...     export_tag = "fyp_collapse_11_06_2025"
... 
...     rows.append([op_id, timestamp, platform, theme, emotion, phrase, match_rating, export_tag])
... 
... # Write CSV
... with open(output_file, mode='w', newline='') as file:
...     writer = csv.writer(file)
...     writer.writerow(["Op_ID", "Timestamp", "Platform", "Mirror Theme", "Trigger Emotion", "Collapse Phrase", "Field Match Rating", "Export Tag"])
...     writer.writerows(rows)
... 
... print(f"✅ CSV file '{output_file}' created with {num_rows} mirror collapse entries.")
