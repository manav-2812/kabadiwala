import React, { useState } from 'react';
import {
  Headphones, AlertCircle, CheckCircle2, Clock,
  Mic, User, ArrowUpRight, MessageSquare, ShieldAlert
} from 'lucide-react';
import { StatusPill } from '../../design/components/StatusPill';

interface SupportTicketItem {
  id: string;
  ticketNo: string;
  category: 'weight_dispute' | 'payment_delay' | 'hazard_guidance' | 'general';
  raisedBy: string;
  role: 'collector' | 'recycler';
  phone: string;
  subject: string;
  description: string;
  hasVoiceNote: boolean;
  slaBreachHours: number;
  isBreached: boolean;
  status: 'open' | 'in_progress' | 'resolved';
}

export const AdminSupportQueue: React.FC = () => {
  const [tickets, setTickets] = useState<SupportTicketItem[]>([
    {
      id: 't-1',
      ticketNo: 'TKT-2026-081',
      category: 'weight_dispute',
      raisedBy: 'Ramesh Kumar',
      role: 'collector',
      phone: '+91 98100 12345',
      subject: 'Scale Tare Variance > 12% at Okhla Hub',
      description: 'Collector weighed 14.5 kg PCB on field spring scale, recycler weigh-bridge recorded 12.8 kg. Hold placed on final payment.',
      hasVoiceNote: true,
      slaBreachHours: 1.2,
      isBreached: false,
      status: 'open'
    },
    {
      id: 't-2',
      ticketNo: 'TKT-2026-079',
      category: 'payment_delay',
      raisedBy: 'Gurpreet Singh',
      role: 'collector',
      phone: '+91 98200 67890',
      subject: 'UPI Gateway Timeout on Axis Bank Ref',
      description: 'Lot KC-LOT-0002 marked weighed, payment initiated but webhook delayed by 18 minutes. Pending fallback cash voucher or re-trigger.',
      hasVoiceNote: false,
      slaBreachHours: 2.4,
      isBreached: true,
      status: 'in_progress'
    },
    {
      id: 't-3',
      ticketNo: 'TKT-2026-075',
      category: 'hazard_guidance',
      raisedBy: 'EcoBirba Circular Recyclers',
      role: 'recycler',
      phone: '+91 11 2681 4040',
      subject: 'Swollen Li-Ion Pouch Cell in Batch DL-14',
      description: 'Incoming scrap contains 2x swollen 5000mAh drone battery packs. Requires immersion container disposal protocol.',
      hasVoiceNote: false,
      slaBreachHours: 0.5,
      isBreached: false,
      status: 'open'
    },
    {
      id: 't-4',
      ticketNo: 'TKT-2026-068',
      category: 'general',
      raisedBy: 'Sunita Devi',
      role: 'collector',
      phone: '+91 98300 11223',
      subject: 'Verification of Ayushman Bharat Insurance Link',
      description: 'Collector completed 10 formalised lots, requesting verification of health cover benefit issuance.',
      hasVoiceNote: true,
      slaBreachHours: 0,
      isBreached: false,
      status: 'resolved'
    }
  ]);

  const [activeTicket, setActiveTicket] = useState<SupportTicketItem | null>(tickets[0]);
  const [replyText, setReplyText] = useState('');

  const handleResolve = (id: string) => {
    setTickets(prev => prev.map(t => t.id === id ? { ...t, status: 'resolved' } : t));
    if (activeTicket?.id === id) {
      setActiveTicket(prev => prev ? { ...prev, status: 'resolved' } : null);
    }
  };

  return (
    <div className="flex flex-col gap-6">
      {/* Title */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-[#E3E0D5] pb-4">
        <div>
          <h2 className="text-2xl font-black text-[#0B3D2E]">Support Desk & Dispute Resolution</h2>
          <p className="text-xs text-[#5B6B62]">
            Automated SLA enforcement, Vernacular voice recordings, and weight variance arbitration
          </p>
        </div>

        <div className="flex items-center gap-2">
          <span className="px-3 py-1 rounded-xl bg-[#FFF0F0] text-[#C93B2B] text-xs font-bold border border-[#C93B2B]/20 flex items-center gap-1.5">
            <Clock size={13} />
            <span>1 Ticket in SLA Breach</span>
          </span>
          <span className="px-3 py-1 rounded-xl bg-[#E4F4EA] text-[#14634A] text-xs font-bold border border-[#14634A]/20">
            Avg Resolution: 24m
          </span>
        </div>
      </div>

      {/* Grid: Queue & Ticket Details */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left: Tickets List (5 cols) */}
        <div className="lg:col-span-5 bg-white rounded-2xl border border-[#E3E0D5] overflow-hidden shadow-xs flex flex-col">
          <div className="p-3.5 bg-[#FAF8F5] border-b border-[#E3E0D5] text-xs font-black text-[#5B6B62] uppercase tracking-wider">
            Active Tickets ({tickets.length})
          </div>

          <div className="divide-y divide-[#E3E0D5] overflow-y-auto max-h-[600px]">
            {tickets.map((t) => {
              const isSelected = activeTicket?.id === t.id;
              return (
                <div
                  key={t.id}
                  onClick={() => setActiveTicket(t)}
                  className={`p-4 cursor-pointer transition-colors ${
                    isSelected ? 'bg-[#FAF8F5] border-l-4 border-l-[#0B3D2E]' : 'hover:bg-[#FAF8F5]/50'
                  }`}
                >
                  <div className="flex items-center justify-between gap-2 mb-1.5">
                    <span className="font-mono text-xs font-black text-[#0B3D2E]">{t.ticketNo}</span>
                    <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                      t.status === 'resolved'
                        ? 'bg-[#E4F4EA] text-[#14634A]'
                        : t.isBreached
                        ? 'bg-[#FFF0F0] text-[#C93B2B]'
                        : 'bg-[#FFF3D6] text-[#A66F00]'
                    }`}>
                      {t.isBreached ? 'SLA BREACH' : t.status.toUpperCase()}
                    </span>
                  </div>

                  <h4 className="text-xs font-bold text-[#14201A] line-clamp-1">{t.subject}</h4>
                  
                  <div className="flex items-center justify-between text-[11px] text-[#5B6B62] mt-2">
                    <span className="flex items-center gap-1 font-medium">
                      <User size={12} />
                      {t.raisedBy} ({t.role})
                    </span>
                    {t.hasVoiceNote && (
                      <span className="flex items-center gap-1 text-[#14634A] font-bold text-[10px]">
                        <Mic size={11} /> Voice Note
                      </span>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Right: Active Ticket Inspection (7 cols) */}
        {activeTicket ? (
          <div className="lg:col-span-7 bg-white rounded-2xl border border-[#E3E0D5] p-5 sm:p-6 shadow-xs flex flex-col justify-between">
            <div>
              {/* Header */}
              <div className="flex items-start justify-between gap-3 border-b border-[#E3E0D5] pb-4">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-xs font-black text-[#0B3D2E]">{activeTicket.ticketNo}</span>
                    <span className="text-xs px-2 py-0.5 rounded bg-[#FAF8F5] text-[#5B6B62] font-semibold border border-[#E3E0D5]">
                      Category: {activeTicket.category.replace(/_/g, ' ')}
                    </span>
                  </div>
                  <h3 className="text-base font-black text-[#14201A] mt-1.5">{activeTicket.subject}</h3>
                </div>

                <div className="text-right">
                  <span className="text-[10px] text-[#5B6B62] block uppercase font-bold">Contact</span>
                  <span className="text-xs font-bold text-[#14201A] font-tabular">{activeTicket.phone}</span>
                </div>
              </div>

              {/* Description Body */}
              <div className="mt-4">
                <span className="text-[11px] font-bold text-[#5B6B62] uppercase tracking-wider block mb-1">
                  Incident Details
                </span>
                <p className="text-xs text-[#14201A] bg-[#FAF8F5] p-3 rounded-xl border border-[#E3E0D5] leading-relaxed">
                  {activeTicket.description}
                </p>
              </div>

              {/* Voice Note Player (Simulation) */}
              {activeTicket.hasVoiceNote && (
                <div className="mt-4 p-3.5 rounded-xl bg-[#E4F4EA] border border-[#14634A]/20 flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-full bg-[#14634A] text-white flex items-center justify-center">
                      <Mic size={16} />
                    </div>
                    <div>
                      <span className="text-xs font-bold text-[#14201A] block">Recorded Vernacular Voice Note</span>
                      <span className="text-[10px] text-[#14634A] font-semibold">Hindi Audio (0:24s) — Transcribed</span>
                    </div>
                  </div>

                  <button
                    onClick={() => alert('Playing voice memo: "Bhaiya weighbridge pe 12.8 kg bataya jabki maine kanta pe 14.5 kg dekha tha..."')}
                    className="px-3 py-1 rounded-lg bg-white border border-[#D1CEBF] text-xs font-bold text-[#0B3D2E] hover:bg-[#F2EFE9] cursor-pointer"
                  >
                    Play Audio
                  </button>
                </div>
              )}

              {/* Auto-Responder SLA timer */}
              <div className="mt-4 flex items-center gap-2 text-xs text-[#5B6B62]">
                <Clock size={14} className="text-[#E9A310]" />
                <span>Auto-SLA: 2-hour guarantee under Citizen Grievance Charter. Assigned to Mediation Desk.</span>
              </div>
            </div>

            {/* Arbitration Resolution Controls */}
            <div className="mt-6 pt-4 border-t border-[#E3E0D5] flex flex-col gap-3">
              <input
                type="text"
                placeholder="Type resolution remark or arbitrator directive..."
                value={replyText}
                onChange={(e) => setReplyText(e.target.value)}
                className="w-full px-3 py-2 rounded-xl border border-[#D1CEBF] text-xs text-[#14201A] focus:outline-none focus:border-[#14634A]"
              />

              <div className="flex items-center justify-end gap-2">
                <button
                  onClick={() => alert('Dispute escalated to CPCB Nodal Officer')}
                  className="px-3.5 py-1.5 rounded-xl bg-white border border-[#D1CEBF] hover:bg-[#F2EFE9] text-[#5B6B62] text-xs font-bold cursor-pointer"
                >
                  Escalate to CPCB
                </button>
                <button
                  onClick={() => handleResolve(activeTicket.id)}
                  className="px-4 py-1.5 rounded-xl bg-[#0B3D2E] hover:bg-[#14634A] text-white text-xs font-bold flex items-center gap-1.5 cursor-pointer shadow-xs"
                >
                  <CheckCircle2 size={14} />
                  <span>Mark Resolved</span>
                </button>
              </div>
            </div>
          </div>
        ) : (
          <div className="lg:col-span-7 bg-white rounded-2xl border border-[#E3E0D5] p-8 text-center text-xs text-[#5B6B62]">
            Select a ticket from the queue to inspect details
          </div>
        )}
      </div>
    </div>
  );
};
