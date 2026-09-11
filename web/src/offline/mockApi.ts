/**
 * Standalone Demo Mock API
 * Kabadiwala Connect — SIH 2026 (PS SIH26229)
 *
 * In-app mock API adapter for the `demoStandalone` flavor.
 * Implements core collector flows with bundled seed data
 * so the app works with ZERO backend and ZERO internet.
 *
 * This module sits behind the existing API client interface:
 * - Intercepts all /api/* requests when demo mode is active
 * - Returns data from IndexedDB (seeded on first launch)
 * - Simulates recycler responses with 3-8s delays
 * - Uses OTP `123456` for login
 *
 * NEVER ships in the `prod` flavor (tree-shaken via env check).
 */

import { getDB } from '../offline/db';

// Only active when VITE_DEMO_STANDALONE is set
const IS_STANDALONE = (import.meta as any).env?.VITE_DEMO_STANDALONE === 'true';

// Simulated personas (one per language)
const DEMO_PERSONAS: Record<string, any> = {
  mr: {
    id: 'demo-collector-mr',
    name: 'Ramesh Jadhav',
    display_name_local: 'रमेश जाधव',
    phone: '9876543210',
    role: 'collector',
    language: 'mr',
    city: 'Pune',
    operating_area: 'Kothrud',
  },
  hi: {
    id: 'demo-collector-hi',
    name: 'Suresh Kumar',
    display_name_local: 'सुरेश कुमार',
    phone: '9876543211',
    role: 'collector',
    language: 'hi',
    city: 'Delhi NCR',
    operating_area: 'Dwarka',
  },
  pa: {
    id: 'demo-collector-pa',
    name: 'Harpreet Singh',
    display_name_local: 'ਹਰਪ੍ਰੀਤ ਸਿੰਘ',
    phone: '9876543212',
    role: 'collector',
    language: 'pa',
    city: 'Ludhiana',
    operating_area: 'Model Town',
  },
  en: {
    id: 'demo-collector-en',
    name: 'Rajesh Sharma',
    display_name_local: 'Rajesh Sharma',
    phone: '9876543213',
    role: 'collector',
    language: 'en',
    city: 'Bangalore',
    operating_area: 'Koramangala',
  },
};

// Seed materials data
const SEED_MATERIALS = [
  { id: 'm1', code: 'PCB', name_en: 'Circuit Boards (PCB)', name_hi: 'सर्किट बोर्ड (PCB)', name_mr: 'सर्किट बोर्ड (PCB)', name_pa: 'ਸਰਕਿਟ ਬੋਰਡ (PCB)', base_price_paise_per_kg: 28000, is_hazardous: true, hazard_note_en: 'Contains lead solder', safety_tip_en: 'Wear gloves' },
  { id: 'm2', code: 'BAT', name_en: 'Batteries', name_hi: 'बैटरी', name_mr: 'बॅटरी', name_pa: 'ਬੈਟਰੀ', base_price_paise_per_kg: 8500, is_hazardous: true, hazard_note_en: 'Contains acid/lithium', safety_tip_en: 'Do not puncture' },
  { id: 'm3', code: 'MAG', name_en: 'Magnets & Motors', name_hi: 'मैग्नेट और मोटर', name_mr: 'चुंबक आणि मोटर', name_pa: 'ਚੁੰਬਕ ਅਤੇ ਮੋਟਰ', base_price_paise_per_kg: 12000, is_hazardous: false, hazard_note_en: '', safety_tip_en: '' },
  { id: 'm4', code: 'CRT', name_en: 'CRT / Monitor Glass', name_hi: 'CRT / मॉनिटर कांच', name_mr: 'CRT / मॉनिटर काच', name_pa: 'CRT / ਮਾਨੀਟਰ ਕੱਚ', base_price_paise_per_kg: 3500, is_hazardous: true, hazard_note_en: 'Contains lead', safety_tip_en: 'Handle carefully' },
  { id: 'm5', code: 'LCD', name_en: 'LCD / LED Panels', name_hi: 'LCD / LED पैनल', name_mr: 'LCD / LED पॅनल', name_pa: 'LCD / LED ਪੈਨਲ', base_price_paise_per_kg: 6000, is_hazardous: false, hazard_note_en: '', safety_tip_en: '' },
  { id: 'm6', code: 'WIR', name_en: 'Wires & Cables', name_hi: 'तार और केबल', name_mr: 'तारा आणि केबल', name_pa: 'ਤਾਰ ਅਤੇ ਕੇਬਲ', base_price_paise_per_kg: 18000, is_hazardous: false, hazard_note_en: '', safety_tip_en: '' },
  { id: 'm7', code: 'PLT', name_en: 'Plastic Casings', name_hi: 'प्लास्टिक बॉडी', name_mr: 'प्लास्टिक बॉडी', name_pa: 'ਪਲਾਸਟਿਕ ਬਾਡੀ', base_price_paise_per_kg: 2000, is_hazardous: false, hazard_note_en: '', safety_tip_en: '' },
  { id: 'm8', code: 'STL', name_en: 'Steel / Iron Scrap', name_hi: 'लोहा / स्टील', name_mr: 'लोखंड / स्टील', name_pa: 'ਲੋਹਾ / ਸਟੀਲ', base_price_paise_per_kg: 2500, is_hazardous: false, hazard_note_en: '', safety_tip_en: '' },
  { id: 'm9', code: 'ALU', name_en: 'Aluminium Scrap', name_hi: 'एल्यूमिनियम', name_mr: 'ॲल्युमिनिअम', name_pa: 'ਅਲੂਮੀਨੀਅਮ', base_price_paise_per_kg: 15000, is_hazardous: false, hazard_note_en: '', safety_tip_en: '' },
  { id: 'm10', code: 'COP', name_en: 'Copper Scrap', name_hi: 'तांबा', name_mr: 'तांबे', name_pa: 'ਤਾਂਬਾ', base_price_paise_per_kg: 55000, is_hazardous: false, hazard_note_en: '', safety_tip_en: '' },
];

