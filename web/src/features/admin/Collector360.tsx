import React, { useState, useEffect } from 'react';
import {
  Users, Search, Shield, AlertTriangle, CheckCircle, Clock,
  ArrowRight, Phone, MapPin, Calendar, IndianRupee, HelpCircle,
  FileText, ExternalLink, X, Filter, ChevronRight, TrendingUp, AlertCircle
} from 'lucide-react';
import { InitialsAvatar } from '../../design/components/InitialsAvatar';

interface CollectorSummary {
  id: string;
  user_id: string;
  collector_code: string;
  display_name: string;
  display_name_local: string | null;
  phone_masked: string;
  preferred_language: string;
  city: string;
  operating_area_name: string;
  wallet_balance_inr: number;
  total_earned_inr: number;
  lots_completed: number;
  rating_avg: number;
  trust_score: number;
  is_synthetic: boolean;
  is_active: boolean;
}

interface CollectorDetail {
  profile: {
    id: string;
    user_id: string;
    collector_code: string;
    display_name: string;
    display_name_local: string | null;
    phone_masked: string;
    preferred_language: string;
    city: string;
    state: string;
    operating_area_name: string;
    coarse_lat: number;
    coarse_lng: number;
    join_date: string;
    last_login_at: string | null;
    is_active: boolean;
    is_synthetic: boolean;
    trust_score: number;
    rating_avg: number;
  };
  financial_summary: {
    wallet_balance_inr: number;
    total_earned_inr: number;
    formal_premium_earned_inr: number;
    pending_dues_count: number;
    pending_dues_total_inr: number;
    pending_dues: Array<{
      transaction_id: string;
      amount_inr: number;
      due_at: string;
    }>;
  };
  lots_summary: {
    total_lots: number;
    completed_lots: number;
    active_lots: number;
    timeline: Array<{
      id: string;
      lot_code: string;
      status: string;
      created_at: string;
      est_weight_kg: number;
      actual_weight_kg: number | null;
      final_amount_inr: number | null;
      items: Array<{ material: string; weight_kg: number }>;
    }>;
  };
  ledger: Array<{
    transaction_id: string;
    receipt_no: string | null;
    created_at: string;
    agreed_inr: number;
    final_inr: number;
    payment_method: string;
    payment_status: string;
    balance_due_inr: number;
    due_status: string;
  }>;
  support_tickets: Array<{
    ticket_no: string;
    category: string;
    status: string;
    priority: string;
    language: string;
    created_at: string;
    resolved_at: string | null;
    csat_score: number | null;
  }>;
  anomalies: Array<{
    id: string;
    code: string;
    severity: string;
    score: number;
    status: string;
    reasons: string[];
  }>;
}

