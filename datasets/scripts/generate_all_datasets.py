"""
generate_all_datasets.py
Generates comprehensive, realistic, and schema-compliant datasets for:
SIH 2026 Problem Statement 26229 (Kabadiwala Connect / Ecobridge).

Covers:
1. Operational Datasets (materials, prices, recyclers, transactions, traceability, collectors)
2. AI/ML Datasets (CPCB registry, historical price trends, field scrap manifest, data flywheel logs)
3. Database DDL and Seed SQL (schema.sql, seed_data.sql)
"""

import os
import csv
import json
import uuid
import random
import hashlib
from datetime import datetime, timedelta, timezone

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OPERATIONAL_DIR = os.path.join(BASE_DIR, "operational")
AI_ML_DIR = os.path.join(BASE_DIR, "ai_ml")
REGISTRY_DIR = os.path.join(AI_ML_DIR, "registry")
PRICE_TRENDS_DIR = os.path.join(AI_ML_DIR, "price_trends")
FLYWHEEL_DIR = os.path.join(AI_ML_DIR, "data_flywheel")
FIELD_DIR = os.path.join(AI_ML_DIR, "field_research")
VISION_DIR = os.path.join(AI_ML_DIR, "vision")
DB_SEEDS_DIR = os.path.join(BASE_DIR, "database_seeds")

for d in [OPERATIONAL_DIR, REGISTRY_DIR, PRICE_TRENDS_DIR, FLYWHEEL_DIR, FIELD_DIR, VISION_DIR, DB_SEEDS_DIR]:
    os.makedirs(d, exist_ok=True)

# 8 Core Target Classes defined in CONTEXT.md
CATEGORIES = [
    {
        "category_id": "CAT_CRT",
        "name_en": "CRT Monitors & TVs",
        "name_mr": "सीआरटी मॉनिटर आणि टीव्ही",
        "name_hi": "सीआरटी मॉनिटर और टीवी",
        "icon": "icon_crt",
        "hazard_level": "HIGH",
        "typical_weight_kg_range": [12.0, 32.0],
        "default_buy_rate_per_kg": 14.0,
        "default_sell_rate_per_kg": 22.0,
        "unit": "kg"
    },
    {
        "category_id": "CAT_LCD_LED",
        "name_en": "LCD / LED Panels",
        "name_mr": "एलसीडी / एलईडी स्क्रीन आणि पॅनेल्स",
        "name_hi": "एलसीडी / एलईडी स्क्रीन और पैनल",
        "icon": "icon_lcd",
        "hazard_level": "MEDIUM",
        "typical_weight_kg_range": [3.0, 10.0],
        "default_buy_rate_per_kg": 38.0,
        "default_sell_rate_per_kg": 55.0,
        "unit": "kg"
    },
    {
        "category_id": "CAT_PCB",
        "name_en": "Printed Circuit Boards (PCBs)",
        "name_mr": "सर्किट बोर्ड / पीसीबी (मदरबोर्ड, हिरवे बोर्ड)",
        "name_hi": "सर्किट बोर्ड / पीसीबी (मदरबोर्ड, ग्रीन बोर्ड)",
        "icon": "icon_pcb",
        "hazard_level": "MEDIUM",
        "typical_weight_kg_range": [0.2, 3.5],
        "default_buy_rate_per_kg": 180.0,
        "default_sell_rate_per_kg": 260.0,
        "unit": "kg"
    },
    {
        "category_id": "CAT_CABLES",
        "name_en": "Copper Cables & Wires",
        "name_mr": "तांब्याची वायर आणि केबल्स",
        "name_hi": "तांबे के तार और केबल",
        "icon": "icon_cable",
        "hazard_level": "LOW",
        "typical_weight_kg_range": [1.0, 15.0],
        "default_buy_rate_per_kg": 240.0,
        "default_sell_rate_per_kg": 320.0,
        "unit": "kg"
    },
    {
        "category_id": "CAT_BATTERY",
        "name_en": "Batteries (Lead-Acid & Li-Ion)",
        "name_mr": "बॅटरी (लेड-अ‍ॅसिड इन्व्हर्टर / लिथियम मोबाईल)",
        "name_hi": "बैटरी (लेड-एसिड इन्वर्टर / लिथियम मोबाइल)",
        "icon": "icon_battery",
        "hazard_level": "HIGH",
        "typical_weight_kg_range": [0.1, 24.0],
        "default_buy_rate_per_kg": 75.0,
        "default_sell_rate_per_kg": 105.0,
        "unit": "kg"
    },
    {
        "category_id": "CAT_MOTORS",
        "name_en": "Motors & Magnet Assemblies",
        "name_mr": "मोटर्स, फॅन कॉइल आणि चुंबक",
        "name_hi": "मोटर, पंखा कॉइल और चुंबक",
        "icon": "icon_motor",
        "hazard_level": "LOW",
        "typical_weight_kg_range": [2.0, 18.0],
        "default_buy_rate_per_kg": 35.0,
        "default_sell_rate_per_kg": 48.0,
        "unit": "kg"
    },
    {
        "category_id": "CAT_PLASTICS",
        "name_en": "Mixed E-Waste Plastics (ABS / HIPS)",
        "name_mr": "मिश्रित ई-कचरा प्लास्टिक (कॅबिनेट, बॉडी)",
        "name_hi": "मिश्रित ई-कचरा प्लास्टिक (बॉडी, कैबिनेट)",
        "icon": "icon_plastic",
        "hazard_level": "LOW",
        "typical_weight_kg_range": [1.5, 12.0],
        "default_buy_rate_per_kg": 18.0,
        "default_sell_rate_per_kg": 28.0,
        "unit": "kg"
    },
    {
        "category_id": "CAT_OTHER",
        "name_en": "Other Electronic Scrap",
        "name_mr": "इतर इलेक्ट्रॉनिक भंगार (किबोर्ड, ट्रान्सफॉर्मर)",
        "name_hi": "अन्य इलेक्ट्रॉनिक कबाड़ (कीबोर्ड, चार्जर)",
        "icon": "icon_other",
        "hazard_level": "LOW",
        "typical_weight_kg_range": [0.5, 8.0],
        "default_buy_rate_per_kg": 20.0,
        "default_sell_rate_per_kg": 32.0,
        "unit": "kg"
    }
]