// Seed recycler/buyers
const SEED_BUYERS = [
  { id: 'b1', name: 'GreenTech Recyclers', display_name_local: 'ग्रीनटेक रिसायकलर्स', rating: 4.7, cpcb_license: 'CPCB-MH-2024-1234', distance_km: 12, response_time_min: 15, specialties: ['PCB', 'BAT', 'COP'], price_premium_pct: 8 },
  { id: 'b2', name: 'EcoWaste Solutions', display_name_local: 'इकोवेस्ट सोल्यूशन्स', rating: 4.3, cpcb_license: 'CPCB-DL-2024-5678', distance_km: 25, response_time_min: 30, specialties: ['WIR', 'ALU', 'STL'], price_premium_pct: 5 },
  { id: 'b3', name: 'MetalPure India', display_name_local: 'मेटलप्युअर इंडिया', rating: 4.5, cpcb_license: 'CPCB-KA-2024-9012', distance_km: 8, response_time_min: 20, specialties: ['COP', 'ALU', 'MAG'], price_premium_pct: 12 },
];

let _demoLotCounter = 1;
let _demoLots: any[] = [];
let _demoTransactions: any[] = [];
let _demoNotifications: any[] = [
  { id: 'n1', type: 'price_alert', title: 'Copper price up 5%', body: 'Copper prices have risen this week', read: false, created_at: new Date().toISOString() },
  { id: 'n2', type: 'safety', title: 'Battery handling reminder', body: 'Always wear gloves when handling batteries', read: false, created_at: new Date().toISOString() },
];

function delay(min: number, max: number): Promise<void> {
  const ms = min + Math.random() * (max - min);
  return new Promise(r => setTimeout(r, ms));
}

/**
 * Handle a mock API request. Returns null if not in standalone mode.
 */
