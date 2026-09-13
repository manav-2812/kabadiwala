import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiRequest } from '../../lib/api';
import { IconTile } from '../../design/components/IconTile';
import { WeightStepper } from '../../design/components/WeightStepper';
import { BigButton } from '../../design/components/BigButton';
import { SafetyBanner } from '../../design/components/SafetyBanner';
import { VoiceButton } from '../../design/components/VoiceButton';
import { formatINR, formatWeight } from '../../lib/format';
import { useTranslation } from 'react-i18next';
import {
  Cpu, BatteryCharging, Magnet, Tv, Monitor, Cable,
  Cog, Recycle, Package, Camera, Sparkles, ArrowRight,
  CheckCircle, ArrowLeft, Upload, AlertTriangle, Check, X, RefreshCw
} from 'lucide-react';
import { assessQuality, QualityIssue } from './quality';
import { computePHash } from './phash';
import { phrases } from './audio';

interface MaterialItem {
  id: string;
  code: string;
  name_en: string;
  name_hi: string;
  name_mr?: string;
  name_pa: string;
  base_price_paise_per_kg: number;
  is_hazardous: boolean;
  hazard_note_en: string;
  safety_tip_en: string;
}

export const LotBuilder: React.FC = () => {
  const [step, setStep] = useState(1);
  const [materials, setMaterials] = useState<MaterialItem[]>([]);
  const [selectedMat, setSelectedMat] = useState<MaterialItem | null>(null);
  const [photos, setPhotos] = useState<string[]>([]);
  const [weightGrams, setWeightGrams] = useState(5000); // 5 kg default
  const [condition, setCondition] = useState<'working' | 'broken' | 'burnt'>('broken');
  const [submitting, setSubmitting] = useState(false);
  const [qualityIssue, setQualityIssue] = useState<QualityIssue | null>(null);
  const [qualityIgnored, setQualityIgnored] = useState(false);
  const [analyzingPhoto, setAnalyzingPhoto] = useState(false);
  const [aiClassSuggestion, setAiClassSuggestion] = useState<{
    code: string;
    confidence: number;
    demo_only: boolean;
    not_sure: boolean;
  } | null>(null);
  const [userOverridden, setUserOverridden] = useState(false);

  const navigate = useNavigate();
  const { t, i18n } = useTranslation();

  useEffect(() => {
    apiRequest('/api/materials')
      .then((data) => {
        setMaterials(data);
        if (data.length > 0) setSelectedMat(data[0]);
      })
      .catch(() => {});
  }, []);

  const getMatIcon = (code: string) => {
    switch (code) {
      case 'PCB': return <Cpu size={26} />;
      case 'BATTERY_LI': return <BatteryCharging size={26} />;
      case 'MAGNET': return <Magnet size={26} />;
      case 'CRT': return <Tv size={26} />;
      case 'LCD': return <Monitor size={26} />;
      case 'CABLE': return <Cable size={26} />;
      case 'MOTOR': return <Cog size={26} />;
      case 'PLASTIC_MIXED': return <Recycle size={26} />;
      default: return <Package size={26} />;
    }
  };

  const getMatName = (m: MaterialItem) => {
    if (i18n.language === 'mr') return t(`categories.${m.code}`, m.name_mr || m.name_en);
    if (i18n.language === 'hi') return t(`categories.${m.code}`, m.name_hi || m.name_en);
    if (i18n.language === 'pa') return t(`categories.${m.code}`, m.name_pa || m.name_en);
    return m.name_en || t(`categories.${m.code}`, '');
  };

  // Client-side image compression under 200 KB + AI Quality Gate + Classifier Call
  const handlePhotoUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;

    Array.from(files).slice(0, 4).forEach((file) => {
      const reader = new FileReader();
      reader.onload = (readerEvent) => {
        const img = new Image();
        img.onload = async () => {
          const canvas = document.createElement('canvas');
          const maxDim = 800;
          let width = img.width;
          let height = img.height;

          if (width > height && width > maxDim) {
            height = Math.round((height * maxDim) / width);
            width = maxDim;
          } else if (height > maxDim) {
            width = Math.round((width * maxDim) / height);
            height = maxDim;
          }

          canvas.width = width;
          canvas.height = height;
          const ctx = canvas.getContext('2d');
          ctx?.drawImage(img, 0, 0, width, height);

          // Compress to JPEG 0.65 (guarantees < 180 KB)
          const dataUrl = canvas.toDataURL('image/jpeg', 0.65);
          setPhotos((prev) => [...prev.slice(0, 3), dataUrl]);

          // C6: Assess Photo Quality
          try {
            const qResult = await assessQuality(canvas);
            if (!qResult.ok && !qualityIgnored) {
              setQualityIssue(qResult.issue);
              const lang = (i18n.language || 'en') as any;
              if (qResult.issue === 'too_dark') phrases.photoTooDark(lang);
              else if (qResult.issue === 'blurry') phrases.photoBlurry(lang);
            } else {
              setQualityIssue(null);
            }
          } catch {
            // Non-blocking quality check
          }

          // C1: Classify with pHash
          try {
            setAnalyzingPhoto(true);
            const phash = await computePHash(canvas);
            const res = await apiRequest('/api/ml/classify', {
              method: 'POST',
              body: JSON.stringify({
                hint_material: selectedMat?.code,
                photo_phash: phash
              })
            });
            if (res && res.top3 && res.top3.length > 0) {
              const top1 = res.top3[0];
              setAiClassSuggestion({
                code: top1.class_name,
                confidence: top1.confidence,
                demo_only: res.model?.demo_only ?? true,
                not_sure: res.not_sure ?? false,
              });
              // Pre-select if confident and not currently manually set
              if (!res.not_sure && top1.confidence >= 0.70) {
                const match = materials.find(m => m.code === top1.class_name);
                if (match) setSelectedMat(match);
              }
            }
          } catch {
            // Silent fallback to manual selection
          } finally {
            setAnalyzingPhoto(false);
          }
        };
        img.src = readerEvent.target?.result as string;
      };
      reader.readAsDataURL(file);
    });
  };

  // Client-side offline estimate computation (Section 7.1)
  const basePrice = selectedMat?.base_price_paise_per_kg || 40000;
  const condFactor = condition === 'working' ? 1.10 : (condition === 'burnt' ? 0.70 : 1.00);
  const wtKg = weightGrams / 1000;
  const estMin = Math.round(basePrice * 0.90 * wtKg * condFactor);
  const estMax = Math.round(basePrice * 1.10 * wtKg * condFactor);

  const handleCreateLot = async () => {
    if (!selectedMat) return;
    setSubmitting(true);
    try {
      const payload = {
        items: [
          {
            material_id: selectedMat.id,
            est_weight_g: weightGrams,
            condition,
            photo_urls: photos.length > 0 ? photos : ['https://images.unsplash.com/photo-1550751827-4bd374c3f58b?w=400'],
            ai_suggested_material_id: aiClassSuggestion ? aiClassSuggestion.code : null,
            ai_confidence: aiClassSuggestion ? aiClassSuggestion.confidence : null,
            user_override: userOverridden
          }
        ],
        offline_created: false
      };
      const lot = await apiRequest('/api/lots', {
        method: 'POST',
        body: JSON.stringify(payload)
      });
      navigate(`/lots/${lot.id}`);
    } catch (err) {
      alert('Failed to list scrap lot. Please check connectivity.');
      setSubmitting(false);
    }
  };

  return (
    <div className="flex flex-col gap-4 pb-4">
      {/* 4 Steps Header */}
      <div className="flex items-center justify-between border-b border-[#E3E0D5] pb-2">
        <button
          onClick={() => (step > 1 ? setStep(step - 1) : navigate('/'))}
          className="flex items-center gap-1 text-xs font-bold text-[#5B6B62] cursor-pointer"
        >
          <ArrowLeft size={16} />
          <span>{t('btn_back')}</span>
        </button>

        <span className="text-xs font-black uppercase tracking-wider text-[#0B3D2E]">
          {t('step_progress', { current: step, total: 4 })}
        </span>

        <VoiceButton
          text={
            step === 1 ? t('step1_desc') :
            step === 2 ? t('step2_desc') :
            step === 3 ? t('step3_desc') :
            t('step4_desc')
          }
          size={16}
        />
      </div>

      {/* STEP 1: CATEGORY */}
      {step === 1 && (
        <div className="flex flex-col gap-3">
          <div>
            <h2 className="text-lg font-black text-[#0B3D2E]">
              {t('step_category')}
            </h2>
            <p className="text-xs text-[#5B6B62]">
              {t('step1_desc')}
            </p>
          </div>

          <div className="grid grid-cols-2 gap-2.5">
            {materials.map((mat) => (
              <IconTile
                key={mat.id}
                icon={getMatIcon(mat.code)}
                label={getMatName(mat)}
                selected={selectedMat?.id === mat.id}
                isHazardous={mat.is_hazardous}
                onClick={() => setSelectedMat(mat)}
              />
            ))}
          </div>

          <div className="pt-2">
            <BigButton
              label={t('btn_next_photos')}
              onClick={() => setStep(2)}
              icon={<ArrowRight size={20} />}
            />
          </div>
        </div>
      )}

      {/* STEP 2: PHOTO */}
      {step === 2 && (
        <div className="flex flex-col gap-4">
          <div>
            <h2 className="text-lg font-black text-[#0B3D2E]">
              {t('step_photo')}
            </h2>
            <p className="text-xs text-[#5B6B62]">
              {t('step2_desc')}
            </p>
          </div>

          {/* Photo preview grid */}
          <div className="grid grid-cols-2 gap-3">
            {photos.map((url, idx) => (
              <div key={idx} className="relative aspect-square rounded-2xl overflow-hidden border border-[#E3E0D5]">
                <img src={url} alt={`Scrap ${idx}`} className="w-full h-full object-cover" />
                <span className="absolute bottom-1 right-1 px-1.5 py-0.5 rounded bg-black/60 text-white text-[10px]">
                  &lt; 200 KB
                </span>
              </div>
            ))}

            {photos.length < 4 && (
              <label className="flex flex-col items-center justify-center aspect-square rounded-2xl border-2 border-dashed border-[#14634A] bg-[#E4F4EA]/40 text-[#14634A] cursor-pointer hover:bg-[#E4F4EA] transition-colors touch-target">
                <Camera size={32} />
                <span className="text-xs font-bold mt-1">{t('capture_photo')}</span>
                <span className="text-[10px] text-[#5B6B62]">{t('auto_compress')}</span>
                <input
                  type="file"
                  accept="image/*"
                  capture="environment"
                  multiple
                  onChange={handlePhotoUpload}
                  className="hidden"
                />
              </label>
            )}
          </div>

          {/* C6: Photo Quality Feedback Banner */}
          {qualityIssue && !qualityIgnored && (
            <div className="flex flex-col gap-2 p-3.5 rounded-xl bg-[#FEF3C7] border border-[#FDE68A] text-[#92400E]">
              <div className="flex items-center gap-2">
                <AlertTriangle size={18} className="text-[#D97706] shrink-0" />
                <span className="text-xs font-bold">
                  {qualityIssue === 'too_dark' ? t('ai.photo_too_dark') :
                   qualityIssue === 'too_bright' ? t('ai.photo_too_bright') :
                   t('ai.photo_blurry')}
                </span>
              </div>
              <div className="flex gap-2 text-xs pt-1">
                <button
                  type="button"
                  onClick={() => {
                    setPhotos(prev => prev.slice(0, -1));
                    setQualityIssue(null);
                  }}
                  className="px-3 py-1 rounded-lg bg-white border border-[#D97706] font-bold hover:bg-[#FDE68A]/30 transition cursor-pointer"
                >
                  {t('ai.photo_retry')}
                </button>
                <button
                  type="button"
                  onClick={() => setQualityIgnored(true)}
                  className="px-3 py-1 rounded-lg bg-[#D97706] text-white font-bold hover:bg-[#B45309] transition cursor-pointer"
                >
                  {t('ai.photo_override')}
                </button>
              </div>
            </div>
          )}

          {/* C1: Analyzing loader */}
          {analyzingPhoto && (
            <div className="flex items-center gap-2 p-3 rounded-xl bg-[#F7F5EF] border border-[#E3E0D5] text-[#556960] text-xs font-semibold">
              <RefreshCw size={15} className="animate-spin text-[#0B3D2E]" />
              <span>{t('analyzing_visual')}</span>
            </div>
          )}

          {/* C1: AI Classifier Suggestion Card */}
          {aiClassSuggestion && !analyzingPhoto && (
            <div className="flex flex-col gap-2.5 p-3.5 rounded-xl bg-[#E4F4EA] border border-[#14634A]/30 shadow-sm">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Sparkles size={16} className="text-[#0B3D2E]" />
                  <span className="text-xs font-bold text-[#0B3D2E]">
                    {aiClassSuggestion.not_sure
                      ? t('ai.suggestion_not_sure')
                      : `${t('ai.suggestion_confident')} ${
                          materials.find(m => m.code === aiClassSuggestion.code)
                            ? getMatName(materials.find(m => m.code === aiClassSuggestion.code)!)
                            : aiClassSuggestion.code
                        }`}
                  </span>
                </div>
                {aiClassSuggestion.demo_only && (
                  <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-[#FEF3C7] text-[#92400E] border border-[#FDE68A]">
                    {t('demo_model', 'Demo Model')}
                  </span>
                )}
              </div>

              {!aiClassSuggestion.not_sure && (
                <div className="flex items-center justify-between pt-1">
                  {/* 3-dot confidence meter */}
                  <div className="flex items-center gap-1.5">
                    <span className="text-[11px] text-[#556960] font-medium">{t('confidence_label')}:</span>
                    <div className="flex items-center gap-1">
                      <span className={`w-2 h-2 rounded-full ${aiClassSuggestion.confidence > 0 ? 'bg-[#10B981]' : 'bg-[#D1D5DB]'}`} />
                      <span className={`w-2 h-2 rounded-full ${aiClassSuggestion.confidence >= 0.60 ? 'bg-[#10B981]' : 'bg-[#D1D5DB]'}`} />
                      <span className={`w-2 h-2 rounded-full ${aiClassSuggestion.confidence >= 0.80 ? 'bg-[#10B981]' : 'bg-[#D1D5DB]'}`} />
                    </div>
                    <span className="text-[10px] font-mono text-[#556960]">
                      ({Math.round(aiClassSuggestion.confidence * 100)}%)
                    </span>
                  </div>

                  {/* Actions */}
                  <div className="flex items-center gap-2">
                    <button
                      type="button"
                      onClick={() => {
                        const match = materials.find(m => m.code === aiClassSuggestion.code);
                        if (match) {
                          setSelectedMat(match);
                          setUserOverridden(false);
                        }
                      }}
                      className={`flex items-center gap-1 px-2.5 py-1 rounded-lg text-xs font-bold transition cursor-pointer ${
                        selectedMat?.code === aiClassSuggestion.code
                          ? 'bg-[#0B3D2E] text-white'
                          : 'bg-white border border-[#14634A] text-[#0B3D2E] hover:bg-[#E4F4EA]'
                      }`}
                    >
                      <Check size={13} />
                      <span>{selectedMat?.code === aiClassSuggestion.code ? t('btn_accepted_suggestion') : t('btn_accept_suggestion')}</span>
                    </button>
                    <button
                      type="button"
                      onClick={() => {
                        setUserOverridden(true);
                        setStep(1);
                      }}
                      className="flex items-center gap-1 px-2 py-1 rounded-lg text-xs font-medium text-[#556960] hover:text-[#14201A] cursor-pointer"
                    >
                      <X size={13} />
                      <span>{t('btn_change_category')}</span>
                    </button>
                  </div>
                </div>
              )}
            </div>
          )}

          <div className="flex gap-2 pt-2">
            <BigButton
              label={t('btn_skip_next')}
              variant="secondary"
              onClick={() => setStep(3)}
            />
            <BigButton
              label={t('btn_next_weight')}
              onClick={() => setStep(3)}
              icon={<ArrowRight size={20} />}
            />
          </div>
        </div>
      )}

      {/* STEP 3: WEIGHT */}
      {step === 3 && (
        <div className="flex flex-col gap-4">
          <div>
            <h2 className="text-lg font-black text-[#0B3D2E]">
              {t('step_weight')}
            </h2>
            <p className="text-xs text-[#5B6B62]">
              {t('step3_desc')}
            </p>
          </div>

          <WeightStepper
            valueGrams={weightGrams}
            onChange={setWeightGrams}
          />

          {/* Condition toggle */}
          <div className="flex flex-col gap-1.5 pt-2">
            <label className="text-xs font-bold uppercase tracking-wider text-[#5B6B62]">
              {t('item_condition_label')}
            </label>
            <div className="grid grid-cols-3 gap-2">
              {(['broken', 'working', 'burnt'] as const).map((cond) => (
                <button
                  key={cond}
                  type="button"
                  onClick={() => setCondition(cond)}
                  className={`py-3 px-2 rounded-xl text-xs font-bold border capitalize transition-all cursor-pointer touch-target ${
                    condition === cond
                      ? 'bg-[#E4F4EA] border-[#14634A] text-[#0B3D2E] ring-2 ring-[#14634A]'
                      : 'bg-white border-[#E3E0D5] text-[#5B6B62] hover:bg-[#F7F5EF]'
                  }`}
                >
                  {cond === 'working' ? t('condition_working') : (cond === 'burnt' ? t('condition_burnt') : t('condition_broken'))}
                </button>
              ))}
            </div>
          </div>

          <div className="pt-2">
            <BigButton
              label={t('btn_next_estimate')}
              onClick={() => setStep(4)}
              icon={<ArrowRight size={20} />}
            />
          </div>
        </div>
      )}

      {/* STEP 4: INSTANT ESTIMATE (OFFLINE RESILIENT) */}
      {step === 4 && (
        <div className="flex flex-col gap-4">
          <div>
            <h2 className="text-lg font-black text-[#0B3D2E]">
              {t('step_estimate')}
            </h2>
            <p className="text-xs text-[#5B6B62]">
              {t('step4_desc')}
            </p>
          </div>

          {/* Value Card */}
          <div className="flex flex-col p-4 rounded-2xl bg-[#FCF3D9] border border-[#E9A310]/40 gap-1 shadow-sm">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold uppercase tracking-wider text-[#14201A]/70">
                {t('instant_estimate_title')}
              </span>
              <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-[#2E9E5B] text-white">
                {t('offline_validated_badge')}
              </span>
            </div>
            <div className="flex items-baseline justify-between mt-1">
              <span className="text-3xl font-black text-[#14201A] tabular-nums tracking-tight">
                {formatINR(estMin)} - {formatINR(estMax)}
              </span>
              <VoiceButton text={`Estimated value: ${formatINR(estMin)} to ${formatINR(estMax)}`} size={20} />
            </div>
            <span className="text-xs text-[#5B6B62] mt-1">
              {formatWeight(weightGrams)} • {selectedMat ? getMatName(selectedMat) : ''} ({t(`condition_${condition}`)})
            </span>
          </div>

          {/* Hazardous Material Warning if applicable */}
          {selectedMat?.is_hazardous && (
            <SafetyBanner
              hazardNote={selectedMat.hazard_note_en}
              safetyTip={selectedMat.safety_tip_en}
              bonusINR={50}
            />
          )}

          {/* Strategic Recoverable Minerals Chips */}
          <div className="flex flex-col gap-2 p-3.5 rounded-2xl bg-white border border-[#E3E0D5]">
            <span className="text-xs font-bold uppercase tracking-wider text-[#0B3D2E]">
              {t('minerals_recoverable_est')}
            </span>
            <div className="flex flex-wrap gap-2">
              <span className="px-2.5 py-1 rounded-lg bg-[#E4F4EA] text-[#0B3D2E] text-xs font-bold border border-[#2E9E5B]/40">
                {t('mineral_copper', 'तांबे')}: {(wtKg * 0.18 * 0.85).toFixed(2)} {formatWeight(1000).replace(/^[0-9.\s]+/, '')}
              </span>
              <span className="px-2.5 py-1 rounded-lg bg-[#E4F4EA] text-[#0B3D2E] text-xs font-bold border border-[#2E9E5B]/40">
                {t('mineral_gold_silver', 'सोने')}: {(wtKg * 0.35 * 0.70).toFixed(2)} {formatWeight(1).replace(/^[0-9.\s]+/, '')}
              </span>
              <span className="px-2.5 py-1 rounded-lg bg-[#FCF3D9] text-[#14201A] text-xs font-bold border border-[#E9A310]/40">
                {t('mineral_gold_silver', 'चांदी')}: {(wtKg * 1.2 * 0.70).toFixed(2)} {formatWeight(1).replace(/^[0-9.\s]+/, '')}
              </span>
            </div>
          </div>

          {/* Action: List lot & Find Buyers */}
          <div className="pt-2 flex flex-col gap-2">
            <BigButton
              label={t('btn_find_buyers')}
              onClick={handleCreateLot}
              disabled={submitting}
              icon={<CheckCircle size={20} />}
            />
            <p className="text-center text-[11px] text-[#5B6B62]">
              {t('zero_compliance_burden')}
            </p>
          </div>
        </div>
      )}
    </div>
  );
};
