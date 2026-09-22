-- ============================================================
-- Kabadiwala Connect (SIH 2026, PS 26229)
-- Database schema v2 for PostgreSQL 13 or newer
--
-- Run order: 01_schema.sql first, then 02_seed.sql
-- To start over: drop the database and create it again, then re-run both files.
--
-- Conventions
--   * IDs are UUIDs. Records made on the phone (lots, photos, handovers,
--     ledger entries) get their UUID on the phone, so it works offline.
--   * Times are TIMESTAMPTZ (stored in UTC).
--   * Weight is in kg. Money is in INR.
-- ============================================================

BEGIN;

-- gen_random_uuid() is built into Postgres 13+, but this line makes the
-- script work on older Postgres versions too, and costs nothing on 13+.
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- 1. Collectors: minimal personal data on purpose (PS requirement)
CREATE TABLE collectors (
    collector_id        UUID PRIMARY KEY,                       -- made on the phone
    preferred_language  TEXT NOT NULL DEFAULT 'mr'
                        CHECK (preferred_language IN ('mr', 'hi', 'en')),
    operating_area      TEXT,                                   -- general area, not an exact address
    display_name        TEXT,                                   -- optional, may stay empty
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 2. Material categories (the icons and names the collector sees)
CREATE TABLE material_categories (
    category_id   TEXT PRIMARY KEY,                             -- e.g. 'CRT', 'PCB'
    name_en       TEXT NOT NULL,
    name_mr       TEXT NOT NULL,
    name_hi       TEXT NOT NULL,
    icon          TEXT,
    hazard_level  TEXT NOT NULL DEFAULT 'LOW'
                  CHECK (hazard_level IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL'))
);

-- 3. Recyclers / aggregators
--    New recyclers start as PENDING. Only VERIFIED ones should be shown to collectors.
CREATE TABLE recyclers (
    recycler_id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name                       TEXT NOT NULL,
    address                    TEXT NOT NULL,
    lat                        NUMERIC(10, 7) NOT NULL CHECK (lat BETWEEN -90 AND 90),
    lng                        NUMERIC(10, 7) NOT NULL CHECK (lng BETWEEN -180 AND 180),
    contact                    TEXT,
    registration_no            TEXT NOT NULL UNIQUE,            -- registration number from the CPCB portal
    authorization_status       TEXT NOT NULL DEFAULT 'PENDING'
                               CHECK (authorization_status IN ('VERIFIED', 'PENDING', 'EXPIRED', 'REVOKED')),
    authorization_valid_until  DATE,
    accepts_whole_units        BOOLEAN NOT NULL DEFAULT TRUE,
    accepts_parts              BOOLEAN NOT NULL DEFAULT FALSE,  -- ask recyclers what they really accept
    service_area               TEXT,
    pickup_available           BOOLEAN NOT NULL DEFAULT FALSE,
    updated_at                 TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 4. Logins for the recycler-side web interface (never store plain passwords)
CREATE TABLE recycler_users (
    user_id        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    recycler_id    UUID NOT NULL REFERENCES recyclers(recycler_id) ON DELETE CASCADE,
    username       TEXT NOT NULL UNIQUE,
    password_hash  TEXT NOT NULL,
    created_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 5. Current rate each recycler offers per category
--    When a rate changes, ALSO insert a row into prices (source_type = 'recycler')
--    so the history is kept.
CREATE TABLE recycler_rates (
    rate_id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    recycler_id          UUID NOT NULL REFERENCES recyclers(recycler_id) ON DELETE CASCADE,
    category_id          TEXT NOT NULL REFERENCES material_categories(category_id),
    offered_rate_per_kg  NUMERIC(10, 2) NOT NULL CHECK (offered_rate_per_kg >= 0),
    updated_at           TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (recycler_id, category_id)
);

-- 6. Price history. INSERT new rows, never UPDATE old ones, or the history is lost.
--    source_type keeps real quotes apart from demo data.
CREATE TABLE prices (
    price_id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    category_id    TEXT NOT NULL REFERENCES material_categories(category_id),
    subcategory    TEXT,
    area           TEXT NOT NULL,
    recorded_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    buying_price   NUMERIC(10, 2) NOT NULL CHECK (buying_price >= 0),
    selling_price  NUMERIC(10, 2) CHECK (selling_price >= 0),
    unit           TEXT NOT NULL DEFAULT 'INR/kg',
    range_low      NUMERIC(10, 2) CHECK (range_low >= 0),
    range_high     NUMERIC(10, 2) CHECK (range_high >= 0),
    recycler_id    UUID REFERENCES recyclers(recycler_id) ON DELETE SET NULL,
    source_type    TEXT NOT NULL CHECK (source_type IN ('field', 'recycler', 'synthetic')),
    CHECK (range_low IS NULL OR range_high IS NULL OR range_low <= range_high)
);

-- 7. Lots: one row per bundle of scrap a collector logs
CREATE TABLE lots (
    lot_id                    UUID PRIMARY KEY,                 -- made on the phone
    short_code                TEXT NOT NULL,                    -- 6-8 characters the recycler can read out
    collector_id              UUID NOT NULL REFERENCES collectors(collector_id),
    category_id               TEXT NOT NULL REFERENCES material_categories(category_id),
    subcategory               TEXT,
    description               TEXT,
    condition                 TEXT,                             -- e.g. whole_unit, dismantled_parts, mixed_scrap
    source_type               TEXT,                             -- e.g. household, commercial, street
    approx_weight_kg          NUMERIC(10, 2) NOT NULL CHECK (approx_weight_kg > 0),
    estimated_value           NUMERIC(10, 2),
    quoted_price              NUMERIC(10, 2),
    final_sale_value          NUMERIC(10, 2),

    -- AI assistance, kept for the AI/ML training dataset
    ai_suggested_category     TEXT REFERENCES material_categories(category_id),
    ai_confidence             NUMERIC(4, 3) CHECK (ai_confidence BETWEEN 0 AND 1),
    ai_model_version          TEXT,
    category_changed_by_user  BOOLEAN,

    collected_at              TIMESTAMPTZ NOT NULL,             -- the PHONE's clock. No default on purpose.
    lat                       NUMERIC(10, 7),
    lng                       NUMERIC(10, 7),
    status                    TEXT NOT NULL DEFAULT 'ESTIMATED'
                              CHECK (status IN ('DRAFT', 'ESTIMATED', 'MATCHED', 'HANDED_OVER',
                                                'CONFIRMED', 'PAID', 'DISPUTED')),
    payment_status            TEXT NOT NULL DEFAULT 'UNPAID'
                              CHECK (payment_status IN ('UNPAID', 'PARTIAL', 'PAID')),
    synced_at                 TIMESTAMPTZ NOT NULL DEFAULT now(),  -- when the SERVER received it

    -- Short codes are made offline, so two phones could pick the same one.
    -- They only have to be unique per collector.
    UNIQUE (collector_id, short_code)
);

-- 8. Photos of a lot (at collection time and at handover time)
CREATE TABLE lot_photos (
    photo_id   UUID PRIMARY KEY,                                -- made on the phone
    lot_id     UUID NOT NULL REFERENCES lots(lot_id) ON DELETE CASCADE,
    stage      TEXT NOT NULL DEFAULT 'collection' CHECK (stage IN ('collection', 'handover')),
    file_path  TEXT NOT NULL,
    sha256     TEXT NOT NULL CHECK (sha256 ~ '^[0-9a-f]{64}$'), -- fingerprint of the photo file
    taken_at   TIMESTAMPTZ NOT NULL,
    uploaded   BOOLEAN NOT NULL DEFAULT FALSE,
    UNIQUE (lot_id, sha256)
);

-- 9. Handovers: the verifiable record that a recycler received the lot
CREATE TABLE handovers (
    handover_id            UUID PRIMARY KEY,                    -- made on the phone
    lot_id                 UUID NOT NULL REFERENCES lots(lot_id),
    recycler_id            UUID NOT NULL REFERENCES recyclers(recycler_id),
    reference_no           TEXT NOT NULL,
    weight_at_handover     NUMERIC(10, 2) NOT NULL CHECK (weight_at_handover > 0),
    lat                    NUMERIC(10, 7),
    lng                    NUMERIC(10, 7),
    handed_over_at         TIMESTAMPTZ NOT NULL,                -- the phone's clock
    recycler_confirmed_at  TIMESTAMPTZ,
    record_hash            TEXT NOT NULL CHECK (record_hash ~ '^[0-9a-f]{64}$'),  -- SHA-256 of the record
    status                 TEXT NOT NULL DEFAULT 'PENDING'
                           CHECK (status IN ('PENDING', 'CONFIRMED', 'REJECTED', 'DISPUTED')),
    UNIQUE (recycler_id, reference_no)
);

-- A lot can have only one open handover at a time, but a REJECTED one
-- may be followed by a new handover to a different recycler.
CREATE UNIQUE INDEX one_open_handover_per_lot
    ON handovers (lot_id) WHERE status IN ('PENDING', 'CONFIRMED');

-- 10. Earnings ledger
CREATE TABLE ledger_entries (
    entry_id      UUID PRIMARY KEY,                             -- made on the phone
    collector_id  UUID NOT NULL REFERENCES collectors(collector_id),
    handover_id   UUID REFERENCES handovers(handover_id),
    amount        NUMERIC(10, 2) NOT NULL CHECK (amount >= 0),
    entry_type    TEXT NOT NULL CHECK (entry_type IN ('payment', 'due')),
    payment_mode  TEXT NOT NULL DEFAULT 'cash' CHECK (payment_mode IN ('cash', 'upi')),
    note          TEXT,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 11. Flags raised when a price or transaction looks abnormal
CREATE TABLE anomaly_flags (
    flag_id      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lot_id       UUID REFERENCES lots(lot_id) ON DELETE CASCADE,
    handover_id  UUID REFERENCES handovers(handover_id) ON DELETE CASCADE,
    rule_name    TEXT NOT NULL,                                 -- e.g. 'price_below_range'
    details      TEXT,
    flagged_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    CHECK (lot_id IS NOT NULL OR handover_id IS NOT NULL)
);

-- Indexes for the queries the app will run most
CREATE INDEX idx_lots_collector       ON lots (collector_id);
CREATE INDEX idx_lots_status          ON lots (status);
CREATE INDEX idx_prices_cat_area_time ON prices (category_id, area, recorded_at DESC);
CREATE INDEX idx_rates_category       ON recycler_rates (category_id);
CREATE INDEX idx_handovers_recycler   ON handovers (recycler_id);
CREATE INDEX idx_ledger_collector     ON ledger_entries (collector_id);
CREATE INDEX idx_photos_sha256        ON lot_photos (sha256);   -- spot the same photo reused on two lots

COMMIT;