import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { apiRequest } from '../../lib/api';
import { BigButton } from '../../design/components/BigButton';
import { Phone, CheckCircle, Navigation, ShieldCheck, Clock, ExternalLink, MapPin } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import { VoiceButton } from '../../design/components/VoiceButton';

export const TrackingView: React.FC = () => {
  const { id } = useParams<{ id: string }>(); // transaction_id
  const [tracking, setTracking] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();
  const { t } = useTranslation();

  const fetchTracking = () => {
    if (!id) return;
    apiRequest(`/api/transactions/${id}/tracking`)
      .then((data) => {
        setTracking(data);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  };

  useEffect(() => {
    fetchTracking();
    const interval = setInterval(fetchTracking, 3000); // Poll tracking updates
    return () => clearInterval(interval);
  }, [id]);

  const handleConfirmArrival = async () => {
    if (!id) return;
    try {
      await apiRequest(`/api/transactions/${id}/arrive`, { method: 'POST' });
      navigate(`/handover/${id}`);
    } catch {
      navigate(`/handover/${id}`);
    }
  };

  if (loading || !tracking) {
    return <div className="p-6 text-center text-xs text-[#5B6B62]">Loading live tracking...</div>;
  }

  return (
    <div className="flex flex-col gap-4 pb-6">
      <div className="flex items-center justify-between border-b border-[#E3E0D5] pb-2">
        <h2 className="text-lg font-black text-[#0B3D2E]">
          {t('tracking_title')}
        </h2>
        <VoiceButton text={`Agent ${tracking.agent_name} is arriving in ${tracking.eta_min} minutes.`} size={18} />
      </div>

      {/* Big ETA Countdown Banner */}
      <div className="p-4 rounded-3xl bg-[#0B3D2E] text-white flex items-center justify-between shadow-md">
        <div>
          <span className="text-xs font-bold text-white/70 uppercase tracking-wider block">
            {t('eta')}
          </span>
          <div className="flex items-baseline gap-1 mt-0.5">
            <span className="text-4xl font-extrabold tabular-nums tracking-tight">
              {tracking.eta_min}
            </span>
            <span className="text-sm font-semibold">{t('mins')}</span>
          </div>
        </div>
        <div className="text-right">
          <span className="text-xs text-[#E9A310] font-bold block">{t('live_telemetry')}</span>
          <span className="text-[11px] text-white/60">{t('speed_kmh', { speed: tracking.speed_kmh || 24 })}</span>
        </div>
      </div>

      {/* Lightweight Live Route Card (Zero-bundle map alternative) */}
      <div className="p-4 rounded-2xl bg-white border border-[#E3E0D5] shadow-xs space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-full bg-[#E4F4EA] flex items-center justify-center text-[#14634A]">
              <Navigation size={16} className="animate-pulse" />
            </div>
            <div>
              <span className="text-xs font-black text-[#0B3D2E] block">{t('en_route_doorstep')}</span>
              <span className="text-[11px] text-[#5B6B62]">{t('coarse_gps_label', { lat: Number(tracking.lat).toFixed(4), lng: Number(tracking.lng).toFixed(4) })}</span>
            </div>
          </div>
          <a
            href={`https://www.google.com/maps/search/?api=1&query=${tracking.lat},${tracking.lng}`}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1 text-xs font-bold text-[#14634A] bg-[#E4F4EA] hover:bg-[#d5edd9] px-3 py-1.5 rounded-xl transition-colors"
          >
            <ExternalLink size={12} />
            <span>{t('btn_open_maps')}</span>
          </a>
        </div>

        {/* Status progress tracker */}
        <div className="w-full bg-[#F7F5EF] h-2 rounded-full overflow-hidden">
          <div className="bg-[#2E9E5B] h-full rounded-full w-3/4 animate-pulse"></div>
        </div>
      </div>

      {/* Agent Card */}
      <div className="p-4 rounded-2xl bg-white border border-[#E3E0D5] flex items-center justify-between gap-3 shadow-xs">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 rounded-full bg-[#E4F4EA] flex items-center justify-center font-bold text-base text-[#0B3D2E]">
            {tracking.agent_name.charAt(0)}
          </div>
          <div>
            <h4 className="text-sm font-bold text-[#0B3D2E]">{tracking.agent_name}</h4>
            <span className="text-xs text-[#5B6B62] block">{tracking.agent_vehicle}</span>
            <span className="text-[10px] text-[#2E9E5B] font-semibold">{t('authorized_pickup_spec')}</span>
          </div>
        </div>

        <a
          href="#"
          onClick={(e) => { e.preventDefault(); }}
          title="Calling is disabled in demo"
          className="flex items-center gap-1.5 px-3 py-2 rounded-xl bg-[#E4F4EA] text-[#0B3D2E] text-xs font-bold opacity-75 cursor-not-allowed touch-target"
        >
          <Phone size={14} />
          <span>{t('btn_call')}</span>
        </a>
      </div>

      {/* Arrival Confirmation Action */}
      <div className="pt-2">
        <BigButton
          label={t('agent_here')}
          onClick={handleConfirmArrival}
          variant="primary"
          icon={<CheckCircle size={20} />}
        />
        <span className="text-center block text-[11px] text-[#5B6B62] mt-1.5">
          {t('tap_when_arrived')}
        </span>
      </div>
    </div>
  );
};
