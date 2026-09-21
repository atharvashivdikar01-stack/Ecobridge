"""
seed_database.py
Initializes the SQLite database 'ecobridge.db' with the complete schema and seeds it from
the operational CSV and JSON datasets. Runs verification queries to demonstrate end-to-end functionality.
"""

import os
import sqlite3
import json
import csv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
OPERATIONAL_DIR = BASE_DIR / "operational"
DB_SEEDS_DIR = BASE_DIR / "database_seeds"
DB_PATH = BASE_DIR.parent / "database" / "ecobridge.db"

def init_and_seed_db():
    print(f"[*] Initializing database at: {DB_PATH}")
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Execute Schema DDL
    schema_file = DB_SEEDS_DIR / "schema.sql"
    with open(schema_file, "r", encoding="utf-8") as f:
        schema_sql = f.read()
    cursor.executescript(schema_sql)
    print("  [OK] Applied database schema DDL.")

    # 2. Seed Material Categories
    categories = [
        ("CAT_CRT", "CRT Monitors & TVs", "सीआरटी मॉनिटर आणि टीव्ही", "सीआरटी मॉनिटर और टीवी", "icon_crt", "HIGH", 14.0, 22.0, "kg"),
        ("CAT_LCD_LED", "LCD / LED Panels", "एलसीडी / एलईडी स्क्रीन आणि पॅनेल्स", "एलसीडी / एलईडी स्क्रीन और पैनल", "icon_lcd", "MEDIUM", 38.0, 55.0, "kg"),
        ("CAT_PCB", "Printed Circuit Boards (PCBs)", "सर्किट बोर्ड / पीसीबी (मदरबोर्ड, हिरवे बोर्ड)", "सर्किट बोर्ड / पीसीबी (मदरबोर्ड, ग्रीन बोर्ड)", "icon_pcb", "MEDIUM", 180.0, 260.0, "kg"),
        ("CAT_CABLES", "Copper Cables & Wires", "तांब्याची वायर आणि केबल्स", "तांबे के तार और केबल", "icon_cable", "LOW", 240.0, 320.0, "kg"),
        ("CAT_BATTERY", "Batteries (Lead-Acid & Li-Ion)", "बॅटरी (लेड-अ‍ॅसिड इन्व्हर्टर / लिथियम मोबाईल)", "बैटरी (लेड-एसिड इन्वर्टर / लिथियम मोबाइल)", "icon_battery", "HIGH", 75.0, 105.0, "kg"),
        ("CAT_MOTORS", "Motors & Magnet Assemblies", "मोटर्स, फॅन कॉइल आणि चुंबक", "मोटर, पंखा कॉइल और चुंबक", "icon_motor", "LOW", 35.0, 48.0, "kg"),
        ("CAT_PLASTICS", "Mixed E-Waste Plastics (ABS / HIPS)", "मिश्रित ई-कचरा प्लास्टिक (कॅबिनेट, बॉडी)", "मिश्रित ई-कचरा प्लास्टिक (बॉडी, कैबिनेट)", "icon_plastic", "LOW", 18.0, 28.0, "kg"),
        ("CAT_OTHER", "Other Electronic Scrap", "इतर इलेक्ट्रॉनिक भंगार (किबोर्ड, ट्रान्सफॉर्मर)", "अन्य इलेक्ट्रॉनिक कबाड़ (कीबोर्ड, चार्जर)", "icon_other", "LOW", 20.0, 32.0, "kg")
    ]
    cursor.executemany("""
        INSERT OR REPLACE INTO material_categories 
        (category_id, name_en, name_mr, name_hi, icon, hazard_level, default_buy_rate, default_sell_rate, unit)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, categories)

    # 3. Seed Collectors
    with open(OPERATIONAL_DIR / "collectors.json", "r", encoding="utf-8") as f:
        collectors = json.load(f)
    cursor.executemany("""
        INSERT OR REPLACE INTO collectors
        (collector_id, preferred_language, operating_area, transaction_count, total_weight_kg, total_cash_earned_inr, pending_dues_inr, created_at)
        VALUES (:collector_id, :preferred_language, :operating_area, :transaction_count, :total_weight_kg, :total_cash_earned_inr, :pending_dues_inr, :created_at)
    """, collectors)

    # 4. Seed Materials
    with open(OPERATIONAL_DIR / "materials.json", "r", encoding="utf-8") as f:
        materials = json.load(f)
    cursor.executemany("""
        INSERT OR REPLACE INTO materials
        (material_id, category_id, sub_category, material_description, image_reference, approximate_weight_kg, condition, source_type, hazard_level, estimated_value_per_kg, unit)
        VALUES (:material_id, :category_id, :sub_category, :material_description, :image_reference, :approximate_weight_kg, :condition, :source_type, :hazard_level, :estimated_value_per_kg, :unit)
    """, materials)

    # 5. Seed Recyclers
    with open(OPERATIONAL_DIR / "recyclers.json", "r", encoding="utf-8") as f:
        recyclers = json.load(f)
    for r in recyclers:
        r_copy = dict(r)
        r_copy["accepted_categories"] = json.dumps(r_copy["accepted_categories"])
        cursor.execute("""
            INSERT OR REPLACE INTO recyclers
            (recycler_id, name, address, lat, lng, contact, email, registration_no, authorization_status, capacity_mta, service_area, pickup_available, min_lot_weight_kg, accepted_categories)
            VALUES (:recycler_id, :name, :address, :lat, :lng, :contact, :email, :registration_no, :authorization_status, :capacity_mta, :service_area, :pickup_available, :min_lot_weight_kg, :accepted_categories)
        """, r_copy)

    # 6. Seed Prices
    with open(OPERATIONAL_DIR / "prices.json", "r", encoding="utf-8") as f:
        prices = json.load(f)
    cursor.executemany("""
        INSERT OR REPLACE INTO prices
        (price_id, category_id, sub_category, location, recorded_at, prevailing_buying_price, selling_quoted_price, unit_of_measurement, market_range_min, market_range_max, recycler_id, source_type)
        VALUES (:price_id, :category_id, :sub_category, :location, :recorded_at, :prevailing_buying_price, :selling_quoted_price, :unit_of_measurement, :market_range_min, :market_range_max, :recycler_id, :source_type)
    """, prices)

    # 7. Seed Transactions
    with open(OPERATIONAL_DIR / "transactions.json", "r", encoding="utf-8") as f:
        transactions = json.load(f)
    cursor.executemany("""
        INSERT OR REPLACE INTO transactions
        (unique_lot_id, short_code, collector_id, category_id, material_sub_category, quantity_weight_kg, quoted_price_per_kg, final_sale_value_inr, recycler_id, collection_location, handover_location, date_time, payment_status, transaction_status)
        VALUES (:unique_lot_id, :short_code, :collector_id, :category_id, :material_sub_category, :quantity_weight_kg, :quoted_price_per_kg, :final_sale_value_inr, :recycler_id, :collection_location, :handover_location, :date_time, :payment_status, :transaction_status)
    """, transactions)

    # 8. Seed Traceability
    with open(OPERATIONAL_DIR / "traceability.json", "r", encoding="utf-8") as f:
        traceability = json.load(f)
    cursor.executemany("""
        INSERT OR REPLACE INTO traceability
        (unique_lot_id, short_code, photograph_ref, photo_sha256, weight_at_collection_kg, weight_at_handover_kg, timestamp_utc, gps_latitude, gps_longitude, handover_reference_number, recycler_confirmation, record_hash_sha256, subsequent_transaction_status)
        VALUES (:unique_lot_id, :short_code, :photograph_ref, :photo_sha256, :weight_at_collection_kg, :weight_at_handover_kg, :timestamp_utc, :gps_latitude, :gps_longitude, :handover_reference_number, :recycler_confirmation, :record_hash_sha256, :subsequent_transaction_status)
    """, traceability)

    conn.commit()
    print("  [OK] Successfully ingested all datasets into SQLite database!")

    # 9. Verification queries
    print("\n--- Running Verification Queries ---")
    
    # Query 1: Category counts
    cursor.execute("SELECT COUNT(*) FROM material_categories")
    print(f"  * Categories count: {cursor.fetchone()[0]}")

    # Query 2: Total transactions & total weight
    cursor.execute("SELECT COUNT(*), SUM(quantity_weight_kg), SUM(final_sale_value_inr) FROM transactions")
    tx_count, total_wt, total_val = cursor.fetchone()
    print(f"  * Transactions: {tx_count} lots, Total Weight: {total_wt:.1f} kg, Total Value: INR {total_val:,.2f}")

    # Query 3: Recyclers accepting PCBs in Maharashtra
    cursor.execute("SELECT name, capacity_mta, registration_no FROM recyclers WHERE accepted_categories LIKE '%CAT_PCB%' LIMIT 3")
    print("  * Sample Authorized Recyclers (PCBs):")
    for row in cursor.fetchall():
        print(f"      - {row[0]} (Cap: {row[1]} MTA, Reg: {row[2]})")

    # Query 4: Traceability check with tamper-evident record hash
    cursor.execute("SELECT unique_lot_id, short_code, weight_at_handover_kg, record_hash_sha256 FROM traceability LIMIT 1")
    t_lot, t_code, t_wt, t_hash = cursor.fetchone()
    print(f"  * Sample Traceability Hash: Lot {t_lot} (Code: {t_code}) -> Weight: {t_wt}kg | SHA-256: {t_hash[:16]}...")

    conn.close()
    print("\n[SUCCESS] SQLite Database fully seeded and operational!")

if __name__ == "__main__":
    init_and_seed_db()
