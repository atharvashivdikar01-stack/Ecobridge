-- ========================================================
-- ECOBRIDGE Production Migration: 20260920000000_init_ecobridge_schema
-- Target: PostgreSQL 16 with PostGIS
-- ========================================================

-- Enable core extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "postgis";

-- --------------------------------------------------------
-- 1. ENUMS
-- --------------------------------------------------------

CREATE TYPE user_role AS ENUM (
  'COLLECTOR',
  'RECYCLER_OPERATOR',
  'RECYCLER_ADMIN',
  'PLATFORM_ADMIN',
  'AUDITOR'
);

CREATE TYPE user_status AS ENUM (
  'ACTIVE',
  'SUSPENDED',
  'PENDING_VERIFICATION',
  'INACTIVE'
);

CREATE TYPE collector_type AS ENUM (
  'INDIVIDUAL_PICKER',
  'KABADIWALA',
  'SCRAP_AGGREGATOR',
  'COMMUNITY_ENTERPRISE'
);

CREATE TYPE permit_type AS ENUM (
  'HAZARDOUS_WASTE_AUTHORIZATION',
  'E_WASTE_DISMANTLER',
  'E_WASTE_RECYCLER',
  'PRO_PRODUCER_RESPONSIBILITY_ORG',
  'REFURBISHER'
);

CREATE TYPE permit_status AS ENUM (
  'ACTIVE',
  'EXPIRED',
  'REVOKED',
  'PENDING_RENEWAL',
  'SUSPENDED'
);

CREATE TYPE hazard_severity AS ENUM (
  'INFO',
  'WARNING',
  'DANGER',
  'CRITICAL'
);

CREATE TYPE hazard_condition AS ENUM (
  'NORMAL',
  'SWOLLEN_BATTERY',
  'LEAKING_ELECTROLYTE',
  'BROKEN_CRT_GLASS',
  'BURNT_COMPONENTS',
  'MERCURY_CONTAINING',
  'CORRODED_TERMINALS'
);

CREATE TYPE lot_status AS ENUM (
  'DRAFT',
  'PENDING_SYNC',
  'COLLECTED',
  'OFFERED',
  'ACCEPTED',
  'IN_TRANSIT',
  'DELIVERED',
  'VERIFIED',
  'SETTLED',
  'CANCELLED',
  'DISPUTED'
);

CREATE TYPE offer_type AS ENUM (
  'DIRECT_BUYOUT',
  'BID',
  'SCHEDULED_PICKUP'
);

CREATE TYPE offer_status AS ENUM (
  'OFFERED',
  'ACCEPTED',
  'REJECTED',
  'EXPIRED',
  'COUNTERED'
);

CREATE TYPE handover_type AS ENUM (
  'COLLECTOR_TO_TRANSPORTER',
  'COLLECTOR_TO_FACILITY',
  'TRANSPORTER_TO_FACILITY'
);

CREATE TYPE handover_status AS ENUM (
  'PENDING',
  'COMPLETED',
  'DISPUTED',
  'REJECTED'
);

CREATE TYPE custody_event_type AS ENUM (
  'CREATION',
  'HAZARD_FLAGGED',
  'OFFER_ACCEPTED',
  'HANDOVER_INITIATED',
  'FACILITY_INTAKE',
  'WEIGHBRIDGE_CONFIRMED',
  'MATERIAL_SORTED',
  'PAYMENT_DISBURSED',
  'DISMANTLED',
  'RECYCLED',
  'EPR_CERTIFICATE_ISSUED'
);

CREATE TYPE transaction_type AS ENUM (
  'ESCROW_LOCK',
  'ESCROW_RELEASE',
  'COLLECTOR_PAYOUT',
  'PLATFORM_FEE',
  'RECYCLER_REFUND'
);

CREATE TYPE transaction_status AS ENUM (
  'PENDING',
  'HELD_IN_ESCROW',
  'SETTLED',
  'FAILED',
  'REFUNDED'
);