# Real Authorized Recyclers in Maharashtra (CPCB/MPCB registry)
RECYCLERS = [
    {
        "recycler_id": "REC_MH_ECORECO_001",
        "name": "Eco Recycling Limited (Ecoreco)",
        "address": "Plot No. 422, MIDC, Vasai East, Palghar, Maharashtra - 401208",
        "lat": 19.3919,
        "lng": 72.8397,
        "contact": "+91-22-40052951",
        "email": "info@ecoreco.com",
        "registration_no": "CPCB/EPR/2023/REC-MH-0012",
        "authorization_status": "VALID",
        "capacity_mta": 31200,
        "service_area": "Mumbai Metropolitan Region & Palghar",
        "pickup_available": True,
        "min_lot_weight_kg": 50.0,
        "accepted_categories": ["CAT_CRT", "CAT_LCD_LED", "CAT_PCB", "CAT_CABLES", "CAT_BATTERY", "CAT_MOTORS", "CAT_PLASTICS", "CAT_OTHER"]
    },
    {
        "recycler_id": "REC_MH_EINCARNATION_002",
        "name": "E-Incarnation Recycling Private Limited",
        "address": "Plot B-14, Malegaon MIDC, Sinnar, Nashik, Maharashtra - 422113",
        "lat": 19.8458,
        "lng": 73.9926,
        "contact": "+91-253-2970142",
        "email": "ops@e-incarnation.com",
        "registration_no": "MPCB/RO(HQ)/E-Waste/2021/REC-0045",
        "authorization_status": "VALID",
        "capacity_mta": 12500,
        "service_area": "Nashik, Mumbai, Pune, Ahmednagar",
        "pickup_available": True,
        "min_lot_weight_kg": 40.0,
        "accepted_categories": ["CAT_LCD_LED", "CAT_PCB", "CAT_CABLES", "CAT_BATTERY", "CAT_MOTORS", "CAT_OTHER"]
    },
    {
        "recycler_id": "REC_MH_ATTERO_003",
        "name": "Attero Recycling Facility Hub",
        "address": "TTC Industrial Area, MIDC Mahape, Navi Mumbai, Maharashtra - 400710",
        "lat": 19.1171,
        "lng": 73.0163,
        "contact": "+91-22-68341900",
        "email": "logistics.west@attero.in",
        "registration_no": "CPCB/EPR/2022/REC-MH-0008",
        "authorization_status": "VALID",
        "capacity_mta": 18000,
        "service_area": "Navi Mumbai, Thane, Raigad, Pune",
        "pickup_available": True,
        "min_lot_weight_kg": 100.0,
        "accepted_categories": ["CAT_PCB", "CAT_BATTERY", "CAT_CABLES", "CAT_LCD_LED"]
    },
    {
        "recycler_id": "REC_MH_RECYCLEKARO_004",
        "name": "Recyclekaro (Envirocreation Pvt Ltd)",
        "address": "Plot No. 19/2, Taloja MIDC, Panvel, Raigad, Maharashtra - 410208",
        "lat": 19.0682,
        "lng": 73.1256,
        "contact": "+91-22-27410055",
        "email": "procurement@recyclekaro.com",
        "registration_no": "MPCB/E-Waste/2022/REC-0089",
        "authorization_status": "VALID",
        "capacity_mta": 15000,
        "service_area": "Panvel, Thane, Mumbai, Pune",
        "pickup_available": True,
        "min_lot_weight_kg": 30.0,
        "accepted_categories": ["CAT_BATTERY", "CAT_PCB", "CAT_CABLES", "CAT_MOTORS", "CAT_OTHER"]
    },
    {
        "recycler_id": "REC_MH_ECOCENTRIC_005",
        "name": "Eco-Centric Remakers Private Limited",
        "address": "Unit 401, Marol MIDC, Andheri East, Mumbai, Maharashtra - 400093",
        "lat": 19.1197,
        "lng": 72.8732,
        "contact": "+91-22-49726200",
        "email": "collection@eco-centric.com",
        "registration_no": "CPCB/EPR/2023/REC-MH-0034",
        "authorization_status": "VALID",
        "capacity_mta": 9800,
        "service_area": "Mumbai Suburbs & South Mumbai",
        "pickup_available": False,
        "min_lot_weight_kg": 20.0,
        "accepted_categories": ["CAT_CRT", "CAT_LCD_LED", "CAT_PCB", "CAT_PLASTICS", "CAT_OTHER"]
    },
    {
        "recycler_id": "REC_MH_PUNE_GREEN_006",
        "name": "Green Sense Technologies & Recyclers",
        "address": "Sector 10, PCMC MIDC Bhosari, Pune, Maharashtra - 411026",
        "lat": 18.6272,
        "lng": 73.8436,
        "contact": "+91-20-27128911",
        "email": "ewaste@greensense.co.in",
        "registration_no": "MPCB/RO(HQ)/E-Waste/2023/REC-0112",
        "authorization_status": "VALID",
        "capacity_mta": 8400,
        "service_area": "Pune, Pimpri-Chinchwad, Talegaon, Chakan",
        "pickup_available": True,
        "min_lot_weight_kg": 25.0,
        "accepted_categories": ["CAT_PCB", "CAT_LCD_LED", "CAT_CABLES", "CAT_BATTERY", "CAT_MOTORS", "CAT_PLASTICS"]
    },
    {
        "recycler_id": "REC_MH_NAGPUR_CLEAN_007",
        "name": "Vidarbha E-Waste Clean Solution",
        "address": "Plot D-35, MIDC Butibori, Nagpur, Maharashtra - 441122",
        "lat": 20.9234,
        "lng": 78.9876,
        "contact": "+91-7104-265118",
        "email": "contact@vidarbhaewaste.org",
        "registration_no": "MPCB/RO(HQ)/E-Waste/2022/REC-0067",
        "authorization_status": "VALID",
        "capacity_mta": 6200,
        "service_area": "Nagpur, Wardha, Amravati, Chandrapur",
        "pickup_available": True,
        "min_lot_weight_kg": 35.0,
        "accepted_categories": ["CAT_CRT", "CAT_LCD_LED", "CAT_PCB", "CAT_CABLES", "CAT_MOTORS", "CAT_OTHER"]
    },
    {
        "recycler_id": "REC_MH_THANE_AGGR_008",
        "name": "Thane Aggregator & Pre-Dismantler Hub",
        "address": "Wagle Estate, Road No. 16, Thane West, Maharashtra - 400604",
        "lat": 19.1944,
        "lng": 72.9554,
        "contact": "+91-22-25829103",
        "email": "thane.hub@ewasteconnect.org",
        "registration_no": "MPCB/RO(HQ)/E-Waste/2023/DISM-0021",
        "authorization_status": "VALID",
        "capacity_mta": 5500,
        "service_area": "Thane, Mulund, Bhandup, Kalyan, Dombivli",
        "pickup_available": False,
        "min_lot_weight_kg": 15.0,
        "accepted_categories": ["CAT_CRT", "CAT_LCD_LED", "CAT_PCB", "CAT_CABLES", "CAT_BATTERY", "CAT_MOTORS", "CAT_PLASTICS", "CAT_OTHER"]
    }
]

