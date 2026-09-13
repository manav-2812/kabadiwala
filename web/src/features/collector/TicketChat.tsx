import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { apiRequest } from '../../lib/api';
import { StatusPill } from '../../design/components/StatusPill';
import { formatDate } from '../../lib/format';
import { ArrowLeft, Send, Mic, Play, Volume2 } from 'lucide-react';
import { VoiceButton } from '../../design/components/VoiceButton';

export const TicketChat: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [ticket, setTicket] = useState<any>(null);
  const [inputMsg, setInputMsg] = useState('');
  const [sending, setSending] = useState(false);
  const navigate = useNavigate();

  const fetchTicket = () => {
    if (!id) return;
    apiRequest('/api/support/tickets')
      .then((tickets) => {
        const found = tickets.find((t: any) => t.id === id);
        if (found) setTicket(found);
      })
      .catch(() => {});
  };

  useEffect(() => {
    fetchTicket();
    const interval = setInterval(fetchTicket, 4000);
    return () => clearInterval(interval);
  }, [id]);

  const handleSend = async () => {
    if (!inputMsg.trim() || !id) return;
    setSending(true);
    try {
      await apiRequest(`/api/support/tickets/${id}/messages`, {
        method: 'POST',
        body: JSON.stringify({ body: inputMsg })
      });
      setInputMsg('');
      fetchTicket();
    } finally {
      setSending(false);
    }
  };

  if (!ticket) {
    return <div className="p-6 text-center text-xs text-[#5B6B62]">Loading ticket thread...</div>;
  }

  return (
    <div className="flex flex-col h-[82vh]">
      {/* Thread Header */}
      <div className="flex items-center justify-between border-b border-[#E3E0D5] pb-2">
        <div className="flex items-center gap-2">
          <button onClick={() => navigate('/support')} className="p-1 text-[#5B6B62] cursor-pointer">
            <ArrowLeft size={20} />
          </button>
          <div>
            <h3 className="text-sm font-bold text-[#0B3D2E]">{ticket.ticket_no}</h3>
            <span className="text-[10px] text-[#5B6B62] capitalize">Category: {ticket.category}</span>
          </div>
        </div>
        <StatusPill status={ticket.status} />
      </div>

      {/* Messages Scroll Area */}
      <div className="flex-1 overflow-y-auto py-4 flex flex-col gap-3">
        {ticket.messages.map((m: any) => {
          const isUser = m.sender_type === 'user';
          return (
            <div
              key={m.id}
              className={`flex flex-col max-w-[80%] ${
                isUser ? 'self-end items-end' : 'self-start items-start'
              }`}
            >
              <div
                className={`p-3 rounded-2xl text-xs leading-relaxed ${
                  isUser
                    ? 'bg-[#14634A] text-white rounded-br-xs'
                    : 'bg-white border border-[#E3E0D5] text-[#14201A] rounded-bl-xs shadow-xs'
                }`}
              >
                <div className="flex items-center justify-between gap-2 mb-1">
                  <span className={`text-[10px] font-bold ${isUser ? 'text-white/80' : 'text-[#0B3D2E]'}`}>
                    {m.sender_name || (isUser ? 'You' : 'Support Assistant')}
                  </span>
                  <VoiceButton
                    text={m.body}
                    size={12}
                    className={isUser ? 'text-white/80 hover:text-white p-0.5' : 'p-0.5'}
                  />
                </div>

                {m.attachment_type === 'voice' ? (
                  <div className="flex items-center gap-2 bg-black/10 p-2 rounded-xl mt-1">
                    <button className="w-6 h-6 rounded-full bg-white text-[#14634A] flex items-center justify-center">
                      <Play size={10} className="ml-0.5" />
                    </button>
                    <span className="text-[11px] font-semibold">Voice Note ({m.duration_s || 18}s)</span>
                  </div>
                ) : (
                  <p>{m.body}</p>
                )}
              </div>
              <span className="text-[10px] text-[#5B6B62] mt-0.5 px-1">
                {formatDate(m.created_at)}
              </span>
            </div>
          );
        })}
      </div>

      {/* Input Bar */}
      <div className="pt-2 border-t border-[#E3E0D5] flex items-center gap-2">
        <input
          type="text"
          value={inputMsg}
          onChange={(e) => setInputMsg(e.target.value)}
          placeholder="Reply to support..."
          onKeyDown={(e) => e.key === 'Enter' && handleSend()}
          className="flex-1 py-2.5 px-4 rounded-xl border border-[#E3E0D5] text-xs bg-white focus:outline-none focus:border-[#14634A]"
        />
        <button
          onClick={handleSend}
          disabled={sending || !inputMsg.trim()}
          className="p-2.5 rounded-xl bg-[#14634A] text-white hover:bg-[#0B3D2E] disabled:opacity-40 cursor-pointer touch-target flex items-center justify-center"
        >
          <Send size={16} />
        </button>
      </div>
    </div>
  );
};
