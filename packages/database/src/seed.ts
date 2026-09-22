// ECOBRIDGE Initial Database Seeder

export interface SeedCategory {
  code: string;
  name: string;
  description: string;
  defaultHazard: 'INFO' | 'WARNING' | 'DANGER' | 'CRITICAL';
}

export interface SeedMaterial {
  categoryCode: string;
  code: string;
  name: string;
  description: string;
  baseUnit: string;
  requiresPermit: boolean;
  standardYield: Record<string, number>;
  minPrice: number;
  maxPrice: number;
  benchmarkPrice: number;
}

export interface SeedSafetyRule {
  materialCode?: string;
  condition: string;
  severity: 'INFO' | 'WARNING' | 'DANGER' | 'CRITICAL';
  titleKey: string;
  messageKey: string;
  requiredPpe: string[];
  prohibitedActions: string[];
  audioPromptKey: string;
}

export const SEED_CATEGORIES: SeedCategory[] = [
  {
    code: 'CAT_ITEW',
    name: 'Information Technology & Telecom Equipment',
    description: 'Centralized data processing, servers, PCs, laptops, mobile phones, printers.',
    defaultHazard: 'WARNING',
  },
  {
    code: 'CAT_CEEW',
    name: 'Consumer Electricals & Electronics',
    description: 'Television sets, CRT monitors, audio amplifiers, refrigerators, microwave ovens.',
    defaultHazard: 'WARNING',
  },
  {
    code: 'CAT_BATT',
    name: 'Batteries & Energy Storage',
    description: 'Lithium-ion batteries, lead-acid batteries, nickel-cadmium accumulators.',
    defaultHazard: 'DANGER',
  },
  {
    code: 'CAT_COMP',
    name: 'Separated High-Purity Metal Components',
    description: 'Deflection yokes, transformers, copper windings, aluminum heatsinks.',
    defaultHazard: 'INFO',
  },
];

export const SEED_MATERIALS: SeedMaterial[] = [
  {
    categoryCode: 'CAT_ITEW',
    code: 'PCB_SERVER_GRADE_A',
    name: 'Server & Telecom Grade A Motherboards',
    description: 'High-grade gold plated motherboards with dual CPU sockets and high precious metal content.',
    baseUnit: 'KG',
    requiresPermit: false,
    standardYield: { Cu: 0.18, Au_ppm: 280, Ag_ppm: 900 },
    minPrice: 1100.0,
    maxPrice: 1550.0,
    benchmarkPrice: 1350.0,
  },
  {
    categoryCode: 'CAT_ITEW',
    code: 'PCB_PC_GRADE_B',
    name: 'Desktop & Laptop Grade B Motherboards',
    description: 'Standard consumer PC and laptop logic boards with green solder masks.',
    baseUnit: 'KG',
    requiresPermit: false,
    standardYield: { Cu: 0.15, Au_ppm: 80, Ag_ppm: 350 },
    minPrice: 420.0,
    maxPrice: 680.0,
    benchmarkPrice: 550.0,
  },
  {
    categoryCode: 'CAT_CEEW',
    code: 'PCB_CONSUMER_GRADE_C',
    name: 'Low-Grade Brown / Consumer PCBs',
    description: 'Single-sided phenolic boards from radios, power supplies, and televisions.',
    baseUnit: 'KG',
    requiresPermit: false,
    standardYield: { Cu: 0.08, Fe: 0.12 },
    minPrice: 80.0,
    maxPrice: 160.0,
    benchmarkPrice: 120.0,
  },
  {
    categoryCode: 'CAT_BATT',
    code: 'BATT_LI_ION_POUCH',
    name: 'Lithium-Ion Pouch & Mobile Batteries',
    description: 'Rechargeable secondary lithium cells extracted from mobile phones and tablets.',
    baseUnit: 'KG',
    requiresPermit: true,
    standardYield: { Co: 0.18, Li: 0.03, Ni: 0.05 },
    minPrice: 240.0,
    maxPrice: 380.0,
    benchmarkPrice: 310.0,
  },
  {
    categoryCode: 'CAT_BATT',
    code: 'BATT_LEAD_ACID',
    name: 'Automotive & Inverter Lead-Acid Batteries',
    description: 'Wet cell lead-acid accumulator blocks with sulphuric acid electrolyte.',
    baseUnit: 'KG',
    requiresPermit: true,
    standardYield: { Pb: 0.55 },
    minPrice: 90.0,
    maxPrice: 130.0,
    benchmarkPrice: 110.0,
  },
  {
    categoryCode: 'CAT_CEEW',
    code: 'CRT_LEADED_GLASS',
    name: 'Cathode Ray Tube (CRT) Funnel & Panel Glass',
    description: 'Heavy display glass containing up to 20% lead oxide in funnel sections.',
    baseUnit: 'KG',
    requiresPermit: true,
    standardYield: { Pb: 0.15 },
    minPrice: 5.0,
    maxPrice: 15.0,
    benchmarkPrice: 10.0,
  },
  {
    categoryCode: 'CAT_COMP',
    code: 'COPPER_DEFLECTION_YOKE',
    name: 'Copper Deflection Yokes & Transformers',
    description: 'High-purity enameled copper wire wound on ferrite cores.',
    baseUnit: 'KG',
    requiresPermit: false,
    standardYield: { Cu: 0.65, Ferrite: 0.35 },
    minPrice: 450.0,
    maxPrice: 620.0,
    benchmarkPrice: 540.0,
  },
];