export async function handleMockRequest(
  endpoint: string,
  method: string = 'GET',
  body?: any,
): Promise<any | null> {
  if (!IS_STANDALONE) return null;

  const lang = localStorage.getItem('kc_language') || 'mr';
  const persona = DEMO_PERSONAS[lang] || DEMO_PERSONAS.mr;

  // ─── Auth ───
  if (endpoint === '/api/auth/request-otp' && method === 'POST') {
    await delay(500, 1000);
    return { success: true, otp_sent: true, demo_otp: '123456' };
  }

  if (endpoint === '/api/auth/verify-otp' && method === 'POST') {
    if (body?.otp === '123456' || body?.otp === 123456) {
      await delay(300, 600);
      return {
        access_token: 'demo-token-standalone',
        user: persona,
      };
    }
    throw { code: 'INVALID_OTP', message_key: 'invalid_otp' };
  }

  if (endpoint === '/api/auth/login' && method === 'POST') {
    await delay(300, 600);
    return { access_token: 'demo-token-standalone', user: persona };
  }

  if (endpoint === '/api/auth/me') {
    return persona;
  }

  // ─── Materials ───
  if (endpoint === '/api/materials') {
    return SEED_MATERIALS;
  }

  // ─── Prices ───
  if (endpoint === '/api/prices/summary') {
    return SEED_MATERIALS.slice(0, 6).map(m => ({
      material_code: m.code,
      material_name: m.name_en,
      base_price_paise_per_kg: m.base_price_paise_per_kg,
      trend: ['Rising', 'Steady', 'Falling'][Math.floor(Math.random() * 3)],
      change_pct: Math.round((Math.random() * 10 - 3) * 10) / 10,
      updated_at: new Date().toISOString(),
    }));
  }

  if (endpoint.startsWith('/api/prices/history')) {
    return { history: [], message: 'Demo mode — no historical data' };
  }

  // ─── Basket ───
  if (endpoint === '/api/basket' && method === 'GET') {
    const db = await getDB();
    const items = await db.getAll('basket');
    return { items, total_items: items.length };
  }

  if (endpoint === '/api/basket' && method === 'POST') {
    const db = await getDB();
    const item = {
      id: `basket-${Date.now()}`,
      material_id: body.material_id,
      material_code: body.material_code,
      weight_g: body.weight_g,
      condition: body.condition || 'broken',
      photo_data: body.photo_data,
      timestamp: Date.now(),
    };
    await db.put('basket', item);
    return item;
  }

  // ─── Lots ───
  if (endpoint === '/api/lots' && method === 'POST') {
    const lot = {
      id: `demo-lot-${_demoLotCounter++}`,
      status: 'pending',
      items: body.items || [],
      total_weight_g: body.total_weight_g || 5000,
      estimated_value_paise: body.estimated_value_paise || 50000,
      created_at: new Date().toISOString(),
      reference_code: `KC${String(_demoLotCounter).padStart(4, '0')}`,
    };
    _demoLots.push(lot);
    return lot;
  }

  if (endpoint.match(/^\/api\/lots$/) && method === 'GET') {
    return _demoLots;
  }

  if (endpoint.match(/^\/api\/lots\/[\w-]+$/)) {
    const lotId = endpoint.split('/').pop();
    return _demoLots.find(l => l.id === lotId) || { id: lotId, status: 'pending', items: [] };
  }

  // ─── Buyers / Quotes ───
  if (endpoint.match(/\/buyers|\/quotes|\/marketplace/)) {
    // Simulate recycler response delay (3-8 seconds)
    await delay(3000, 8000);
    return SEED_BUYERS.map((b, i) => ({
      ...b,
      quote_paise: Math.round(50000 * (1 + b.price_premium_pct / 100)),
      quoted_at: new Date().toISOString(),
      rank: i + 1,
    }));
  }

  // ─── Transactions ───
  if (endpoint.match(/\/transactions/) && method === 'POST') {
    const tx = {
      id: `demo-tx-${Date.now()}`,
      lot_id: body.lot_id,
      buyer_id: body.buyer_id,
      status: 'pending_handover',
      otp: '123456',
      ...body,
    };
    _demoTransactions.push(tx);
    return tx;
  }

  if (endpoint.match(/\/transactions\/[\w-]+$/)) {
    const txId = endpoint.split('/').pop();
    return _demoTransactions.find(t => t.id === txId) || {
      id: txId, status: 'pending_handover', items: [],
      otp: '123456',
    };
  }

  // ─── Wallet ───
  if (endpoint === '/api/wallet') {
    return {
      balance_paise: 1250000,
      total_earned_paise: 8750000,
      total_transactions: 47,
      pending_paise: 125000,
    };
  }

  if (endpoint === '/api/wallet/dues') {
    return [
      { buyer_name: 'GreenTech Recyclers', amount_paise: 75000, due_date: new Date(Date.now() + 86400000 * 3).toISOString() },
    ];
  }

  if (endpoint === '/api/wallet/transactions') {
    return [];
  }

  // ─── Notifications ───
  if (endpoint === '/api/notifications') {
    return _demoNotifications;
  }

  // ─── Support ───
  if (endpoint === '/api/support/tickets' && method === 'GET') {
    return [];
  }
  if (endpoint === '/api/support/tickets' && method === 'POST') {
    return { id: `demo-ticket-${Date.now()}`, status: 'open', created_at: new Date().toISOString() };
  }

  // ─── Safety ───
  if (endpoint === '/api/safety') {
    return {
      guidelines: SEED_MATERIALS.filter(m => m.is_hazardous).map(m => ({
        material_code: m.code,
        material_name: m.name_en,
        hazard_note: m.hazard_note_en,
        safety_tip: m.safety_tip_en,
      })),
    };
  }

  // ─── ML ───
  if (endpoint === '/api/ml/classify' && method === 'POST') {
    await delay(1000, 2000);
    const codes = SEED_MATERIALS.map(m => m.code);
    return {
      predicted_code: codes[Math.floor(Math.random() * codes.length)],
      confidence: Math.round(60 + Math.random() * 30) / 100,
      demo_only: true,
      not_sure: Math.random() < 0.3,
    };
  }

  // ─── Handover confirm ───
  if (endpoint.match(/\/handover/) && method === 'POST') {
    await delay(1000, 2000);
    return { status: 'completed', confirmed_at: new Date().toISOString() };
  }

  // ─── Default fallback ───
  console.info(`[Mock API] Unhandled: ${method} ${endpoint}`);
  return { status: 'ok', demo: true };
}

/**
 * Check if standalone demo mode is active.
 */
export function isStandaloneDemo(): boolean {
  return IS_STANDALONE;
}
