/**
 * ECOBRIDGE • Recycler Portal & Traceability Server
 * Zero-dependency Node.js HTTP server serving static frontend assets and REST API endpoints.
 */

const http = require('http');
const fs = require('fs');
const path = require('path');
const url = require('url');

const PORT = process.env.PORT || 3001;
const PUBLIC_DIR = path.join(__dirname, 'public');
const DATASETS_DIR = path.join(__dirname, '..', '..', 'datasets', 'operational');

// MIME types dictionary
const MIME_TYPES = {
  '.html': 'text/html; charset=UTF-8',
  '.css': 'text/css; charset=UTF-8',
  '.js': 'application/javascript; charset=UTF-8',
  '.json': 'application/json; charset=UTF-8',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.svg': 'image/svg+xml',
  '.ico': 'image/x-icon',
  '.woff2': 'font/woff2',
  '.woff': 'font/woff',
  '.ttf': 'font/ttf'
};

// In-memory mock traceability data cache
let operationalTraceability = [];
try {
  const tracePath = path.join(DATASETS_DIR, 'traceability.json');
  if (fs.existsSync(tracePath)) {
    operationalTraceability = JSON.parse(fs.readFileSync(tracePath, 'utf8'));
    console.log(`[Ecobridge Server] Loaded ${operationalTraceability.length} records from operational/traceability.json`);
  }
} catch (err) {
  console.warn('[Ecobridge Server] Could not read operational/traceability.json:', err.message);
}

