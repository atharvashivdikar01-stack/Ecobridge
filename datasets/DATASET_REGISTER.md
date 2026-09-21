# Ecobridge Dataset Register
**SIH 2026 Problem Statement 26229 — Kabadiwala Connect**  
*Single Source of Truth for Project Datasets, Schemas, Sources, and Ethical Governance*

---

## 1. Executive Summary & Compliance Overview

Under SIH 2026 Problem Statement 26229, our platform (**Ecobridge**) is engineered to bridge informal e-waste collectors (*kabadiwalas*) with formal, authorized recyclers in India. This repository contains the complete dataset architecture spanning two major pillars:

1. **Core Operational Datasets (Mandated by Problem Statement)**:
   - Materials Catalog (`materials.csv`, `materials.json`)
   - Fair Price Intelligence (`prices.csv`, `prices.json`)
   - Authorized Recycler Registry (`recyclers.csv`, `recyclers.json`)
   - Operational Transactions (`transactions.csv`, `transactions.json`)
   - End-to-End Traceability (`traceability.csv`, `traceability.json`)
   - Privacy-First Collector Profiles (`collectors.csv`, `collectors.json`)

2. **AI/ML & Field Training Datasets**:
   - Seeded CPCB EPR Portal Recycler Registry (`cpcb_recycler_registry.csv`, `cpcb_recycler_registry.json`)
   - 12-Month Historical Price Trends (`price_trends_historical.csv`, `price_intelligence.json`)
   - Primary Field Scrap Yard Photo Manifest (`field_scrap_manifest.csv`)
   - In-App Confirmed Label Data Flywheel (`confirmed_labels.csv`, `flywheel_logs.jsonl`)
   - Vision Training & Benchmark Dataset (`data.yaml`, `classes.txt`, annotated YOLO images & labels)
   - Genuine Field E-Waste Photography (`giz_ewaste_samples/` sourced from GIZ E-Waste-Database, CC-BY-4.0)

---

## 2. Master Dataset Catalog

| Dataset Identifier | Domain | Records | Primary File Formats | Source / Provenance | Data Honesty Tag | Primary Consumer |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `DS_OPERATIONAL_MATERIALS` | Operational | 108 items | CSV, JSON, SQL | Field scrap catalog + JNARDDC benchmarks | `field` / `standard` | Android Room DB, Valuation engine |
| `DS_OPERATIONAL_PRICES` | Operational | 192 rates | CSV, JSON, SQL | Field survey quotes + Recycler rate sheets | `field`, `recycler`, `synthetic` | Spoken price board, Net-earning optimizer |
| `DS_OPERATIONAL_RECYCLERS` | Operational | 8 facilities | CSV, JSON, SQL | MPCB / CPCB official registry (Maharashtra) | `official_registry` | Recycler ranking engine & portal |
| `DS_OPERATIONAL_TX` | Operational | 119 lots | CSV, JSON, SQL | Platform lot transaction cycle | `operational_log` | Flask REST API, Ledger module |
| `DS_OPERATIONAL_TRACE` | Operational | 119 records | CSV, JSON, SQL | Tamper-evident SHA-256 digital handovers | `verifiable_receipt` | Traceability audit, Recycler receipt |
| `DS_OPERATIONAL_COLLECTORS`| Operational | 40 profiles | CSV, JSON, SQL | Informal collector profiles (Zero PII) | `field_profile` | Collector offline app, Earnings ledger |
| `DS_OPERATIONAL_AUDIO_PROMPTS`| Operational | 28 prompts | CSV, JSON | Vernacular audio guidance (Marathi/Hindi) | `vernacular_audio` | Android `res/raw/` audio player |
| `DS_AIML_CPCB_REGISTRY` | AI/ML & Gov | 10 facilities | CSV, JSON | CPCB E-Waste EPR Management Portal | `official_registry` | Verification filter, EPR compliance |
| `DS_AIML_PRICE_TRENDS` | AI/ML Models | 360 points | CSV, JSON | 15-month aggregated market movement | `field`, `recycler`, `synthetic` | Moving-average trend detection |
| `DS_AIML_DATA_FLYWHEEL` | AI/ML Models | 84 logs | CSV, JSON, JSONL | Collector icon-grid feedback vs TFLite | `in_app_feedback` | Active learning retraining pipeline |
| `DS_AIML_FIELD_MANIFEST` | Field Research | 112 photos | CSV, JSON | Scrap yard photo collection manifest | `field_survey` | Computer vision training & test bench |
| `DS_AIML_VISION_BENCHMARK` | Vision (YOLO) | 56 sets | Images + Labels | 8-class YOLOv8 / TFLite format | `benchmark` | On-device TFLite material classifier |
| `DS_AIML_GIZ_FIELD_IMAGES` | Vision (Field) | 12+ images | 800px JPEGs | GIZ E-Waste-Database (Hugging Face) | `real_field_data` | Visual model robustness & domain transfer |
| `DS_AIML_MOBILE_WEIGHTS` | Mobile AI | 8 classes | .pt, .json, .txt | PyTorch Mobile & TFLite metadata | `trained_weights` | Android CameraX material classifier |