CREATE TYPE escrow_status AS ENUM (
  'ACTIVE',
  'RELEASED',
  'FORFEITED',
  'DISPUTED'
);

CREATE TYPE payout_method AS ENUM (
  'UPI',
  'IMPS',
  'BANK_TRANSFER',
  'CASH_VOUCHER'
);

CREATE TYPE payout_status AS ENUM (
  'INITIATED',
  'PROCESSING',
  'SUCCESS',
  'FAILURE',
  'REVERSED'
);

CREATE TYPE audit_action AS ENUM (
  'CREATE',
  'UPDATE',
  'DELETE',
  'STATUS_CHANGE',
  'OVERRIDE',
  'LOGIN',
  'PERMISSION_CHANGE'
);

-- --------------------------------------------------------
-- 2. HELPER FUNCTIONS & TRIGGERS
-- --------------------------------------------------------

CREATE OR REPLACE FUNCTION trigger_set_timestamp()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- --------------------------------------------------------
-- 3. USERS & COLLECTOR PROFILES
-- --------------------------------------------------------

CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  phone VARCHAR(20) NOT NULL UNIQUE,
  full_name VARCHAR(255) NOT NULL,
  email VARCHAR(255) UNIQUE,
  password_hash VARCHAR(255),
  role user_role NOT NULL DEFAULT 'COLLECTOR',
  status user_status NOT NULL DEFAULT 'ACTIVE',
  preferred_language VARCHAR(10) NOT NULL DEFAULT 'en',
  avatar_url TEXT,
  created_at TIMESTAMPTZ(6) NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ(6) NOT NULL DEFAULT NOW()
);

CREATE TRIGGER set_timestamp_users
BEFORE UPDATE ON users
FOR EACH ROW EXECUTE FUNCTION trigger_set_timestamp();

CREATE TABLE collector_profiles (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
  collector_type collector_type NOT NULL DEFAULT 'INDIVIDUAL_PICKER',
  national_id_number VARCHAR(100),
  national_id_type VARCHAR(50),
  bank_account_number VARCHAR(50),
  ifsc_code VARCHAR(20),
  upi_id VARCHAR(100),
  trust_score NUMERIC(5, 2) NOT NULL DEFAULT 1.00 CHECK (trust_score >= 0.00 AND trust_score <= 5.00),
  total_lots_collected INT NOT NULL DEFAULT 0,
  total_weight_kg NUMERIC(12, 3) NOT NULL DEFAULT 0.000,
  verified_at TIMESTAMPTZ(6),
  created_at TIMESTAMPTZ(6) NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ(6) NOT NULL DEFAULT NOW()
);

CREATE TRIGGER set_timestamp_collector_profiles
BEFORE UPDATE ON collector_profiles
FOR EACH ROW EXECUTE FUNCTION trigger_set_timestamp();

-- --------------------------------------------------------
-- 4. RECYCLERS & FACILITIES
-- --------------------------------------------------------

CREATE TABLE recycler_companies (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
  company_name VARCHAR(255) NOT NULL,
  trade_license_number VARCHAR(100) NOT NULL UNIQUE,
  gst_number VARCHAR(50) UNIQUE,
  cpcb_registration_no VARCHAR(100) NOT NULL UNIQUE,
  contact_person VARCHAR(100) NOT NULL,
  contact_phone VARCHAR(20) NOT NULL,
  contact_email VARCHAR(255),
  operating_status user_status NOT NULL DEFAULT 'PENDING_VERIFICATION',
  created_at TIMESTAMPTZ(6) NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ(6) NOT NULL DEFAULT NOW()
);

CREATE TRIGGER set_timestamp_recycler_companies
BEFORE UPDATE ON recycler_companies
FOR EACH ROW EXECUTE FUNCTION trigger_set_timestamp();

