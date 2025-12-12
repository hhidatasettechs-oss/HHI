import os
import subprocess

REPO_PATH = r"H:\Hollow_House_Institute"  # CHANGE if your local path is different
DOCS_PATH = os.path.join(REPO_PATH, "docs")

files = {
    "licensing.md": """# Licensing Overview

All datasets published under Hollow House Institute are governed by Creative Commons and custom commercial licenses where specified.

## Default License
- CC BY-NC-SA 4.0
- Attribution required
- Non-commercial use only
- Share-alike required for derivatives

## Commercial Licensing
Commercial, enterprise, and AI training rights require a separate written license agreement.

Contact: amyb1665@gmail.com
""",

    "access_and_pricing.md": """# Researcher Access & Pricing

## Access Tiers
- Public (Open Research)
- Academic (Verified Researchers)
- Enterprise / Commercial

## Pricing
Pricing is determined by:
- Dataset size
- Sensitivity level
- Commercial intent
""",

    "dataset_store.md": """# Dataset Store & Status

| Dataset | Description | Status |
|--------|-------------|--------|
| AI–Human Relations | Relational AI data | Active |
| Somatic Field Systems | Body-based intelligence | Active |
| Mirror Grid Logs | Meta-consciousness datasets | Restricted |
""",

    "ai_safety_policy.md": """# AI Safety Policy

All datasets must be used in alignment with:
- Human rights
- Non-harm
- Transparency
- Informed consent
""",

    "researcher_access_application.md": """# Researcher Access Application

Email the following information to amyb1665@gmail.com:

- Full Name
- Institutional Affiliation
- Research Purpose
- Dataset Requested
- Intended Outputs
""",

    "enterprise_terms_of_service.md": """# Enterprise Terms of Service

Enterprise licenses include:
- Commercial AI training
- Product integration
- Redistribution rights
""",

    "data_broker_disclosure.md": """# Data Broker Disclosure

Hollow House Institute does not sell personal data to data brokers.
""",

    "ethics_and_limits.md": """# Ethics & Permitted Use

Permitted:
- Research
- Consciousness studies
- AI alignment

Not allowed:
- Political manipulation
- Surveillance capitalism
""",

    "anonymization_protocol.md": """# Anonymization Protocol

All datasets undergo:
- Removal of direct identifiers
- Time-shifting
- Location fuzzing
""",

    "model_card_template.md": """# Model Card Template

## Model Name:
## Version:
## Training Data:
## Intended Use:
## Limitations:
""",

    "dataset_card_template.md": """# Dataset Card Template

## Dataset Name:
## Description:
## Source:
## License:
## Sensitivity Level:
""",

    "investor_dataset_summary.md": """# Investor Dataset Summary

Hollow House Institute datasets focus on:
- Consciousness research
- Relational AI

Revenue Streams:
- Enterprise licensing
- Research subscriptions
"""
}

os.makedirs(DOCS_PATH, exist_ok=True)

for filename, content in files.items():
    with open(os.path.join(DOCS_PATH, filename), "w", encoding="utf-8") as f:
        f.write(content)

subprocess.run(["git", "add", "docs"], cwd=REPO_PATH)
subprocess.run(["git", "commit", "-m", "Add professional dataset governance documentation"], cwd=REPO_PATH)
subprocess.run(["git", "push"], cwd=REPO_PATH)

print("✅ All docs created and pushed successfully.")