---

## 3. Detailed Dataset Specifications

### 3.1 Material Dataset (`operational/materials.csv`, `materials.json`)
- **Purpose**: Defines standard scrap classifications, physical weight ranges, hazard indicators, and base valuations.
- **The 8 Standard E-Waste Classes**:
  1. `CAT_CRT`: Cathode Ray Tube monitors and televisions. High hazard (lead/funnel glass).
  2. `CAT_LCD_LED`: LCD and LED monitors, TV panels, and laptop screens. Medium hazard (mercury CCFL).
  3. `CAT_PCB`: Printed Circuit Boards (high-grade motherboard, telecom, PSU, brown board). Medium hazard.
  4. `CAT_CABLES`: Insulated copper wiring, flexible house wires, appliance cords. Low hazard.
  5. `CAT_BATTERY`: Lead-Acid inverter/UPS batteries, Li-Ion smartphone and laptop packs. High hazard (acid, fire).
  6. `CAT_MOTORS`: Compressor motors, ceiling fan stators, hard drive neodymium magnets. Low hazard.
  7. `CAT_PLASTICS`: Flame-retardant ABS and HIPS monitor and appliance casings. Low hazard.
  8. `CAT_OTHER`: Mixed electronic appliances, transformers, keyboards, chargers. Low hazard.
- **Key Schema Attributes**:
  - `material_id`: Unique identifier (`MAT_0001` to `MAT_0108`)
  - `category_id`: Foreign key to `material_categories`
  - `category_name_en`, `category_name_mr`, `category_name_hi`: Multilingual representations (Devanagari script)
  - `sub_category`: Descriptive scrap type (e.g. *High-Grade Motherboard (PC / Server)*)
  - `condition`: `INTACT`, `DAMAGED`, `PARTIALLY_STRIPPED`, `SCRAP_BULK`
  - `source_type`: `HOUSEHOLD_COLLECTION`, `INFORMAL_KABADIWALA`, `COMMERCIAL_OFFICE`, `LOCAL_AGGREGATOR`
  - `hazard_level`: `LOW`, `MEDIUM`, `HIGH`
  - `estimated_value_per_kg`: Floating point rate in INR

### 3.2 Fair Price Dataset (`operational/prices.csv`, `prices.json`)
- **Purpose**: Feeds the offline cached price board with spoken price trends and recycler buying offers.
- **Geographic Coverage**: Key scrap aggregation hubs in Maharashtra (Dharavi, Kurla, TTC Mahape, Wagle Estate Thane, Bhosari Pune, Sinnar Nashik, Butibori Nagpur).
- **Data Honesty Tagging**:
  - `field`: Real prices gathered during visits to scrap dealers and kabadiwalas.
  - `recycler`: Official offered rates from authorized recycling facilities.
  - `synthetic`: Controlled synthetic variations clearly tagged to demonstrate multi-month trend charts.

### 3.3 Authorized Recycler Dataset (`operational/recyclers.csv`, `recyclers.json`)
- **Purpose**: Powers recycler ranking, distance calculation, pickup scheduling, and lot allocation.
- **Featured Authorized Entities**:
  1. *Eco Recycling Limited (Ecoreco)* — Vasai East, Palghar (31,200 MTA)
  2. *E-Incarnation Recycling Pvt Ltd* — Sinnar MIDC, Nashik (12,500 MTA)
  3. *Attero Recycling Facility Hub* — TTC Mahape, Navi Mumbai (18,000 MTA)
  4. *Recyclekaro (Envirocreation)* — Taloja MIDC, Panvel (15,000 MTA)
  5. *Eco-Centric Remakers Pvt Ltd* — Marol MIDC, Andheri East (9,800 MTA)
  6. *Green Sense Technologies* — Bhosari MIDC, Pune (8,400 MTA)
  7. *Vidarbha E-Waste Clean Solution* — Butibori MIDC, Nagpur (6,200 MTA)
  8. *Thane Aggregator & Pre-Dismantler Hub* — Wagle Estate, Thane (5,500 MTA)
- **Key Attributes**: Registration numbers conforming to CPCB EPR portal standards, GPS coordinates, operational capacities, minimum lot thresholds, and pickup availability flags.

### 3.4 Operational Transactions (`operational/transactions.csv`, `transactions.json`)
- **Purpose**: Maintains state machine history for e-waste lots from initial photo capture to confirmed payment.
- **Lifecycle States**: `DRAFT` ➔ `ESTIMATED` ➔ `MATCHED` ➔ `HANDED_OVER` ➔ `CONFIRMED` ➔ `PAID` (or `DISPUTED`).
- **Payment Modes**: Explicitly supports `PAID_CASH` (cash by default for informal workers) and `PAID_UPI`.

