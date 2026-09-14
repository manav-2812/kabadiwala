import React, { useState, useEffect } from 'react';
import { apiRequest } from '../../lib/api';
import {
  GitCommit, ShieldCheck, AlertOctagon, CheckCircle2,
  RefreshCw, Wrench, Bug, Search, FileText, ArrowDown, ExternalLink
} from 'lucide-react';
import { formatWeight, formatINR } from '../../lib/format';

interface TraceEvent {
  id: string;
  lot_id: string;
  seq: number;
  event_type: string;
  actor_role: string;
  payload: any;
  geo_lat: number | null;
  geo_lng: number | null;
  occurred_at: string;
  prev_hash: string;
  event_hash: string;
}

interface VerificationResult {
  valid: boolean;
  total_events: number;
  broken_at_seq: number | null;
  last_hash: string;
}

export const TraceabilityExplorer: React.FC = () => {
  const [lotCode, setLotCode] = useState('KC-LOT-0001');
  const [lotId, setLotId] = useState('lot-1');
  const [events, setEvents] = useState<TraceEvent[]>([]);
  const [verification, setVerification] = useState<VerificationResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [actionMessage, setActionMessage] = useState<string | null>(null);

  const fetchTraceData = async (code: string) => {
    setLoading(true);
    setActionMessage(null);
    try {
      // Find lot by code from marketplace or lots list
      const lotsRes = await apiRequest('/api/dashboard/recycler/marketplace');
      const found = Array.isArray(lotsRes) ? lotsRes.find((l: any) => l.lot_code === code) : null;
      const targetLotId = found ? found.id : 'lot-1';
      setLotId(targetLotId);

      const [traceRes, verifyRes] = await Promise.all([
        apiRequest(`/api/lots/${targetLotId}/trace`),
        apiRequest(`/api/lots/${targetLotId}/trace/verify`),
      ]);
      setEvents(traceRes || []);
      setVerification(verifyRes || null);
    } catch (err: any) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTraceData(lotCode);
  }, [lotCode]);

  const handleSimulateTamper = async () => {
    setLoading(true);
    try {
      const res = await apiRequest('/api/demo/tamper', {
        method: 'POST',
        body: JSON.stringify({ lot_code: lotCode })
      });
      setActionMessage(res.message || 'Tampering simulated in event chain.');
      // Re-fetch
      const [traceRes, verifyRes] = await Promise.all([
        apiRequest(`/api/lots/${lotId}/trace`),
        apiRequest(`/api/lots/${lotId}/trace/verify`),
      ]);
      setEvents(traceRes || []);
      setVerification(verifyRes || null);
    } catch (err: any) {
      setActionMessage('Failed to tamper: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleRepairChain = async () => {
    setLoading(true);
    try {
      const res = await apiRequest('/api/demo/repair', {
        method: 'POST',
        body: JSON.stringify({ lot_code: lotCode })
      });
      setActionMessage(res.message || 'Cryptographic integrity restored.');
      const [traceRes, verifyRes] = await Promise.all([
        apiRequest(`/api/lots/${lotId}/trace`),
        apiRequest(`/api/lots/${lotId}/trace/verify`),
      ]);
      setEvents(traceRes || []);
      setVerification(verifyRes || null);
    } catch (err: any) {
      setActionMessage('Failed to repair: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleReverify = async () => {
    setLoading(true);
    try {
      const verifyRes = await apiRequest(`/api/lots/${lotId}/trace/verify`);
      setVerification(verifyRes);
      setActionMessage('Verification re-calculated on live database state.');
    } catch (err: any) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col gap-6">
      {/* Title */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-[#E3E0D5] pb-4">
        <div>
          <h2 className="text-2xl font-black text-[#0B3D2E]">Cryptographic Traceability Explorer</h2>
          <p className="text-xs text-[#5B6B62]">
            Immutable SHA-256 chain-of-custody audit trail from informal collection to CPCB smelter
          </p>
        </div>

        {/* Preset lot selectors */}
        <div className="flex items-center gap-1.5 overflow-x-auto">
          {['KC-LOT-0001', 'KC-LOT-0002', 'KC-LOT-0003', 'KC-LOT-0004'].map((code) => (
            <button
              key={code}
              onClick={() => setLotCode(code)}
              className={`px-3 py-1.5 rounded-lg text-xs font-mono font-bold cursor-pointer transition-all ${
                lotCode === code
                  ? 'bg-[#0B3D2E] text-white shadow-xs'
                  : 'bg-white border border-[#D1CEBF] text-[#5B6B62] hover:text-[#14201A]'
              }`}
            >
              {code}
            </button>
          ))}
        </div>
      </div>

      {/* Judge Simulation Controls Bar */}
      <div className="bg-[#FAF8F5] border border-[#E3E0D5] rounded-2xl p-4 flex flex-col md:flex-row items-start md:items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <span className="text-xs font-black uppercase text-[#0B3D2E] tracking-wider bg-[#E4F4EA] px-2.5 py-1 rounded-md">
            Judge Interactive Tools
          </span>
          <span className="text-xs text-[#5B6B62]">
            Test cryptographic resilience against unauthorized ledger alteration
          </span>
        </div>

        <div className="flex items-center gap-2 flex-wrap">
          <button
            onClick={handleSimulateTamper}
            disabled={loading}
            className="px-3.5 py-1.5 rounded-xl bg-[#FFF0F0] border border-[#C93B2B]/30 hover:bg-[#FFE5E5] text-[#C93B2B] text-xs font-bold flex items-center gap-1.5 cursor-pointer touch-target"
          >
            <Bug size={14} />
            <span>Simulate Tampering (Corrupt Hash)</span>
          </button>

          <button
            onClick={handleRepairChain}
            disabled={loading}
            className="px-3.5 py-1.5 rounded-xl bg-[#E4F4EA] border border-[#14634A]/30 hover:bg-[#D1ECD9] text-[#14634A] text-xs font-bold flex items-center gap-1.5 cursor-pointer touch-target"
          >
            <Wrench size={14} />
            <span>Repair Chain (Recompute Hashes)</span>
          </button>

          <button
            onClick={handleReverify}
            disabled={loading}
            className="px-3 py-1.5 rounded-xl bg-white border border-[#D1CEBF] hover:bg-[#F2EFE9] text-[#14201A] text-xs font-bold flex items-center gap-1.5 cursor-pointer touch-target"
          >
            <RefreshCw size={13} className={loading ? 'animate-spin' : ''} />
            <span>Verify</span>
          </button>

          <button
            onClick={() => window.open(`/verify/${lotCode}`, '_blank')}
            className="px-3 py-1.5 rounded-xl bg-white border border-[#D1CEBF] hover:bg-[#F2EFE9] text-[#0B3D2E] text-xs font-bold flex items-center gap-1.5 cursor-pointer touch-target"
          >
            <ExternalLink size={13} />
            <span>Public Certificate</span>
          </button>
        </div>
      </div>

      {/* Action toast message */}
      {actionMessage && (
        <div className="p-3 rounded-xl bg-[#FFF3D6] border border-[#E9A310]/30 text-[#A66F00] text-xs font-bold flex items-center gap-2">
          <span>{actionMessage}</span>
        </div>
      )}

      {/* Audit Banner */}
      {verification && (
        <div className={`p-4 rounded-2xl border flex items-center justify-between ${
          verification.valid
            ? 'bg-[#E4F4EA] border-[#14634A]/30 text-[#14634A]'
            : 'bg-[#FFF0F0] border-[#C93B2B]/40 text-[#C93B2B]'
        }`}>
          <div className="flex items-center gap-3">
            {verification.valid ? (
              <ShieldCheck size={28} className="shrink-0" />
            ) : (
              <AlertOctagon size={28} className="shrink-0" />
            )}
            <div>
              <h3 className="text-base font-black">
                {verification.valid
                  ? `Cryptographic Audit Passed: 100% Chain Integrity (${verification.total_events} Events Sealed)`
                  : `SECURITY ALERT: Audit Chain Compromised! Broken at Seq #${verification.broken_at_seq}`}
              </h3>
              <p className="text-xs opacity-90 mt-0.5">
                {verification.valid
                  ? 'All sequential SHA-256 event hashes match original geostamps, weights, and UPI payment signatures.'
                  : 'Hash mismatch detected. One or more records were illegally altered after creation.'}
              </p>
            </div>
          </div>

          <div className="hidden sm:block text-right">
            <span className="text-[10px] uppercase font-bold opacity-75 block">Latest Merkle Leaf</span>
            <span className="font-mono text-xs font-bold">
              {verification.last_hash.slice(0, 16)}...
            </span>
          </div>
        </div>
      )}

      {/* Visual Hash Chain Events */}
      <div className="space-y-4">
        {events.map((ev, index) => {
          const isBrokenSeq = verification && !verification.valid && verification.broken_at_seq === ev.seq;
          return (
            <div key={ev.id || index} className="flex flex-col items-center">
              {/* Event Card */}
              <div className={`w-full bg-white rounded-2xl border p-4 sm:p-5 transition-all shadow-xs ${
                isBrokenSeq ? 'border-red-500 ring-2 ring-red-500/20 bg-red-50/20' : 'border-[#E3E0D5]'
              }`}>
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-[#E3E0D5] pb-3">
                  <div className="flex items-center gap-2.5">
                    <span className="w-6 h-6 rounded-full bg-[#0B3D2E] text-white flex items-center justify-center font-black text-xs">
                      {ev.seq}
                    </span>
                    <h4 className="text-sm font-black text-[#14201A] uppercase tracking-wide">
                      {ev.event_type.replace(/_/g, ' ')}
                    </h4>
                    <span className="px-2 py-0.5 rounded-md bg-[#FAF8F5] border border-[#E3E0D5] text-[10px] font-bold text-[#5B6B62]">
                      Actor: {ev.actor_role}
                    </span>
                  </div>

                  <span className="text-xs text-[#5B6B62] font-tabular">
                    {new Date(ev.occurred_at).toLocaleString()}
                  </span>
                </div>

                {/* Event Payload & Hashes */}
                <div className="mt-3 grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
                  {/* Left: Payload parameters */}
                  <div>
                    <span className="font-bold text-[#5B6B62] uppercase text-[10px] tracking-wider block mb-1.5">
                      Attestation Payload
                    </span>
                    <pre className="p-2.5 rounded-xl bg-[#FAF8F5] border border-[#E3E0D5] text-[11px] font-mono text-[#14201A] overflow-x-auto whitespace-pre-wrap">
                      {JSON.stringify(ev.payload, null, 2)}
                    </pre>
                  </div>

                  {/* Right: Cryptographic Hashes */}
                  <div className="flex flex-col justify-between">
                    <div>
                      <span className="font-bold text-[#5B6B62] uppercase text-[10px] tracking-wider block mb-1.5">
                        Cryptographic Hash Link
                      </span>
                      <div className="space-y-1.5 font-mono text-[11px]">
                        <div className="p-2 rounded-lg bg-[#FAF8F5] border border-[#E3E0D5]">
                          <span className="text-[10px] text-[#5B6B62] block font-sans">Previous Hash (PrevHash)</span>
                          <span className="text-[#5B6B62] truncate block">{ev.prev_hash}</span>
                        </div>
                        <div className={`p-2 rounded-lg border ${
                          isBrokenSeq ? 'bg-red-50 border-red-300 text-red-700' : 'bg-[#E4F4EA]/40 border-[#14634A]/30 text-[#0B3D2E]'
                        }`}>
                          <span className="text-[10px] block font-sans font-bold">
                            {isBrokenSeq ? 'TAMPERED EVENT HASH' : 'Event Hash (SHA-256)'}
                          </span>
                          <span className="font-bold truncate block">{ev.event_hash}</span>
                        </div>
                      </div>
                    </div>

                    {ev.geo_lat && (
                      <div className="text-[11px] text-[#5B6B62] mt-2 font-tabular">
                        Geostamp: {ev.geo_lat.toFixed(5)}, {ev.geo_lng?.toFixed(5)} (Signed GPS lock)
                      </div>
                    )}
                  </div>
                </div>
              </div>

              {/* Chain connector line */}
              {index < events.length - 1 && (
                <div className="py-2 flex flex-col items-center">
                  <div className="w-0.5 h-4 bg-[#D1CEBF]" />
                  <ArrowDown size={14} className="text-[#5B6B62]" />
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};
