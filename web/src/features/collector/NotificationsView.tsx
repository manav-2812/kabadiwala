import React, { useEffect, useState } from 'react';
import { apiRequest } from '../../lib/api';
import { formatDate } from '../../lib/format';
import { VoiceButton } from '../../design/components/VoiceButton';
import { Bell, CheckCheck, MessageSquare, ArrowLeft } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';

export const NotificationsView: React.FC = () => {
  const [notifications, setNotifications] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();
  const { t } = useTranslation();

  const fetchNotifications = () => {
    apiRequest('/api/notifications')
      .then((data) => {
        setNotifications(data);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  };

  useEffect(() => {
    fetchNotifications();
  }, []);

  const handleMarkAllRead = async () => {
    await apiRequest('/api/notifications/read-all', { method: 'POST' });
    fetchNotifications();
  };

  return (
    <div className="flex flex-col gap-4 pb-6">
      <div className="flex items-center justify-between border-b border-[#E3E0D5] pb-2">
        <div className="flex items-center gap-2">
          <button onClick={() => navigate(-1)} className="p-1 text-[#5B6B62] cursor-pointer">
            <ArrowLeft size={20} />
          </button>
          <h2 className="text-lg font-black text-[#0B3D2E]">
            {t('notifications')}
          </h2>
        </div>

        <button
          onClick={handleMarkAllRead}
          className="flex items-center gap-1 text-xs font-bold text-[#14634A] hover:underline cursor-pointer"
        >
          <CheckCheck size={14} />
          <span>Mark all read</span>
        </button>
      </div>

      {loading ? (
        <div className="p-6 text-center text-xs text-[#5B6B62]">Loading messages...</div>
      ) : notifications.length === 0 ? (
        <div className="p-8 text-center text-xs text-[#5B6B62] bg-white rounded-2xl border border-[#E3E0D5]">
          No new notifications.
        </div>
      ) : (
        <div className="flex flex-col gap-3">
          {notifications.map((n) => (
            <div
              key={n.id}
              className={`flex flex-col p-3.5 rounded-2xl border transition-all gap-2 ${
                n.read_at ? 'bg-white border-[#E3E0D5]' : 'bg-[#E4F4EA]/30 border-[#2E9E5B]/40'
              }`}
            >
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-2">
                  <div className="p-1.5 rounded-lg bg-[#E4F4EA] text-[#0B3D2E]">
                    <Bell size={14} />
                  </div>
                  <h4 className="text-xs font-bold text-[#0B3D2E]">{n.title}</h4>
                </div>

                <div className="flex items-center gap-1">
                  <span className="text-[10px] text-[#5B6B62]">{formatDate(n.created_at)}</span>
                  <VoiceButton text={`${n.title}. ${n.body}`} size={14} />
                </div>
              </div>

              <p className="text-xs text-[#14201A] font-medium leading-relaxed pl-7">
                {n.body}
              </p>

              {/* SMS Preview Panel (Section 12A(H)) */}
              <div className="ml-7 p-2 rounded-xl bg-[#F7F5EF] border border-[#E3E0D5] flex items-center gap-2 text-[11px] text-[#5B6B62]">
                <MessageSquare size={13} className="shrink-0 text-[#14634A]" />
                <span className="truncate"><b>SMS Preview:</b> {n.sms_preview}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