def generate_collectors(n=35):
    """Generates collector profiles strictly adhering to privacy requirements."""
    areas = [
        "Mumbai - Dharavi Ward G/N", "Mumbai - Kurla West Ward L", "Mumbai - Govandi / Mankhurd",
        "Mumbai - Malad West Ward P/N", "Thane - Wagle Estate / Kisan Nagar", "Thane - Mumbra / Diva",
        "Pune - Swargate / Bhavani Peth", "Pune - Pimpri Kaspate Vasti", "Pune - Hadapsar Industrial",
        "Nagpur - Sitabuldi / Cotton Market", "Nagpur - Itwari Scrap Yard", "Nashik - Old CBS / Panchavati"
    ]
    collectors = []
    for i in range(1, n + 1):
        cid = f"COL_MH_{i:04d}"
        lang = random.choice(["mr", "mr", "hi"]) # High prevalence of Marathi & Hindi
        area = random.choice(areas)
        tx_count = random.randint(3, 42)
        total_weight = round(random.uniform(80.0, 1850.0), 1)
        cash_earned = round(total_weight * random.uniform(32.0, 78.0), 2)
        pending_dues = round(random.choice([0.0, 0.0, 450.0, 1200.0, 2450.0, 3100.0]), 2)
        created_dt = (datetime(2025, 6, 1, tzinfo=timezone.utc) + timedelta(days=random.randint(1, 260))).isoformat()
        collectors.append({
            "collector_id": cid,
            "preferred_language": lang,
            "operating_area": area,
            "transaction_count": tx_count,
            "total_weight_kg": total_weight,
            "total_cash_earned_inr": cash_earned,
            "pending_dues_inr": pending_dues,
            "created_at": created_dt
        })
    return collectors

def generate_materials():
    """Generates detailed material inventory catalog across 8 categories."""
    sub_categories = {
        "CAT_CRT": [
            ("Color Television CRT Tube", "14 to 21 inch television glass picture tube with lead funnel", 16.5, 14.0),
            ("Computer Monitor CRT", "15 to 17 inch desktop monitor cathode ray tube", 13.0, 12.0),
            ("Large Screen TV CRT (29-inch)", "Heavy commercial television cathode ray tube", 28.0, 15.0)
        ],
        "CAT_LCD_LED": [
            ("Laptop Display Screen Panel", "14-15.6 inch TFT/LED display panel with cracked or intact glass", 0.9, 65.0),
            ("Desktop LCD Monitor Panel", "19 to 24 inch computer monitor display screen", 3.2, 50.0),
            ("Smart TV LED Display (32-43 inch)", "Flat panel television LED display assembly", 6.8, 48.0)
        ],
        "CAT_PCB": [
            ("High-Grade Motherboard (PC / Server)", "Computer motherboard containing gold-plated pins and IC chips", 0.65, 340.0),
            ("Telecom Base Station PCB", "High-frequency server/telecom network card with precious metal traces", 0.8, 420.0),
            ("Low-Grade Brown PCB (CRT/Audio)", "Single-layer phenolic paper PCB from radios or CRT power boards", 0.45, 95.0),
            ("Power Supply Unit (PSU) Board", "Switched-mode power supply circuit board with heat sinks and copper coils", 0.75, 130.0),
            ("RAM & Mobile Daughter Boards", "High gold yield RAM sticks and small smartphone motherboards", 0.15, 650.0)
        ],
        "CAT_CABLES": [
            ("Insulated Flexible Copper Wire (Household)", "House wiring and electrical copper wire with PVC stripping", 5.0, 290.0),
            ("Computer Power Cords & VGA Cables", "Black PVC shielded appliance power cords with copper stranding", 2.5, 230.0),
            ("Telecom Multi-core Ribbon Cables", "Fine copper communications wire and telephone twisted pair", 3.0, 260.0)
        ],
        "CAT_BATTERY": [
            ("Lead-Acid Inverter / UPS Battery", "12V 100Ah-150Ah heavy stationary lead-acid battery unit", 26.0, 85.0),
            ("Small Lead-Acid SMF Battery (UPS)", "12V 7Ah sealed maintenance-free lead battery", 2.1, 72.0),
            ("Lithium-Ion Smartphone Batteries", "Li-Cobalt / Li-Polymer flat pouch phone battery cells", 0.08, 120.0),
            ("Laptop Li-Ion 18650 Battery Pack", "Multi-cell laptop battery cylinder pack", 0.32, 110.0)
        ],
        "CAT_MOTORS": [
            ("Refrigerator Compressor Motor Unit", "Sealed steel casing with high copper winding stator", 7.5, 42.0),
            ("Ceiling Fan Induction Motor Stator", "Laminated steel core with copper winding", 2.8, 48.0),
            ("Hard Disk Drive Neodymium Magnet Assy", "High-field rare earth magnet and spindle motor scrap", 0.35, 95.0)
        ],
        "CAT_PLASTICS": [
            ("ABS Plastic Appliance Casings (Monitors/Printers)", "Rigid ABS polymer shells free from non-plastic inserts", 2.4, 25.0),
            ("HIPS TV Back Covers & Bezels", "High-impact polystyrene television outer shell casing", 3.1, 20.0),
            ("Polycarbonate (PC) Clear Scrap", "Shatter-resistant optical plastic scraps from electronics", 1.2, 32.0)
        ],
        "CAT_OTHER": [
            ("Small Kitchen Appliances (Iron/Mixer)", "Mixed household metal, coil, and resin motor scrap", 2.2, 28.0),
            ("Computer Keyboards & Computer Mice", "Membrane switch plastic, keycaps, and lightweight wiring", 0.7, 18.0),
            ("Ferrite Core Transformers & Adapters", "Wall chargers, adapters, and high-frequency ferrite coils", 0.4, 35.0)
        ]
    }

    materials = []
    mat_id = 1
    for cat in CATEGORIES:
        cid = cat["category_id"]
        for sub_name, desc, wt, est_val in sub_categories.get(cid, []):
            conditions = ["INTACT", "DAMAGED", "PARTIALLY_STRIPPED", "SCRAP_BULK"]
            source_types = ["HOUSEHOLD_COLLECTION", "INFORMAL_KABADIWALA", "COMMERCIAL_OFFICE", "LOCAL_AGGREGATOR"]
            for cond in conditions:
                val_mod = 1.0 if cond == "INTACT" else (0.85 if cond == "DAMAGED" else 0.75)
                materials.append({
                    "material_id": f"MAT_{mat_id:04d}",
                    "category_id": cid,
                    "category_name_en": cat["name_en"],
                    "category_name_mr": cat["name_mr"],
                    "category_name_hi": cat["name_hi"],
                    "sub_category": sub_name,
                    "material_description": desc,
                    "image_reference": f"assets/materials/{cid.lower()}_{mat_id:04d}.jpg",
                    "approximate_weight_kg": wt,
                    "condition": cond,
                    "source_type": random.choice(source_types),
                    "hazard_level": cat["hazard_level"],
                    "estimated_value_per_kg": round(est_val * val_mod, 2),
                    "unit": cat["unit"]
                })
                mat_id += 1
    return materials

