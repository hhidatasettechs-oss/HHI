# 03_Datasets — Public Dataset Infrastructure

## Purpose
This directory contains **public-safe dataset infrastructure** for the Hollow House Institute (HHI).
It exposes *how datasets are defined, validated, and constructed* without distributing any commercial,
sensitive, or human-identifiable data.

## What This Directory Contains
- **Dataset builders** (*.py)
  Scripts defining dataset construction logic, validation rules, and processing flows.
- **Schemas & indices** (*.json, *.jsonl)
  Structural definitions and non-sensitive derived artifacts.
- **Metadata descriptors** (*.metadata.json)
  Versioning, provenance, and governance metadata for reproducibility.

## What This Directory Does NOT Contain
- Raw human-source data
- OPS or Codex narrative bodies
- Identity, likeness, biometric, or personal materials
- Commercial dataset payloads or ZIP distributions

## Governance & Safety
All contents are non-identifying, license-safe for public viewing, and aligned with HHI audit,
anonymization, and data-minimization standards.

Commercial datasets and identity-protected materials are intentionally excluded and released only
through controlled channels.

## Intended Use
- Transparency for researchers and partners
- Reproducible dataset engineering patterns
- Audit-ready demonstration of HHI dataset governance

This directory represents **infrastructure, not inventory**.
