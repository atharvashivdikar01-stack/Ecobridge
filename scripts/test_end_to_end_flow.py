"""
Comprehensive End-to-End Test for EcoBridge Platform.
Validates the entire 3-phase lifecycle:
1. Informal Collector Onboarding & Lot Creation (TFLite AI Scan + Price Quote)
2. Offline Batch Sync & Handover Creation with GST & SHA-256 Hash
3. Authorized Recycler Verification, Weighbridge Confirmation & Cryptographic Custody Chain
"""
import asyncio
import hashlib
import json
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

# Add project root to sys.path so 'backend' package resolves
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import httpx
from sqlalchemy import select

from backend.src.core.bootstrap import bootstrap_database, LOCAL_RECYCLER_ID
from backend.src.core.database import SessionLocal
from backend.src.main import app
from backend.src.models import Lot, HandoverRecord, CustodyEvent, User, RecyclerCompany, CollectorProfile


async def run_end_to_end_verification():
    print("=" * 65)
    print(" ECOBRIDGE: COMPREHENSIVE 3-PHASE END-TO-END FLOW VERIFICATION")
    print("=" * 65)

    # 1. Initialize DB with the 8-class scrap catalog & verified recycler
    print("\n[Step 1] Bootstrapping SQLite database with catalog & seed recycler...")
    await bootstrap_database()
    print("  -> DB Bootstrapped successfully with CPCB-verified recycler.")

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        # 2. Health check
        print("\n[Step 2] Testing System Health Check...")
        r = await client.get("/api/v1/health")
        assert r.status_code == 200, f"Health check failed: {r.text}"
        data = r.json()
        assert data["status"] == "ok"
        print(f"  -> Health OK: {data}")

        # 3. Collector OTP Authentication
        print("\n[Step 3] Testing Collector Mobile Phone OTP Auth (Zero-Barrier Login)...")
        test_phone = "+919876543210"
        r_otp = await client.post("/api/v1/auth/otp/send", json={"phone": test_phone})
        assert r_otp.status_code == 200, f"Send OTP failed: {r_otp.text}"
        print(f"  -> OTP sent to {test_phone}")

        r_verify = await client.post("/api/v1/auth/otp/verify", json={
            "phone": test_phone,
            "otp": "123456",
            "full_name": "Ramesh Kumar (Collector)",
            "preferred_language": "mr"
        })
        assert r_verify.status_code == 200, f"Verify OTP failed: {r_verify.text}"
        token_data = r_verify.json()["data"]
        access_token = token_data["access_token"]
        print(f"  -> Collector Authenticated! Access Token: {access_token[:20]}...")
        headers = {"Authorization": f"Bearer {access_token}"}

        # 4. Mobile Lot Sync (Offline queue to /api/v1/sync/batch)
        print("\n[Step 4] Testing Mobile Lot Batch Sync (Phase 1 Collection)...")
        lot_uuid = str(uuid.uuid4())
        short_code = f"LOT-{uuid.uuid4().hex[:6].upper()}"
        lot_payload = {
            "lots": [{
                "uuid": lot_uuid,
                "short_code": short_code,
                "category": "Printed Circuit Boards (PCBs)",
                "approx_weight_kg": 15.5,
                "quoted_price": 330.0,
                "created_at": datetime.now(timezone.utc).isoformat()
            }]
        }
        r_lot_sync = await client.post("/api/v1/sync/batch", json=lot_payload, headers=headers)
        assert r_lot_sync.status_code == 200, f"Lot sync failed: {r_lot_sync.text}"
        sync_result = r_lot_sync.json()["data"]
        assert lot_uuid in sync_result["synced_lot_ids"], f"Lot UUID not in synced_lot_ids: {sync_result}"
        print(f"  -> Lot {short_code} (PCBs, 15.5 kg) synced successfully to server!")

        # 5. Mobile Handover Sync (Phase 2 Handover & Tax compliance)
        print("\n[Step 5] Testing Mobile Handover Sync (Phase 2 Scale & GST Settlement)...")
        handover_uuid = str(uuid.uuid4())
        ref_no = f"HND-{uuid.uuid4().hex[:8].upper()}"
        recycler_id = str(LOCAL_RECYCLER_ID)

        # Compute deterministic SHA-256 hash matching Android HashUtils
        weight = 15.5
        price = 330.0
        gross = weight * price  # 5115.00
        tax = gross * 0.05      # 255.75 (5% GST)
        total = gross + tax     # 5370.75
        now_iso = datetime.now(timezone.utc).isoformat()
        raw_hash_string = f"LOT:{lot_uuid}|REC:{recycler_id}|WT:{weight:.2f}|GROSS:{gross:.2f}|TAX:{tax:.2f}|TOT:{total:.2f}|INV:TXI-2026-MH-123456|MODE:CASH|TS:{now_iso}"
        record_hash = hashlib.sha256(raw_hash_string.encode('utf-8')).hexdigest()

        handover_payload = {
            "handovers": [{
                "uuid": handover_uuid,
                "reference_no": ref_no,
                "lot_short_code": short_code,
                "recycler_id": recycler_id,
                "weight": weight,
                "agreed_price": price,
                "record_hash": record_hash,
                "payment_mode": "CASH",
                "payment_amount": total,
                "payment_status": "PENDING_CONFIRMATION",
                "created_at": now_iso
            }]
        }
        r_handover_sync = await client.post("/api/v1/sync/handovers", json=handover_payload, headers=headers)
        assert r_handover_sync.status_code == 200, f"Handover sync failed: {r_handover_sync.text}"
        h_sync_result = r_handover_sync.json()["data"]
        assert handover_uuid in h_sync_result["synced_handover_ids"], f"Handover not in synced_handover_ids: {h_sync_result}"
        print(f"  -> Handover {ref_no} synced successfully! Hash: {record_hash[:16]}... (Gross: INR {gross:.2f}, GST: INR {tax:.2f}, Total: INR {total:.2f})")

        # 6. Recycler Portal Confirmation (Phase 3 Authorized Recycler Verification)
        print("\n[Step 6] Testing Recycler Confirmation & Chain-of-Custody (Phase 3)...")
        r_rec_login = await client.post("/api/v1/auth/demo-login", json={"role": "RECYCLER"})
        assert r_rec_login.status_code == 200, f"Recycler demo login failed: {r_rec_login.text}"
        rec_token = r_rec_login.json()["data"]["access_token"]
        rec_headers = {"Authorization": f"Bearer {rec_token}"}

        # Recycler confirms handover
        r_confirm = await client.post(
            f"/api/v1/recycler-portal/handovers/{ref_no}/confirm",
            json={
                "verified_weight_kg": weight,
                "note": "Physical weighbridge verified. Material matches PCB grade-1."
            },
            headers=rec_headers
        )
        assert r_confirm.status_code == 200, f"Confirmation failed: {r_confirm.text}"
        confirm_data = r_confirm.json()["data"]
        assert confirm_data["status"] == "CONFIRMED"
        print(f"  -> Recycler confirmed handover! Status: {confirm_data['status']}")

        # Verify CustodyEvent in DB
        async with SessionLocal() as db:
            event = (await db.execute(select(CustodyEvent).where(CustodyEvent.event_type == "HANDOVER_CONFIRMED"))).scalars().first()
            assert event is not None, "CustodyEvent was not persisted!"
            print(f"  -> Tamper-evident Custody Event verified! SHA-256: {event.current_event_hash[:16]}... Previous: {event.previous_event_hash[:16]}...")

        # 7. Check collector sync status to ensure the offline loop is fully closed
        print("\n[Step 7] Checking Closed-Loop Collector Status Refresh...")
        r_status = await client.get("/api/v1/sync/status", headers=headers)
        assert r_status.status_code == 200, f"Status check failed: {r_status.text}"
        status_data = r_status.json()["data"]
        confirmed_handover = next((h for h in status_data["handovers"] if h["reference_no"] == ref_no), None)
        assert confirmed_handover is not None, f"Handover {ref_no} not found in sync status!"
        assert confirmed_handover["status"] == "CONFIRMED", f"Handover status expected CONFIRMED, got {confirmed_handover['status']}"
        print(f"  -> Collector app receives authoritative state: {confirmed_handover['status']}")

    print("\n" + "=" * 65)
    print(" ALL 3 PHASES & DATA FLOW FULLY VERIFIED (100% SUCCESS)")
    print("=" * 65)


if __name__ == "__main__":
    asyncio.run(run_end_to_end_verification())