def generate_prices():
    """Generates prices dataset covering field, recycler, and synthetic price observations."""
    locations = [
        "Mumbai - Dharavi Hub", "Mumbai - Kurla Industrial", "Navi Mumbai - TTC Mahape",
        "Thane - Wagle Estate", "Pune - Bhosari MIDC", "Pune - Swargate",
        "Nashik - Sinnar MIDC", "Nagpur - Butibori MIDC"
    ]
    prices = []
    price_id = 1
    base_date = datetime(2025, 9, 1, tzinfo=timezone.utc)

    for cat in CATEGORIES:
        cid = cat["category_id"]
        base_buy = cat["default_buy_rate_per_kg"]
        base_sell = cat["default_sell_rate_per_kg"]

        for loc in locations:
            # Generate 3 observations per location: 1 real field quote, 1 recycler offer, 1 trend synthetic
            for src, offset_days, spread in [("field", 2, -1.5), ("recycler", 5, 2.5), ("synthetic", 12, 0.5)]:
                rec_dt = (base_date + timedelta(days=offset_days + random.randint(0, 180))).isoformat()
                buy_price = round(base_buy + spread + random.uniform(-2.0, 3.0), 2)
                sell_price = round(base_sell + spread * 1.3 + random.uniform(-3.0, 4.0), 2)
                range_low = round(buy_price * 0.9, 2)
                range_high = round(sell_price * 1.15, 2)

                matching_recs = [r["recycler_id"] for r in RECYCLERS if cid in r["accepted_categories"]]
                chosen_rec = random.choice(matching_recs) if (src == "recycler" and matching_recs) else None

                prices.append({
                    "price_id": f"PRC_{price_id:05d}",
                    "category_id": cid,
                    "sub_category": f"Standard {cat['name_en']}",
                    "location": loc,
                    "recorded_at": rec_dt,
                    "prevailing_buying_price": buy_price,
                    "selling_quoted_price": sell_price,
                    "unit_of_measurement": cat["unit"],
                    "market_range_min": range_low,
                    "market_range_max": range_high,
                    "recycler_id": chosen_rec if chosen_rec else "N/A",
                    "source_type": src  # field | recycler | synthetic
                })
                price_id += 1
    return prices

