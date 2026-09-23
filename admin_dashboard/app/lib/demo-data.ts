export interface DemoCollector {
  id: string;
  name: string;
  hub: string;
  phone: string;
  totalKgStaged: number;
  lotsCount: number;
  trustScore: number;
  kycStatus: 'VERIFIED' | 'PENDING';
  kycDocType: string;
  lastActive: string;
}

export interface DemoRecycler {
  id: string;
  companyName: string;
  cpcbRegistrationNo: string;
  location: string;
  monthlyCapacityKg: number;
  lotsReceived: number;
  operatingStatus: 'VERIFIED' | 'PENDING_AUDIT';
  weighbridgeScaleId: string;
  lastIntake: string;
}

export interface DemoLot {
  id: string;
  lotCode: string;
  materialName: string;
  category: 'PCBs' | 'Batteries' | 'Glass/CRTs' | 'Telecom' | 'Mixed';
  collectorName: string;
  collectorHub: string;
  recyclerName?: string;
  estimatedWeightKg: number;
  verifiedWeightKg?: number;
  aiClassification: string;
  aiConfidence: number;
  hazardCondition: 'NORMAL' | 'SWOLLEN_BATTERY' | 'BROKEN_CRT_LEAD' | 'BURNT_PCB';
  hazardSeverity: 'NONE' | 'CRITICAL' | 'MODERATE' | 'LOW';
  status: 'COLLECTED' | 'ACCEPTED' | 'HANDED_OVER' | 'SETTLED';
  agreedPricePerKg: number;
  totalValueInr: number;
  isTraceable: boolean;
  custodyHash: string;
  createdAt: string;
  weighbridgeSlip?: string;
}

export interface DemoTransaction {
  id: string;
  referenceNo: string;
  lotCode: string;
  collectorName: string;
  recyclerName: string;
  verifiedWeightKg: number;
  agreedPricePerKg: number;
  totalAmountInr: number;
  paymentMethod: 'IMMEDIATE_UPI' | 'WEIGHBRIDGE_CASH' | 'NEFT_ESCROW';
  settledAt: string;
  weighbridgeSlip: string;
  custodyHash: string;
}

export const DEMO_DATA_DISCLAIMER = {
  isDemo: true,
  badgeText: "DEMO DATA",
  simulationNotice:
    "SIMULATION TELEMETRY: The figures displayed across this dashboard (12 Collectors, 8 Recyclers, 47 Lots, 32 Transactions, 284 kg Formalized E-Waste, 96% Traceable Lots) are test fixtures for demonstration and architecture evaluation. They do not constitute certified statutory filings or live field claims.",
  lastSyncTimestamp: "2026-09-23T08:45:00+05:30",
  environment: "STAGING_SIMULATION",
};

export const DEMO_SUMMARY_METRICS = {
  collectorsActive: 12,
  verifiedRecyclers: 8,
  lotsCreated: 47,
  transactions: 32,
  formalizedEwasteKg: 284,
  traceableLotsPercent: 96,
  traceableLotsCount: 45,
  totalDisbursedInr: 412850,
  averageIntakeWeightKg: 8.87,
  hazardAlertCount: 4,
};

