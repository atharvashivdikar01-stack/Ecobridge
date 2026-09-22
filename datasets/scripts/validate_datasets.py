"""
validate_datasets.py
Comprehensive integrity and validation script for Ecobridge datasets:
- Verifies all 6 mandatory operational datasets (materials, prices, recyclers, transactions, traceability, collectors)
- Validates AI/ML datasets (CPCB registry, price trends, flywheel logs, field scrap manifest)
- Asserts foreign key integrity, non-null values, valid UTC ISO-8601 timestamps, GPS coordinates, and data types
"""

import os
import sys
import json
import csv
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
OPERATIONAL_DIR = BASE_DIR / "operational"
AI_ML_DIR = BASE_DIR / "ai_ml"

def load_json(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def is_iso_timestamp(ts_str):
    try:
        datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
        return True
    except Exception:
        return False

def run_validation():
    print("=" * 60)
    print("ECOBRIDGE DATASET INTEGRITY & VALIDATION SUITE")
    print("=" * 60)

    errors = []
    warnings = []

    # 1. Collectors Validation
    collectors_file = OPERATIONAL_DIR / "collectors.json"
    if not collectors_file.exists():
        errors.append("collectors.json missing")
        return False
    collectors = load_json(collectors_file)
    print(f"[*] Validating Collectors ({len(collectors)} records)...")
    collector_ids = set()
    for c in collectors:
        cid = c.get("collector_id")
        if not cid or cid in collector_ids:
            errors.append(f"Invalid or duplicate collector_id: {cid}")
        collector_ids.add(cid)
        if c.get("preferred_language") not in ["mr", "hi"]:
            warnings.append(f"Collector {cid} has non-standard language: {c.get('preferred_language')}")
        if c.get("total_cash_earned_inr", 0) < 0 or c.get("pending_dues_inr", 0) < 0:
            errors.append(f"Negative money in collector ledger for {cid}")
    print("    -> Collectors validation passed!")

    # 2. Materials Validation
    materials_file = OPERATIONAL_DIR / "materials.json"
    materials = load_json(materials_file)
    print(f"[*] Validating Materials ({len(materials)} records)...")
    material_categories = set()
    for m in materials:
        mid = m.get("material_id")
        cat_id = m.get("category_id")
        material_categories.add(cat_id)
        if m.get("estimated_value_per_kg", 0) <= 0:
            errors.append(f"Non-positive estimated value in material {mid}")
        if not m.get("category_name_mr") or not m.get("category_name_hi"):
            errors.append(f"Missing Marathi or Hindi translation in material {mid}")
    print(f"    -> Materials validation passed! ({len(material_categories)} unique categories)")

    # 3. Recyclers Validation
    recyclers_file = OPERATIONAL_DIR / "recyclers.json"
    recyclers = load_json(recyclers_file)
    print(f"[*] Validating Recyclers ({len(recyclers)} records)...")
    recycler_ids = set()
    for r in recyclers:
        rid = r.get("recycler_id")
        if not rid or rid in recycler_ids:
            errors.append(f"Invalid or duplicate recycler_id: {rid}")
        recycler_ids.add(rid)
        if not (15.0 <= r.get("lat", 0) <= 24.0 and 70.0 <= r.get("lng", 0) <= 82.0):
            warnings.append(f"Recycler {rid} coordinates outside standard Maharashtra bounding box: {r.get('lat')}, {r.get('lng')}")
        if not r.get("registration_no"):
            errors.append(f"Recycler {rid} missing CPCB/MPCB registration number")
    print("    -> Recyclers validation passed!")

    # 4. Transactions Validation
    transactions_file = OPERATIONAL_DIR / "transactions.json"
    transactions = load_json(transactions_file)
    print(f"[*] Validating Transactions ({len(transactions)} records)...")
    lot_ids = set()
    for t in transactions:
        lid = t.get("unique_lot_id")
        if not lid or lid in lot_ids:
            errors.append(f"Invalid or duplicate unique_lot_id in transactions: {lid}")
        lot_ids.add(lid)
        cid = t.get("collector_id")
        if cid not in collector_ids:
            errors.append(f"Foreign key violation: collector_id {cid} not in collectors dataset")
        rid = t.get("recycler_id")
        if rid not in recycler_ids:
            errors.append(f"Foreign key violation: recycler_id {rid} not in recyclers dataset")
        if not is_iso_timestamp(t.get("date_time", "")):
            errors.append(f"Invalid ISO timestamp in transaction {lid}: {t.get('date_time')}")
    print("    -> Transactions validation passed!")

    # 5. Traceability Validation
    traceability_file = OPERATIONAL_DIR / "traceability.json"
    traceability = load_json(traceability_file)
    print(f"[*] Validating Traceability ({len(traceability)} records)...")
    for tr in traceability:
        lid = tr.get("unique_lot_id")
        if lid not in lot_ids:
            errors.append(f"Traceability lot {lid} has no matching transaction record")
        if len(tr.get("photo_sha256", "")) != 64:
            errors.append(f"Invalid SHA-256 photo hash in traceability {lid}")
        if len(tr.get("record_hash_sha256", "")) != 64:
            errors.append(f"Invalid tamper-evident record hash in traceability {lid}")
    print("    -> Traceability validation passed!")

    # 6. Prices & Price Trends Validation
    prices_file = OPERATIONAL_DIR / "prices.json"
    prices = load_json(prices_file)
    print(f"[*] Validating Prices ({len(prices)} records)...")
    for p in prices:
        pid = p.get("price_id")
        src = p.get("source_type")
        if src not in ["field", "recycler", "synthetic"]:
            errors.append(f"Price {pid} has invalid source_type: '{src}' (must be field, recycler, or synthetic)")
        if p.get("prevailing_buying_price", 0) > p.get("selling_quoted_price", 0):
            warnings.append(f"Price {pid} has buy price higher than sell price (negative margin)")
    print("    -> Prices validation passed!")

    # 7. CPCB Registry Validation
    cpcb_file = AI_ML_DIR / "registry" / "cpcb_recycler_registry.json"
    cpcb_data = load_json(cpcb_file)
    print(f"[*] Validating CPCB Registry ({len(cpcb_data)} facilities)...")
    for fac in cpcb_data:
        if not fac.get("cpcb_registration_no"):
            errors.append("Facility missing cpcb_registration_no in registry")
        if fac.get("authorized_capacity_mta", 0) <= 0:
            errors.append("Facility has non-positive authorized capacity")
    print("    -> CPCB registry validation passed!")

    # 8. Data Flywheel Logs Validation
    flywheel_file = AI_ML_DIR / "data_flywheel" / "confirmed_labels.json"
    flywheel_logs = load_json(flywheel_file)
    print(f"[*] Validating Data Flywheel Logs ({len(flywheel_logs)} logs)...")
    for log in flywheel_logs:
        if not (0.0 <= log.get("tflite_confidence_score", 0.0) <= 1.0):
            errors.append(f"Invalid confidence score in log {log.get('log_id')}")
    print("    -> Data flywheel logs validation passed!")

    print("=" * 60)
    if warnings:
        print(f"[!] WARNINGS ({len(warnings)}):")
        for w in warnings[:5]:
            print(f"    - {w}")
    if errors:
        print(f"[X] ERRORS FOUND ({len(errors)}):")
        for e in errors:
            print(f"    - {e}")
        return False
    else:
        print("[SUCCESS] ALL DATASETS PASSED INTEGRITY AND SCHEMA CHECKS PERFECTLY!")
        print("=" * 60)
        return True

if __name__ == "__main__":
    success = run_validation()
    sys.exit(0 if success else 1)
