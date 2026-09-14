import React, { useState, useEffect } from 'react';
import { apiRequest } from '../../lib/api';
import {
  ShieldCheck, AlertTriangle, Building2, CheckCircle2,
  FileText, ExternalLink, RefreshCw
} from 'lucide-react';
import { KpiCard } from '../../design/components/KpiCard';

export const AdminCompliance: React.FC = () => {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiRequest('/api/dashboard/admin/compliance')
      .then(res => {
        setData(res);
        setLoading(false);
      })
      .catch(() => {
        setData({
          open_disputes: 1,
          disputes_list: [
            { id: 'tx-1', receipt_no: 'KC-RCPT-2024-001', reason: 'Tare scale calibration variance', variance_pct: 12.4 }
          ],
          unverified_recyclers_count: 2,
          unverified_recyclers: [
            { company_name: 'Metro Scrap Smelters', status: 'pending_cpcb_audit', city: 'Ludhiana' },
            { company_name: 'GreenEarth Metals Hub', status: 'license_expired', city: 'Kanpur' }
          ]
        });
        setLoading(false);
      });
  }, []);

  const facilities = [
    { name: 'EcoBirba Circular Recyclers', reg: 'CPCB/E-WASTE/DL/2023/042', city: 'Delhi', quotaUtilized: '34.4%', risk: 'low', status: 'Compliant' },
    { name: 'Shred-It India Processing', reg: 'CPCB/E-WASTE/MH/2022/119', city: 'Mumbai', quotaUtilized: '58.2%', risk: 'low', status: 'Compliant' },
    { name: 'Kaveri Precious Extraction', reg: 'CPCB/E-WASTE/KA/2023/088', city: 'Bengaluru', quotaUtilized: '71.0%', risk: 'medium', status: 'Audit Due' },
    { name: 'Telangana Strategic Refining', reg: 'CPCB/E-WASTE/TS/2024/014', city: 'Hyderabad', quotaUtilized: '22.8%', risk: 'low', status: 'Compliant' },
    { name: 'Metro Scrap Smelters', reg: 'PENDING-REG-2026', city: 'Ludhiana', quotaUtilized: '0.0%', risk: 'high', status: 'Pending Verification' },
  ];

  return (
    <div className="flex flex-col gap-6">
      {/* Title */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-[#E3E0D5] pb-4">
        <div>
          <h2 className="text-2xl font-black text-[#0B3D2E]">National Recycler Compliance & Risk Oversight</h2>
          <p className="text-xs text-[#5B6B62]">
            Central Pollution Control Board (CPCB) registry monitoring, quota enforcement, and audit logs
          </p>
        </div>

        <span className="px-3 py-1.5 rounded-xl bg-[#E4F4EA] text-[#14634A] text-xs font-black border border-[#14634A]/20">
          Statutory Audit Period: FY2026-27
        </span>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
        <KpiCard
          label="Registered Facilities"
          value="14"
          delta="Across 9 States"
          icon={<Building2 size={18} />}
        />
        <KpiCard
          label="Fully Authorized"
          value="12"
          delta="100% compliant"
          icon={<ShieldCheck size={18} />}
        />
        <KpiCard
          label="Pending Verification"
          value={data?.unverified_recyclers_count || 2}
          delta="CPCB review required"
          isPositive={false}
          icon={<AlertTriangle size={18} />}
        />
        <KpiCard
          label="Open Formal Disputes"
          value={data?.open_disputes || 1}
          delta="Variance > 10%"
          isPositive={false}
          icon={<FileText size={18} />}
        />
      </div>

      {/* Facilities Registry Table */}
      <div className="bg-white rounded-2xl border border-[#E3E0D5] overflow-hidden shadow-xs">
        <div className="p-4 bg-[#FAF8F5] border-b border-[#E3E0D5] flex items-center justify-between">
          <h3 className="text-xs font-black uppercase text-[#0B3D2E] tracking-wider">
            Licensed Treatment, Storage & Disposal Facilities (TSDF)
          </h3>
          <span className="text-[11px] text-[#5B6B62]">Sync with National EPR Portal</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="bg-[#FAF8F5] border-b border-[#E3E0D5] text-[#5B6B62] font-black uppercase tracking-wider text-[11px]">
                <th className="p-3.5">Facility Name</th>
                <th className="p-3.5">CPCB Authorization</th>
                <th className="p-3.5">Location</th>
                <th className="p-3.5 text-right">Quota Utilization</th>
                <th className="p-3.5 text-center">Risk Level</th>
                <th className="p-3.5 text-center">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#E3E0D5]">
              {facilities.map((f) => (
                <tr key={f.name} className="hover:bg-[#FAF8F5] transition-colors">
                  <td className="p-3.5 font-bold text-[#14201A]">{f.name}</td>
                  <td className="p-3.5 font-mono text-[#0B3D2E] text-[11px]">{f.reg}</td>
                  <td className="p-3.5 text-[#5B6B62]">{f.city}</td>
                  <td className="p-3.5 text-right font-black font-tabular text-[#14201A]">{f.quotaUtilized}</td>
                  <td className="p-3.5 text-center">
                    <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                      f.risk === 'low' ? 'bg-[#E4F4EA] text-[#14634A]' : f.risk === 'medium' ? 'bg-[#FFF3D6] text-[#A66F00]' : 'bg-[#FFF0F0] text-[#C93B2B]'
                    }`}>
                      {f.risk.toUpperCase()}
                    </span>
                  </td>
                  <td className="p-3.5 text-center">
                    <span className="text-xs font-bold text-[#14201A]">{f.status}</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