export const DEMO_COLLECTORS: DemoCollector[] = [
  { id: 'col-01', name: 'Ramesh Kumar', hub: 'Dharavi 13th Compound', phone: '+91 98201 14201', totalKgStaged: 34.2, lotsCount: 6, trustScore: 98, kycStatus: 'VERIFIED', kycDocType: 'Aadhaar Verified', lastActive: '12 mins ago' },
  { id: 'col-02', name: 'Sunita Devi', hub: 'Kurla West E-Cluster', phone: '+91 98330 91823', totalKgStaged: 28.5, lotsCount: 5, trustScore: 96, kycStatus: 'VERIFIED', kycDocType: 'Aadhaar Verified', lastActive: '25 mins ago' },
  { id: 'col-03', name: 'Imran Sheikh', hub: 'Sakinaka Aggregator Guild', phone: '+91 97690 44109', totalKgStaged: 42.1, lotsCount: 7, trustScore: 99, kycStatus: 'VERIFIED', kycDocType: 'Voter ID Verified', lastActive: '4 mins ago' },
  { id: 'col-04', name: 'Vijay Mane', hub: 'Chembur Scrap Depot', phone: '+91 98199 87621', totalKgStaged: 22.4, lotsCount: 4, trustScore: 94, kycStatus: 'VERIFIED', kycDocType: 'Aadhaar Verified', lastActive: '1 hr ago' },
  { id: 'col-05', name: 'Rajeshwari P.', hub: 'Bandra Reclamation Guild', phone: '+91 98212 34509', totalKgStaged: 19.3, lotsCount: 3, trustScore: 95, kycStatus: 'VERIFIED', kycDocType: 'PAN Card Verified', lastActive: '2 hrs ago' },
  { id: 'col-06', name: 'Amit Jadhav', hub: 'Goregaon West Hub', phone: '+91 97022 89012', totalKgStaged: 26.0, lotsCount: 4, trustScore: 97, kycStatus: 'VERIFIED', kycDocType: 'Aadhaar Verified', lastActive: '45 mins ago' },
  { id: 'col-07', name: 'Mohammad Arif', hub: 'Govandi Dumping Ground Perimeter', phone: '+91 98920 65123', totalKgStaged: 31.8, lotsCount: 5, trustScore: 98, kycStatus: 'VERIFIED', kycDocType: 'Aadhaar Verified', lastActive: '18 mins ago' },
  { id: 'col-08', name: 'Anita Shinde', hub: 'Mulund Check Naka Aggregator', phone: '+91 98670 12984', totalKgStaged: 18.2, lotsCount: 3, trustScore: 93, kycStatus: 'VERIFIED', kycDocType: 'Aadhaar Verified', lastActive: '3 hrs ago' },
  { id: 'col-09', name: 'Santosh Kadam', hub: 'Kalyan Scrap Yard', phone: '+91 99300 78219', totalKgStaged: 21.0, lotsCount: 3, trustScore: 92, kycStatus: 'VERIFIED', kycDocType: 'Voter ID Verified', lastActive: '4 hrs ago' },
  { id: 'col-10', name: 'Fatima Begum', hub: 'Mankhurd E-Waste Guild', phone: '+91 98191 67234', totalKgStaged: 15.4, lotsCount: 2, trustScore: 94, kycStatus: 'VERIFIED', kycDocType: 'Aadhaar Verified', lastActive: '5 hrs ago' },
  { id: 'col-11', name: 'Ganesh Patil', hub: 'Thane MIDC Wagle Estate', phone: '+91 98205 90128', totalKgStaged: 25.1, lotsCount: 4, trustScore: 96, kycStatus: 'VERIFIED', kycDocType: 'Aadhaar Verified', lastActive: '1 hr ago' },
  { id: 'col-12', name: 'Deepak Chauhan', hub: 'Andheri East Industrial Hub', phone: '+91 98700 34190', totalKgStaged: 33.0, lotsCount: 5, trustScore: 99, kycStatus: 'VERIFIED', kycDocType: 'PAN Card Verified', lastActive: '30 mins ago' },
];