export const SEED_SAFETY_RULES: SeedSafetyRule[] = [
  {
    materialCode: 'BATT_LI_ION_POUCH',
    condition: 'SWOLLEN_BATTERY',
    severity: 'DANGER',
    titleKey: 'safety.swollen_battery.title',
    messageKey: 'safety.swollen_battery.message',
    requiredPpe: ['HEAT_RESISTANT_GLOVES', 'SAFETY_GOGGLES', 'FIREPROOF_CONTAINER'],
    prohibitedActions: ['DO_NOT_PUNCTURE', 'DO_NOT_EXPOSE_TO_HEAT', 'DO_NOT_COMPRESS'],
    audioPromptKey: 'audio.alert.swollen_battery',
  },
  {
    materialCode: 'CRT_LEADED_GLASS',
    condition: 'BROKEN_CRT_GLASS',
    severity: 'DANGER',
    titleKey: 'safety.broken_crt.title',
    messageKey: 'safety.broken_crt.message',
    requiredPpe: ['CUT_RESISTANT_GLOVES', 'N95_RESPIRATOR', 'SAFETY_GOGGLES'],
    prohibitedActions: ['DO_NOT_INHALE_PHOSPHOR_DUST', 'DO_NOT_BREAK_IMPLOSION_BAND'],
    audioPromptKey: 'audio.alert.broken_crt',
  },
  {
    condition: 'BURNT_COMPONENTS',
    severity: 'WARNING',
    titleKey: 'safety.burnt_pcb.title',
    messageKey: 'safety.burnt_pcb.message',
    requiredPpe: ['NITRILE_GLOVES', 'ORGANIC_VAPOR_MASK'],
    prohibitedActions: ['NO_OPEN_FLAME_SMELTING', 'DO_NOT_WASH_IN_OPEN_DRAINS'],
    audioPromptKey: 'audio.alert.burnt_pcb',
  },
  {
    materialCode: 'BATT_LEAD_ACID',
    condition: 'LEAKING_ELECTROLYTE',
    severity: 'CRITICAL',
    titleKey: 'safety.leaking_acid.title',
    messageKey: 'safety.leaking_acid.message',
    requiredPpe: ['ACID_RESISTANT_APRON', 'HEAVY_RUBBER_GLOVES', 'FACE_SHIELD'],
    prohibitedActions: ['DO_NOT_TOUCH_BAREHANDED', 'NO_WATER_ON_CONCENTRATED_ACID'],
    audioPromptKey: 'audio.alert.leaking_acid',
  },
];

export const SEED_COMMODITY_PRICES = [
  { commoditySymbol: 'CU', exchangeSource: 'LME', currency: 'INR', spotPrice: 785.5, unit: 'KG' },
  { commoditySymbol: 'AU', exchangeSource: 'MCX', currency: 'INR', spotPrice: 6450000.0, unit: 'KG' },
  { commoditySymbol: 'AG', exchangeSource: 'MCX', currency: 'INR', spotPrice: 84500.0, unit: 'KG' },
  { commoditySymbol: 'AL', exchangeSource: 'LME', currency: 'INR', spotPrice: 215.0, unit: 'KG' },
  { commoditySymbol: 'PB', exchangeSource: 'LME', currency: 'INR', spotPrice: 185.0, unit: 'KG' },
  { commoditySymbol: 'LI', exchangeSource: 'DOMESTIC', currency: 'INR', spotPrice: 1750.0, unit: 'KG' },
];

export async function runSeed(): Promise<void> {
  console.log('🌱 Starting ECOBRIDGE Reference Data Seeding...');
  console.log(`- Loaded ${SEED_CATEGORIES.length} Categories`);
  console.log(`- Loaded ${SEED_MATERIALS.length} Materials`);
  console.log(`- Loaded ${SEED_SAFETY_RULES.length} Safety & Hazard Guidance Rules`);
  console.log(`- Loaded ${SEED_COMMODITY_PRICES.length} Commodity Base Prices`);
  console.log('✅ Seed dataset prepared successfully.');
}

if (require.main === module) {
  runSeed().catch((err) => {
    console.error('❌ Seeding failed:', err);
    process.exit(1);
  });
}
