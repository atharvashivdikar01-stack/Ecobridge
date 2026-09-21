# Ecobridge Datasets Repository
**Smart India Hackathon (SIH 2026) — Problem Statement 26229**  
*Kabadiwala Connect — Bringing the Informal Collector into the Formal Recycling Chain*

This directory houses all the structured datasets, computer vision assets, CPCB registry seeds, and automated pipeline scripts for the Ecobridge platform.

---

## Directory Structure

```
datasets/
├── README.md                      # This quickstart guide
├── DATASET_REGISTER.md            # Comprehensive dataset catalog & metadata register
│
├── operational/                   # Core Operational Datasets (PS Mandate)
│   ├── materials.csv & .json      # 8 e-waste classes, weights, condition, hazard level
│   ├── prices.csv & .json         # Prevailing buy/sell rates across Maharashtra hubs
│   ├── recyclers.csv & .json      # Authorized MPCB/CPCB recyclers with capacity & GPS
│   ├── transactions.csv & .json   # Lot lifecycle records (cash/UPI, lot statuses)
│   ├── traceability.csv & .json   # Tamper-evident SHA-256 digital custody receipts
│   └── collectors.csv & .json     # Privacy-first collector profiles (Zero PII)
│
├── ai_ml/                         # AI/ML, Field Research & Computer Vision Data
│   ├── vision/                    # Object detection & classification datasets
│   │   ├── data.yaml              # YOLOv8 & TFLite dataset configuration
│   │   ├── classes.txt            # 8 target classes (CRT, LCD, PCB, Cables, etc.)
│   │   ├── images/ (train, val)   # Benchmark annotated training images (640x640)
│   │   ├── labels/ (train, val)   # Normalized YOLO bounding boxes
│   │   └── giz_ewaste_samples/    # Real field e-waste photos (GIZ repository, CC-BY-4.0)
│   ├── field_research/            # Primary field survey assets
│   │   ├── field_scrap_manifest.csv # Scrap lot photo survey metadata
│   │   └── classes/               # Dedicated directories for the 8 scrap categories
│   ├── data_flywheel/             # In-app collector feedback logs
│   │   ├── confirmed_labels.csv   # Collector confirmations vs TFLite predictions
│   │   └── flywheel_logs.jsonl    # Streaming feedback logs for model retraining
│   ├── registry/                  # Seeded CPCB EPR Portal Registry
│   │   ├── cpcb_recycler_registry.csv
│   │   └── cpcb_recycler_registry.json
│   └── price_trends/              # Market price intelligence
│       ├── price_trends_historical.csv # 15-month historical time-series
│       └── price_intelligence.json
│
├── database_seeds/                # Database DDL and Initial Seed Scripts
│   ├── schema.sql                 # SQLite & PostgreSQL compatible DDL
│   └── seed_data.sql              # SQL INSERT statements
│
└── scripts/                       # Automation & Validation Tools
    ├── generate_all_datasets.py   # Master generator for all operational/AIML datasets
    ├── download_vision_datasets.py# Hugging Face & Roboflow vision dataset downloader
    ├── validate_datasets.py       # Dataset integrity & referential consistency checker
    └── seed_database.py           # SQLite database generator & test query suite
```

---

## Quick Start Guide

### 1. Validate All Datasets
To verify that all foreign keys, timestamps, geographic coordinates, and data honesty tags are valid:
```bash
python datasets/scripts/validate_datasets.py
```

### 2. Seed the Local SQLite Database
To create or refresh `database/ecobridge.db` and run verification queries:
```bash
python datasets/scripts/seed_database.py
```

### 3. Download Vision Datasets
- **GIZ Real Field Photos (Hugging Face)**:
  ```bash
  python datasets/scripts/download_vision_datasets.py --giz-count 20
  ```
- **Roboflow Universe Datasets (Optional)**:
  ```bash
  python datasets/scripts/download_vision_datasets.py --roboflow --workspace electronic-waste --project electronic-waste-dataset --api-key YOUR_KEY
  ```

---

## Core Specifications Summary

- **8 E-Waste Classes**: CRT, LCD/LED Panels, PCBs, Copper Cables, Batteries, Motors & Magnets, Mixed Plastics, Other E-Waste.
- **Multilingual Support**: English, Marathi (`mr`), and Hindi (`hi`) Devanagari labels throughout.
- **Data Honesty**: Explicit `source_type` (`field`, `recycler`, `synthetic`) tags on all market price records.
- **Privacy First**: Zero unnecessary personally identifiable information (PII) stored in collector profiles.
