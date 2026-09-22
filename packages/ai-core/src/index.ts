export type HazardLevel = 'NORMAL' | 'LOW' | 'MEDIUM' | 'HIGH';

export type MaterialClassification = {
  materialCode: string;
  confidence: number;
  hazard: HazardLevel;
};
