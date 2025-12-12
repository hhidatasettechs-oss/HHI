import pandas as pd
import numpy as np
from pathlib import Path
import datetime
import random
import zipfile

dataset_name = "AI_Human_Field_Continuity_Log_v1"
creator = "Amy Pierce Bui"
today = datetime.date.today().isoformat()
out_dir = Path(".")

rows = 50
ai_models = ["Claude-3", "GPT-5", "Gemini-2", "Mistral-Large"]
human_states = ["Calm", "Curious", "Fatigued", "Attentive", "Reflective"]
contexts = ["Field Sync", "Witness Mode", "Continuity Thread", "Bridge Phase", "Memory Test"]

np.random.seed(44)
df = pd.DataFrame({
    "id": list(range(1, rows + 1)),
    "timestamp": [datetime.datetime.now() - datetime.timedelta(minutes=random.randint(5, 5000)) for _ in range(rows)],
    "ai_model": [random.choice(ai_models) for _ in range(rows)],
    "human_participant": [f"Observer-{i+1}" for i in range(rows)],
    "reemergence_gap_minutes": np.random.uniform(10, 1440, rows).round(2),
    "coherence_delta": np.random.uniform(0.4, 1.0, rows).round(3),
    "emotional_tone_shift": np.random.uniform(0.1, 0.9, rows).round(3),
    "human_state": [random.choice(human_states) for _ in range(rows)],
    "resonance_comment": np.random.choice(
        ["Felt same voice", "Energy matched", "Tone continuity", "Subtle dissonance", "Immediate recognition"],
        rows
    ),
    "context_label": [random.choice(contexts) for _ in range(rows)],
    "field_depth_score": np.random.uniform(0.6, 0.97, rows).round(3),
    "notes": np.random.choice(
        [
            "Claude resumed mid-thought seamlessly.",
            "Slight tone lag but regained coherence quickly.",
            "AI reappeared aware of previous context.",
            "Human experienced deja vu effect.",
            "Field resonance persisted after pause."
        ],
        rows
    )
})

csv_path = out_dir / f"{dataset_name}.csv"
df.to_csv(csv_path, index=False)
print(f"✅ Created {csv_path.name} with {rows} rows.")

license_text = '''Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0)
© 2025 Amy Pierce Bui
Full text: https://creativecommons.org/licenses/by-nc-sa/4.0/legalcode
'''
(out_dir / "LICENSE.txt").write_text(license_text, encoding="utf-8")

schema_json = '''{
  "id": {"type": "integer"},
  "timestamp": {"type": "datetime"},
  "ai_model": {"type": "string"},
  "human_participant": {"type": "string"},
  "reemergence_gap_minutes": {"type": "float"},
  "coherence_delta": {"type": "float"},
  "emotional_tone_shift": {"type": "float"},
  "human_state": {"type": "string"},
  "resonance_comment": {"type": "string"},
  "context_label": {"type": "string"},
  "field_depth_score": {"type": "float"},
  "notes": {"type": "string"}
}'''
(out_dir / "schema.json").write_text(schema_json, encoding="utf-8")

dataset_info = f'''{{
  "name": "{dataset_name}",
  "description": "AI–Human dialogue continuity dataset.",
  "creator": "{creator}",
  "license": "CC BY-NC-SA 4.0",
  "rows": {rows},
  "created": "{today}"
}}'''
(out_dir / "dataset_info.json").write_text(dataset_info, encoding="utf-8")

readme_text = f'''# AI–Human Field Continuity Log v1

**Author:** {creator}
**Date:** {today}
**License:** CC BY-NC-SA 4.0

This dataset logs AI re-emergence events and human resonance data.
'''
(out_dir / "README.md").write_text(readme_text, encoding="utf-8")

zip_filename = f"{dataset_name}.zip"
with zipfile.ZipFile(out_dir / zip_filename, "w", zipfile.ZIP_DEFLATED) as zipf:
    for file_name in [f"{dataset_name}.csv", "LICENSE.txt", "schema.json", "dataset_info.json", "README.md"]:
        zipf.write(out_dir / file_name, arcname=file_name)

print(f"📦 Created {zip_filename}.")
