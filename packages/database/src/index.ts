// @ecobridge/database client entrypoint

export * from './types';

export interface PostGISPoint {
  latitude: number;
  longitude: number;
}

/**
 * Format longitude & latitude into PostGIS WKT (Well-Known Text) format: POINT(lng lat)
 */
export function toPointWKT(point: PostGISPoint): string {
  return `SRID=4326;POINT(${point.longitude} ${point.latitude})`;
}

/**
 * Parse WKT POINT or GeoJSON coordinates into PostGISPoint
 */
export function parsePoint(wktOrCoordinates: string | [number, number]): PostGISPoint | null {
  if (Array.isArray(wktOrCoordinates)) {
    return {
      longitude: wktOrCoordinates[0],
      latitude: wktOrCoordinates[1],
    };
  }

  const match = wktOrCoordinates.match(/POINT\s*\(\s*([-\d.]+)\s+([-\d.]+)\s*\)/i);
  if (!match) return null;

  return {
    longitude: parseFloat(match[1]),
    latitude: parseFloat(match[2]),
  };
}

/**
 * Generates an append-only custody event payload hash using Node's crypto
 */
export function computeCustodyHash(
  previousHash: string,
  lotId: string,
  sequenceNumber: number,
  eventType: string,
  actorId: string,
  timestamp: string,
  payload: Record<string, unknown>
): string {
  // eslint-disable-next-line @typescript-eslint/no-var-requires
  const crypto = require('crypto');
  const serialized = JSON.stringify({
    previousHash,
    lotId,
    sequenceNumber,
    eventType,
    actorId,
    timestamp,
    payload,
  });
  return crypto.createHash('sha256').update(serialized).digest('hex');
}
