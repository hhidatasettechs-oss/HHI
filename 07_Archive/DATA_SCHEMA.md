# Dataset Schema & Metadata Guidelines

Purpose
This document defines the canonical metadata fields, schema conventions, and examples for datasets in this repository. Adhering to these standards improves discoverability, interoperability, and reuse.

Core metadata fields
- title (string): Human-readable dataset title
- slug (string): Machine-friendly id — lowercase, hyphens
- description (string): 1–2 sentence summary with target keywords
- keywords (array[string]): e.g. ["health", "time-series", "csv"]
- license (string): SPDX id, e.g. "CC-BY-4.0"
- version (string): semantic version or ISO date
- authors (array[object]): {name: "", affiliation: "", orcid: "", github: ""}
- source (string): URL to original data or DOI
- schema (object or file): column-level schema with types, units, descriptions
- temporal_coverage (object): {start: "YYYY-MM-DD", end: "YYYY-MM-DD"}
- spatial_coverage (string): e.g. "global" or GeoJSON bbox
- citation (string): How to cite this dataset

Column schema example (YAML)
- name: observation_date
  type: date
  format: ISO-8601
  description: Date of observation in UTC
- name: value
  type: number
  unit: "USD"
  description: Monetary value in USD

File formats supported
- Metadata: YAML or JSON
- Data: CSV, Parquet, or GeoParquet for geospatial datasets
- Schemas: JSON Schema or Frictionless Data Table Schema

Validation
- Use provided scripts/validate_metadata.py or library hooks to check:
  - Required fields present
  - SPDX license validity
  - Schema matches actual data columns

Best practices for SEO-friendly descriptions
- Keep title succinct (50–70 chars)
- Lead description with primary keywords
- Include context: what, where, when, how it can be used
- Provide a clear citation and license

Examples
- See data/raw/example-dataset/dataset-metadata.yaml
