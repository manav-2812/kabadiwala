import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiRequest } from '../../lib/api';
import { VoiceButton } from '../../design/components/VoiceButton';
import { StatusPill } from '../../design/components/StatusPill';
import { BigButton } from '../../design/components/BigButton';
import {
  HelpCircle, MessageSquare, Phone, ChevronDown,
  ChevronUp, Mic, Send, Plus, Shield
} from 'lucide-react';
import { useTranslation } from 'react-i18next';

export const SupportHub: React.FC = () => {
  const [faqs, setFaqs] = useState<any[]>([]);
  const [tickets, setTickets] = useState<any[]>([]);
  const [expandedFaq, setExpandedFaq] = useState<string | null>(null);
  const [showNewTicket, setShowNewTicket] = useState(false);
  const [category, setCategory] = useState('payment');
  const [message, setMessage] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const [voiceRecorded, setVoiceRecorded] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  
  const navigate = useNavigate();
  const { t, i18n } = useTranslation();

  const fetchSupport = () => {
    apiRequest(`/api/support/faqs?lang=${i18n.language}`)
      .then(setFaqs)
      .catch(() => {});

    apiRequest('/api/support/tickets')
      .then(setTickets)
      .catch(() => {});
  };

  useEffect(() => {
    fetchSupport();
  }, [i18n.language]);

  const handleToggleRecord = () => {
    if (!isRecording) {
      setIsRecording(true);
      setTimeout(() => {
        setIsRecording(false);
        setVoiceRecorded(true);
        if (!message) setMessage('Voice note recorded (18s)');
      }, 3000); // Simulate 3s speech capture
    } else {
      setIsRecording(false);
      setVoiceRecorded(true);
    }
  };

  const handleCreateTicket = async () => {
    if (!message) return;
    setSubmitting(true);
    try {
      const res = await apiRequest('/api/support/tickets', {
        method: 'POST',
        body: JSON.stringify({
          category,
          message,
          language: i18n.language,
          attachment_type: voiceRecorded ? 'voice' : 'none',
          duration_s: voiceRecorded ? 18 : null
        })
      });
      setShowNewTicket(false);
      setMessage('');
      setVoiceRecorded(false);
      fetchSupport();
      navigate(`/support/ticket/${res.id}`);
    } catch {
      alert('Ticket logged');
      setShowNewTicket(false);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="flex flex-col gap-4 pb-6">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-[#E3E0D5] pb-2">
        <div className="flex items-center gap-2">
          <HelpCircle size={22} className="text-[#0B3D2E]" />
          <h2 className="text-lg font-black text-[#0B3D2E]">
            {t('help_center')}
          </h2>
        </div>
        <button
          onClick={() => setShowNewTicket(true)}
          className="flex items-center gap-1 px-3 py-1.5 rounded-xl bg-[#14634A] text-white text-xs font-bold cursor-pointer"
        >
          <Plus size={14} />
          <span>New Ticket</span>
        </button>
      </div>

      {/* Direct Contact Cards */}
      <div className="grid grid-cols-2 gap-2.5">
        <a
          href="#"
          onClick={(e) => { e.preventDefault(); }}
          title="Calling is disabled in demo"
          className="flex items-center gap-2 p-3 rounded-2xl bg-white border border-[#E3E0D5] opacity-75 cursor-not-allowed touch-target"
        >
          <div className="p-2 rounded-xl bg-[#E4F4EA] text-[#0B3D2E]">
            <Phone size={18} />
          </div>
          <div>
            <span className="text-xs font-bold text-[#14201A] block">Toll-Free Support</span>
            <span className="text-[10px] text-[#5B6B62]">1800-11-2233 (Demo)</span>
          </div>
        </a>

        <a
          href="https://wa.me/919876543210"
          target="_blank"
          rel="noreferrer"
          className="flex items-center gap-2 p-3 rounded-2xl bg-white border border-[#E3E0D5] hover:border-[#14634A] touch-target"
        >
          <div className="p-2 rounded-xl bg-[#E4F4EA] text-[#2E9E5B]">
            <MessageSquare size={18} />
          </div>
          <div>
            <span className="text-xs font-bold text-[#14201A] block">WhatsApp Help</span>
            <span className="text-[10px] text-[#5B6B62]">Instant Reply</span>
          </div>
        </a>
      </div>

      {/* My Tickets Section */}
      {tickets.length > 0 && (
        <div className="flex flex-col gap-2">
          <span className="text-xs font-bold uppercase tracking-wider text-[#5B6B62]">
            My Support Tickets ({tickets.length})
          </span>
          <div className="flex flex-col gap-2">
            {tickets.map((t) => (
              <div
                key={t.id}
                onClick={() => navigate(`/support/ticket/${t.id}`)}
                className="p-3.5 bg-white rounded-2xl border border-[#E3E0D5] flex items-center justify-between cursor-pointer hover:border-[#14634A] shadow-xs"
              >
                <div>
                  <div className="flex items-center gap-1.5">
                    <h5 className="text-xs font-bold text-[#0B3D2E]">{t.ticket_no}</h5>
                    <StatusPill status={t.status} />
                  </div>
                  <span className="text-[11px] text-[#5B6B62] block mt-0.5 capitalize">
                    Category: {t.category} • {t.messages.length} message(s)
                  </span>
                </div>
                <span className="text-xs font-bold text-[#14634A]">View Chat &rarr;</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Voice-Enabled FAQs */}
      <div className="flex flex-col gap-2 pt-2">
        <span className="text-xs font-bold uppercase tracking-wider text-[#5B6B62]">
          Frequently Asked Questions (Voice Enabled)
        </span>

        <div className="flex flex-col gap-2">
          {faqs.map((f) => {
            const isOpen = expandedFaq === f.id;
            return (
              <div
                key={f.id}
                className="p-3.5 bg-white rounded-2xl border border-[#E3E0D5] flex flex-col gap-2"
              >
                <div
                  onClick={() => setExpandedFaq(isOpen ? null : f.id)}
                  className="flex items-center justify-between cursor-pointer"
                >
                  <span className="text-xs font-bold text-[#0B3D2E] pr-2">
                    {f.question}
                  </span>
                  <div className="flex items-center gap-1 shrink-0">
                    <VoiceButton text={`${f.question}. Answer: ${f.answer}`} size={16} />
                    {isOpen ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                  </div>
                </div>

                {isOpen && (
                  <p className="text-xs text-[#14201A] font-medium leading-relaxed pt-2 border-t border-[#E3E0D5]">
                    {f.answer}
                  </p>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* New Ticket Modal */}
      {showNewTicket && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-xs flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-3xl p-6 max-w-sm w-full border border-[#E3E0D5] shadow-2xl flex flex-col gap-4">
            <h3 className="text-base font-bold text-[#0B3D2E]">Create Support Request</h3>

            <div className="flex flex-col gap-1">
              <label className="text-xs font-semibold text-[#5B6B62]">Problem Category</label>
              <select
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                className="p-2.5 rounded-xl border border-[#E3E0D5] text-xs font-semibold"
              >
                <option value="payment">Payment & Bank Transfer</option>
                <option value="dispute">Weight or Price Discrepancy</option>
                <option value="pickup">Pickup Agent Delay</option>
                <option value="safety">Hazardous Scrap Guidance</option>
                <option value="app_help">Application / Language Help</option>
                <option value="other">Other Inquiry</option>
              </select>
            </div>

            <div className="flex flex-col gap-1">
              <label className="text-xs font-semibold text-[#5B6B62]">Your Message or Voice Note</label>
              <textarea
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                placeholder="Type your question or record voice note below..."
                className="p-3 rounded-xl border border-[#E3E0D5] text-xs font-medium h-24 focus:outline-none"
              />
            </div>

            {/* Voice Note Button */}
            <div className="flex items-center justify-between p-2.5 rounded-xl bg-[#F7F5EF] border border-[#E3E0D5]">
              <div className="flex items-center gap-2">
                <button
                  type="button"
                  onClick={handleToggleRecord}
                  className={`p-2 rounded-full cursor-pointer transition-colors ${
                    isRecording ? 'bg-[#D64545] text-white animate-pulse' : 'bg-[#14634A] text-white'
                  }`}
                >
                  <Mic size={16} />
                </button>
                <span className="text-xs text-[#14201A] font-semibold">
                  {isRecording ? 'Recording (say anything)...' : (voiceRecorded ? 'Voice Note Attached (18s)' : 'Record Voice Note (Up to 60s)')}
                </span>
              </div>
            </div>

            <div className="flex gap-2 pt-2">
              <button
                onClick={() => setShowNewTicket(false)}
                className="flex-1 py-3 rounded-xl bg-[#F7F5EF] text-[#5B6B62] text-xs font-bold cursor-pointer"
              >
                Cancel
              </button>
              <button
                onClick={handleCreateTicket}
                disabled={submitting || !message}
                className="flex-1 py-3 rounded-xl bg-[#14634A] text-white text-xs font-bold cursor-pointer disabled:opacity-50"
              >
                Submit Ticket
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
