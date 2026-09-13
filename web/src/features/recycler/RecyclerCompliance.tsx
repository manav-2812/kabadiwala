import React from 'react';
import {
  ShieldCheck, AlertTriangle, CheckCircle2, Clock,
  FileCheck, ArrowUpRight, Award, ExternalLink
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export const RecyclerCompliance: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="flex flex-col gap-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-[#E3E0D5] pb-4">
        <div>
          <h2 className="text-2xl font-black text-[#0B3D2E]">Statutory Compliance & Audits</h2>
          <p className="text-xs text-[#5B6B62]">
            Authorizations, EPR targets, and environmental safeguards under E-Waste (Management) Rules 2022
          </p>
        </div>

        <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-xl bg-[#E4F4EA] text-[#14634A] border border-[#14634A]/20 text-xs font-black">
          <ShieldCheck size={16} />
          <span>CPCB Registered: DL/2023/042</span>
        </div>
      </div>

      {/* Main License Card */}
      <div className="bg-white rounded-2xl border border-[#E3E0D5] p-5 sm:p-6 shadow-xs">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 border-b border-[#E3E0D5] pb-4">
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-black uppercase tracking-wider text-[#14634A] bg-[#E4F4EA] px-2.5 py-0.5 rounded-md">
                Certified Category-1 Recycler
              </span>
              <span className="text-xs text-[#5B6B62] font-semibold">SPCB Validated</span>
            </div>
            <h3 className="text-lg font-black text-[#14201A] mt-1">EcoBirba Circular Recyclers Pvt. Ltd.</h3>
            <p className="text-xs text-[#5B6B62]">Plot 48, Okhla Industrial Area Phase-III, New Delhi 110020</p>
          </div>

          <div className="flex items-center gap-3">
            <div className="text-right">
              <span className="text-[10px] text-[#5B6B62] uppercase tracking-wider block font-bold">License Expiry</span>
              <span className="text-sm font-black font-tabular text-[#0B3D2E]">31 Dec 2027</span>
            </div>
            <div className="w-10 h-10 rounded-full bg-[#E4F4EA] text-[#14634A] flex items-center justify-center">
              <Award size={22} />
            </div>
          </div>
        </div>

        {/* Capacity & Quota bar */}
        <div className="mt-5">
          <div className="flex items-center justify-between text-xs mb-1.5">
            <span className="font-bold text-[#14201A]">Annual Intake Quota (Form 1 Authorization)</span>
            <span className="font-black font-tabular text-[#0B3D2E]">412.8 / 1,200 Tonnes (34.4%)</span>
          </div>
          <div className="w-full h-3 rounded-full bg-[#E3E0D5] overflow-hidden">
            <div className="h-full bg-[#14634A] rounded-full transition-all" style={{ width: '34.4%' }} />
          </div>
          <div className="flex justify-between text-[11px] text-[#5B6B62] mt-1 font-tabular">
            <span>Intake to date: 412.8 MT</span>
            <span>Permitted Headroom: 787.2 MT</span>
          </div>
        </div>
      </div>

      {/* Grid: Safeguards & Statutory Filings */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Statutory Filings */}
        <div className="bg-white rounded-2xl border border-[#E3E0D5] p-5 shadow-xs flex flex-col justify-between">
          <div>
            <h4 className="text-sm font-black text-[#0B3D2E] flex items-center gap-2 mb-4">
              <FileCheck size={18} />
              <span>Statutory Return Filings</span>
            </h4>

            <div className="space-y-3 text-xs">
              <div className="p-3 rounded-xl bg-[#FAF8F5] border border-[#E3E0D5] flex items-center justify-between">
                <div>
                  <span className="font-bold text-[#14201A] block">Form 3 Annual E-Waste Return (FY25)</span>
                  <span className="text-[10px] text-[#5B6B62]">Acknowledged by DPCC on 28-Jun-2025</span>
                </div>
                <span className="px-2 py-0.5 rounded-md bg-[#E4F4EA] text-[#14634A] font-bold text-[10px]">
                  Submitted
                </span>
              </div>

              <div className="p-3 rounded-xl bg-[#FAF8F5] border border-[#E3E0D5] flex items-center justify-between">
                <div>
                  <span className="font-bold text-[#14201A] block">Form 4 Half-Yearly Log (H1 FY26)</span>
                  <span className="text-[10px] text-[#5B6B62]">Due in 42 days (30-Nov-2026)</span>
                </div>
                <span className="px-2 py-0.5 rounded-md bg-[#F2EFE9] text-[#0B3D2E] font-bold text-[10px]">
                  In Draft (92%)
                </span>
              </div>

              <div className="p-3 rounded-xl bg-[#FAF8F5] border border-[#E3E0D5] flex items-center justify-between">
                <div>
                  <span className="font-bold text-[#14201A] block">EPR Certificate Generation Portal</span>
                  <span className="text-[10px] text-[#5B6B62]">Sync via CPCB REST API v2</span>
                </div>
                <span className="px-2 py-0.5 rounded-md bg-[#E4F4EA] text-[#14634A] font-bold text-[10px]">
                  Active Sync
                </span>
              </div>
            </div>
          </div>

          <div className="mt-4 pt-3 border-t border-[#E3E0D5]">
            <a
              href="https://cpcb.nic.in"
              target="_blank"
              rel="noreferrer"
              className="text-xs font-bold text-[#14634A] hover:underline flex items-center gap-1"
            >
              <span>Visit National CPCB EPR Registry</span>
              <ExternalLink size={12} />
            </a>
          </div>
        </div>

        {/* Environmental Safeguards */}
        <div className="bg-white rounded-2xl border border-[#E3E0D5] p-5 shadow-xs">
          <h4 className="text-sm font-black text-[#0B3D2E] flex items-center gap-2 mb-4">
            <CheckCircle2 size={18} />
            <span>Hazard & Environmental Safeguards</span>
          </h4>

          <div className="space-y-3 text-xs">
            <div className="flex items-start gap-3 p-3 rounded-xl bg-[#FAF8F5] border border-[#E3E0D5]">
              <div className="w-6 h-6 rounded-full bg-[#E4F4EA] text-[#14634A] flex items-center justify-center shrink-0 mt-0.5">
                ✓
              </div>
              <div>
                <span className="font-bold text-[#14201A] block">RoHS De-soldering Air Filtration</span>
                <p className="text-[11px] text-[#5B6B62] mt-0.5">
                  HEPA + activated carbon multi-stage scrubbers prevent lead, cadmium and bromine emissions during component extraction.
                </p>
              </div>
            </div>

            <div className="flex items-start gap-3 p-3 rounded-xl bg-[#FAF8F5] border border-[#E3E0D5]">
              <div className="w-6 h-6 rounded-full bg-[#E4F4EA] text-[#14634A] flex items-center justify-center shrink-0 mt-0.5">
                ✓
              </div>
              <div>
                <span className="font-bold text-[#14201A] block">Lithium Battery Inert Depleting</span>
                <p className="text-[11px] text-[#5B6B62] mt-0.5">
                  Automated saline bath discharge system ensures zero thermal runaway risk during cathode/anode shredding.
                </p>
              </div>
            </div>

            <div className="flex items-start gap-3 p-3 rounded-xl bg-[#FAF8F5] border border-[#E3E0D5]">
              <div className="w-6 h-6 rounded-full bg-[#E4F4EA] text-[#14634A] flex items-center justify-center shrink-0 mt-0.5">
                ✓
              </div>
              <div>
                <span className="font-bold text-[#14201A] block">Zero Liquid Discharge (ZLD)</span>
                <p className="text-[11px] text-[#5B6B62] mt-0.5">
                  Closed-loop hydrometallurgical recovery process recirculates 98.4% of chemical leachates without ground release.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Cryptographic Traceability Notice */}
      <div className="bg-[#0B3D2E] text-white rounded-2xl p-5 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <span className="text-xs font-bold text-[#E9A310] uppercase tracking-wider block">Tamper-Evident Custody</span>
          <h4 className="text-base font-black text-white mt-0.5">Cryptographic Audit Chain for Every Intake</h4>
          <p className="text-xs text-white/70 max-w-xl mt-1">
            Every transaction is sealed with an immutable SHA-256 hash chaining geostamp, tare weight, and inspector digital signatures.
          </p>
        </div>

        <button
          onClick={() => navigate('/admin/trace')}
          className="px-4 py-2 rounded-xl bg-[#E9A310] hover:bg-[#D8950B] text-black text-xs font-black shrink-0 cursor-pointer shadow-sm touch-target"
        >
          Open Chain Explorer
        </button>
      </div>
    </div>
  );
};