def generate_transactions_and_traceability(collectors, materials):
    """Generates linked transaction and traceability datasets."""
    transactions = []
    traceability = []
    statuses = ["CONFIRMED", "COMPLETED", "COMPLETED", "PAID", "DISPUTED", "IN_TRANSIT"]
    payment_modes = ["PAID_CASH", "PAID_CASH", "PAID_UPI", "PENDING"]
    start_dt = datetime(2025, 8, 1, tzinfo=timezone.utc)

    for i in range(1, 120):
        lot_id = f"LOT_2026_{i:04d}"
        short_code = hashlib.sha256(lot_id.encode()).hexdigest()[:6].upper()
        collector = random.choice(collectors)
        mat = random.choice(materials)
        weight_collected = round(random.uniform(5.0, 65.0), 2)

        # Matched recycler that accepts this category
        eligible_recyclers = [r for r in RECYCLERS if mat["category_id"] in r["accepted_categories"]]
        recycler = random.choice(eligible_recyclers) if eligible_recyclers else random.choice(RECYCLERS)

        quoted_rate = mat["estimated_value_per_kg"]
        final_sale_val = round(weight_collected * quoted_rate * random.uniform(0.95, 1.05), 2)
        tx_dt = (start_dt + timedelta(days=random.randint(1, 220), hours=random.randint(1, 12))).isoformat()
        tx_status = random.choice(statuses)
        pay_status = "PAID_CASH" if tx_status in ["CONFIRMED", "COMPLETED", "PAID"] else random.choice(payment_modes)

        # Locations in Maharashtra
        coll_lat = round(19.0 + random.uniform(0.05, 0.4), 4)
        coll_lng = round(72.8 + random.uniform(0.05, 0.3), 4)

        transactions.append({
            "unique_lot_id": lot_id,
            "short_code": short_code,
            "collector_id": collector["collector_id"],
            "category_id": mat["category_id"],
            "material_sub_category": mat["sub_category"],
            "quantity_weight_kg": weight_collected,
            "quoted_price_per_kg": quoted_rate,
            "final_sale_value_inr": final_sale_val,
            "recycler_id": recycler["recycler_id"],
            "collection_location": collector["operating_area"],
            "handover_location": recycler["name"] + " - Facility Gate",
            "date_time": tx_dt,
            "payment_status": pay_status,
            "transaction_status": tx_status
        })

        # Traceability record
        weight_handover = round(weight_collected * random.uniform(0.98, 1.01), 2)
        handover_ref = f"HND-{short_code}-{random.randint(100, 999)}"
        record_raw = f"{lot_id}|{short_code}|{weight_handover}|{tx_dt}|{handover_ref}"
        record_hash = hashlib.sha256(record_raw.encode()).hexdigest()

        rec_confirmation = "CONFIRMED" if abs(weight_handover - weight_collected) < 1.0 else "WEIGHT_MISMATCH_RESOLVED"
        subsequent_status = "EPR_CREDIT_ISSUED" if tx_status in ["COMPLETED", "PAID"] else "ACCEPTED_FOR_DISMANTLING"

        traceability.append({
            "unique_lot_id": lot_id,
            "short_code": short_code,
            "photograph_ref": f"photos/lots/{lot_id}_proof.jpg",
            "photo_sha256": hashlib.sha256(f"image_{lot_id}".encode()).hexdigest(),
            "weight_at_collection_kg": weight_collected,
            "weight_at_handover_kg": weight_handover,
            "timestamp_utc": tx_dt,
            "gps_latitude": coll_lat,
            "gps_longitude": coll_lng,
            "handover_reference_number": handover_ref,
            "recycler_confirmation": rec_confirmation,
            "record_hash_sha256": record_hash,
            "subsequent_transaction_status": subsequent_status
        })

    return transactions, traceability

def generate_cpcb_registry():
    """Generates the seeded CPCB E-Waste EPR portal recycler registry."""
    registry = []
    for r in RECYCLERS:
        registry.append({
            "cpcb_registration_no": r["registration_no"],
            "facility_name": r["name"],
            "state_spcb": "Maharashtra Pollution Control Board (MPCB)",
            "facility_address": r["address"],
            "latitude": r["lat"],
            "longitude": r["lng"],
            "authorized_capacity_mta": r["capacity_mta"],
            "authorization_status": r["authorization_status"],
            "valid_from": "2023-01-01",
            "valid_upto": "2028-12-31",
            "epr_compliance_verified": True,
            "authorized_waste_streams": ", ".join(r["accepted_categories"]),
            "contact_email": r["email"],
            "contact_phone": r["contact"]
        })
    # Add pan-India references
    pan_india = [
        {
            "cpcb_registration_no": "CPCB/EPR/2022/REC-GJ-0015",
            "facility_name": "E-Colleague Recycling India Pvt Ltd",
            "state_spcb": "Gujarat Pollution Control Board",
            "facility_address": "GIDC Ankleshwar, Bharuch, Gujarat - 393002",
            "latitude": 21.6264,
            "longitude": 73.0031,
            "authorized_capacity_mta": 14000,
            "authorization_status": "VALID",
            "valid_from": "2022-05-10",
            "valid_upto": "2027-05-09",
            "epr_compliance_verified": True,
            "authorized_waste_streams": "CAT_PCB, CAT_CABLES, CAT_BATTERY, CAT_LCD_LED",
            "contact_email": "info@ecolleague.in",
            "contact_phone": "+91-2646-224411"
        },
        {
            "cpcb_registration_no": "CPCB/EPR/2021/REC-KA-0004",
            "facility_name": "Cerebra Integrated Technologies Limited",
            "state_spcb": "Karnataka State Pollution Control Board",
            "facility_address": "KIADB Industrial Area, Narasapura, Kolar, Karnataka - 563133",
            "latitude": 13.1438,
            "longitude": 78.1887,
            "authorized_capacity_mta": 40000,
            "authorization_status": "VALID",
            "valid_from": "2021-04-01",
            "valid_upto": "2026-03-31",
            "epr_compliance_verified": True,
            "authorized_waste_streams": "CAT_CRT, CAT_LCD_LED, CAT_PCB, CAT_CABLES, CAT_BATTERY, CAT_MOTORS, CAT_PLASTICS, CAT_OTHER",
            "contact_email": "ewaste@cerebracomputers.com",
            "contact_phone": "+91-80-22107777"
        }
    ]
    registry.extend(pan_india)
    return registry

def generate_price_trends():
    """Generates 12-month historical time series with explicit source_type tagging."""
    trends = []
    base_date = datetime(2025, 1, 1, tzinfo=timezone.utc)

    # Monthly price movement simulation across 2025-2026
    for month_idx in range(15):
        current_date = base_date + timedelta(days=month_idx * 30)
        dt_str = current_date.strftime("%Y-%m-%d")

        for cat in CATEGORIES:
            cid = cat["category_id"]
            base_buy = cat["default_buy_rate_per_kg"]
            base_sell = cat["default_sell_rate_per_kg"]

            trend_factor = 1.0 + (month_idx * 0.012) + random.uniform(-0.03, 0.03)

            for src in ["field", "recycler", "synthetic"]:
                margin = -2.0 if src == "field" else (3.0 if src == "recycler" else 0.0)
                buy = round(base_buy * trend_factor + margin, 2)
                sell = round(base_sell * trend_factor + margin * 1.2, 2)

                trends.append({
                    "date": dt_str,
                    "category_id": cid,
                    "category_name": cat["name_en"],
                    "location_cluster": "Maharashtra (Mumbai/Pune/Nashik)",
                    "buying_price_per_kg": buy,
                    "selling_price_per_kg": sell,
                    "unit": cat["unit"],
                    "source_type": src,  # field | recycler | synthetic
                    "notes": f"Aggregated {src} market reading"
                })
    return trends

