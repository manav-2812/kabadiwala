import React, { useState } from 'react';
import {
  Boxes, Download, FileText, CheckCircle2,
  Calendar, ArrowUpRight, Search, ShieldCheck, Printer
} from 'lucide-react';
import { KpiCard } from '../../design/components/KpiCard';
import { formatINR, formatWeight } from '../../lib/format';

interface InventoryItem {
  id: string;
  category: string;
  materialName: string;
  weightKg: number;
  marketRateKg: number;
  totalValuePaise: number;
  cpcbCategory: string;
  storageBay: string;
}

interface ManifestEntry {
  id: string;
  lotCode: string;
  receiptNo: string;
  collectorName: string;
  material: string;
  weightKg: number;
  dateReceived: string;
  eprCredits: number;
  status: 'verified' | 'processed' | 'in_storage';
}

export const RecyclerInventory: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'inventory' | 'manifest'>('inventory');
  const [search, setSearch] = useState('');

  // Realistic seeded inventory state
  const inventoryData: InventoryItem[] = [
    { id: 'inv-1', category: 'High Value', materialName: 'High-Grade Telecom PCBs', weightKg: 1420.5, marketRateKg: 420, totalValuePaise: 59661000, cpcbCategory: 'ITEW1', storageBay: 'Bay-A1 (Secure)' },
    { id: 'inv-2', category: 'Batteries', materialName: 'Lithium-Ion EV & Laptop Packs', weightKg: 3850.0, marketRateKg: 185, totalValuePaise: 71225000, cpcbCategory: 'BATT-LI', storageBay: 'Bay-B3 (Fire-Safe)' },
    { id: 'inv-3', category: 'Metals', materialName: 'Stripped High-Purity Copper Cables', weightKg: 5120.0, marketRateKg: 510, totalValuePaise: 261120000, cpcbCategory: 'MET-CU', storageBay: 'Bay-C2 (Dry)' },
    { id: 'inv-4', category: 'Strategic', materialName: 'Neodymium Rare-Earth Hard Drive Magnets', weightKg: 640.0, marketRateKg: 240, totalValuePaise: 15360000, cpcbCategory: 'MIN-ND', storageBay: 'Bay-A2 (Enclosed)' },
    { id: 'inv-5', category: 'Displays', materialName: 'Flat Panel LED/LCD Monitors', weightKg: 2900.0, marketRateKg: 65, totalValuePaise: 18850000, cpcbCategory: 'ITEW4', storageBay: 'Bay-D1' },
    { id: 'inv-6', category: 'Plastics', materialName: 'Shredded ABS/PC Plastic Casings', weightKg: 6400.0, marketRateKg: 35, totalValuePaise: 22400000, cpcbCategory: 'ITEW-PL', storageBay: 'Bay-E4' },
  ];

  const manifestData: ManifestEntry[] = [
    { id: 'm-1', lotCode: 'KC-LOT-0001', receiptNo: 'KC-RCPT-2024-001', collectorName: 'Ramesh Kumar (DL-09)', material: 'High-Grade PCBs', weightKg: 5.2, dateReceived: '2026-09-18', eprCredits: 52, status: 'verified' },
    { id: 'm-2', lotCode: 'KC-LOT-0002', receiptNo: 'KC-RCPT-2024-002', collectorName: 'Gurpreet Singh (PB-10)', material: 'Lithium-Ion Packs', weightKg: 10.0, dateReceived: '2026-09-17', eprCredits: 100, status: 'processed' },
    { id: 'm-3', lotCode: 'KC-LOT-0003', receiptNo: 'KC-RCPT-2024-003', collectorName: 'Sunita Devi (DL-14)', material: 'Copper Wire', weightKg: 15.5, dateReceived: '2026-09-16', eprCredits: 155, status: 'verified' },
    { id: 'm-4', lotCode: 'KC-LOT-0004', receiptNo: 'KC-RCPT-2024-004', collectorName: 'Harbhajan Singh (PB-02)', material: 'Rare-Earth Magnets', weightKg: 2.0, dateReceived: '2026-09-16', eprCredits: 20, status: 'in_storage' },
    { id: 'm-5', lotCode: 'KC-LOT-0007', receiptNo: 'KC-RCPT-2024-005', collectorName: 'Mohd. Imran (DL-03)', material: 'Telecom PCBs', weightKg: 8.4, dateReceived: '2026-09-15', eprCredits: 84, status: 'verified' },
  ];

  const filteredInventory = inventoryData.filter(i => 
    i.materialName.toLowerCase().includes(search.toLowerCase()) ||
    i.cpcbCategory.toLowerCase().includes(search.toLowerCase())
  );

  const filteredManifest = manifestData.filter(m =>
    m.lotCode.toLowerCase().includes(search.toLowerCase()) ||
    m.receiptNo.toLowerCase().includes(search.toLowerCase()) ||
    m.collectorName.toLowerCase().includes(search.toLowerCase())
  );

  const handleDownloadCSV = () => {
    window.open('/api/dashboard/admin/export?format=csv', '_blank');
  };

  const handleOpenReceiptPDF = (receiptNo: string) => {
    window.open(`/api/documents/${receiptNo}/pdf`, '_blank');
  };

  return (
    <div className="flex flex-col gap-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-[#E3E0D5] pb-4">
        <div>
          <h2 className="text-2xl font-black text-[#0B3D2E]">EPR Inventory & Manifest</h2>
          <p className="text-xs text-[#5B6B62]">
            Statutory tracking of intake, warehouse bays, and CPCB Form 6 manifests
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={handleDownloadCSV}
            className="px-3.5 py-2 rounded-xl bg-[#0B3D2E] hover:bg-[#14634A] text-white text-xs font-bold flex items-center gap-2 cursor-pointer shadow-sm touch-target"
          >
            <Download size={14} />
            <span>Export Manifest (CSV)</span>
          </button>
          <button
            onClick={() => handleOpenReceiptPDF('KC-RCPT-2024-001')}
            className="px-3.5 py-2 rounded-xl bg-white border border-[#D1CEBF] hover:bg-[#F2EFE9] text-[#0B3D2E] text-xs font-bold flex items-center gap-2 cursor-pointer shadow-sm touch-target"
          >
            <Printer size={14} />
            <span>Print Form 6 PDF</span>
          </button>
        </div>
      </div>

      {/* KPI Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
        <KpiCard
          label="Total Stock on Site"
          value="20.33 T"
          delta="6 bays operational"
          icon={<Boxes size={18} />}
        />
        <KpiCard
          label="Stock Asset Value"
          value="₹44.86 L"
          delta="Mark-to-market"
          icon={<ShieldCheck size={18} />}
        />
        <KpiCard
          label="EPR Credits Generated"
          value="4,110 Pts"
          delta="100% CPCB verified"
          icon={<CheckCircle2 size={18} />}
        />
        <KpiCard
          label="Form 6 Manifests"
          value="120 Lots"
          delta="0 pending filings"
          icon={<FileText size={18} />}
        />
      </div>

      {/* View Switcher Tabs & Search */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div className="flex items-center bg-[#E3E0D5] p-1 rounded-xl w-fit">
          <button
            onClick={() => setActiveTab('inventory')}
            className={`px-4 py-1.5 rounded-lg text-xs font-bold transition-all cursor-pointer ${
              activeTab === 'inventory' ? 'bg-white text-[#0B3D2E] shadow-sm' : 'text-[#5B6B62] hover:text-[#14201A]'
            }`}
          >
            Bay Inventory (Stock)
          </button>
          <button
            onClick={() => setActiveTab('manifest')}
            className={`px-4 py-1.5 rounded-lg text-xs font-bold transition-all cursor-pointer ${
              activeTab === 'manifest' ? 'bg-white text-[#0B3D2E] shadow-sm' : 'text-[#5B6B62] hover:text-[#14201A]'
            }`}
          >
            Statutory Manifest Log
          </button>
        </div>

        <div className="relative w-full sm:w-64">
          <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-[#5B6B62]" />
          <input
            type="text"
            placeholder={activeTab === 'inventory' ? 'Filter materials or bays...' : 'Search lot or receipt...'}
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-9 pr-3 py-1.5 rounded-xl border border-[#D1CEBF] bg-white text-xs text-[#14201A] focus:outline-none focus:border-[#14634A]"
          />
        </div>
      </div>

      {/* Tab 1: Bay Inventory */}
      {activeTab === 'inventory' && (
        <div className="bg-white rounded-2xl border border-[#E3E0D5] overflow-hidden shadow-xs">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="bg-[#FAF8F5] border-b border-[#E3E0D5] text-[#5B6B62] font-black uppercase tracking-wider text-[11px]">
                  <th className="p-3.5">Material & Category</th>
                  <th className="p-3.5">CPCB Code</th>
                  <th className="p-3.5">Storage Bay</th>
                  <th className="p-3.5 text-right">Physical Stock</th>
                  <th className="p-3.5 text-right">Market Rate</th>
                  <th className="p-3.5 text-right">Asset Value</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#E3E0D5]">
                {filteredInventory.map((item) => (
                  <tr key={item.id} className="hover:bg-[#FAF8F5] transition-colors">
                    <td className="p-3.5 font-bold text-[#14201A]">
                      <div>{item.materialName}</div>
                      <span className="text-[10px] text-[#5B6B62] font-semibold">{item.category}</span>
                    </td>
                    <td className="p-3.5 font-mono text-[#0B3D2E] font-bold">
                      {item.cpcbCategory}
                    </td>
                    <td className="p-3.5">
                      <span className="px-2 py-0.5 rounded-md bg-[#F2EFE9] text-[#14201A] font-semibold text-[11px]">
                        {item.storageBay}
                      </span>
                    </td>
                    <td className="p-3.5 text-right font-black font-tabular text-[#0B3D2E] text-sm">
                      {formatWeight(item.weightKg)}
                    </td>
                    <td className="p-3.5 text-right font-tabular text-[#5B6B62]">
                      ₹{item.marketRateKg}/kg
                    </td>
                    <td className="p-3.5 text-right font-black font-tabular text-[#14201A]">
                      {formatINR(item.totalValuePaise)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Tab 2: Manifest Log */}
      {activeTab === 'manifest' && (
        <div className="bg-white rounded-2xl border border-[#E3E0D5] overflow-hidden shadow-xs">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="bg-[#FAF8F5] border-b border-[#E3E0D5] text-[#5B6B62] font-black uppercase tracking-wider text-[11px]">
                  <th className="p-3.5">Lot & Receipt</th>
                  <th className="p-3.5">Collector (Source)</th>
                  <th className="p-3.5">Material</th>
                  <th className="p-3.5 text-right">Weight</th>
                  <th className="p-3.5 text-center">Date Received</th>
                  <th className="p-3.5 text-center">EPR Status</th>
                  <th className="p-3.5 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#E3E0D5]">
                {filteredManifest.map((entry) => (
                  <tr key={entry.id} className="hover:bg-[#FAF8F5] transition-colors">
                    <td className="p-3.5 font-mono font-bold text-[#0B3D2E]">
                      <div>{entry.lotCode}</div>
                      <span className="text-[10px] text-[#5B6B62]">{entry.receiptNo}</span>
                    </td>
                    <td className="p-3.5 font-medium text-[#14201A]">
                      {entry.collectorName}
                    </td>
                    <td className="p-3.5 font-medium text-[#14201A]">
                      {entry.material}
                    </td>
                    <td className="p-3.5 text-right font-black font-tabular text-[#14201A]">
                      {formatWeight(entry.weightKg)}
                    </td>
                    <td className="p-3.5 text-center text-[#5B6B62] font-tabular">
                      {entry.dateReceived}
                    </td>
                    <td className="p-3.5 text-center">
                      <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-[#E4F4EA] text-[#14634A]">
                        <CheckCircle2 size={11} />
                        CPCB Form 6 OK
                      </span>
                    </td>
                    <td className="p-3.5 text-right">
                      <button
                        onClick={() => handleOpenReceiptPDF(entry.receiptNo)}
                        className="p-1.5 rounded-lg border border-[#D1CEBF] hover:bg-[#F2EFE9] text-[#0B3D2E] inline-flex items-center gap-1 text-[11px] font-bold cursor-pointer"
                        title="Download Certificate PDF"
                      >
                        <FileText size={13} />
                        <span>PDF</span>
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};