CREATE TABLE recycler_facilities (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  recycler_id UUID NOT NULL REFERENCES recycler_companies(id) ON DELETE CASCADE,
  facility_name VARCHAR(255) NOT NULL,
  address_line1 VARCHAR(255) NOT NULL,
  address_line2 VARCHAR(255),
  city VARCHAR(100) NOT NULL,
  state VARCHAR(100) NOT NULL,
  postal_code VARCHAR(20) NOT NULL,
  latitude NUMERIC(10, 8) NOT NULL,
  longitude NUMERIC(11, 8) NOT NULL,
  location GEOGRAPHY(Point, 4326) NOT NULL,
  daily_capacity_kg NUMERIC(10, 2) NOT NULL DEFAULT 0.00,
  accepts_hazardous BOOLEAN NOT NULL DEFAULT false,
  is_active BOOLEAN NOT NULL DEFAULT true,
  created_at TIMESTAMPTZ(6) NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ(6) NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_recycler_facilities_location ON recycler_facilities USING GIST (location);
CREATE INDEX idx_recycler_facilities_recycler_id ON recycler_facilities (recycler_id);

CREATE TRIGGER set_timestamp_recycler_facilities
BEFORE UPDATE ON recycler_facilities
FOR EACH ROW EXECUTE FUNCTION trigger_set_timestamp();

CREATE TABLE authorization_records (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  facility_id UUID NOT NULL REFERENCES recycler_facilities(id) ON DELETE CASCADE,
  authority_name VARCHAR(100) NOT NULL,
  permit_type permit_type NOT NULL,
  permit_number VARCHAR(100) NOT NULL UNIQUE,
  issued_date DATE NOT NULL,
  expiry_date DATE NOT NULL,
  status permit_status NOT NULL DEFAULT 'ACTIVE',
  document_url TEXT,
  verified_at TIMESTAMPTZ(6),
  created_at TIMESTAMPTZ(6) NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ(6) NOT NULL DEFAULT NOW(),
  CONSTRAINT check_permit_dates CHECK (expiry_date >= issued_date)
);

CREATE INDEX idx_authorization_records_facility ON authorization_records (facility_id);
CREATE INDEX idx_authorization_records_expiry ON authorization_records (expiry_date);

CREATE TRIGGER set_timestamp_authorization_records
BEFORE UPDATE ON authorization_records
FOR EACH ROW EXECUTE FUNCTION trigger_set_timestamp();

-- --------------------------------------------------------
-- 5. WASTE TAXONOMY, MATERIALS & SAFETY GUIDANCE
-- --------------------------------------------------------

CREATE TABLE waste_categories (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  code VARCHAR(50) NOT NULL UNIQUE,
  name VARCHAR(150) NOT NULL,
  description TEXT,
  default_hazard hazard_severity NOT NULL DEFAULT 'INFO',
  is_active BOOLEAN NOT NULL DEFAULT true,
  created_at TIMESTAMPTZ(6) NOT NULL DEFAULT NOW()
);

CREATE TABLE materials (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  category_id UUID NOT NULL REFERENCES waste_categories(id) ON DELETE RESTRICT,
  code VARCHAR(100) NOT NULL UNIQUE,
  name VARCHAR(200) NOT NULL,
  description TEXT,
  base_unit VARCHAR(20) NOT NULL DEFAULT 'KG',
  standard_yield_json JSONB,
  requires_permit BOOLEAN NOT NULL DEFAULT false,
  is_active BOOLEAN NOT NULL DEFAULT true,
  created_at TIMESTAMPTZ(6) NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ(6) NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_materials_category ON materials (category_id);
CREATE TRIGGER set_timestamp_materials
BEFORE UPDATE ON materials
FOR EACH ROW EXECUTE FUNCTION trigger_set_timestamp();

CREATE TABLE safety_guidance (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  material_id UUID REFERENCES materials(id) ON DELETE CASCADE,
  hazard_condition hazard_condition NOT NULL DEFAULT 'NORMAL',
  severity hazard_severity NOT NULL DEFAULT 'INFO',
  title_key VARCHAR(100) NOT NULL,
  message_key VARCHAR(255) NOT NULL,
  required_ppe_json JSONB NOT NULL DEFAULT '[]'::jsonb,
  prohibited_actions_json JSONB NOT NULL DEFAULT '[]'::jsonb,
  emergency_protocol_key VARCHAR(100),
  audio_prompt_key VARCHAR(100),
  created_at TIMESTAMPTZ(6) NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_safety_guidance_material ON safety_guidance (material_id);
CREATE INDEX idx_safety_guidance_condition ON safety_guidance (hazard_condition);

-- --------------------------------------------------------
-- 6. PRICING & COMMODITY INDICES
-- --------------------------------------------------------

CREATE TABLE commodity_price_indices (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  commodity_symbol VARCHAR(20) NOT NULL,
  exchange_source VARCHAR(50) NOT NULL,
  currency VARCHAR(10) NOT NULL DEFAULT 'INR',
  spot_price NUMERIC(14, 4) NOT NULL,
  unit VARCHAR(20) NOT NULL DEFAULT 'KG',
  effective_timestamp TIMESTAMPTZ(6) NOT NULL,
  recorded_at TIMESTAMPTZ(6) NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_commodity_price_symbol_time ON commodity_price_indices (commodity_symbol, effective_timestamp DESC);

CREATE TABLE material_price_bands (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  material_id UUID NOT NULL REFERENCES materials(id) ON DELETE CASCADE,
  grade VARCHAR(50) NOT NULL DEFAULT 'STANDARD',
  min_price_per_unit NUMERIC(12, 2) NOT NULL,
  max_price_per_unit NUMERIC(12, 2) NOT NULL,
  benchmark_price_per_unit NUMERIC(12, 2) NOT NULL,
  currency VARCHAR(10) NOT NULL DEFAULT 'INR',
  effective_from TIMESTAMPTZ(6) NOT NULL,
  effective_to TIMESTAMPTZ(6),
  is_active BOOLEAN NOT NULL DEFAULT true,
  created_at TIMESTAMPTZ(6) NOT NULL DEFAULT NOW(),
  CONSTRAINT check_price_range CHECK (max_price_per_unit >= min_price_per_unit AND benchmark_price_per_unit >= min_price_per_unit AND benchmark_price_per_unit <= max_price_per_unit)
);

CREATE INDEX idx_material_price_bands_lookup ON material_price_bands (material_id, is_active);

-- --------------------------------------------------------
-- 7. LOTS, ITEMS & IMAGES
-- --------------------------------------------------------

CREATE TABLE lots (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  lot_code VARCHAR(50) NOT NULL UNIQUE,
  collector_id UUID NOT NULL REFERENCES collector_profiles(id) ON DELETE RESTRICT,
  designated_facility_id UUID REFERENCES recycler_facilities(id) ON DELETE SET NULL,
  status lot_status NOT NULL DEFAULT 'COLLECTED',
  total_estimated_weight_kg NUMERIC(12, 3) NOT NULL DEFAULT 0.000,
  total_verified_weight_kg NUMERIC(12, 3),
  estimated_value NUMERIC(12, 2) NOT NULL DEFAULT 0.00,
  final_value NUMERIC(12, 2),
  currency VARCHAR(10) NOT NULL DEFAULT 'INR',
  origin_latitude NUMERIC(10, 8),
  origin_longitude NUMERIC(11, 8),
  origin_location GEOGRAPHY(Point, 4326),
  origin_address TEXT,
  offline_created_at TIMESTAMPTZ(6) NOT NULL,
  synced_at TIMESTAMPTZ(6),
  created_at TIMESTAMPTZ(6) NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ(6) NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_lots_collector ON lots (collector_id);
CREATE INDEX idx_lots_status ON lots (status);
CREATE INDEX idx_lots_created_at ON lots (created_at);
CREATE INDEX idx_lots_origin_location ON lots USING GIST (origin_location);

CREATE TRIGGER set_timestamp_lots
BEFORE UPDATE ON lots
FOR EACH ROW EXECUTE FUNCTION trigger_set_timestamp();

CREATE TABLE lot_items (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  lot_id UUID NOT NULL REFERENCES lots(id) ON DELETE CASCADE,
  material_id UUID NOT NULL REFERENCES materials(id) ON DELETE RESTRICT,
  quantity INT NOT NULL DEFAULT 1 CHECK (quantity > 0),
  unit VARCHAR(20) NOT NULL DEFAULT 'KG',
  estimated_weight_kg NUMERIC(12, 3) NOT NULL CHECK (estimated_weight_kg >= 0),
  verified_weight_kg NUMERIC(12, 3) CHECK (verified_weight_kg IS NULL OR verified_weight_kg >= 0),
  ai_confidence_score NUMERIC(5, 4) CHECK (ai_confidence_score IS NULL OR (ai_confidence_score >= 0 AND ai_confidence_score <= 1)),
  detected_hazard hazard_condition NOT NULL DEFAULT 'NORMAL',
  safety_guidance_id UUID REFERENCES safety_guidance(id) ON DELETE SET NULL,
  unit_price_estimated NUMERIC(12, 2) NOT NULL DEFAULT 0.00,
  unit_price_verified NUMERIC(12, 2),
  subtotal_estimated NUMERIC(12, 2) NOT NULL DEFAULT 0.00,
  subtotal_final NUMERIC(12, 2),
  notes TEXT,
  created_at TIMESTAMPTZ(6) NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ(6) NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_lot_items_lot ON lot_items (lot_id);
CREATE INDEX idx_lot_items_material ON lot_items (material_id);

CREATE TRIGGER set_timestamp_lot_items
BEFORE UPDATE ON lot_items
FOR EACH ROW EXECUTE FUNCTION trigger_set_timestamp();

CREATE TABLE lot_images (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  lot_id UUID NOT NULL REFERENCES lots(id) ON DELETE CASCADE,
  lot_item_id UUID REFERENCES lot_items(id) ON DELETE SET NULL,
  image_url TEXT NOT NULL,
  image_hash VARCHAR(64) NOT NULL, -- SHA-256
  latitude NUMERIC(10, 8),
  longitude NUMERIC(11, 8),
  captured_at TIMESTAMPTZ(6) NOT NULL,
  is_proof_of_collection BOOLEAN NOT NULL DEFAULT false,
  created_at TIMESTAMPTZ(6) NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_lot_images_lot ON lot_images (lot_id);
CREATE INDEX idx_lot_images_hash ON lot_images (image_hash);

-- --------------------------------------------------------
-- 8. OFFERS & HANDOVERS
-- --------------------------------------------------------

CREATE TABLE lot_offers (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  lot_id UUID NOT NULL REFERENCES lots(id) ON DELETE CASCADE,
  recycler_id UUID NOT NULL REFERENCES recycler_companies(id) ON DELETE RESTRICT,
  facility_id UUID REFERENCES recycler_facilities(id) ON DELETE SET NULL,
  offer_type offer_type NOT NULL DEFAULT 'DIRECT_BUYOUT',
  offered_total_price NUMERIC(12, 2) NOT NULL,
  pickup_cost_deduction NUMERIC(12, 2) NOT NULL DEFAULT 0.00,
  net_collector_earning NUMERIC(12, 2) NOT NULL,
  currency VARCHAR(10) NOT NULL DEFAULT 'INR',
  breakdown_json JSONB,
  status offer_status NOT NULL DEFAULT 'OFFERED',
  expires_at TIMESTAMPTZ(6) NOT NULL,
  created_at TIMESTAMPTZ(6) NOT NULL DEFAULT NOW(),
  responded_at TIMESTAMPTZ(6),
  CONSTRAINT check_net_earning CHECK (net_collector_earning = offered_total_price - pickup_cost_deduction)
);

CREATE INDEX idx_lot_offers_lot ON lot_offers (lot_id);
CREATE INDEX idx_lot_offers_recycler ON lot_offers (recycler_id);
CREATE INDEX idx_lot_offers_status ON lot_offers (status);

CREATE TABLE handovers (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  lot_id UUID NOT NULL REFERENCES lots(id) ON DELETE CASCADE,
  facility_id UUID REFERENCES recycler_facilities(id) ON DELETE SET NULL,
  handover_type handover_type NOT NULL,
  source_actor_id UUID NOT NULL REFERENCES users(id),
  destination_actor_id UUID NOT NULL REFERENCES users(id),
  handover_timestamp TIMESTAMPTZ(6) NOT NULL DEFAULT NOW(),
  latitude NUMERIC(10, 8),
  longitude NUMERIC(11, 8),
  location GEOGRAPHY(Point, 4326),
  qr_token_scanned VARCHAR(255),
  weighbridge_slip_number VARCHAR(100),
  weighbridge_gross_kg NUMERIC(12, 3),
  weighbridge_tare_kg NUMERIC(12, 3),
  weighbridge_net_kg NUMERIC(12, 3),
  scale_calibration_id VARCHAR(100),
  signed_manifest_hash VARCHAR(64),
  status handover_status NOT NULL DEFAULT 'PENDING',
  created_at TIMESTAMPTZ(6) NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_handovers_lot ON handovers (lot_id);
CREATE INDEX idx_handovers_location ON handovers USING GIST (location);

-- --------------------------------------------------------
-- 9. TRACEABILITY & EPR COMPLIANCE
-- --------------------------------------------------------

CREATE TABLE custody_events (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  lot_id UUID NOT NULL REFERENCES lots(id) ON DELETE CASCADE,
  sequence_number INT NOT NULL,
  event_type custody_event_type NOT NULL,
  actor_id UUID NOT NULL REFERENCES users(id),
  actor_role user_role NOT NULL,
  latitude NUMERIC(10, 8),
  longitude NUMERIC(11, 8),
  location GEOGRAPHY(Point, 4326),
  event_timestamp TIMESTAMPTZ(6) NOT NULL DEFAULT NOW(),
  event_payload_json JSONB NOT NULL,
  previous_event_hash VARCHAR(64) NOT NULL,
  current_event_hash VARCHAR(64) NOT NULL,
  digital_signature TEXT,
  created_at TIMESTAMPTZ(6) NOT NULL DEFAULT NOW(),
  CONSTRAINT uq_lot_sequence UNIQUE (lot_id, sequence_number)
);

CREATE INDEX idx_custody_events_lot ON custody_events (lot_id);
CREATE INDEX idx_custody_events_hash ON custody_events (current_event_hash);
CREATE INDEX idx_custody_events_timestamp ON custody_events (event_timestamp);

CREATE TABLE epr_certificates (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  certificate_number VARCHAR(100) NOT NULL UNIQUE,
  lot_id UUID NOT NULL REFERENCES lots(id) ON DELETE RESTRICT,
  recycler_id UUID NOT NULL REFERENCES recycler_companies(id) ON DELETE RESTRICT,
  total_weight_kg NUMERIC(12, 3) NOT NULL,
  material_category VARCHAR(100) NOT NULL,
  destruction_method VARCHAR(150) NOT NULL,
  certificate_hash VARCHAR(64) NOT NULL UNIQUE,
  spcb_filing_reference VARCHAR(100),
  issued_at TIMESTAMPTZ(6) NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_epr_certificates_recycler ON epr_certificates (recycler_id);
CREATE INDEX idx_epr_certificates_lot ON epr_certificates (lot_id);

-- --------------------------------------------------------
-- 10. TRANSACTIONS, ESCROW & PAYMENTS
-- --------------------------------------------------------

CREATE TABLE transactions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  reference_number VARCHAR(100) NOT NULL UNIQUE,
  transaction_type transaction_type NOT NULL,
  lot_id UUID REFERENCES lots(id) ON DELETE SET NULL,
  sender_user_id UUID REFERENCES users(id) ON DELETE SET NULL,
  recipient_user_id UUID REFERENCES users(id) ON DELETE SET NULL,
  amount NUMERIC(12, 2) NOT NULL CHECK (amount >= 0),
  currency VARCHAR(10) NOT NULL DEFAULT 'INR',
  status transaction_status NOT NULL DEFAULT 'PENDING',
  notes TEXT,
  created_at TIMESTAMPTZ(6) NOT NULL DEFAULT NOW(),
  settled_at TIMESTAMPTZ(6)
);

CREATE INDEX idx_transactions_reference ON transactions (reference_number);
CREATE INDEX idx_transactions_lot ON transactions (lot_id);
CREATE INDEX idx_transactions_status ON transactions (status);

CREATE TABLE escrow_holds (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  transaction_id UUID NOT NULL UNIQUE REFERENCES transactions(id) ON DELETE CASCADE,
  recycler_id UUID NOT NULL REFERENCES recycler_companies(id) ON DELETE RESTRICT,
  held_amount NUMERIC(12, 2) NOT NULL CHECK (held_amount > 0),
  currency VARCHAR(10) NOT NULL DEFAULT 'INR',
  status escrow_status NOT NULL DEFAULT 'ACTIVE',
  locked_at TIMESTAMPTZ(6) NOT NULL DEFAULT NOW(),
  released_at TIMESTAMPTZ(6)
);

CREATE INDEX idx_escrow_holds_recycler ON escrow_holds (recycler_id);
CREATE INDEX idx_escrow_holds_status ON escrow_holds (status);

CREATE TABLE payment_payouts (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  transaction_id UUID NOT NULL UNIQUE REFERENCES transactions(id) ON DELETE CASCADE,
  collector_id UUID NOT NULL REFERENCES collector_profiles(id) ON DELETE RESTRICT,
  payout_method payout_method NOT NULL DEFAULT 'UPI',
  gateway_reference VARCHAR(150) UNIQUE,
  gateway_response_json JSONB,
  amount NUMERIC(12, 2) NOT NULL CHECK (amount > 0),
  currency VARCHAR(10) NOT NULL DEFAULT 'INR',
  status payout_status NOT NULL DEFAULT 'INITIATED',
  initiated_at TIMESTAMPTZ(6) NOT NULL DEFAULT NOW(),
  completed_at TIMESTAMPTZ(6)
);

CREATE INDEX idx_payment_payouts_collector ON payment_payouts (collector_id);
CREATE INDEX idx_payment_payouts_status ON payment_payouts (status);

-- --------------------------------------------------------
-- 11. AUDIT & COMPLIANCE LOGS
-- --------------------------------------------------------

CREATE TABLE audit_logs (
  id BIGSERIAL PRIMARY KEY,
  entity_name VARCHAR(100) NOT NULL,
  entity_id VARCHAR(100) NOT NULL,
  action audit_action NOT NULL,
  actor_id UUID REFERENCES users(id) ON DELETE SET NULL,
  ip_address VARCHAR(45),
  user_agent TEXT,
  before_state JSONB,
  after_state JSONB,
  reason TEXT,
  created_at TIMESTAMPTZ(6) NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_audit_logs_entity ON audit_logs (entity_name, entity_id);
CREATE INDEX idx_audit_logs_actor ON audit_logs (actor_id);
CREATE INDEX idx_audit_logs_created ON audit_logs (created_at);