export const Collector360: React.FC = () => {
  const [collectors, setCollectors] = useState<CollectorSummary[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [detail, setDetail] = useState<CollectorDetail | null>(null);
  const [detailLoading, setDetailLoading] = useState<boolean>(false);

  // Filters
  const [search, setSearch] = useState<string>('');
  const [langFilter, setLangFilter] = useState<string>('all');
  const [cityFilter, setCityFilter] = useState<string>('all');

  useEffect(() => {
    fetchCollectors();
  }, []);

  const fetchCollectors = async () => {
    try {
      setLoading(true);
      const res = await fetch('/api/admin/collectors');
      if (res.ok) {
        const data = await res.json();
        setCollectors(data);
      }
    } catch (err) {
      console.error('Error fetching collectors:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectCollector = async (id: string) => {
    setSelectedId(id);
    setDetail(null);
    setDetailLoading(true);
    try {
      const res = await fetch(`/api/admin/collectors/${id}/360`);
      if (res.ok) {
        const data = await res.json();
        setDetail(data);
      }
    } catch (err) {
      console.error('Error fetching collector 360:', err);
    } finally {
      setDetailLoading(false);
    }
  };

  const filtered = collectors.filter((c) => {
    const matchesSearch =
      c.display_name.toLowerCase().includes(search.toLowerCase()) ||
      c.collector_code.toLowerCase().includes(search.toLowerCase()) ||
      (c.display_name_local && c.display_name_local.includes(search)) ||
      c.operating_area_name.toLowerCase().includes(search.toLowerCase());

    const matchesLang = langFilter === 'all' || c.preferred_language === langFilter;
    const matchesCity = cityFilter === 'all' || c.city.toLowerCase() === cityFilter.toLowerCase();

    return matchesSearch && matchesLang && matchesCity;
  });

  const cities = Array.from(new Set(collectors.map((c) => c.city)));

  const getLanguageLabel = (lang: string) => {
    switch (lang) {
      case 'mr': return 'मराठी (MR)';
      case 'hi': return 'हिन्दी (HI)';
      case 'pa': return 'ਪੰਜਾਬੀ (PA)';
      case 'en': return 'English (EN)';
      default: return lang.toUpperCase();
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[#E3E0D5] pb-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-black text-[#0B3D2E]">Collector 360 Registry</h1>
            <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-[#E7F3EF] text-[#0B3D2E]">
              {collectors.length} Registered
            </span>
          </div>
          <p className="text-xs text-[#5B6B62] mt-1">
            Comprehensive lifecycle, earnings reconciliation, trust indices, and traceability timeline per collector.
            <span className="text-[#0B3D2E] font-semibold ml-1">PS Data Minimization Enforced:</span> Coarse operating centers only.
          </p>
        </div>

        {/* Search & Filters */}
        <div className="flex items-center gap-2 flex-wrap">
          <div className="relative">
            <Search className="absolute left-3 top-2.5 text-[#5B6B62]" size={15} />
            <input
              type="text"
              placeholder="Search by name, local script, code..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="pl-9 pr-3 py-1.5 bg-white border border-[#E3E0D5] rounded-xl text-xs text-[#14201A] focus:outline-none focus:border-[#0B3D2E] w-64"
            />
          </div>

          <select
            value={langFilter}
            onChange={(e) => setLangFilter(e.target.value)}
            className="px-3 py-1.5 bg-white border border-[#E3E0D5] rounded-xl text-xs text-[#14201A] focus:outline-none font-semibold cursor-pointer"
          >
            <option value="all">All Languages</option>
            <option value="mr">Marathi (मराठी)</option>
            <option value="hi">Hindi (हिन्दी)</option>
            <option value="pa">Punjabi (ਪੰਜਾਬੀ)</option>
            <option value="en">English</option>
          </select>

          <select
            value={cityFilter}
            onChange={(e) => setCityFilter(e.target.value)}
            className="px-3 py-1.5 bg-white border border-[#E3E0D5] rounded-xl text-xs text-[#14201A] focus:outline-none font-semibold cursor-pointer"
          >
            <option value="all">All Cities</option>
            {cities.map((city) => (
              <option key={city} value={city}>
                {city}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Main Grid: Roster List */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filtered.map((c) => (
          <div
            key={c.id}
            onClick={() => handleSelectCollector(c.id)}
            className="bg-white border border-[#E3E0D5] rounded-2xl p-4 hover:border-[#0B3D2E] hover:shadow-md transition-all cursor-pointer group flex flex-col justify-between"
          >
            <div>
              <div className="flex items-start justify-between gap-3">
                <div className="flex items-center gap-3">
                  <InitialsAvatar name={c.display_name} size="md" />
                  <div>
                    <h3 className="font-bold text-sm text-[#14201A] group-hover:text-[#0B3D2E] transition-colors flex items-center gap-1.5">
                      {c.display_name}
                      {c.display_name_local && (
                        <span className="text-xs text-[#0B3D2E] font-medium px-1.5 py-0.2 rounded bg-[#E7F3EF]">
                          {c.display_name_local}
                        </span>
                      )}
                    </h3>
                    <div className="flex items-center gap-2 mt-0.5 text-[11px] text-[#5B6B62]">
                      <span className="font-mono font-semibold text-[#0B3D2E]">{c.collector_code}</span>
                      <span>&bull;</span>
                      <span>{getLanguageLabel(c.preferred_language)}</span>
                    </div>
                  </div>
                </div>

                <span className="px-2 py-0.5 rounded-full text-[10px] font-black bg-amber-50 text-amber-900 border border-amber-200">
                  Trust: {c.trust_score}
                </span>
              </div>

              {/* Area & City */}
              <div className="flex items-center gap-1.5 text-xs text-[#5B6B62] mt-3 bg-[#F7F5EF] px-2.5 py-1.5 rounded-xl">
                <MapPin size={13} className="text-[#0B3D2E] shrink-0" />
                <span className="truncate">{c.operating_area_name}, {c.city}</span>
              </div>

              {/* Quick Metrics */}
              <div className="grid grid-cols-3 gap-2 mt-3 pt-3 border-t border-[#E3E0D5]/60 text-center">
                <div>
                  <span className="text-[10px] text-[#5B6B62] block">Total Earned</span>
                  <span className="text-xs font-black text-[#0B3D2E]">₹{c.total_earned_inr.toLocaleString('en-IN')}</span>
                </div>
                <div>
                  <span className="text-[10px] text-[#5B6B62] block">Lots Done</span>
                  <span className="text-xs font-bold text-[#14201A]">{c.lots_completed}</span>
                </div>
                <div>
                  <span className="text-[10px] text-[#5B6B62] block">Rating</span>
                  <span className="text-xs font-bold text-amber-700">★ {c.rating_avg.toFixed(1)}</span>
                </div>
              </div>
            </div>

            <div className="flex items-center justify-between mt-3 pt-2 text-[11px] text-[#0B3D2E] font-bold border-t border-[#E3E0D5]/40">
              <span>Open 360 Dossier</span>
              <ChevronRight size={14} className="group-hover:translate-x-1 transition-transform" />
            </div>
          </div>
        ))}
      </div>

      {filtered.length === 0 && !loading && (
        <div className="text-center py-12 bg-white rounded-2xl border border-[#E3E0D5]">
          <Users size={32} className="mx-auto text-[#5B6B62] mb-2 opacity-40" />
          <p className="text-sm font-bold text-[#14201A]">No collectors matching criteria</p>
          <p className="text-xs text-[#5B6B62] mt-1">Try clearing search keywords or filters.</p>
        </div>
      )}

      {/* Collector 360 Modal Dossier */}
      {selectedId && (
        <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-xs flex items-center justify-center p-4 overflow-y-auto">
          <div className="bg-[#F7F5EF] rounded-3xl border border-[#E3E0D5] w-full max-w-4xl max-h-[90vh] flex flex-col shadow-2xl overflow-hidden">
            {/* Modal Header */}
            <div className="bg-[#0B3D2E] text-white p-6 flex items-start justify-between relative">
              {detail ? (
                <div className="flex items-start gap-4">
                  <InitialsAvatar name={detail.profile.display_name} size="lg" className="border-2 border-white/30" />
                  <div>
                    <div className="flex items-center gap-3">
                      <h2 className="text-xl font-black text-white">{detail.profile.display_name}</h2>
                      {detail.profile.display_name_local && (
                        <span className="text-sm font-semibold text-[#E9A310] bg-white/10 px-2.5 py-0.5 rounded-lg">
                          {detail.profile.display_name_local}
                        </span>
                      )}
                      <span className="px-2 py-0.5 rounded text-[11px] font-mono bg-white/20 text-white font-bold">
                        {detail.profile.collector_code}
                      </span>
                    </div>

                    <div className="flex items-center gap-4 text-xs text-white/80 mt-2">
                      <span className="flex items-center gap-1">
                        <MapPin size={13} className="text-[#E9A310]" />
                        {detail.profile.operating_area_name}, {detail.profile.city} ({detail.profile.coarse_lat}, {detail.profile.coarse_lng})
                      </span>
                      <span>&bull;</span>
                      <span className="flex items-center gap-1">
                        <Calendar size={13} />
                        Joined {new Date(detail.profile.join_date).toLocaleDateString()}
                      </span>
                      <span>&bull;</span>
                      <span className="font-semibold text-[#E9A310]">{getLanguageLabel(detail.profile.preferred_language)}</span>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 rounded-full bg-white/20 animate-pulse"></div>
                  <div className="space-y-2">
                    <div className="w-48 h-5 bg-white/20 rounded animate-pulse"></div>
                    <div className="w-32 h-3 bg-white/20 rounded animate-pulse"></div>
                  </div>
                </div>
              )}

              <button
                onClick={() => setSelectedId(null)}
                className="p-1.5 rounded-full hover:bg-white/20 text-white/80 hover:text-white transition-colors cursor-pointer"
              >
                <X size={20} />
              </button>
            </div>

            {/* Modal Body */}
            <div className="p-6 overflow-y-auto space-y-6 flex-1">
              {detailLoading && !detail && (
                <div className="text-center py-16">
                  <div className="w-8 h-8 border-3 border-[#0B3D2E] border-t-transparent rounded-full animate-spin mx-auto mb-3"></div>
                  <p className="text-xs text-[#5B6B62] font-bold">Compiling 360 dossier from verified ledgers...</p>
                </div>
              )}

              {detail && (
                <>
                  {/* Financial & Premium Highlights */}
                  <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
                    <div className="bg-white border border-[#E3E0D5] p-4 rounded-2xl shadow-xs">
                      <span className="text-[11px] text-[#5B6B62] font-bold block">Total Formal Earnings</span>
                      <span className="text-xl font-black text-[#0B3D2E] mt-1 block">
                        ₹{detail.financial_summary.total_earned_inr.toLocaleString('en-IN')}
                      </span>
                      <span className="text-[10px] text-[#5B6B62] mt-1 block">Reconciled via dual cash confirmation</span>
                    </div>

                    <div className="bg-white border border-[#E3E0D5] p-4 rounded-2xl shadow-xs">
                      <span className="text-[11px] text-[#5B6B62] font-bold block">Formal Premium Earned</span>
                      <span className="text-xl font-black text-emerald-700 mt-1 block">
                        +₹{detail.financial_summary.formal_premium_earned_inr.toLocaleString('en-IN')}
                      </span>
                      <span className="text-[10px] text-emerald-800 font-semibold mt-1 block">
                        Assumed 14.5% vs informal market
                      </span>
                    </div>

                    <div className="bg-white border border-[#E3E0D5] p-4 rounded-2xl shadow-xs">
                      <span className="text-[11px] text-[#5B6B62] font-bold block">Active Wallet Balance</span>
                      <span className="text-xl font-black text-[#14201A] mt-1 block">
                        ₹{detail.financial_summary.wallet_balance_inr.toLocaleString('en-IN')}
                      </span>
                      <span className="text-[10px] text-[#5B6B62] mt-1 block">Instant withdraw via Aadhaar/UPI</span>
                    </div>

                    <div className="bg-white border border-[#E3E0D5] p-4 rounded-2xl shadow-xs">
                      <span className="text-[11px] text-[#5B6B62] font-bold block">Pending Buyer Dues</span>
                      <span className={`text-xl font-black mt-1 block ${detail.financial_summary.pending_dues_total_inr > 0 ? 'text-amber-700' : 'text-[#0B3D2E]'}`}>
                        ₹{detail.financial_summary.pending_dues_total_inr.toLocaleString('en-IN')}
                      </span>
                      <span className="text-[10px] text-[#5B6B62] mt-1 block">
                        {detail.financial_summary.pending_dues_count} pending settlement(s)
                      </span>
                    </div>
                  </div>

                  {/* Anomaly & Risk Flags */}
                  {detail.anomalies.length > 0 && (
                    <div className="bg-amber-50 border border-amber-200 rounded-2xl p-4">
                      <div className="flex items-center gap-2 text-amber-900 font-bold text-xs mb-2">
                        <AlertTriangle size={15} className="text-amber-600" />
                        <span>Active System Flags ({detail.anomalies.length})</span>
                      </div>
                      <div className="space-y-2">
                        {detail.anomalies.map((anom) => (
                          <div key={anom.id} className="bg-white/80 p-2.5 rounded-xl border border-amber-200/60 flex items-start justify-between text-xs">
                            <div>
                              <span className="font-mono font-bold text-amber-900">{anom.code}</span>
                              <p className="text-[#5B6B62] text-[11px] mt-0.5">{anom.reasons.join(', ')}</p>
                            </div>
                            <span className="px-2 py-0.5 rounded text-[10px] font-black uppercase tracking-wider bg-red-100 text-red-800">
                              {anom.severity}
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Lots Timeline */}
                  <div className="bg-white border border-[#E3E0D5] rounded-2xl p-5 shadow-xs">
                    <h3 className="font-bold text-sm text-[#0B3D2E] mb-3 flex items-center justify-between">
                      <span>Lots Lifecycle Timeline ({detail.lots_summary.total_lots})</span>
                      <span className="text-xs font-semibold text-[#5B6B62]">
                        {detail.lots_summary.completed_lots} Completed &bull; {detail.lots_summary.active_lots} Active
                      </span>
                    </h3>

                    <div className="space-y-3 max-h-64 overflow-y-auto pr-1">
                      {detail.lots_summary.timeline.map((lot) => (
                        <div key={lot.id} className="p-3 rounded-xl bg-[#F7F5EF] border border-[#E3E0D5] flex items-center justify-between text-xs">
                          <div>
                            <div className="flex items-center gap-2">
                              <span className="font-mono font-bold text-[#0B3D2E]">{lot.lot_code}</span>
                              <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                                lot.status === 'completed'
                                  ? 'bg-emerald-100 text-emerald-900'
                                  : lot.status === 'cancelled'
                                  ? 'bg-rose-100 text-rose-800'
                                  : 'bg-blue-100 text-blue-800'
                              }`}>
                                {lot.status.toUpperCase()}
                              </span>
                            </div>
                            <div className="text-[11px] text-[#5B6B62] mt-1 flex items-center gap-2">
                              <span>{new Date(lot.created_at).toLocaleDateString()}</span>
                              <span>&bull;</span>
                              <span>{lot.items.map(i => `${i.material} (${i.weight_kg} kg)`).join(', ')}</span>
                            </div>
                          </div>

                          <div className="text-right">
                            <span className="font-black text-sm text-[#0B3D2E] block">
                              {lot.final_amount_inr ? `₹${lot.final_amount_inr.toLocaleString('en-IN')}` : 'In Negotiation'}
                            </span>
                            <span className="text-[10px] text-[#5B6B62]">
                              {lot.actual_weight_kg ? `${lot.actual_weight_kg.toFixed(1)} kg` : `${lot.est_weight_kg.toFixed(1)} kg est.`}
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Multilingual Support History */}
                  <div className="bg-white border border-[#E3E0D5] rounded-2xl p-5 shadow-xs">
                    <h3 className="font-bold text-sm text-[#0B3D2E] mb-3 flex items-center justify-between">
                      <span>Support &amp; Grievance History</span>
                      <span className="text-xs text-[#5B6B62]">{detail.support_tickets.length} Ticket(s)</span>
                    </h3>

                    {detail.support_tickets.length === 0 ? (
                      <p className="text-xs text-[#5B6B62] italic py-2">No support grievances raised by this collector.</p>
                    ) : (
                      <div className="space-y-2 max-h-48 overflow-y-auto">
                        {detail.support_tickets.map((t) => (
                          <div key={t.ticket_no} className="p-3 rounded-xl bg-[#F7F5EF] border border-[#E3E0D5] flex items-center justify-between text-xs">
                            <div>
                              <div className="flex items-center gap-2">
                                <span className="font-mono font-bold text-[#14201A]">{t.ticket_no}</span>
                                <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-white border border-[#E3E0D5]">
                                  {t.category}
                                </span>
                              </div>
                              <span className="text-[10px] text-[#5B6B62] block mt-1">
                                {new Date(t.created_at).toLocaleDateString()} &bull; Lang: {t.language.toUpperCase()}
                              </span>
                            </div>

                            <div className="text-right">
                              <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                                t.status === 'resolved' ? 'bg-emerald-100 text-emerald-900' : 'bg-amber-100 text-amber-900'
                              }`}>
                                {t.status.toUpperCase()}
                              </span>
                              {t.csat_score && (
                                <span className="text-[10px] text-amber-600 font-bold block mt-1">
                                  CSAT: ★ {t.csat_score}/5
                                </span>
                              )}
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </>
              )}
            </div>

            {/* Modal Footer */}
            <div className="bg-white border-t border-[#E3E0D5] p-4 flex items-center justify-between text-xs text-[#5B6B62]">
              <span className="flex items-center gap-1.5">
                <Shield size={13} className="text-[#0B3D2E]" />
                PS Data Minimization: Verified fictional composite record (is_synthetic=True)
              </span>
              <button
                onClick={() => setSelectedId(null)}
                className="px-4 py-1.5 rounded-xl bg-[#0B3D2E] text-white font-bold hover:bg-[#07271D] transition-colors cursor-pointer"
              >
                Close Dossier
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