### 3.5 Traceability Dataset (`operational/traceability.csv`, `traceability.json`)
- **Purpose**: Provides a verifiable receipt and digital chain of custody.
- **Tamper-Evidence Architecture**:
  - `photo_sha256`: Cryptographic digest of the scrap lot photo taken at collection.
  - `record_hash_sha256`: SHA-256 hash computed over `lot_id|short_code|weight_at_handover|timestamp|handover_ref` ensuring lot integrity cannot be altered post-handover.
  - `recycler_confirmation`: `CONFIRMED`, `WEIGHT_MISMATCH_RESOLVED`.
  - `subsequent_transaction_status`: `ACCEPTED_FOR_DISMANTLING`, `EPR_CREDIT_ISSUED`.

### 3.6 Privacy-First Collector Profiles (`operational/collectors.csv`, `collectors.json`)
- **Purpose**: Powers offline authentication, earnings ledger, and localized vernacular audio settings.
- **Privacy Design**:
  - Strict compliance with problem statement constraints: **Zero personal identifying data**.
  - No Aadhaar numbers, no residential addresses, no mandatory personal names.
  - Profiling is restricted to: `collector_id`, `preferred_language` (`mr` or `hi`), `operating_area` (Ward/Zone level only), transaction totals, and cash ledger balances.

---

## 4. AI/ML Training Datasets

### 4.1 Vision Training & Benchmark Dataset (`ai_ml/vision/`)
- **Format**: YOLOv8 and TensorFlow Lite compatible annotations.
- **Files**:
  - `data.yaml`: Dataset configuration linking to train, val, and test splits with English, Marathi, and Hindi class labels.
  - `classes.txt`: Ordered list of the 8 target classes.
  - `images/train/`, `images/val/`: Standardized 640x640 training imagery.
  - `labels/train/`, `labels/val/`: Normalized bounding boxes (`<class> <x_center> <y_center> <width> <height>`).
  - `giz_ewaste_samples/`: High-resolution real-world scrap photographs downloaded from the GIZ E-Waste repository (CC-BY-4.0).

### 4.2 Data Flywheel In-App Confirmed Labels (`ai_ml/data_flywheel/`)
- **Concept**: When a collector takes a photo, on-device TFLite suggests a material class. If the confidence is low or incorrect, the collector taps the correct icon in the vernacular grid.
- **Files**: `confirmed_labels.csv`, `flywheel_logs.jsonl`.
- **Fields**: `log_id`, `image_hash`, `tflite_predicted_category`, `tflite_confidence_score`, `collector_confirmed_category`, `feedback_action` (`ACCEPTED_AS_SUGGESTED` vs `CORRECTED_BY_COLLECTOR`), `timestamp_utc`.

### 4.3 12-Month Historical Price Trends (`ai_ml/price_trends/`)
- **Files**: `price_trends_historical.csv`, `price_intelligence.json`.
- **Characteristics**: Monthly time-series data capturing price movements across copper, high-grade printed circuits, inverter batteries, and polymers, enabling moving-average trend arrows on the Android price board.

---

## 5. Scripts & Automation

All automated utilities are stored in `datasets/scripts/`:

1. **`generate_all_datasets.py`**:
   Regenerates all operational and AI/ML datasets, DDL scripts, and seed files.
   ```bash
   python datasets/scripts/generate_all_datasets.py
   ```

2. **`download_vision_datasets.py`**:
   Downloads real field e-waste images from the Hugging Face GIZ repository and supports downloading Roboflow Universe datasets using an API key.
   ```bash
   # Download GIZ real field photos and generate YOLO benchmark data:
   python datasets/scripts/download_vision_datasets.py --giz-count 20

   # Download from Roboflow Universe (optional):
   python datasets/scripts/download_vision_datasets.py --roboflow --workspace electronic-waste --project electronic-waste-dataset --api-key YOUR_KEY
   ```

3. **`validate_datasets.py`**:
   Asserts foreign key integrity, non-null constraints, timestamp formats, and data honesty tags across all CSVs and JSONs.
   ```bash
   python datasets/scripts/validate_datasets.py
   ```

4. **`seed_database.py`**:
   Applies `schema.sql` and populates the SQLite database (`database/ecobridge.db`), executing test queries to verify live operation.
   ```bash
   python datasets/scripts/seed_database.py
   ```

---

## 6. Ethical Governance & Data Honesty Statement

1. **Synthetic vs Real Data**: Every price observation in `prices.csv` and `price_trends_historical.csv` is explicitly tagged with `source_type: field | recycler | synthetic`. At no point is synthetic data disguised as real field research.
2. **Legal Positioning**: The traceability dataset represents a verifiable receipt and audit trail for voluntary market transactions. It is **not** claimed as a legal hazardous waste transport manifest under regulatory statutes.
3. **Informal Worker Protection**: Collector privacy is guarded by design to prevent predatory surveillance or informal sector harassment.