export const DEMO_RECYCLERS: DemoRecycler[] = [
  { id: 'rec-01', companyName: 'EcoRecycle Maharashtra Pvt Ltd', cpcbRegistrationNo: 'CPCB-MH-2024-0891', location: 'Navi Mumbai, TTC Industrial Area', monthlyCapacityKg: 15000, lotsReceived: 11, operatingStatus: 'VERIFIED', weighbridgeScaleId: 'SCALE-WB-8812', lastIntake: '15 mins ago' },
  { id: 'rec-02', companyName: 'Western Smelting & Refining Corp', cpcbRegistrationNo: 'CPCB-MH-2023-0412', location: 'Taloja MIDC, Raigad', monthlyCapacityKg: 25000, lotsReceived: 9, operatingStatus: 'VERIFIED', weighbridgeScaleId: 'SCALE-WB-4109', lastIntake: '40 mins ago' },
  { id: 'rec-03', companyName: 'GreenTech Circular Alloys Ltd', cpcbRegistrationNo: 'CPCB-MH-2024-1102', location: 'Mahape, Navi Mumbai', monthlyCapacityKg: 10000, lotsReceived: 6, operatingStatus: 'VERIFIED', weighbridgeScaleId: 'SCALE-WB-9923', lastIntake: '2 hrs ago' },
  { id: 'rec-04', companyName: 'Apex Urban Mining & E-Waste Ltd', cpcbRegistrationNo: 'CPCB-MH-2022-0199', location: 'Dombivli MIDC Phase II', monthlyCapacityKg: 30000, lotsReceived: 8, operatingStatus: 'VERIFIED', weighbridgeScaleId: 'SCALE-WB-3341', lastIntake: '1 hr ago' },
  { id: 'rec-05', companyName: 'MahaEwaste Hydrometallurgical', cpcbRegistrationNo: 'CPCB-MH-2024-1422', location: 'Rabale MIDC', monthlyCapacityKg: 12000, lotsReceived: 5, operatingStatus: 'VERIFIED', weighbridgeScaleId: 'SCALE-WB-7104', lastIntake: '3 hrs ago' },
  { id: 'rec-06', companyName: 'Phoenix Metallurgical Solutions', cpcbRegistrationNo: 'CPCB-MH-2023-0781', location: 'Ambernath Industrial Belt', monthlyCapacityKg: 20000, lotsReceived: 4, operatingStatus: 'VERIFIED', weighbridgeScaleId: 'SCALE-WB-2190', lastIntake: '5 hrs ago' },
  { id: 'rec-07', companyName: 'CleanEarth Hydrometallurgy Ltd', cpcbRegistrationNo: 'CPCB-MH-2024-0988', location: 'Turbhe MIDC, Sector 20', monthlyCapacityKg: 8000, lotsReceived: 3, operatingStatus: 'VERIFIED', weighbridgeScaleId: 'SCALE-WB-5561', lastIntake: '6 hrs ago' },
  { id: 'rec-08', companyName: 'Sahyadri Precious Metals Recovery', cpcbRegistrationNo: 'CPCB-MH-2023-0301', location: 'Panvel Industrial Zone', monthlyCapacityKg: 18000, lotsReceived: 1, operatingStatus: 'VERIFIED', weighbridgeScaleId: 'SCALE-WB-6209', lastIntake: '1 day ago' },
];