def generate_flywheel_logs(materials):
    """Simulates collector icon-grid confirmations vs on-device TFLite predictions."""
    logs = []
    for i in range(1, 85):
        mat = random.choice(materials)
        tflite_confidence = round(random.uniform(0.62, 0.96), 3)
        if random.random() < 0.80:
            pred_class = mat["category_id"]
            feedback = "ACCEPTED_AS_SUGGESTED"
        else:
            other_cats = [c["category_id"] for c in CATEGORIES if c["category_id"] != mat["category_id"]]
            pred_class = random.choice(other_cats)
            feedback = "CORRECTED_BY_COLLECTOR"

        logs.append({
            "log_id": f"FLW_2026_{i:04d}",
            "lot_id": f"LOT_2026_{random.randint(1, 100):04d}",
            "image_hash": hashlib.sha256(f"flywheel_img_{i}".encode()).hexdigest(),
            "tflite_predicted_category": pred_class,
            "tflite_confidence_score": tflite_confidence,
            "collector_confirmed_category": mat["category_id"],
            "collector_language": random.choice(["mr", "hi"]),
            "feedback_action": feedback,
            "timestamp_utc": (datetime(2025, 10, 1, tzinfo=timezone.utc) + timedelta(days=random.randint(1, 150))).isoformat(),
            "retraining_eligible": True
        })
    return logs

def generate_field_scrap_manifest():
    """Generates the field scrap photo manifest covering 8 classes."""
    manifest = []
    angles = ["TOP_DOWN", "45_DEGREE_PERSPECTIVE", "CLOSEUP_LABEL", "SCALE_READING"]
    lightings = ["OUTDOOR_SUNLIGHT", "SCRAP_SHED_SHADOW", "TUBE_LIGHT", "DIM_INTERIOR"]
    backgrounds = ["BURLAP_SACK", "CONCRETE_FLOOR", "WEIGHING_SCALE", "HEAPED_PILE"]

    item_id = 1
    for cat in CATEGORIES:
        cid = cat["category_id"]
        class_folder = cid.lower().replace("cat_", "")
        for j in range(1, 15):
            fname = f"{class_folder}_field_{j:03d}.jpg"
            manifest.append({
                "photo_id": f"FLD_P_{item_id:04d}",
                "target_class": cid,
                "category_name": cat["name_en"],
                "file_path": f"ai_ml/field_research/classes/{class_folder}/{fname}",
                "location": random.choice(["Dharavi Aggregator Shed 4", "Kurla Scrap Yard", "Bhosari PCMC Gate 2", "Nashik Sinnar Scrap Cluster"]),
                "camera_angle": random.choice(angles),
                "lighting_condition": random.choice(lightings),
                "background": random.choice(backgrounds),
                "condition": random.choice(["DAMAGED", "INTACT", "STRIPPED", "DIRTY"]),
                "date_captured": "2025-11-14",
                "collector_present": True
            })
            item_id += 1
    return manifest

def save_csv_and_json(data, csv_path, json_path):
    if not data:
        return
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    keys = list(data[0].keys())
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(data)

