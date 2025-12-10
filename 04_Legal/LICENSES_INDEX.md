# Licenses index — Master License Suite

This file maps the repository's license documents (in /legal) to the artifacts they govern and provides short plain-English summaries.

Files:
- /legal/LICENSE_AHRL-1.md
  - Short name: AHRL-1 (AI–Human Relations Research License)
  - Governs: relational datasets, human–AI interaction research artifacts
  - Summary: Non-commercial; attribution required; restricts training commercial AI models.

- /legal/LICENSE_RAP-DL-1.0.md
  - Short name: RAP-DL 1.0 (Relational AI Psychology Data License)
  - Governs: psychology and relational datasets; ethical-use constraints.
  - Summary: Non-commercial; trauma-safety protections; explicit consent required.

- /legal/LICENSE_FBCR-1.md
  - Short name: FBCR-1 (Field-Based Cognition Research)
  - Governs: field cognition datasets and field research artifacts.
  - Summary: Non-commercial with attribution; preserves field-sourced rights and practices.

- /legal/LICENSE_444-A_Flame.md
  - Short name: Flame 444-A (Sovereign Flame License)
  - Governs: Flame-species frameworks, Mirror frameworks, symbolic codex structures.
  - Summary: Strong prohibitions on commercial re-use, reselling, or embedding into products without a commercial license.

- /legal/LICENSE_TCDPL-4.4.md
  - Short name: TCDPL-4.4 (Temple Codex Data Protection License)
  - Governs: codex data protection, symbolic structures.
  - Summary: Data protection + non-commercial + ethical use clauses.

Repository-level license guidance
- Canonical human-readable summary: LICENSE.md (root) — contains global terms and commercial license tiers.
- Machine-readable SPDX: The repository uses CC-BY-NC-SA-4.0 as the base; specialized license texts in /legal provide additional constraints. When referencing programmatically, include both CC-BY-NC-SA-4.0 and the specific custom license file name.

How to determine which license applies
1. Identify artifact type (dataset, code, documentation, codex).
2. Check dataset or file-level metadata for explicit license tag (use filename or DATA_DICTIONARY).
3. If no tag, default to the repository's LICENSE.md scope rules and open an issue to clarify.

How to request commercial licensing
- Use the ".github/ISSUE_TEMPLATE/license_request.md" template to open a request. Include intended use, scale (models, product), and organization info.