export const DEMO_LOTS: DemoLot[] = [
  {
    id: 'lot-001',
    lotCode: 'LOT-2026-047',
    materialName: 'High-Grade Telecom Server Motherboards',
    category: 'PCBs',
    collectorName: 'Imran Sheikh',
    collectorHub: 'Sakinaka Aggregator Guild',
    recyclerName: 'EcoRecycle Maharashtra Pvt Ltd',
    estimatedWeightKg: 11.5,
    verifiedWeightKg: 11.2,
    aiClassification: 'Server Multi-Layer PCB (Gold/Palladium contacts)',
    aiConfidence: 0.984,
    hazardCondition: 'NORMAL',
    hazardSeverity: 'NONE',
    status: 'SETTLED',
    agreedPricePerKg: 1450,
    totalValueInr: 16240,
    isTraceable: true,
    custodyHash: '3f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a',
    createdAt: '2026-09-23T08:15:00+05:30',
    weighbridgeSlip: 'WB-2026-9821',
  },
  {
    id: 'lot-002',
    lotCode: 'LOT-2026-046',
    materialName: 'Swollen Li-Ion Pouch Batteries (Laptops)',
    category: 'Batteries',
    collectorName: 'Ramesh Kumar',
    collectorHub: 'Dharavi 13th Compound',
    recyclerName: 'Apex Urban Mining & E-Waste Ltd',
    estimatedWeightKg: 6.8,
    verifiedWeightKg: 6.5,
    aiClassification: 'Lithium Cobalt Oxide (LCO) Cells',
    aiConfidence: 0.962,
    hazardCondition: 'SWOLLEN_BATTERY',
    hazardSeverity: 'CRITICAL',
    status: 'SETTLED',
    agreedPricePerKg: 380,
    totalValueInr: 2470,
    isTraceable: true,
    custodyHash: '8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c',
    createdAt: '2026-09-23T07:50:00+05:30',
    weighbridgeSlip: 'WB-2026-9819',
  },
  {
    id: 'lot-003',
    lotCode: 'LOT-2026-045',
    materialName: 'Broken CRT Television Lead Funnel Glass',
    category: 'Glass/CRTs',
    collectorName: 'Deepak Chauhan',
    collectorHub: 'Andheri East Industrial Hub',
    recyclerName: 'Western Smelting & Refining Corp',
    estimatedWeightKg: 18.0,
    verifiedWeightKg: 17.6,
    aiClassification: 'Leaded Silicate CRT Funnel Glass',
    aiConfidence: 0.941,
    hazardCondition: 'BROKEN_CRT_LEAD',
    hazardSeverity: 'MODERATE',
    status: 'SETTLED',
    agreedPricePerKg: 45,
    totalValueInr: 792,
    isTraceable: true,
    custodyHash: '1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f',
    createdAt: '2026-09-23T07:20:00+05:30',
    weighbridgeSlip: 'WB-2026-9814',
  },
  {
    id: 'lot-004',
    lotCode: 'LOT-2026-044',
    materialName: 'Telecom Copper Wire & Deflection Coils',
    category: 'Telecom',
    collectorName: 'Mohammad Arif',
    collectorHub: 'Govandi Perimeter',
    recyclerName: 'GreenTech Circular Alloys Ltd',
    estimatedWeightKg: 14.5,
    verifiedWeightKg: 14.2,
    aiClassification: 'Electrolytic Tough Pitch Copper (99.9% Cu)',
    aiConfidence: 0.978,
    hazardCondition: 'NORMAL',
    hazardSeverity: 'NONE',
    status: 'SETTLED',
    agreedPricePerKg: 680,
    totalValueInr: 9656,
    isTraceable: true,
    custodyHash: '4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c',
    createdAt: '2026-09-23T06:55:00+05:30',
    weighbridgeSlip: 'WB-2026-9808',
  },
  {
    id: 'lot-005',
    lotCode: 'LOT-2026-043',
    materialName: 'Mixed Desktop Motherboards (Socket 775/1155)',
    category: 'PCBs',
    collectorName: 'Sunita Devi',
    collectorHub: 'Kurla West E-Cluster',
    recyclerName: 'EcoRecycle Maharashtra Pvt Ltd',
    estimatedWeightKg: 12.0,
    verifiedWeightKg: 11.8,
    aiClassification: 'Mid-Grade Multi-IC Desktop PCBs',
    aiConfidence: 0.965,
    hazardCondition: 'NORMAL',
    hazardSeverity: 'NONE',
    status: 'SETTLED',
    agreedPricePerKg: 620,
    totalValueInr: 7316,
    isTraceable: true,
    custodyHash: '7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f',
    createdAt: '2026-09-23T06:30:00+05:30',
    weighbridgeSlip: 'WB-2026-9802',
  },
  {
    id: 'lot-006',
    lotCode: 'LOT-2026-042',
    materialName: 'Burnt Power Supply PCBs (Phenolic Resin)',
    category: 'PCBs',
    collectorName: 'Amit Jadhav',
    collectorHub: 'Goregaon West Hub',
    recyclerName: 'MahaEwaste Hydrometallurgical',
    estimatedWeightKg: 8.5,
    verifiedWeightKg: 8.2,
    aiClassification: 'Single-Sided Low-Grade Power Supply Board',
    aiConfidence: 0.932,
    hazardCondition: 'BURNT_PCB',
    hazardSeverity: 'LOW',
    status: 'SETTLED',
    agreedPricePerKg: 120,
    totalValueInr: 984,
    isTraceable: true,
    custodyHash: '0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c',
    createdAt: '2026-09-23T06:05:00+05:30',
    weighbridgeSlip: 'WB-2026-9799',
  },
  {
    id: 'lot-007',
    lotCode: 'LOT-2026-041',
    materialName: 'Telecom BTS Radio Relay Units',
    category: 'Telecom',
    collectorName: 'Ganesh Patil',
    collectorHub: 'Thane MIDC Wagle Estate',
    recyclerName: 'Apex Urban Mining & E-Waste Ltd',
    estimatedWeightKg: 15.0,
    verifiedWeightKg: 14.8,
    aiClassification: 'Telecom Transceiver Units with Gold-Plated Pins',
    aiConfidence: 0.989,
    hazardCondition: 'NORMAL',
    hazardSeverity: 'NONE',
    status: 'SETTLED',
    agreedPricePerKg: 950,
    totalValueInr: 14060,
    isTraceable: true,
    custodyHash: '2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e',
    createdAt: '2026-09-23T05:40:00+05:30',
    weighbridgeSlip: 'WB-2026-9791',
  },
  {
    id: 'lot-008',
    lotCode: 'LOT-2026-040',
    materialName: 'Smartphone Logic Boards & RAM Sticks',
    category: 'PCBs',
    collectorName: 'Vijay Mane',
    collectorHub: 'Chembur Scrap Depot',
    recyclerName: 'Phoenix Metallurgical Solutions',
    estimatedWeightKg: 5.2,
    verifiedWeightKg: 5.0,
    aiClassification: 'Ultra High-Grade SMD Gold Plated Cellular PCBs',
    aiConfidence: 0.991,
    hazardCondition: 'NORMAL',
    hazardSeverity: 'NONE',
    status: 'SETTLED',
    agreedPricePerKg: 3200,
    totalValueInr: 16000,
    isTraceable: true,
    custodyHash: '5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b',
    createdAt: '2026-09-23T05:15:00+05:30',
    weighbridgeSlip: 'WB-2026-9788',
  },
  {
    id: 'lot-009',
    lotCode: 'LOT-2026-039',
    materialName: '18650 Cylindrical Battery Modules',
    category: 'Batteries',
    collectorName: 'Imran Sheikh',
    collectorHub: 'Sakinaka Aggregator Guild',
    recyclerName: 'EcoRecycle Maharashtra Pvt Ltd',
    estimatedWeightKg: 9.0,
    verifiedWeightKg: 8.8,
    aiClassification: 'NMC 18650 Power Tool Packs',
    aiConfidence: 0.957,
    hazardCondition: 'SWOLLEN_BATTERY',
    hazardSeverity: 'CRITICAL',
    status: 'SETTLED',
    agreedPricePerKg: 420,
    totalValueInr: 3696,
    isTraceable: true,
    custodyHash: '7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d',
    createdAt: '2026-09-22T21:45:00+05:30',
    weighbridgeSlip: 'WB-2026-9774',
  },
  {
    id: 'lot-010',
    lotCode: 'LOT-2026-038',
    materialName: 'Staged Optical Fiber Transceivers & Router Cards',
    category: 'Telecom',
    collectorName: 'Rajeshwari P.',
    collectorHub: 'Bandra Reclamation Guild',
    recyclerName: 'Western Smelting & Refining Corp',
    estimatedWeightKg: 7.2,
    verifiedWeightKg: undefined,
    aiClassification: 'Telecom SFP Transceivers',
    aiConfidence: 0.948,
    hazardCondition: 'NORMAL',
    hazardSeverity: 'NONE',
    status: 'ACCEPTED',
    agreedPricePerKg: 850,
    totalValueInr: 6120,
    isTraceable: true,
    custodyHash: '9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f',
    createdAt: '2026-09-23T08:30:00+05:30',
  },
  {
    id: 'lot-011',
    lotCode: 'LOT-2026-037',
    materialName: 'Cracked CRT Monitor Shadow Masks & Neck Assemblies',
    category: 'Glass/CRTs',
    collectorName: 'Santosh Kadam',
    collectorHub: 'Kalyan Scrap Yard',
    recyclerName: undefined,
    estimatedWeightKg: 10.4,
    verifiedWeightKg: undefined,
    aiClassification: 'Heavy Lead Glass with Electron Gun Mount',
    aiConfidence: 0.912,
    hazardCondition: 'BROKEN_CRT_LEAD',
    hazardSeverity: 'CRITICAL',
    status: 'COLLECTED',
    agreedPricePerKg: 50,
    totalValueInr: 520,
    isTraceable: false,
    custodyHash: 'PENDING_INITIAL_MERKLE_ANCHOR',
    createdAt: '2026-09-23T08:42:00+05:30',
  },
  {
    id: 'lot-012',
    lotCode: 'LOT-2026-036',
    materialName: 'Mixed Small Domestic E-Waste (Appliances)',
    category: 'Mixed',
    collectorName: 'Fatima Begum',
    collectorHub: 'Mankhurd E-Waste Guild',
    recyclerName: undefined,
    estimatedWeightKg: 8.0,
    verifiedWeightKg: undefined,
    aiClassification: 'Low grade mixed iron/copper small scrap',
    aiConfidence: 0.887,
    hazardCondition: 'NORMAL',
    hazardSeverity: 'NONE',
    status: 'COLLECTED',
    agreedPricePerKg: 90,
    totalValueInr: 720,
    isTraceable: false,
    custodyHash: 'PENDING_INITIAL_MERKLE_ANCHOR',
    createdAt: '2026-09-23T08:44:00+05:30',
  },
];