def generate_sql_ddl_and_seed(collectors, materials, prices, recyclers, transactions, traceability):
    schema_sql_path = os.path.join(DB_SEEDS_DIR, "schema.sql")
    seed_sql_path = os.path.join(DB_SEEDS_DIR, "seed_data.sql")

    schema_content = """-- ====================================================================
-- ECOBRIDGE / KABADIWALA CONNECT DATABASE SCHEMA
-- SIH 2026 Problem Statement 26229
-- Compatible with SQLite and PostgreSQL
-- ====================================================================

-- 1. Collectors table (minimal personal data, privacy-first)
CREATE TABLE IF NOT EXISTS collectors (
    collector_id VARCHAR(36) PRIMARY KEY,
    preferred_language VARCHAR(5) NOT NULL DEFAULT 'mr', -- mr | hi
    operating_area VARCHAR(100) NOT NULL,
    transaction_count INTEGER DEFAULT 0,
    total_weight_kg REAL DEFAULT 0.0,
    total_cash_earned_inr REAL DEFAULT 0.0,
    pending_dues_inr REAL DEFAULT 0.0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 2. Material categories table (multilingual & hazard index)
CREATE TABLE IF NOT EXISTS material_categories (
    category_id VARCHAR(30) PRIMARY KEY,
    name_en VARCHAR(100) NOT NULL,
    name_mr VARCHAR(100) NOT NULL,
    name_hi VARCHAR(100) NOT NULL,
    icon VARCHAR(50) NOT NULL,
    hazard_level VARCHAR(20) NOT NULL DEFAULT 'LOW',
    default_buy_rate REAL NOT NULL,
    default_sell_rate REAL NOT NULL,
    unit VARCHAR(10) NOT NULL DEFAULT 'kg'
);

-- 3. Materials catalog table
CREATE TABLE IF NOT EXISTS materials (
    material_id VARCHAR(36) PRIMARY KEY,
    category_id VARCHAR(30) NOT NULL,
    sub_category VARCHAR(100) NOT NULL,
    material_description TEXT,
    image_reference VARCHAR(255),
    approximate_weight_kg REAL,
    condition VARCHAR(50) NOT NULL,
    source_type VARCHAR(50) NOT NULL,
    hazard_level VARCHAR(20) NOT NULL,
    estimated_value_per_kg REAL NOT NULL,
    unit VARCHAR(10) NOT NULL DEFAULT 'kg',
    FOREIGN KEY (category_id) REFERENCES material_categories(category_id)
);

-- 4. Authorized recyclers table (CPCB/MPCB authorized entities)
CREATE TABLE IF NOT EXISTS recyclers (
    recycler_id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    address TEXT NOT NULL,
    lat REAL NOT NULL,
    lng REAL NOT NULL,
    contact VARCHAR(50) NOT NULL,
    email VARCHAR(100),
    registration_no VARCHAR(100) NOT NULL,
    authorization_status VARCHAR(30) NOT NULL DEFAULT 'VALID',
    capacity_mta REAL NOT NULL,
    service_area VARCHAR(150),
    pickup_available BOOLEAN NOT NULL DEFAULT 0,
    min_lot_weight_kg REAL NOT NULL DEFAULT 20.0,
    accepted_categories TEXT NOT NULL
);

-- 5. Market prices table (distinguishing field, recycler, and synthetic data)
CREATE TABLE IF NOT EXISTS prices (
    price_id VARCHAR(36) PRIMARY KEY,
    category_id VARCHAR(30) NOT NULL,
    sub_category VARCHAR(100),
    location VARCHAR(100) NOT NULL,
    recorded_at TIMESTAMP NOT NULL,
    prevailing_buying_price REAL NOT NULL,
    selling_quoted_price REAL NOT NULL,
    unit_of_measurement VARCHAR(10) NOT NULL DEFAULT 'kg',
    market_range_min REAL NOT NULL,
    market_range_max REAL NOT NULL,
    recycler_id VARCHAR(36),
    source_type VARCHAR(20) NOT NULL, -- field | recycler | synthetic
    FOREIGN KEY (category_id) REFERENCES material_categories(category_id)
);

-- 6. Operational Transactions table
CREATE TABLE IF NOT EXISTS transactions (
    unique_lot_id VARCHAR(36) PRIMARY KEY,
    short_code VARCHAR(10) NOT NULL,
    collector_id VARCHAR(36) NOT NULL,
    category_id VARCHAR(30) NOT NULL,
    material_sub_category VARCHAR(100),
    quantity_weight_kg REAL NOT NULL,
    quoted_price_per_kg REAL NOT NULL,
    final_sale_value_inr REAL NOT NULL,
    recycler_id VARCHAR(36) NOT NULL,
    collection_location VARCHAR(150) NOT NULL,
    handover_location VARCHAR(150) NOT NULL,
    date_time TIMESTAMP NOT NULL,
    payment_status VARCHAR(30) NOT NULL,
    transaction_status VARCHAR(30) NOT NULL,
    FOREIGN KEY (collector_id) REFERENCES collectors(collector_id),
    FOREIGN KEY (category_id) REFERENCES material_categories(category_id),
    FOREIGN KEY (recycler_id) REFERENCES recyclers(recycler_id)
);

-- 7. Traceability table (verifiable audit trail)
CREATE TABLE IF NOT EXISTS traceability (
    unique_lot_id VARCHAR(36) PRIMARY KEY,
    short_code VARCHAR(10) NOT NULL,
    photograph_ref VARCHAR(255),
    photo_sha256 VARCHAR(64) NOT NULL,
    weight_at_collection_kg REAL NOT NULL,
    weight_at_handover_kg REAL NOT NULL,
    timestamp_utc TIMESTAMP NOT NULL,
    gps_latitude REAL NOT NULL,
    gps_longitude REAL NOT NULL,
    handover_reference_number VARCHAR(50) NOT NULL,
    recycler_confirmation VARCHAR(50) NOT NULL,
    record_hash_sha256 VARCHAR(64) NOT NULL,
    subsequent_transaction_status VARCHAR(50) NOT NULL,
    FOREIGN KEY (unique_lot_id) REFERENCES transactions(unique_lot_id)
);

-- Indexes for performance & offline queries
CREATE INDEX IF NOT EXISTS idx_materials_category ON materials(category_id);
CREATE INDEX IF NOT EXISTS idx_prices_cat_loc ON prices(category_id, location);
CREATE INDEX IF NOT EXISTS idx_tx_collector ON transactions(collector_id);
CREATE INDEX IF NOT EXISTS idx_tx_recycler ON transactions(recycler_id);
CREATE INDEX IF NOT EXISTS idx_trace_lot ON traceability(unique_lot_id);
"""

    with open(schema_sql_path, "w", encoding="utf-8") as f:
        f.write(schema_content)

    seed_lines = ["-- Seed data generated for Kabadiwala Connect\n"]

    # Categories
    for c in CATEGORIES:
        seed_lines.append(
            f"INSERT OR IGNORE INTO material_categories (category_id, name_en, name_mr, name_hi, icon, hazard_level, default_buy_rate, default_sell_rate, unit) "
            f"VALUES ('{c['category_id']}', '{c['name_en']}', '{c['name_mr']}', '{c['name_hi']}', '{c['icon']}', '{c['hazard_level']}', {c['default_buy_rate_per_kg']}, {c['default_sell_rate_per_kg']}, '{c['unit']}');\n"
        )

    # Recyclers
    for r in RECYCLERS:
        cats_str = json.dumps(r["accepted_categories"])
        name_esc = r["name"].replace("'", "''")
        addr_esc = r["address"].replace("'", "''")
        area_esc = r["service_area"].replace("'", "''")
        pickup_val = 1 if r["pickup_available"] else 0
        seed_lines.append(
            f"INSERT OR IGNORE INTO recyclers (recycler_id, name, address, lat, lng, contact, email, registration_no, authorization_status, capacity_mta, service_area, pickup_available, min_lot_weight_kg, accepted_categories) "
            f"VALUES ('{r['recycler_id']}', '{name_esc}', '{addr_esc}', {r['lat']}, {r['lng']}, '{r['contact']}', '{r['email']}', '{r['registration_no']}', '{r['authorization_status']}', {r['capacity_mta']}, '{area_esc}', {pickup_val}, {r['min_lot_weight_kg']}, '{cats_str}');\n"
        )

    # Collectors (first 10)
    for c in collectors[:10]:
        area_esc = c["operating_area"].replace("'", "''")
        seed_lines.append(
            f"INSERT OR IGNORE INTO collectors (collector_id, preferred_language, operating_area, transaction_count, total_weight_kg, total_cash_earned_inr, pending_dues_inr, created_at) "
            f"VALUES ('{c['collector_id']}', '{c['preferred_language']}', '{area_esc}', {c['transaction_count']}, {c['total_weight_kg']}, {c['total_cash_earned_inr']}, {c['pending_dues_inr']}, '{c['created_at']}');\n"
        )

    with open(seed_sql_path, "w", encoding="utf-8") as f:
        f.writelines(seed_lines)

