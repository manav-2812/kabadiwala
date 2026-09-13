import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../auth/authStore';
import { VoiceButton } from '../../design/components/VoiceButton';
import { StatusPill } from '../../design/components/StatusPill';
import { apiRequest } from '../../lib/api';
import { formatINR } from '../../lib/format';
import { useTranslation } from 'react-i18next';
import { speakMaterialRate } from '../../lib/spokenPriceBoard';
import {
  ShieldAlert, TrendingUp, HelpCircle, Shield,
  ArrowRight, Sparkles, MapPin, AlertCircle, Plus,
  Layers, Wallet, CheckCircle2, Award, Phone,
  Coins, Volume2, ArrowUpRight, ArrowDownRight, Compass,
  Scale
} from 'lucide-react';

export const Home: React.FC = () => {
  const { user } = useAuthStore();
  const { t, i18n } = useTranslation();
  const navigate = useNavigate();

  const [wallet, setWallet] = useState<any>(null);
  const [activeLot, setActiveLot] = useState<any>(null);
  const [topPrices, setTopPrices] = useState<any[]>([]);
  const [dues, setDues] = useState<any[]>([]);

  useEffect(() => {
    apiRequest('/api/wallet')
      .then(setWallet)
      .catch(() => {});

    apiRequest('/api/wallet/dues')
      .then((d) => setDues(d || []))
      .catch(() => {});

    apiRequest('/api/lots?collector_only=true')
      .then((lots) => {
        if (lots && lots.length > 0) {
          const ongoing = lots.find(
            (l: any) => l.status !== 'completed' && l.status !== 'cancelled' && l.status !== 'draft'
          );
          setActiveLot(ongoing || lots[0]);
        }
      })
      .catch(() => {});

    apiRequest('/api/prices/summary')
      .then((data) => {
        if (data) setTopPrices(data.slice(0, 4));
      })
      .catch(() => {});
  }, []);

  const userLang = user?.language || 'mr';
  const displayNameLocal = user?.display_name_local;
  const showLocalName = (i18n.language === userLang || (i18n.language !== 'en' && Boolean(displayNameLocal))) && displayNameLocal;
  let effectiveName = showLocalName ? displayNameLocal : (user?.name || 'Ramesh Kumar');
  if (effectiveName.startsWith('Collector')) {
    const num = effectiveName.replace('Collector', '').trim();
    const colRole = t('role_collector');
    effectiveName = num ? `${colRole} ${num}` : colRole;
  }
  const greetingPrefix = i18n.language === 'mr' ? 'नमस्कार' : i18n.language === 'pa' ? 'ਸਤਿ ਸ੍ਰੀ ਅਕਾਲ' : i18n.language === 'hi' ? 'नमस्ते' : 'Namaste';
  const greetingText = i18n.language === 'mr'
    ? `${greetingPrefix} ${effectiveName}, कबाडीवाला कनेक्ट मध्ये आपले स्वागत आहे.`
    : i18n.language === 'pa'
    ? `${greetingPrefix} ${effectiveName}, ਕਬਾੜੀਵਾਲਾ ਕਨੈਕਟ ਵਿੱਚ ਜੀ ਆਇਆਂ ਨੂੰ।`
    : i18n.language === 'hi'
    ? `${greetingPrefix} ${effectiveName}, कबाड़ीवाला कनेक्ट में आपका स्वागत है।`
    : `Namaste ${effectiveName}, welcome to Kabadiwala Connect.`;
  const city = user?.profile?.city || 'Delhi NCR';
  const areaName = user?.profile?.operating_area_name;
  const areaDisplay = areaName ? `${areaName}, ${city}` : `${city} ${t('hub_center')}`;

  const getMatName = (p: any) => {
    if (i18n.language === 'mr') return t(`categories.${p.material_code}`, p.name_mr || p.name_en);
    if (i18n.language === 'hi') return t(`categories.${p.material_code}`, p.name_hi || p.name_en);
    if (i18n.language === 'pa') return t(`categories.${p.material_code}`, p.name_pa || p.name_en);
    return p.name_en || t(`categories.${p.material_code}`, '');
  };

  const handleSpeak = (e: React.MouseEvent, p: any) => {
    e.stopPropagation();
    const currentRate = Math.round(p.current_price_paise_per_kg / 100);
    speakMaterialRate(p.material_code, getMatName(p), currentRate, i18n.language);
  };

  const pendingDuesTotal = wallet?.pending_dues_paise || dues.reduce((acc, d) => acc + (d.balance_paise || 0), 0);
  const cashInHand = wallet?.wallet_balance_paise || 245000;
  const formalPremium = wallet?.formal_premium_paise || 42000;
  const lotsCompleted = wallet?.lots_completed || 47;

  return (
    <div className="flex flex-col gap-6 w-full">
      {/* 1. HERO EXECUTIVE COMMAND BANNER — Full desktop span */}
      <section className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-[#0B3D2E] via-[#0F4C3A] to-[#14634A] text-white p-6 sm:p-8 shadow-lg border border-white/10">
        {/* Subtle Decorative Background Contours */}
        <div className="absolute top-0 right-0 -mt-8 -mr-8 w-64 h-64 rounded-full bg-white/5 blur-2xl pointer-events-none" />
        <div className="absolute bottom-0 left-1/3 -mb-12 w-80 h-80 rounded-full bg-[#2E9E5B]/10 blur-3xl pointer-events-none" />

        <div className="relative z-10 flex flex-col gap-6">
          {/* Top Row: Collector Profile, Status Pill, Quick Actions */}
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div className="flex items-start sm:items-center gap-3.5">
              <div className="w-13 h-13 rounded-2xl bg-white/15 backdrop-blur-md flex items-center justify-center text-white text-xl font-black shadow-inner border border-white/20 shrink-0">
                {effectiveName.charAt(0)}
              </div>
              <div>
                <div className="flex items-center gap-2 flex-wrap">
                  <h2 className="text-xl sm:text-2xl font-black tracking-tight text-white">
                    {greetingPrefix}, {effectiveName}
                  </h2>
                  {showLocalName && user?.name && (
                    <span className="text-xs text-white/60 font-medium">({user.name})</span>
                  )}
                  <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-[#2E9E5B]/30 border border-[#2E9E5B]/50 text-[11px] font-bold text-[#A8F0C6]">
                    <CheckCircle2 size={12} />
                    {t('badge_cpcb_certified')}
                  </span>
                </div>
                <div className="flex items-center gap-2 text-xs text-white/75 mt-0.5">
                  <span className="flex items-center gap-1">
                    <MapPin size={12} className="text-[#E9A310]" />
                    {areaDisplay}
                  </span>
                  <span>•</span>
                  <span>PS SIH26229 • {t('ministry_of_mines')}</span>
                  <div className="ml-1">
                    <VoiceButton text={greetingText} size={15} />
                  </div>
                </div>
              </div>
            </div>

            {/* Direct Quick Action CTAs */}
            <div className="flex items-center gap-2.5 self-start md:self-auto">
              <button
                onClick={() => navigate('/add-scrap')}
                className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-[#E9A310] hover:bg-[#d6930a] active:scale-95 text-black font-extrabold text-xs shadow-md cursor-pointer transition-all touch-target"
              >
                <Plus size={16} className="stroke-[3]" />
                <span>{t('btn_add_scrap')}</span>
              </button>
              <button
                onClick={() => navigate('/prices')}
                className="flex items-center gap-1.5 px-3.5 py-2.5 rounded-xl bg-white/10 hover:bg-white/20 text-white font-bold text-xs border border-white/20 transition-all cursor-pointer touch-target"
              >
                <TrendingUp size={15} />
                <span>{t('btn_price_board')}</span>
              </button>
            </div>
          </div>

          {/* Bottom Row: 4 High-Impact KPI Stat Cards */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 pt-2">
            {/* KPI 1: Cash In Hand */}
            <div
              onClick={() => navigate('/wallet')}
              className="p-4 rounded-2xl bg-white/10 hover:bg-white/15 backdrop-blur-md border border-white/15 transition-all cursor-pointer flex flex-col justify-between shadow-xs"
            >
              <div className="flex items-center justify-between text-xs text-white/70 font-semibold mb-1">
                <span>{t('today_earnings')}</span>
                <Coins size={16} className="text-[#E9A310]" />
              </div>
              <span className="text-2xl sm:text-3xl font-black text-white tabular-nums">
                {formatINR(cashInHand)}
              </span>
              <span className="text-[11px] text-[#A8F0C6] font-bold mt-1 flex items-center gap-1">
                <CheckCircle2 size={11} />
                {t('cash_first_handover')}
              </span>
            </div>

            {/* KPI 2: Formal Premium Uplift */}
            <div
              onClick={() => navigate('/wallet')}
              className="p-4 rounded-2xl bg-white/10 hover:bg-white/15 backdrop-blur-md border border-white/15 transition-all cursor-pointer flex flex-col justify-between shadow-xs"
            >
              <div className="flex items-center justify-between text-xs text-white/70 font-semibold mb-1">
                <span>{t('formal_premium')}</span>
                <Award size={16} className="text-[#A8F0C6]" />
              </div>
              <span className="text-2xl sm:text-3xl font-black text-[#A8F0C6] tabular-nums">
                +{formatINR(formalPremium)}
              </span>
              <span className="text-[11px] text-white/80 font-medium mt-1">
                {t('formal_premium_sub')}
              </span>
            </div>

            {/* KPI 3: Lots Completed */}
            <div
              onClick={() => navigate('/lots')}
              className="p-4 rounded-2xl bg-white/10 hover:bg-white/15 backdrop-blur-md border border-white/15 transition-all cursor-pointer flex flex-col justify-between shadow-xs"
            >
              <div className="flex items-center justify-between text-xs text-white/70 font-semibold mb-1">
                <span>{t('lots_processed')}</span>
                <Layers size={16} className="text-[#E9A310]" />
              </div>
              <span className="text-2xl sm:text-3xl font-black text-white tabular-nums">
                {lotsCompleted} {t('lots_count_unit')}
              </span>
              <span className="text-[11px] text-white/80 font-medium mt-1">
                {t('cpcb_form6_certified')}
              </span>
            </div>

            {/* KPI 4: Critical Minerals Contributed */}
            <div
              onClick={() => navigate('/admin')}
              className="p-4 rounded-2xl bg-white/10 hover:bg-white/15 backdrop-blur-md border border-white/15 transition-all cursor-pointer flex flex-col justify-between shadow-xs"
            >
              <div className="flex items-center justify-between text-xs text-white/70 font-semibold mb-1">
                <span>{t('strategic_recovery')}</span>
                <Sparkles size={16} className="text-[#A8F0C6]" />
              </div>
              <span className="text-2xl sm:text-3xl font-black text-white tabular-nums">
                142.8 kg
              </span>
              <span className="text-[11px] text-[#A8F0C6] font-bold mt-1">
                {t('strategic_recovery_sub')}
              </span>
            </div>
          </div>
        </div>
      </section>

      {/* 2. MAIN RESPONSIVE GRID: 8 Cols Main Content + 4 Cols Strategic Sidebar */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* LEFT / MAIN COLUMN (8 Columns on desktop) */}
        <div className="lg:col-span-8 flex flex-col gap-5">
          {/* Prominent Pending Buyer Dues Banner (When dues exist) */}
          {pendingDuesTotal > 0 && (
            <div
              onClick={() => navigate('/wallet')}
              className="p-5 rounded-3xl bg-gradient-to-r from-[#FFF9E6] to-[#FFF3CD] border-2 border-[#E9A310] cursor-pointer shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-4 hover:border-[#cf8f09] transition-all"
            >
              <div className="flex items-start sm:items-center gap-3.5">
                <div className="w-12 h-12 rounded-2xl bg-[#E9A310]/20 flex items-center justify-center text-[#946200] shrink-0 border border-[#E9A310]/30">
                  <AlertCircle size={26} />
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <h3 className="text-base font-extrabold text-[#0B3D2E]">
                      {t('pending_dues')}
                    </h3>
                    <span className="px-2.5 py-0.5 rounded-full bg-[#E9A310] text-black text-[11px] font-black uppercase shadow-2xs">
                      {t('dues_pending_count', { count: dues.length || 1 })}
                    </span>
                  </div>
                  <p className="text-xs text-[#5B6B62] mt-0.5">
                    {t('pending_dues_desc')}
                  </p>
                </div>
              </div>

              <div className="flex items-center sm:flex-col items-end justify-between shrink-0">
                <span className="text-xl sm:text-2xl font-black text-[#D64545] tabular-nums block">
                  {formatINR(pendingDuesTotal)}
                </span>
                <div className="flex items-center gap-1.5 text-xs font-bold text-[#14634A] hover:underline">
                  <span>{t('open_earnings_ledger')}</span>
                  <ArrowRight size={14} />
                </div>
              </div>
            </div>
          )}

          {/* Active Lot Live Status Card */}
          {activeLot && (
            <div className="p-5 rounded-3xl bg-white border border-[#E3E0D5] shadow-xs flex flex-col gap-4">
              <div className="flex items-center justify-between border-b border-[#F0EFE9] pb-3">
                <div className="flex items-center gap-2.5">
                  <div className="p-2 rounded-xl bg-[#E4F4EA] text-[#0B3D2E]">
                    <Layers size={18} />
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-bold text-[#5B6B62]">{t('active_transaction')}</span>
                      <span className="text-xs font-black text-[#0B3D2E]">{activeLot.lot_code}</span>
                    </div>
                    <span className="text-sm font-bold text-[#14201A]">
                      {activeLot.status === 'in_transit'
                        ? t('status_en_route')
                        : activeLot.status === 'awaiting_confirm'
                        ? t('status_weighin_ready')
                        : t('status_quotes_received')}
                    </span>
                  </div>
                </div>
                <StatusPill status={activeLot.status} />
              </div>

              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pt-1">
                <div className="flex items-center gap-4 text-xs text-[#5B6B62]">
                  <div>
                    <span className="block text-[10px] uppercase font-bold text-[#8D9B93]">{t('estimated_value')}</span>
                    <span className="text-base font-extrabold text-[#0B3D2E] tabular-nums">
                      {formatINR(activeLot.est_total_min_paise)} - {formatINR(activeLot.est_total_max_paise)}
                    </span>
                  </div>
                  <div className="h-7 w-px bg-[#E3E0D5]" />
                  <div>
                    <span className="block text-[10px] uppercase font-bold text-[#8D9B93]">{t('estimated_weight')}</span>
                    <span className="text-sm font-bold text-[#14201A]">
                      {(activeLot.est_total_weight_g / 1000).toFixed(1)} kg
                    </span>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <button
                    onClick={() => navigate(`/lots/${activeLot.id}`)}
                    className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-[#0B3D2E] hover:bg-[#14634A] text-white text-xs font-bold shadow-xs cursor-pointer transition-all"
                  >
                    <span>{t('btn_view_details')}</span>
                    <ArrowRight size={14} />
                  </button>
                  {activeLot.transaction && (
                    <button
                      onClick={() => navigate(`/tracking/${activeLot.transaction.id}`)}
                      className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-[#E4F4EA] hover:bg-[#d5eee0] text-[#0B3D2E] text-xs font-bold transition-all cursor-pointer"
                    >
                      <Compass size={14} />
                      <span>{t('btn_live_route')}</span>
                    </button>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Today's Market Highlights — 4 Top Movers with Spoken Voice Button */}
          <div className="p-5 rounded-3xl bg-white border border-[#E3E0D5] shadow-xs flex flex-col gap-4">
            <div className="flex items-center justify-between border-b border-[#F0EFE9] pb-3">
              <div className="flex items-center gap-2">
                <div className="p-2 rounded-xl bg-[#FCF3D9] text-[#E9A310]">
                  <TrendingUp size={18} />
                </div>
                <div>
                  <h3 className="text-base font-black text-[#0B3D2E]">
                    {t('market_rates_title')}
                  </h3>
                  <span className="text-xs text-[#5B6B62]">
                    {t('market_rates_subtitle', { city })}
                  </span>
                </div>
              </div>
              <button
                onClick={() => navigate('/prices')}
                className="text-xs font-bold text-[#14634A] hover:underline flex items-center gap-1 cursor-pointer"
              >
                <span>{t('btn_complete_price_board')}</span>
                <ArrowRight size={13} />
              </button>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
              {topPrices.map((p) => {
                const isPos = p.change_pct_14d >= 0;
                return (
                  <div
                    key={p.material_code}
                    onClick={() => navigate('/prices')}
                    className="p-3.5 rounded-2xl bg-[#F8FAF9] hover:bg-white border border-[#E3E0D5] hover:border-[#14634A] hover:shadow-xs transition-all cursor-pointer flex flex-col justify-between gap-3 group"
                  >
                    <div>
                      <div className="flex items-start justify-between">
                        <span className="text-xs font-bold text-[#14201A] group-hover:text-[#0B3D2E] line-clamp-1">
                          {getMatName(p)}
                        </span>
                        <button
                          onClick={(e) => handleSpeak(e, p)}
                          className="p-1 rounded-lg text-[#5B6B62] hover:text-[#0B3D2E] hover:bg-[#E4F4EA] transition-colors"
                          title="Listen rate in your language"
                        >
                          <Volume2 size={15} />
                        </button>
                      </div>
                      <div className="mt-1 flex items-baseline gap-1">
                        <span className="text-lg font-black text-[#0B3D2E] tabular-nums">
                          {formatINR(p.current_price_paise_per_kg)}
                        </span>
                        <span className="text-[11px] text-[#5B6B62] font-semibold">{t('unit_per_kg')}</span>
                      </div>
                    </div>

                    <div className="flex items-center justify-between text-[11px] font-bold pt-1 border-t border-[#E3E0D5]/50">
                      <span className="text-[10px] text-[#8D9B93]">{t('shift_14d')}</span>
                      <span className={`flex items-center gap-0.5 ${isPos ? 'text-[#2E9E5B]' : 'text-[#D64545]'}`}>
                        {isPos ? <ArrowUpRight size={13} /> : <ArrowDownRight size={13} />}
                        {isPos ? `+${p.change_pct_14d}%` : `${p.change_pct_14d}%`}
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* JNARDDC Strategic Minerals Impact Widget */}
          <div className="p-5 rounded-3xl bg-white border border-[#E3E0D5] shadow-xs flex flex-col gap-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="p-2 rounded-xl bg-[#E4F4EA] text-[#0B3D2E]">
                  <Scale size={18} />
                </div>
                <div>
                  <h3 className="text-sm font-black text-[#0B3D2E]">
                    {t('minerals_contribution_title')}
                  </h3>
                  <span className="text-xs text-[#5B6B62]">
                    {t('minerals_contribution_sub')}
                  </span>
                </div>
              </div>
              <span className="text-xs font-bold text-[#14634A] bg-[#E4F4EA] px-2.5 py-1 rounded-full border border-[#2E9E5B]/20">
                {t('badge_science_validated')}
              </span>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-1">
              <div className="p-3 rounded-2xl bg-[#FAF8F5] border border-[#E3E0D5] flex flex-col">
                <span className="text-[10px] uppercase font-bold text-[#8D9B93]">{t('mineral_copper')}</span>
                <span className="text-lg font-black text-[#0B3D2E] tabular-nums mt-0.5">92.4 kg</span>
                <span className="text-[10px] text-[#2E9E5B] font-semibold mt-1">{t('mineral_copper_sub')}</span>
              </div>
              <div className="p-3 rounded-2xl bg-[#FAF8F5] border border-[#E3E0D5] flex flex-col">
                <span className="text-[10px] uppercase font-bold text-[#8D9B93]">{t('mineral_lithium')}</span>
                <span className="text-lg font-black text-[#0B3D2E] tabular-nums mt-0.5">18.6 kg</span>
                <span className="text-[10px] text-[#2E9E5B] font-semibold mt-1">{t('mineral_lithium_sub')}</span>
              </div>
              <div className="p-3 rounded-2xl bg-[#FAF8F5] border border-[#E3E0D5] flex flex-col">
                <span className="text-[10px] uppercase font-bold text-[#8D9B93]">{t('mineral_neodymium')}</span>
                <span className="text-lg font-black text-[#0B3D2E] tabular-nums mt-0.5">8.1 kg</span>
                <span className="text-[10px] text-[#2E9E5B] font-semibold mt-1">{t('mineral_neodymium_sub')}</span>
              </div>
              <div className="p-3 rounded-2xl bg-[#FAF8F5] border border-[#E3E0D5] flex flex-col">
                <span className="text-[10px] uppercase font-bold text-[#8D9B93]">{t('mineral_gold_silver')}</span>
                <span className="text-lg font-black text-[#0B3D2E] tabular-nums mt-0.5">42.5 g</span>
                <span className="text-[10px] text-[#2E9E5B] font-semibold mt-1">{t('mineral_gold_silver_sub')}</span>
              </div>
            </div>
          </div>
        </div>

        {/* RIGHT / SIDEBAR COLUMN (4 Columns on desktop) */}
        <div className="lg:col-span-4 flex flex-col gap-5">
          {/* Daily Safe Handling & Hazard Advisory Card */}
          <div
            onClick={() => navigate('/safety')}
            className="p-5 rounded-3xl bg-white border border-[#E3E0D5] hover:border-[#D64545] cursor-pointer shadow-xs transition-all flex flex-col gap-3 group"
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-xs font-black uppercase tracking-wider text-[#D64545]">
                <div className="p-1.5 rounded-lg bg-[#FBE7E7] text-[#D64545]">
                  <ShieldAlert size={16} />
                </div>
                <span>{t('safety_tip_title')}</span>
              </div>
              <VoiceButton
                text={t('safety_tip_voice')}
                size={16}
              />
            </div>

            <p className="text-xs text-[#14201A] font-medium leading-relaxed">
              {t('safety_tip_body')}
            </p>

            <div className="flex items-center justify-between text-xs font-bold text-[#D64545] pt-2 border-t border-[#F0EFE9]">
              <span>{t('view_hazard_protocols')}</span>
              <ArrowRight size={14} className="group-hover:translate-x-0.5 transition-transform" />
            </div>
          </div>

          {/* Quick Action Navigation Hubs */}
          <div className="grid grid-cols-2 gap-3">
            <button
              onClick={() => navigate('/support')}
              className="flex flex-col p-4 rounded-2xl bg-white border border-[#E3E0D5] hover:border-[#14634A] text-left cursor-pointer transition-all shadow-2xs group"
            >
              <div className="w-10 h-10 rounded-xl bg-[#E4F4EA] text-[#0B3D2E] flex items-center justify-center mb-2">
                <HelpCircle size={20} />
              </div>
              <span className="text-xs font-bold text-[#14201A] group-hover:text-[#0B3D2E]">
                {t('help_center')}
              </span>
              <span className="text-[10px] text-[#5B6B62] mt-0.5">
                {t('help_center_sub')}
              </span>
            </button>

            <button
              onClick={() => navigate('/safety')}
              className="flex flex-col p-4 rounded-2xl bg-white border border-[#E3E0D5] hover:border-[#14634A] text-left cursor-pointer transition-all shadow-2xs group"
            >
              <div className="w-10 h-10 rounded-xl bg-[#FCF3D9] text-[#E9A310] flex items-center justify-center mb-2">
                <Shield size={20} />
              </div>
              <span className="text-xs font-bold text-[#14201A] group-hover:text-[#0B3D2E]">
                {t('safety_hub_title')}
              </span>
              <span className="text-[10px] text-[#5B6B62] mt-0.5">
                {t('safety_hub_sub')}
              </span>
            </button>
          </div>

          {/* Statutory MSP Guarantee Compliance Card */}
          <div className="p-5 rounded-3xl bg-gradient-to-br from-[#FAF8F5] to-[#F3F0E6] border border-[#E3E0D5] shadow-xs flex flex-col gap-2.5">
            <div className="flex items-center gap-2">
              <span className="text-xs font-black text-[#0B3D2E] uppercase tracking-wider">
                {t('statutory_msp_title')}
              </span>
              <span className="text-[10px] px-2 py-0.5 rounded-full bg-[#E4F4EA] text-[#14634A] font-bold border border-[#2E9E5B]/20">
                {t('badge_cpcb_enforced')}
              </span>
            </div>
            <p className="text-xs text-[#5B6B62] leading-relaxed">
              {t('statutory_msp_desc')}
            </p>
            <div className="pt-2 border-t border-[#E3E0D5]/60 flex items-center justify-between text-[11px] font-bold text-[#0B3D2E]">
              <span>{t('rule_12a_title')}</span>
              <CheckCircle2 size={14} className="text-[#2E9E5B]" />
            </div>
          </div>

          {/* Dedicated Earnings Ledger Shortcut */}
          <div
            onClick={() => navigate('/wallet')}
            className="p-4 rounded-2xl bg-[#E4F4EA] border border-[#2E9E5B]/40 hover:bg-[#d5eee0] transition-all cursor-pointer flex items-center justify-between"
          >
            <div className="flex items-center gap-3">
              <div className="p-2.5 rounded-xl bg-[#0B3D2E] text-white">
                <Wallet size={18} />
              </div>
              <div>
                <h4 className="text-xs font-black text-[#0B3D2E] uppercase tracking-wider">
                  {t('earnings_ledger_title')}
                </h4>
                <span className="text-[11px] text-[#14634A] font-semibold">
                  {t('earnings_ledger_sub')}
                </span>
              </div>
            </div>
            <ArrowRight size={16} className="text-[#0B3D2E]" />
          </div>
        </div>
      </div>
    </div>
  );
};