export const DEMO_TRANSACTIONS: DemoTransaction[] = [
  { id: 'tx-001', referenceNo: 'TXN-2026-032', lotCode: 'LOT-2026-047', collectorName: 'Imran Sheikh', recyclerName: 'EcoRecycle Maharashtra', verifiedWeightKg: 11.2, agreedPricePerKg: 1450, totalAmountInr: 16240, paymentMethod: 'IMMEDIATE_UPI', settledAt: '2026-09-23 08:34', weighbridgeSlip: 'WB-2026-9821', custodyHash: '3f7a8b9c...f7a' },
  { id: 'tx-002', referenceNo: 'TXN-2026-031', lotCode: 'LOT-2026-046', collectorName: 'Ramesh Kumar', recyclerName: 'Apex Urban Mining', verifiedWeightKg: 6.5, agreedPricePerKg: 380, totalAmountInr: 2470, paymentMethod: 'WEIGHBRIDGE_CASH', settledAt: '2026-09-23 08:12', weighbridgeSlip: 'WB-2026-9819', custodyHash: '8b9c0d1e...9c' },
  { id: 'tx-003', referenceNo: 'TXN-2026-030', lotCode: 'LOT-2026-045', collectorName: 'Deepak Chauhan', recyclerName: 'Western Smelting', verifiedWeightKg: 17.6, agreedPricePerKg: 45, totalAmountInr: 792, paymentMethod: 'IMMEDIATE_UPI', settledAt: '2026-09-23 07:45', weighbridgeSlip: 'WB-2026-9814', custodyHash: '1e2f3a4b...2f' },
  { id: 'tx-004', referenceNo: 'TXN-2026-029', lotCode: 'LOT-2026-044', collectorName: 'Mohammad Arif', recyclerName: 'GreenTech Circular', verifiedWeightKg: 14.2, agreedPricePerKg: 680, totalAmountInr: 9656, paymentMethod: 'IMMEDIATE_UPI', settledAt: '2026-09-23 07:15', weighbridgeSlip: 'WB-2026-9808', custodyHash: '4b5c6d7e...5c' },
  { id: 'tx-005', referenceNo: 'TXN-2026-028', lotCode: 'LOT-2026-043', collectorName: 'Sunita Devi', recyclerName: 'EcoRecycle Maharashtra', verifiedWeightKg: 11.8, agreedPricePerKg: 620, totalAmountInr: 7316, paymentMethod: 'IMMEDIATE_UPI', settledAt: '2026-09-23 06:48', weighbridgeSlip: 'WB-2026-9802', custodyHash: '7e8f9a0b...8f' },
  { id: 'tx-006', referenceNo: 'TXN-2026-027', lotCode: 'LOT-2026-042', collectorName: 'Amit Jadhav', recyclerName: 'MahaEwaste Hydrometallurgical', verifiedWeightKg: 8.2, agreedPricePerKg: 120, totalAmountInr: 984, paymentMethod: 'WEIGHBRIDGE_CASH', settledAt: '2026-09-23 06:22', weighbridgeSlip: 'WB-2026-9799', custodyHash: '0b1c2d3e...1c' },
  { id: 'tx-007', referenceNo: 'TXN-2026-026', lotCode: 'LOT-2026-041', collectorName: 'Ganesh Patil', recyclerName: 'Apex Urban Mining', verifiedWeightKg: 14.8, agreedPricePerKg: 950, totalAmountInr: 14060, paymentMethod: 'IMMEDIATE_UPI', settledAt: '2026-09-23 05:58', weighbridgeSlip: 'WB-2026-9791', custodyHash: '2d3e4f5a...3e' },
  { id: 'tx-008', referenceNo: 'TXN-2026-025', lotCode: 'LOT-2026-040', collectorName: 'Vijay Mane', recyclerName: 'Phoenix Metallurgical', verifiedWeightKg: 5.0, agreedPricePerKg: 3200, totalAmountInr: 16000, paymentMethod: 'NEFT_ESCROW', settledAt: '2026-09-23 05:30', weighbridgeSlip: 'WB-2026-9788', custodyHash: '5a6b7c8d...6b' },
  { id: 'tx-009', referenceNo: 'TXN-2026-024', lotCode: 'LOT-2026-039', collectorName: 'Imran Sheikh', recyclerName: 'EcoRecycle Maharashtra', verifiedWeightKg: 8.8, agreedPricePerKg: 420, totalAmountInr: 3696, paymentMethod: 'IMMEDIATE_UPI', settledAt: '2026-09-22 22:04', weighbridgeSlip: 'WB-2026-9774', custodyHash: '7c8d9e0f...8d' },
];

export const MATERIAL_VOLUME_BREAKDOWN = [
  { name: 'Printed Circuit Boards (PCBs)', weightKg: 112.4, sharePct: 39.6, color: '#10b981', badge: 'High Value Gold/Pd' },
  { name: 'Telecom & Networking Relays', weightKg: 74.2, sharePct: 26.1, color: '#06b6d4', badge: 'High Grade Copper' },
  { name: 'CRT & Monitor Leaded Glass', weightKg: 56.8, sharePct: 20.0, color: '#f59e0b', badge: 'Hazard Managed' },
  { name: 'Lithium-Ion Battery Modules', weightKg: 40.6, sharePct: 14.3, color: '#f43f5e', badge: 'Special Safety PPE' },
];
