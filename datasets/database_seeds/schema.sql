-- ====================================================================
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