const server = http.createServer((req, res) => {
  const parsedUrl = url.parse(req.url, true);
  const pathname = parsedUrl.pathname;

  // Add CORS headers
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization, Idempotency-Key');

  if (req.method === 'OPTIONS') {
    res.writeHead(204);
    res.end();
    return;
  }

  // 1. API Route: GET /api/v1/traceability/:lot_id
  if (pathname.startsWith('/api/v1/traceability/')) {
    const lotId = decodeURIComponent(pathname.replace('/api/v1/traceability/', '')).toUpperCase();
    
    // Check for operational dataset match
    const foundRecord = operationalTraceability.find(r => 
      (r.unique_lot_id && r.unique_lot_id.toUpperCase() === lotId) ||
      (r.short_code && r.short_code.toUpperCase() === lotId)
    );

    const responsePayload = {
      success: true,
      timestamp: new Date().toISOString(),
      data: {
        lot_id: lotId,
        source: foundRecord ? "operational_database" : "verified_simulated_ledger",
        record: foundRecord || null
      }
    };

    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify(responsePayload, null, 2));
    return;
  }

  // 1b. API Route: POST /api/v1/payments/confirm
  if (pathname === '/api/v1/payments/confirm' && req.method === 'POST') {
    let body = '';
    req.on('data', chunk => { body += chunk.toString(); });
    req.on('end', () => {
      let parsed = {};
      try { parsed = JSON.parse(body); } catch (e) {}
      const method = parsed.payment_method || 'CASH';
      const amount = parsed.amount || 6407.40;
      const lotId = parsed.lot_id || 'ECO-26-MH-004821';
      const txnRef = method === 'CASH' ? `CSH-MH26-4821-${Math.floor(100+Math.random()*900)}` : `UPI/${Date.now()}/AXIS`;

      const responsePayload = {
        success: true,
        timestamp: new Date().toISOString(),
        data: {
          lot_id: lotId,
          amount_inr: amount,
          payment_method: method,
          status: 'CONFIRMED',
          txn_ref: txnRef,
          beneficiary: 'Raju Shinde (#842)'
        }
      };

      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify(responsePayload, null, 2));
    });
    return;
  }

  // 1c. API Route: GET /api/v1/earnings
  if (pathname === '/api/v1/earnings') {
    const responsePayload = {
      success: true,
      timestamp: new Date().toISOString(),
      data: {
        collector_id: 'KAB-MH-842',
        collector_name: 'Raju Shinde',
        today_inr: 6407.40,
        pending_inr: 1200.00,
        completed_inr: 17450.00,
        total_inr: 25057.40
      }
    };

    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify(responsePayload, null, 2));
    return;
  }

  // 1d. API Route: POST /api/v1/sync (Offline Queue Sync)
  if (pathname === '/api/v1/sync' && req.method === 'POST') {
    let body = '';
    req.on('data', chunk => { body += chunk.toString(); });
    req.on('end', () => {
      let parsed = {};
      try { parsed = JSON.parse(body); } catch (e) {}
      const mutations = Array.isArray(parsed.mutations) ? parsed.mutations : [];
      const results = [];

      mutations.forEach(mut => {
        const lotId = mut.lot_id || (mut.payload && mut.payload.lot_id) || 'ECO-26-MH-004822';
        const recordType = mut.record_type || 'Lot Creation';

        // Ingest into server operational traceability
        if (mut.payload && (recordType.toLowerCase().includes('lot') || recordType === 'LOT_CREATION')) {
          const lotObj = mut.payload;
          const existingIdx = operationalTraceability.findIndex(r =>
            (r.unique_lot_id && r.unique_lot_id.toUpperCase() === lotId.toUpperCase()) ||
            (r.short_code && r.short_code.toUpperCase() === lotId.slice(-6).toUpperCase())
          );
          const formattedRecord = {
            unique_lot_id: lotId,
            short_code: lotObj.short_code || lotId.slice(-6),
            category: lotObj.category_name || "Printed Circuit Boards (Grade A)",
            gross_weight_kg: lotObj.weight_summary?.weighbridge_gross_kg || 48.50,
            verified_net_weight_kg: lotObj.weight_summary?.verified_net_kg || 48.25,
            status: lotObj.overall_status || "COLLECTED",
            collector_id: "KAB-MH-842",
            collector_name: lotObj.collector?.name || "Raju Shinde",
            location: lotObj.collector?.location_name || "Dharavi Ward G/N, Mumbai",
            timestamp: mut.created_at || new Date().toISOString(),
            raw_data: lotObj
          };

          if (existingIdx >= 0) {
            operationalTraceability[existingIdx] = formattedRecord;
          } else {
            operationalTraceability.unshift(formattedRecord);
          }
        }

        results.push({
          id: mut.id,
          lot_id: lotId,
          record_type: recordType,
          status: 'SYNCHRONIZED',
          message: recordType.toLowerCase().includes('lot') ? '✓ Lot synchronized' : '✓ Transaction synchronized',
          synced_at: new Date().toISOString()
        });
      });

      console.log(`[Ecobridge Server] Synchronized ${mutations.length} offline mutations successfully.`);

      const responsePayload = {
        success: true,
        timestamp: new Date().toISOString(),
        data: {
          synced_count: mutations.length,
          results: results
        }
      };

      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify(responsePayload, null, 2));
    });
    return;
  }

  // 1e. API Route: POST /api/v1/lots (Online Lot Creation)
  if (pathname === '/api/v1/lots' && req.method === 'POST') {
    let body = '';
    req.on('data', chunk => { body += chunk.toString(); });
    req.on('end', () => {
      let parsed = {};
      try { parsed = JSON.parse(body); } catch (e) {}
      const lotId = parsed.lot_id || `ECO-26-MH-${Math.floor(100000 + Math.random() * 900000)}`;

      const formattedRecord = {
        unique_lot_id: lotId,
        short_code: parsed.short_code || lotId.slice(-6),
        category: parsed.category_name || "Printed Circuit Boards",
        gross_weight_kg: parsed.gross_weight_kg || 48.50,
        verified_net_weight_kg: parsed.verified_net_weight_kg || 48.25,
        status: "LOT_CREATED",
        collector_id: "KAB-MH-842",
        collector_name: parsed.collector?.name || "Raju Shinde",
        location: parsed.collector?.location_name || "Dharavi Ward G/N, Mumbai",
        timestamp: new Date().toISOString(),
        raw_data: parsed
      };

      operationalTraceability.unshift(formattedRecord);

      res.writeHead(201, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({
        success: true,
        timestamp: new Date().toISOString(),
        data: {
          lot_id: lotId,
          status: 'LOT_CREATED',
          message: '✓ Lot created and recorded in ledger'
        }
      }, null, 2));
    });
    return;
  }

  // 2. Health check route
  if (pathname === '/health' || pathname === '/api/v1/health') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({
      success: true,
      status: "HEALTHY",
      service: "@ecobridge/recycler-portal",
      port: PORT,
      timestamp: new Date().toISOString()
    }));
    return;
  }

  // 3. Static File Serving from /public
  let safePath = path.normalize(pathname).replace(/^(\.\.[\/\\])+/, '');
  if (safePath === '/' || safePath === '\\') {
    safePath = '/index.html';
  }

  const filePath = path.join(PUBLIC_DIR, safePath);

  fs.stat(filePath, (err, stats) => {
    if (err || !stats.isFile()) {
      // Fallback to index.html for SPA-like navigation
      const indexPath = path.join(PUBLIC_DIR, 'index.html');
      fs.readFile(indexPath, (idxErr, content) => {
        if (idxErr) {
          res.writeHead(404, { 'Content-Type': 'text/plain' });
          res.end('404 Not Found');
          return;
        }
        res.writeHead(200, { 'Content-Type': 'text/html; charset=UTF-8' });
        res.end(content);
      });
      return;
    }

    const ext = path.extname(filePath).toLowerCase();
    const contentType = MIME_TYPES[ext] || 'application/octet-stream';

    fs.readFile(filePath, (readErr, data) => {
      if (readErr) {
        res.writeHead(500, { 'Content-Type': 'text/plain' });
        res.end('500 Internal Server Error');
        return;
      }
      res.writeHead(200, { 'Content-Type': contentType });
      res.end(data);
    });
  });
});

server.listen(PORT, () => {
  console.log(`\n=======================================================`);
  console.log(`🌿 ECOBRIDGE Recycler Portal & Traceability Server`);
  console.log(`🚀 Live at: http://localhost:${PORT}`);
  console.log(`🔍 Demo Lot: http://localhost:${PORT}/?lot=ECO-26-MH-004821`);
  console.log(`=======================================================\n`);
});
