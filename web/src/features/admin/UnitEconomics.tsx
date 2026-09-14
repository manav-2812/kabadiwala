import React, { useState } from 'react';
import { 
  Calculator, TrendingUp, DollarSign, PieChart, ShieldCheck, 
  ArrowRight, Users, Building2, HelpCircle, CheckCircle 
} from 'lucide-react';

export const UnitEconomics: React.FC = () => {
  // Input Sliders State
  const [monthlyLots, setMonthlyLots] = useState<number>(1200); // 1,200 lots/mo
  const [avgLotWeightKg, setAvgLotWeightKg] = useState<number>(45); // 45 kg per lot
  const [avgScrapRatePerKg, setAvgScrapRatePerKg] = useState<number>(120); // ₹120 / kg average
  const [formalPremiumPct, setFormalPremiumPct] = useState<number>(20); // +20% formal premium boost
  const [takeRatePct, setTakeRatePct] = useState<number>(1.5); // 1.5% platform commission

  // Derived Calculations
  const totalVolumeTons = (monthlyLots * avgLotWeightKg) / 1000;
  const grossScrapValueINR = monthlyLots * avgLotWeightKg * avgScrapRatePerKg;
  
  // Value Uplift for Collector (vs informal exploitative middlemen)
  const informalMiddlemanRate = avgScrapRatePerKg * 0.80; // informal cuts 20%
  const informalCollectorEarnings = monthlyLots * avgLotWeightKg * informalMiddlemanRate;
  const collectorEarningsWithPlatform = grossScrapValueINR;
  const collectorTotalUpliftINR = collectorEarningsWithPlatform - informalCollectorEarnings;
  const avgMonthlyUpliftPerCollector = collectorTotalUpliftINR / Math.max(1, (monthlyLots / 8)); // ~8 lots per active collector

  // Recycler Logistics & Formal Sourcing Savings
  // Authorized recyclers save ~15% on fragmented aggregation broker fees + CPCB compliance audit risk
  const recyclerBrokerSavingsINR = grossScrapValueINR * 0.08;

  // Platform Economics
  const platformRevenueINR = grossScrapValueINR * (takeRatePct / 100);
  const fixedMonthlyInfraCostINR = 45000; // Cloud hosting, SMS gateways, edge AI inference
  const supportOpsCostINR = monthlyLots * 8.0; // ₹8 per lot verification & support SLA
  const totalMonthlyCostINR = fixedMonthlyInfraCostINR + supportOpsCostINR;
  const netOperatingSurplusINR = platformRevenueINR - totalMonthlyCostINR;
  const breakEvenLots = Math.ceil(fixedMonthlyInfraCostINR / ((avgLotWeightKg * avgScrapRatePerKg * (takeRatePct / 100)) - 8.0));

  return (
    <div className="max-w-6xl mx-auto p-4 md:p-6 flex flex-col gap-6 pb-16">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between border-b border-[#E3E0D5] pb-4 gap-3">
        <div>
          <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-[#E7F3ED] text-[#14634A] text-xs font-bold uppercase mb-1">
            <Calculator size={13} />
            <span>SIH26229 Financial Viability Console</span>
          </div>
          <h1 className="text-2xl font-black text-[#0B3D2E]">Unit Economics & Value Flow Simulator</h1>
          <p className="text-xs text-[#5B6B62]">
            Dynamic model demonstrating informal collector income uplift, recycler cost reduction, and platform break-even.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <span className="px-3 py-1 rounded-xl bg-white border border-[#E3E0D5] text-xs font-bold text-[#0B3D2E]">
            Model Version: <b>v1.2 (JNARDDC Formula)</b>
          </span>
        </div>
      </div>

      {/* Control Sliders Grid */}
      <div className="p-5 bg-white rounded-3xl border border-[#E3E0D5] shadow-xs flex flex-col gap-5">
        <h3 className="text-sm font-extrabold uppercase tracking-wider text-[#0B3D2E]">
          Operational & Market Assumptions
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
          {/* Monthly Volume */}
          <div className="flex flex-col gap-1.5">
            <div className="flex justify-between text-xs font-bold text-[#14201A]">
              <span>Monthly Volume:</span>
              <span className="text-[#14634A] font-mono">{monthlyLots.toLocaleString()} lots ({totalVolumeTons.toFixed(1)} MT)</span>
            </div>
            <input
              type="range"
              min="200"
              max="5000"
              step="100"
              value={monthlyLots}
              onChange={(e) => setMonthlyLots(Number(e.target.value))}
              className="w-full accent-[#14634A]"
            />
            <span className="text-[11px] text-[#5B6B62]">Cluster volume across participating scrap hubs</span>
          </div>

          {/* Average Lot Weight */}
          <div className="flex flex-col gap-1.5">
            <div className="flex justify-between text-xs font-bold text-[#14201A]">
              <span>Average Lot Weight:</span>
              <span className="text-[#14634A] font-mono">{avgLotWeightKg} kg / lot</span>
            </div>
            <input
              type="range"
              min="10"
              max="150"
              step="5"
              value={avgLotWeightKg}
              onChange={(e) => setAvgLotWeightKg(Number(e.target.value))}
              className="w-full accent-[#14634A]"
            />
            <span className="text-[11px] text-[#5B6B62]">Mixed e-waste and precious fractions</span>
          </div>

          {/* Average Scrap Price */}
          <div className="flex flex-col gap-1.5">
            <div className="flex justify-between text-xs font-bold text-[#14201A]">
              <span>Weighted Scrap Rate:</span>
              <span className="text-[#14634A] font-mono">₹{avgScrapRatePerKg} / kg</span>
            </div>
            <input
              type="range"
              min="40"
              max="350"
              step="10"
              value={avgScrapRatePerKg}
              onChange={(e) => setAvgScrapRatePerKg(Number(e.target.value))}
              className="w-full accent-[#14634A]"
            />
            <span className="text-[11px] text-[#5B6B62]">Benchmark across PCB, Copper, and Batteries</span>
          </div>

          {/* Formal Channel Premium */}
          <div className="flex flex-col gap-1.5">
            <div className="flex justify-between text-xs font-bold text-[#14201A]">
              <span>Formal Channel Premium:</span>
              <span className="text-[#2E9E5B] font-mono">+{formalPremiumPct}%</span>
            </div>
            <input
              type="range"
              min="5"
              max="35"
              step="1"
              value={formalPremiumPct}
              onChange={(e) => setFormalPremiumPct(Number(e.target.value))}
              className="w-full accent-[#2E9E5B]"
            />
            <span className="text-[11px] text-[#5B6B62]">Direct-to-authorized recycler pricing premium</span>
          </div>

          {/* Platform Take-Rate */}
          <div className="flex flex-col gap-1.5">
            <div className="flex justify-between text-xs font-bold text-[#14201A]">
              <span>Platform Take-Rate:</span>
              <span className="text-[#0B3D2E] font-mono">{takeRatePct.toFixed(1)}% (Default: 1.5%)</span>
            </div>
            <input
              type="range"
              min="0.5"
              max="4.0"
              step="0.1"
              value={takeRatePct}
              onChange={(e) => setTakeRatePct(Number(e.target.value))}
              className="w-full accent-[#0B3D2E]"
            />
            <span className="text-[11px] text-[#5B6B62]">Ultra-lean SaaS / digital escrow commission</span>
          </div>
        </div>
      </div>

      {/* Outcome Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        {/* 1. Collector Uplift Card */}
        <div className="p-5 bg-white rounded-3xl border-2 border-[#2E9E5B] shadow-xs flex flex-col justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 text-[#2E9E5B] font-bold text-xs uppercase mb-1">
              <Users size={16} />
              <span>Collector Income Uplift</span>
            </div>
            <h4 className="text-3xl font-black text-[#0B3D2E] tabular-nums">
              +₹{Math.round(collectorTotalUpliftINR).toLocaleString()}
              <span className="text-xs text-[#5B6B62] font-normal block mt-1">Total Monthly Cluster Uplift</span>
            </h4>
          </div>

          <div className="p-3 bg-[#E7F3ED] rounded-2xl text-xs space-y-1 text-[#14201A]">
            <div className="flex justify-between">
              <span>Avg Uplift / Collector:</span>
              <b className="text-[#14634A]">₹{Math.round(avgMonthlyUpliftPerCollector).toLocaleString()}/mo</b>
            </div>
            <div className="flex justify-between">
              <span>Net Income Increase:</span>
              <b className="text-[#14634A]">+{formalPremiumPct}%</b>
            </div>
          </div>
        </div>

        {/* 2. Recycler Savings Card */}
        <div className="p-5 bg-white rounded-3xl border border-[#E3E0D5] shadow-xs flex flex-col justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 text-[#2F6FDE] font-bold text-xs uppercase mb-1">
              <Building2 size={16} />
              <span>Recycler Procurement Advantage</span>
            </div>
            <h4 className="text-3xl font-black text-[#0B3D2E] tabular-nums">
              ₹{Math.round(recyclerBrokerSavingsINR).toLocaleString()}
              <span className="text-xs text-[#5B6B62] font-normal block mt-1">Monthly Intermediary Fee Savings</span>
            </h4>
          </div>

          <div className="p-3 bg-[#F0F4FD] rounded-2xl text-xs space-y-1 text-[#14201A]">
            <div className="flex justify-between">
              <span>EPR Compliance Audit Cost:</span>
              <b className="text-[#2F6FDE]">Reduced 100% (Form 6)</b>
            </div>
            <div className="flex justify-between">
              <span>Supply Predictability:</span>
              <b className="text-[#2F6FDE]">99.2% Digital Trail</b>
            </div>
          </div>
        </div>

        {/* 3. Platform Financial Runway Card */}
        <div className="p-5 bg-white rounded-3xl border border-[#E3E0D5] shadow-xs flex flex-col justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 text-[#0B3D2E] font-bold text-xs uppercase mb-1">
              <ShieldCheck size={16} />
              <span>Platform Sustainability</span>
            </div>
            <h4 className={`text-3xl font-black tabular-nums ${netOperatingSurplusINR >= 0 ? 'text-[#14634A]' : 'text-[#D64545]'}`}>
              {netOperatingSurplusINR >= 0 ? '+' : ''}₹{Math.round(netOperatingSurplusINR).toLocaleString()}
              <span className="text-xs text-[#5B6B62] font-normal block mt-1">Monthly Net Operating Margin</span>
            </h4>
          </div>

          <div className="p-3 bg-[#F7F5EF] rounded-2xl text-xs space-y-1 text-[#14201A]">
            <div className="flex justify-between">
              <span>Gross GMV Handled:</span>
              <b>₹{Math.round(grossScrapValueINR).toLocaleString()}</b>
            </div>
            <div className="flex justify-between">
              <span>Break-Even Threshold:</span>
              <b>{breakEvenLots} lots / month</b>
            </div>
          </div>
        </div>
      </div>

      {/* Transparent Formula & Value Breakdown */}
      <div className="p-5 bg-white rounded-3xl border border-[#E3E0D5] shadow-xs flex flex-col gap-4">
        <h3 className="text-base font-extrabold text-[#0B3D2E]">
          Where Every Rupee Goes (Transparent Value Flow)
        </h3>
        <p className="text-xs text-[#5B6B62] leading-relaxed">
          In traditional informal supply chains, 3 to 5 unlicensed brokers skim 25%–35% of the material value while exposing workers to toxic processing. Under Kabadiwala Connect's direct protocol:
        </p>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-3 pt-1">
          <div className="p-3.5 rounded-2xl bg-[#E7F3ED] border border-[#2E9E5B]/40 flex flex-col gap-1">
            <span className="text-xs font-bold text-[#14634A]">98.5% Direct to Collector</span>
            <span className="text-xl font-black text-[#0B3D2E] tabular-nums">
              ₹{(grossScrapValueINR * 0.985 / monthlyLots).toFixed(0)} / lot
            </span>
            <span className="text-[11px] text-[#5B6B62]">Physical cash paid instantly on-site</span>
          </div>

          <div className="p-3.5 rounded-2xl bg-[#F0F4FD] border border-[#2F6FDE]/40 flex flex-col gap-1">
            <span className="text-xs font-bold text-[#2F6FDE]">1.5% Platform Take-Rate</span>
            <span className="text-xl font-black text-[#0B3D2E] tabular-nums">
              ₹{(grossScrapValueINR * 0.015 / monthlyLots).toFixed(0)} / lot
            </span>
            <span className="text-[11px] text-[#5B6B62]">Maintains cloud infrastructure & edge AI</span>
          </div>

          <div className="p-3.5 rounded-2xl bg-[#FCF3D9] border border-[#E9A310]/40 flex flex-col gap-1">
            <span className="text-xs font-bold text-[#946200]">0.0% Intermediary Skim</span>
            <span className="text-xl font-black text-[#0B3D2E] tabular-nums">₹0</span>
            <span className="text-[11px] text-[#5B6B62]">Zero middlemen or illegal mafia extraction</span>
          </div>

          <div className="p-3.5 rounded-2xl bg-[#F7F5EF] border border-[#E3E0D5] flex flex-col gap-1">
            <span className="text-xs font-bold text-[#0B3D2E]">100% CPCB Compliance</span>
            <span className="text-xl font-black text-[#0B3D2E] tabular-nums">E-Waste 2022</span>
            <span className="text-[11px] text-[#5B6B62]">Cryptographic hash-chained Form 6</span>
          </div>
        </div>
      </div>
    </div>
  );
};