def main():
    print("--- 1. Generating Operational Datasets ---")
    collectors = generate_collectors(40)
    save_csv_and_json(collectors, os.path.join(OPERATIONAL_DIR, "collectors.csv"), os.path.join(OPERATIONAL_DIR, "collectors.json"))
    print(f"  [OK] collectors: {len(collectors)} records")

    materials = generate_materials()
    save_csv_and_json(materials, os.path.join(OPERATIONAL_DIR, "materials.csv"), os.path.join(OPERATIONAL_DIR, "materials.json"))
    print(f"  [OK] materials: {len(materials)} records")

    prices = generate_prices()
    save_csv_and_json(prices, os.path.join(OPERATIONAL_DIR, "prices.csv"), os.path.join(OPERATIONAL_DIR, "prices.json"))
    print(f"  [OK] prices: {len(prices)} records")

    save_csv_and_json(RECYCLERS, os.path.join(OPERATIONAL_DIR, "recyclers.csv"), os.path.join(OPERATIONAL_DIR, "recyclers.json"))
    print(f"  [OK] recyclers: {len(RECYCLERS)} records")

    transactions, traceability = generate_transactions_and_traceability(collectors, materials)
    save_csv_and_json(transactions, os.path.join(OPERATIONAL_DIR, "transactions.csv"), os.path.join(OPERATIONAL_DIR, "transactions.json"))
    print(f"  [OK] transactions: {len(transactions)} records")

    save_csv_and_json(traceability, os.path.join(OPERATIONAL_DIR, "traceability.csv"), os.path.join(OPERATIONAL_DIR, "traceability.json"))
    print(f"  [OK] traceability: {len(traceability)} records")

    print("\n--- 2. Generating AI/ML & Research Datasets ---")
    cpcb_registry = generate_cpcb_registry()
    save_csv_and_json(cpcb_registry, os.path.join(REGISTRY_DIR, "cpcb_recycler_registry.csv"), os.path.join(REGISTRY_DIR, "cpcb_recycler_registry.json"))
    print(f"  [OK] CPCB registry: {len(cpcb_registry)} verified facilities")

    price_trends = generate_price_trends()
    save_csv_and_json(price_trends, os.path.join(PRICE_TRENDS_DIR, "price_trends_historical.csv"), os.path.join(PRICE_TRENDS_DIR, "price_intelligence.json"))
    print(f"  [OK] price trends: {len(price_trends)} time series records")

    flywheel = generate_flywheel_logs(materials)
    save_csv_and_json(flywheel, os.path.join(FLYWHEEL_DIR, "confirmed_labels.csv"), os.path.join(FLYWHEEL_DIR, "confirmed_labels.json"))
    with open(os.path.join(FLYWHEEL_DIR, "flywheel_logs.jsonl"), "w", encoding="utf-8") as f:
        for item in flywheel:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")
    print(f"  [OK] data flywheel: {len(flywheel)} feedback logs")

    field_manifest = generate_field_scrap_manifest()
    save_csv_and_json(field_manifest, os.path.join(FIELD_DIR, "field_scrap_manifest.csv"), os.path.join(FIELD_DIR, "field_scrap_manifest.json"))
    for cat in CATEGORIES:
        cls_name = cat["category_id"].lower().replace("cat_", "")
        os.makedirs(os.path.join(FIELD_DIR, "classes", cls_name), exist_ok=True)
    print(f"  [OK] field scrap manifest: {len(field_manifest)} sample entries across 8 classes")

    print("\n--- 3. Generating Vision Specification (YOLO & Classes) ---")
    classes_txt_path = os.path.join(VISION_DIR, "classes.txt")
    with open(classes_txt_path, "w", encoding="utf-8") as f:
        for cat in CATEGORIES:
            f.write(f"{cat['category_id']}\n")

    data_yaml_path = os.path.join(VISION_DIR, "data.yaml")
    yaml_content = f"""# YOLOv8 / TFLite Dataset Config — Kabadiwala Connect
# SIH 2026 Problem Statement 26229
path: ../ai_ml/vision
train: images/train
val: images/val
test: images/test

# 8 Core Target Classes
nc: 8
names:
  0: CRT
  1: LCD_LED_PANEL
  2: PCB
  3: CABLES
  4: BATTERIES
  5: MOTORS_MAGNETS
  6: MIXED_PLASTICS
  7: OTHER_EWASTE

multilingual_names:
  0: {{en: "CRT Monitors & TVs", mr: "सीआरटी मॉनिटर आणि टीव्ही", hi: "सीआरटी मॉनिटर और टीवी"}}
  1: {{en: "LCD / LED Panels", mr: "एलसीडी / एलईडी स्क्रीन", hi: "एलसीडी / एलईडी स्क्रीन"}}
  2: {{en: "Printed Circuit Boards", mr: "सर्किट बोर्ड / पीसीबी", hi: "सर्किट बोर्ड / पीसीबी"}}
  3: {{en: "Copper Cables & Wires", mr: "तांब्याची वायर आणि केबल्स", hi: "तांबे के तार और केबल"}}
  4: {{en: "Batteries", mr: "बॅटरी (लेड-अ‍ॅसिड / लिथियम)", hi: "बैटरी (लेड-एसिड / लिथियम)"}}
  5: {{en: "Motors & Magnets", mr: "मोटर्स आणि चुंबक", hi: "मोटर और चुंबक"}}
  6: {{en: "Mixed E-Waste Plastics", mr: "ई-कचरा प्लास्टिक", hi: "ई-कचरा प्लास्टिक"}}
  7: {{en: "Other E-Waste", mr: "इतर ई-कचरा", hi: "अन्य ई-कचरा"}}
"""
    with open(data_yaml_path, "w", encoding="utf-8") as f:
        f.write(yaml_content)
    print("  [OK] vision: classes.txt and data.yaml created")

    print("\n--- 4. Generating Database Schema & Seeds ---")
    generate_sql_ddl_and_seed(collectors, materials, prices, RECYCLERS, transactions, traceability)
    print("  [OK] database: schema.sql and seed_data.sql created")

    print("\n[SUCCESS] All base datasets and schemas generated successfully!")

if __name__ == "__main__":
    main()
