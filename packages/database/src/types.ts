// Database Enums & Entity Types

export type UserRole =
  | 'COLLECTOR'
  | 'RECYCLER_OPERATOR'
  | 'RECYCLER_ADMIN'
  | 'PLATFORM_ADMIN'
  | 'AUDITOR';

export type UserStatus =
  | 'ACTIVE'
  | 'SUSPENDED'
  | 'PENDING_VERIFICATION'
  | 'INACTIVE';

export type CollectorType =
  | 'INDIVIDUAL_PICKER'
  | 'KABADIWALA'
  | 'SCRAP_AGGREGATOR'
  | 'COMMUNITY_ENTERPRISE';

export type PermitType =
  | 'HAZARDOUS_WASTE_AUTHORIZATION'
  | 'E_WASTE_DISMANTLER'
  | 'E_WASTE_RECYCLER'
  | 'PRO_PRODUCER_RESPONSIBILITY_ORG'
  | 'REFURBISHER';

export type PermitStatus =
  | 'ACTIVE'
  | 'EXPIRED'
  | 'REVOKED'
  | 'PENDING_RENEWAL'
  | 'SUSPENDED';

export type HazardSeverity = 'INFO' | 'WARNING' | 'DANGER' | 'CRITICAL';

export type HazardCondition =
  | 'NORMAL'
  | 'SWOLLEN_BATTERY'
  | 'LEAKING_ELECTROLYTE'
  | 'BROKEN_CRT_GLASS'
  | 'BURNT_COMPONENTS'
  | 'MERCURY_CONTAINING'
  | 'CORRODED_TERMINALS';

export type LotStatus =
  | 'DRAFT'
  | 'PENDING_SYNC'
  | 'COLLECTED'
  | 'OFFERED'
  | 'ACCEPTED'
  | 'IN_TRANSIT'
  | 'DELIVERED'
  | 'VERIFIED'
  | 'SETTLED'
  | 'CANCELLED'
  | 'DISPUTED';

export type OfferType = 'DIRECT_BUYOUT' | 'BID' | 'SCHEDULED_PICKUP';

export type OfferStatus =
  | 'OFFERED'
  | 'ACCEPTED'
  | 'REJECTED'
  | 'EXPIRED'
  | 'COUNTERED';

export type HandoverType =
  | 'COLLECTOR_TO_TRANSPORTER'
  | 'COLLECTOR_TO_FACILITY'
  | 'TRANSPORTER_TO_FACILITY';

export type HandoverStatus =
  | 'PENDING'
  | 'COMPLETED'
  | 'DISPUTED'
  | 'REJECTED';

export type CustodyEventType =
  | 'CREATION'
  | 'HAZARD_FLAGGED'
  | 'OFFER_ACCEPTED'
  | 'HANDOVER_INITIATED'
  | 'FACILITY_INTAKE'
  | 'WEIGHBRIDGE_CONFIRMED'
  | 'MATERIAL_SORTED'
  | 'PAYMENT_DISBURSED'
  | 'DISMANTLED'
  | 'RECYCLED'
  | 'EPR_CERTIFICATE_ISSUED';

export type TransactionType =
  | 'ESCROW_LOCK'
  | 'ESCROW_RELEASE'
  | 'COLLECTOR_PAYOUT'
  | 'PLATFORM_FEE'
  | 'RECYCLER_REFUND';

export type TransactionStatus =
  | 'PENDING'
  | 'HELD_IN_ESCROW'
  | 'SETTLED'
  | 'FAILED'
  | 'REFUNDED';

export type EscrowStatus = 'ACTIVE' | 'RELEASED' | 'FORFEITED' | 'DISPUTED';

export type PayoutMethod = 'UPI' | 'IMPS' | 'BANK_TRANSFER' | 'CASH_VOUCHER';

export type PayoutStatus =
  | 'INITIATED'
  | 'PROCESSING'
  | 'SUCCESS'
  | 'FAILURE'
  | 'REVERSED';

export type AuditAction =
  | 'CREATE'
  | 'UPDATE'
  | 'DELETE'
  | 'STATUS_CHANGE'
  | 'OVERRIDE'
  | 'LOGIN'
  | 'PERMISSION_CHANGE';
