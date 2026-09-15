import React, { useState, useEffect, useRef } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import {
  KeyRound, ArrowRight,
  CheckCircle2, Volume2,
  UserPlus, LogIn, ArrowLeft,
  AlertCircle, RefreshCw, Smartphone, Edit3, MessageCircle,
  Mail
} from 'lucide-react';
import { useAuthStore } from './authStore';
import { speak } from '../../lib/voice';
import { LanguageSwitch } from '../../design/components/LanguageSwitch';

interface LoginViewProps {
  defaultTab?: 'login' | 'signup';
}

export const LoginView: React.FC<LoginViewProps> = ({ defaultTab }) => {
  const { t, i18n } = useTranslation();
  const navigate = useNavigate();
  const location = useLocation();
  const { login, requestOtp, signup } = useAuthStore();

  // Active Mode: 'login' | 'signup'
  const isSignupPath = location.pathname.includes('signup') || defaultTab === 'signup';
  const [activeTab, setActiveTab] = useState<'login' | 'signup'>(isSignupPath ? 'signup' : 'login');

  // Step: 'form' | 'otp'
  const [step, setStep] = useState<'form' | 'otp'>('form');

  // Auth Method: 'phone' | 'email'
  const [authMethod, setAuthMethod] = useState<'phone' | 'email'>('phone');
  const [email, setEmail] = useState('');

  // Form states (clean defaults, no hardcoded fake numbers)
  const [phone, setPhone] = useState('');
  const [name, setName] = useState('');
  const [role, setRole] = useState<'collector' | 'recycler' | 'aggregator'>('collector');
  const [city, setCity] = useState('Delhi NCR');
  const [companyName, setCompanyName] = useState('');
  const [cpcbLicense, setCpcbLicense] = useState('');

  // 6-digit OTP segmented states
  const [otpDigits, setOtpDigits] = useState<string[]>(['', '', '', '', '', '']);
  const otpInputsRef = useRef<(HTMLInputElement | null)[]>([]);
  const [resendSeconds, setResendSeconds] = useState(30);

  const [otpInfo, setOtpInfo] = useState<{
    delivered: boolean;
    provider: string;
    message: string;
  } | null>(null);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const CITIES = [
    'Delhi NCR', 'Mumbai', 'Ludhiana', 'Chandigarh',
    'Jaipur', 'Lucknow', 'Bengaluru', 'Ranchi'
  ];

  // Resend countdown timer
  useEffect(() => {
    if (step !== 'otp' || resendSeconds <= 0) return;
    const timer = setInterval(() => {
      setResendSeconds((prev) => (prev > 0 ? prev - 1 : 0));
    }, 1000);
    return () => clearInterval(timer);
  }, [step, resendSeconds]);

  useEffect(() => {
    if (location.pathname.includes('signup')) {
      setActiveTab('signup');
    }
  }, [location.pathname]);

  const handleTabChange = (tab: 'login' | 'signup') => {
    setActiveTab(tab);
    setStep('form');
    setError(null);
    setOtpInfo(null);
    setOtpDigits(['', '', '', '', '', '']);
  };

  const startOtpFlow = (res: any) => {
    if (res?.dev_otp) {
      console.log(`[KC Auth] OTP Code: ${res.dev_otp}`);
    }
    setOtpInfo({
      delivered: !!res.delivered,
      provider: res?.provider || (authMethod === 'email' ? 'Email Gateway' : 'SMS Gateway'),
      message: res?.message || 'Verification code sent.'
    });
    setOtpDigits(['', '', '', '', '', '']);
    setStep('otp');
    setResendSeconds(30);
    setTimeout(() => { otpInputsRef.current[0]?.focus(); }, 100);

    // Clean vernacular voice guidance
    if (authMethod === 'email') {
      if (i18n.language === 'mr') {
        speak('कृपया तुमच्या ईमेलवर आलेला ६ अंकी पडताळणी कोड टाका.', 'mr');
      } else if (i18n.language === 'hi') {
        speak('कृपया अपने ईमेल पर आया ६ अंकों का सत्यापन कोड दर्ज करें।', 'hi');
      } else if (i18n.language === 'pa') {
        speak('ਕਿਰਪਾ ਕਰਕੇ ਆਪਣੇ ਈਮੇਲ ਤੇ ਆਇਆ 6-ਅੰਕੀ ਪੁਸ਼ਟੀ ਕੋਡ ਦਰਜ ਕਰੋ।', 'pa');
      } else {
        speak('Please enter the 6-digit verification code sent to your email.', 'en');
      }
    } else {
      if (i18n.language === 'mr') {
        speak('कृपया तुमच्या मोबाईलवर आलेला ६ अंकी पडताळणी कोड टाका.', 'mr');
      } else if (i18n.language === 'hi') {
        speak('कृपया अपने मोबाइल पर आया ६ अंकों का सत्यापन कोड दर्ज करें।', 'hi');
      } else if (i18n.language === 'pa') {
        speak('ਕਿਰਪਾ ਕਰਕੇ ਆਪਣੇ ਮੋਬਾਈਲ ਤੇ ਆਇਆ 6-ਅੰਕੀ ਪੁਸ਼ਟੀ ਕੋਡ ਦਰਜ ਕਰੋ।', 'pa');
      } else {
        speak('Please enter the 6-digit verification code sent to your phone.', 'en');
      }
    }
  };

  const handleSendLoginOTP = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (authMethod === 'email') {
      const cleanEmail = email.trim().toLowerCase();
      if (!cleanEmail || !cleanEmail.includes('@') || !cleanEmail.includes('.')) {
        setError('Please enter a valid email address');
        return;
      }
      setLoading(true);
      setError(null);
      try {
        const res = await requestOtp(cleanEmail, true);
        startOtpFlow(res);
      } catch (err: any) {
        setError(err.message || 'Failed to send verification code. Please try again.');
      } finally {
        setLoading(false);
      }
      return;
    }

    const cleanPhone = phone.replace(/\D/g, '');
    if (cleanPhone.length < 10) {
      setError('Please enter a valid 10-digit mobile number');
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const res = await requestOtp(cleanPhone, false);
      startOtpFlow(res);
    } catch (err: any) {
      setError(err.message || 'Failed to send verification code. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleSendSignupOTP = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!name.trim()) {
      setError('Please enter your full name');
      return;
    }

    if (authMethod === 'email') {
      const cleanEmail = email.trim().toLowerCase();
      if (!cleanEmail || !cleanEmail.includes('@') || !cleanEmail.includes('.')) {
        setError('Please enter a valid email address');
        return;
      }
      setLoading(true);
      setError(null);
      try {
        const res = await signup({
          email: cleanEmail,
          name: name.trim(),
          role,
          language: i18n.language || 'mr',
          city,
          company_name: companyName.trim() || undefined,
          cpcb_license_no: cpcbLicense.trim() || undefined
        });
        startOtpFlow(res);
      } catch (err: any) {
        setError(err.message || 'Registration failed. Please try again.');
      } finally {
        setLoading(false);
      }
      return;
    }

    const cleanPhone = phone.replace(/\D/g, '');
    if (cleanPhone.length < 10) {
      setError('Please enter a valid 10-digit mobile number');
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const res = await signup({
        phone: cleanPhone,
        name: name.trim(),
        role,
        language: i18n.language || 'mr',
        city,
        company_name: companyName.trim() || undefined,
        cpcb_license_no: cpcbLicense.trim() || undefined
      });
      startOtpFlow(res);
    } catch (err: any) {
      setError(err.message || 'Registration failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // OTP Input handlers
  const handleDigitChange = (index: number, value: string) => {
    const cleaned = value.replace(/\D/g, '');
    if (!cleaned) {
      const updated = [...otpDigits];
      updated[index] = '';
      setOtpDigits(updated);
      return;
    }

    // If pasted multiple digits
    if (cleaned.length > 1) {
      const chars = cleaned.slice(0, 6).split('');
      const updated = [...otpDigits];
      chars.forEach((c, idx) => {
        if (idx < 6) updated[idx] = c;
      });
      setOtpDigits(updated);
      const nextIdx = Math.min(chars.length, 5);
      otpInputsRef.current[nextIdx]?.focus();
      return;
    }

    // Single digit input
    const updated = [...otpDigits];
    updated[index] = cleaned[0];
    setOtpDigits(updated);

    if (index < 5 && cleaned[0]) {
      otpInputsRef.current[index + 1]?.focus();
    }
  };

  const handleKeyDown = (index: number, e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Backspace' && !otpDigits[index] && index > 0) {
      otpInputsRef.current[index - 1]?.focus();
    } else if (e.key === 'ArrowLeft' && index > 0) {
      otpInputsRef.current[index - 1]?.focus();
    } else if (e.key === 'ArrowRight' && index < 5) {
      otpInputsRef.current[index + 1]?.focus();
    }
  };

  const handlePaste = (e: React.ClipboardEvent) => {
    e.preventDefault();
    const pasted = e.clipboardData.getData('text').replace(/\D/g, '').slice(0, 6);
    if (!pasted) return;
    const updated = [...otpDigits];
    pasted.split('').forEach((char, idx) => {
      if (idx < 6) updated[idx] = char;
    });
    setOtpDigits(updated);
    const nextIdx = Math.min(pasted.length, 5);
    otpInputsRef.current[nextIdx]?.focus();
  };

  const fullOtp = otpDigits.join('');

  const handleVerifyOTP = async (e: React.FormEvent) => {
    e.preventDefault();
    if (fullOtp.length < 6) {
      setError('Please enter all 6 digits of your verification code');
      return;
    }
    setLoading(true);
    setError(null);
    try {
      if (authMethod === 'email') {
        await login(email.trim().toLowerCase(), fullOtp, true);
      } else {
        const cleanPhone = phone.replace(/\D/g, '');
        await login(cleanPhone, fullOtp, false);
      }

      // Route based on role
      const currentUser = useAuthStore.getState().user;
      const targetRole = currentUser?.role || role;
      if (targetRole === 'recycler') {
        navigate('/recycler');
      } else if (targetRole === 'aggregator') {
        navigate('/aggregator');
      } else {
        navigate('/');
      }
    } catch (err: any) {
      setError(err.message || 'Invalid verification code. Please check and try again.');
    } finally {
      setLoading(false);
    }
  };

  // Format phone number cleanly for presentation (e.g., 98765 43201)
  const formatPhone = (raw: string) => {
    const d = raw.replace(/\D/g, '');
    if (d.length <= 5) return d;
    return `${d.slice(0, 5)} ${d.slice(5, 10)}`;
  };

  return (
    <div className="min-h-screen bg-[#F8FAF9] flex flex-col justify-between text-[#14201A] font-sans antialiased selection:bg-[#E4F4EA]">
      {/* Top Header */}
      <header className="px-4 sm:px-8 py-3.5 flex items-center justify-between border-b border-[#E3E0D5] bg-white/95 backdrop-blur-md shadow-xs sticky top-0 z-20">
        <div
          className="flex items-center gap-3 cursor-pointer"
          onClick={() => navigate('/')}
        >
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-[#0B3D2E] to-[#14634A] text-white flex items-center justify-center font-black text-lg shadow-sm">
            KC
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-base font-black text-[#0B3D2E] leading-tight">
                {t('app_name')}
              </h1>
              <span className="hidden sm:inline-flex items-center gap-1 text-[10px] font-bold px-2 py-0.5 rounded-full bg-[#E4F4EA] text-[#14634A] border border-[#2E9E5B]/30">
                <span className="w-1.5 h-1.5 rounded-full bg-[#2E9E5B] animate-pulse" />
                {t('header_live_grid')}
              </span>
            </div>
            <span className="text-[11px] text-[#5B6B62] font-semibold block">
              {t('header_portal_subtitle')}
            </span>
          </div>
        </div>

        {/* Vernacular Language Selector Header */}
        <LanguageSwitch compact />
      </header>

      {/* Main Authentication Card */}
      <main className="flex-1 px-4 py-8 sm:py-12 flex items-center justify-center">
        <div className="max-w-md w-full bg-white rounded-3xl border border-[#E3E0D5] p-6 sm:p-8 shadow-xl shadow-[#0B3D2E]/5 transition-all">
          
          {/* STEP 1: Phone & Info Form */}
          {step === 'form' && (
            <div>
              {/* Vernacular Language Switcher Section */}
              <div className="mb-6">
                <div className="flex items-center justify-between mb-2.5">
                  <span className="text-[11px] font-extrabold uppercase tracking-wider text-[#14634A] bg-[#E4F4EA] px-2.5 py-1 rounded-md">
                    {i18n.language === 'mr' ? '१. भाषा निवडा' : i18n.language === 'pa' ? '1. ਭਾਸ਼ਾ ਚੁਣੋ' : i18n.language === 'hi' ? '1. भाषा चुनें' : '1. Select Language'}
                  </span>
                  <button
                    type="button"
                    onClick={() => {
                      if (i18n.language === 'mr') speak('आपली भाषा निवडा आणि पुढे जा.', 'mr');
                      else if (i18n.language === 'hi') speak('अपनी भाषा चुनें और आगे बढ़ें.', 'hi');
                      else if (i18n.language === 'pa') speak('ਆਪਣੀ ਭਾਸ਼ਾ ਚੁਣੋ ਅਤੇ ਅੱਗੇ ਵਧੋ।', 'pa');
                      else speak('Please choose your language to continue.', 'en');
                    }}
                    className="p-1.5 rounded-full bg-[#FAF8F5] hover:bg-[#F2EFE9] text-[#0B3D2E] border border-[#E3E0D5] cursor-pointer transition-colors"
                    title="Voice Prompt"
                  >
                    <Volume2 size={15} />
                  </button>
                </div>
                <LanguageSwitch compact={false} />
              </div>

              {/* Tab Switcher: Log In vs Sign Up */}
              <div className="flex p-1.5 bg-[#F0EFE9] rounded-2xl mb-6">
                <button
                  type="button"
                  onClick={() => handleTabChange('login')}
                  className={`flex-1 flex items-center justify-center gap-2 py-2.5 rounded-xl text-xs font-black transition-all cursor-pointer ${
                    activeTab === 'login'
                      ? 'bg-[#0B3D2E] text-white shadow-xs'
                      : 'text-[#5B6B62] hover:text-[#14201A]'
                  }`}
                >
                  <LogIn size={15} />
                  <span>{t('tab_login')}</span>
                </button>
                <button
                  type="button"
                  onClick={() => handleTabChange('signup')}
                  className={`flex-1 flex items-center justify-center gap-2 py-2.5 rounded-xl text-xs font-black transition-all cursor-pointer ${
                    activeTab === 'signup'
                      ? 'bg-[#0B3D2E] text-white shadow-xs'
                      : 'text-[#5B6B62] hover:text-[#14201A]'
                  }`}
                >
                  <UserPlus size={15} />
                  <span>{t('tab_signup')}</span>
                </button>
              </div>

              {/* Title & Description */}
              <div className="mb-5">
                <h2 className="text-xl font-black text-[#14201A] tracking-tight">
                  {activeTab === 'login' ? t('login_title') : t('signup_title')}
                </h2>
                <p className="text-xs text-[#5B6B62] mt-1 font-medium leading-relaxed">
                  {activeTab === 'login' ? t('login_subtitle') : t('signup_subtitle')}
                </p>
              </div>

              {/* Error Banner */}
              {error && (
                <div className="mb-4 p-3 rounded-2xl bg-[#FFF0F0] border border-[#C93B2B]/30 text-[#C93B2B] text-xs font-bold flex items-center gap-2 animate-in fade-in">
                  <AlertCircle size={16} className="shrink-0" />
                  <span>{error}</span>
                </div>
              )}

              {/* LOGIN FORM */}
              {activeTab === 'login' && (
                <form onSubmit={handleSendLoginOTP} className="space-y-4">
                  {/* Method Toggle: Mobile vs Email */}
                  <div className="flex p-1 bg-[#F0EFE9] rounded-xl mb-3">
                    <button
                      type="button"
                      onClick={() => { setAuthMethod('phone'); setError(null); }}
                      className={`flex-1 flex items-center justify-center gap-1.5 py-2 rounded-lg text-xs font-bold transition-all cursor-pointer ${
                        authMethod === 'phone'
                          ? 'bg-white text-[#0B3D2E] shadow-xs'
                          : 'text-[#5B6B62] hover:text-[#14201A]'
                      }`}
                    >
                      <Smartphone size={14} />
                      <span>{t('tab_phone')}</span>
                    </button>
                    <button
                      type="button"
                      onClick={() => { setAuthMethod('email'); setError(null); }}
                      className={`flex-1 flex items-center justify-center gap-1.5 py-2 rounded-lg text-xs font-bold transition-all cursor-pointer ${
                        authMethod === 'email'
                          ? 'bg-white text-[#0B3D2E] shadow-xs'
                          : 'text-[#5B6B62] hover:text-[#14201A]'
                      }`}
                    >
                      <Mail size={14} />
                      <span>{t('tab_email')}</span>
                    </button>
                  </div>

                  {authMethod === 'phone' ? (
                    <div>
                      <label className="block text-xs font-bold text-[#14201A] mb-1.5">
                        {t('label_mobile')}
                      </label>
                      <div className="relative flex items-center">
                        <div className="absolute left-3.5 flex items-center gap-1.5 pointer-events-none">
                          <span className="text-base leading-none">🇮🇳</span>
                          <span className="font-mono font-bold text-xs text-[#5B6B62]">+91</span>
                        </div>
                        <input
                          type="tel"
                          value={phone}
                          onChange={(e) => setPhone(e.target.value.replace(/\D/g, '').slice(0, 10))}
                          placeholder="98765 43210"
                          className="w-full pl-18 pr-4 py-3 rounded-2xl border border-[#D1CEBF] font-mono font-bold text-base text-[#14201A] tracking-wider focus:outline-none focus:border-[#14634A] focus:ring-3 focus:ring-[#14634A]/10 bg-white transition-all"
                          required
                          autoFocus
                        />
                      </div>
                      <div className="flex items-center justify-between text-[11px] text-[#5B6B62] mt-1.5 font-medium">
                        <span>Standard 10-digit mobile</span>
                        <span className="text-[#14634A] font-bold flex items-center gap-1">
                          <CheckCircle2 size={12} /> Instant OTP Delivery
                        </span>
                      </div>
                    </div>
                  ) : (
                    <div>
                      <label className="block text-xs font-bold text-[#14201A] mb-1.5">
                        {t('label_email')}
                      </label>
                      <div className="relative flex items-center">
                        <div className="absolute left-3.5 flex items-center pointer-events-none text-[#5B6B62]">
                          <Mail size={17} />
                        </div>
                        <input
                          type="email"
                          value={email}
                          onChange={(e) => setEmail(e.target.value)}
                          placeholder="name@example.com"
                          className="w-full pl-10 pr-4 py-3 rounded-2xl border border-[#D1CEBF] font-semibold text-sm text-[#14201A] focus:outline-none focus:border-[#14634A] focus:ring-3 focus:ring-[#14634A]/10 bg-white transition-all"
                          required
                          autoFocus
                        />
                      </div>
                      <div className="flex items-center justify-between text-[11px] text-[#5B6B62] mt-1.5 font-medium">
                        <span>Official or personal email</span>
                        <span className="text-[#14634A] font-bold flex items-center gap-1">
                          <CheckCircle2 size={12} /> Instant OTP Delivery
                        </span>
                      </div>
                    </div>
                  )}

                  <button
                    type="submit"
                    disabled={loading || (authMethod === 'phone' ? phone.length < 10 : !email.includes('@'))}
                    className="w-full py-3.5 rounded-2xl bg-[#0B3D2E] hover:bg-[#14634A] active:scale-98 disabled:opacity-50 text-white font-extrabold text-sm shadow-md hover:shadow-lg flex items-center justify-center gap-2 cursor-pointer transition-all"
                  >
                    {loading ? (
                      <RefreshCw size={18} className="animate-spin" />
                    ) : (
                      <>
                        <span>{t('btn_send_otp')}</span>
                        <ArrowRight size={16} />
                      </>
                    )}
                  </button>

                  <div className="text-center pt-2">
                    <span className="text-xs text-[#5B6B62]">{t('prompt_new_user')} </span>
                    <button
                      type="button"
                      onClick={() => handleTabChange('signup')}
                      className="text-xs font-bold text-[#14634A] hover:underline cursor-pointer"
                    >
                      {t('tab_signup')}
                    </button>
                  </div>
                </form>
              )}

              {/* SIGN UP FORM */}
              {activeTab === 'signup' && (
                <form onSubmit={handleSendSignupOTP} className="space-y-4">
                  <div>
                    <label className="block text-xs font-bold text-[#14201A] mb-1.5">
                      {t('label_fullname')}
                    </label>
                    <input
                      type="text"
                      value={name}
                      onChange={(e) => setName(e.target.value)}
                      placeholder="e.g. Ramesh Kumar"
                      className="w-full px-4 py-3 rounded-2xl border border-[#D1CEBF] font-bold text-sm text-[#14201A] focus:outline-none focus:border-[#14634A] focus:ring-3 focus:ring-[#14634A]/10 bg-white transition-all"
                      required
                    />
                  </div>

                  {/* Method Toggle: Mobile vs Email */}
                  <div>
                    <label className="block text-xs font-bold text-[#14201A] mb-1.5">
                      {authMethod === 'phone' ? t('label_mobile') : t('label_email')}
                    </label>
                    <div className="flex p-1 bg-[#F0EFE9] rounded-xl mb-3">
                      <button
                        type="button"
                        onClick={() => { setAuthMethod('phone'); setError(null); }}
                        className={`flex-1 flex items-center justify-center gap-1.5 py-2 rounded-lg text-xs font-bold transition-all cursor-pointer ${
                          authMethod === 'phone'
                            ? 'bg-white text-[#0B3D2E] shadow-xs'
                            : 'text-[#5B6B62] hover:text-[#14201A]'
                        }`}
                      >
                        <Smartphone size={14} />
                        <span>{t('tab_phone')}</span>
                      </button>
                      <button
                        type="button"
                        onClick={() => { setAuthMethod('email'); setError(null); }}
                        className={`flex-1 flex items-center justify-center gap-1.5 py-2 rounded-lg text-xs font-bold transition-all cursor-pointer ${
                          authMethod === 'email'
                            ? 'bg-white text-[#0B3D2E] shadow-xs'
                            : 'text-[#5B6B62] hover:text-[#14201A]'
                        }`}
                      >
                        <Mail size={14} />
                        <span>{t('tab_email')}</span>
                      </button>
                    </div>

                    {authMethod === 'phone' ? (
                      <div className="relative flex items-center">
                        <div className="absolute left-3.5 flex items-center gap-1.5 pointer-events-none">
                          <span className="text-base leading-none">🇮🇳</span>
                          <span className="font-mono font-bold text-xs text-[#5B6B62]">+91</span>
                        </div>
                        <input
                          type="tel"
                          value={phone}
                          onChange={(e) => setPhone(e.target.value.replace(/\D/g, '').slice(0, 10))}
                          placeholder="98765 43210"
                          className="w-full pl-18 pr-4 py-3 rounded-2xl border border-[#D1CEBF] font-mono font-bold text-base text-[#14201A] tracking-wider focus:outline-none focus:border-[#14634A] focus:ring-3 focus:ring-[#14634A]/10 bg-white transition-all"
                          required
                        />
                      </div>
                    ) : (
                      <div className="relative flex items-center">
                        <div className="absolute left-3.5 flex items-center pointer-events-none text-[#5B6B62]">
                          <Mail size={17} />
                        </div>
                        <input
                          type="email"
                          value={email}
                          onChange={(e) => setEmail(e.target.value)}
                          placeholder="name@example.com"
                          className="w-full pl-10 pr-4 py-3 rounded-2xl border border-[#D1CEBF] font-semibold text-sm text-[#14201A] focus:outline-none focus:border-[#14634A] focus:ring-3 focus:ring-[#14634A]/10 bg-white transition-all"
                          required
                        />
                      </div>
                    )}
                  </div>

                  {/* Role Selector */}
                  <div>
                    <label className="block text-xs font-bold text-[#14201A] mb-1.5">
                      {t('label_role')}
                    </label>
                    <div className="grid grid-cols-3 gap-2">
                      <button
                        type="button"
                        onClick={() => setRole('collector')}
                        className={`p-3 rounded-2xl border text-left transition-all cursor-pointer flex flex-col justify-between ${
                          role === 'collector'
                            ? 'bg-[#E4F4EA] border-[#2E9E5B] text-[#0B3D2E] shadow-xs'
                            : 'bg-white border-[#E3E0D5] text-[#5B6B62] hover:bg-[#FAF8F5]'
                        }`}
                      >
                        <span className="text-base mb-1">♻️</span>
                        <span className="text-xs font-black block">{t('role_collector')}</span>
                      </button>

                      <button
                        type="button"
                        onClick={() => setRole('recycler')}
                        className={`p-3 rounded-2xl border text-left transition-all cursor-pointer flex flex-col justify-between ${
                          role === 'recycler'
                            ? 'bg-[#E4F4EA] border-[#2E9E5B] text-[#0B3D2E] shadow-xs'
                            : 'bg-white border-[#E3E0D5] text-[#5B6B62] hover:bg-[#FAF8F5]'
                        }`}
                      >
                        <span className="text-base mb-1">🏭</span>
                        <span className="text-xs font-black block">{t('role_recycler')}</span>
                      </button>

                      <button
                        type="button"
                        onClick={() => setRole('aggregator')}
                        className={`p-3 rounded-2xl border text-left transition-all cursor-pointer flex flex-col justify-between ${
                          role === 'aggregator'
                            ? 'bg-[#E4F4EA] border-[#2E9E5B] text-[#0B3D2E] shadow-xs'
                            : 'bg-white border-[#E3E0D5] text-[#5B6B62] hover:bg-[#FAF8F5]'
                        }`}
                      >
                        <span className="text-base mb-1">📦</span>
                        <span className="text-xs font-black block">{t('role_aggregator')}</span>
                      </button>
                    </div>
                  </div>

                  <div>
                    <label className="block text-xs font-bold text-[#14201A] mb-1.5">
                      {t('label_city')}
                    </label>
                    <select
                      value={city}
                      onChange={(e) => setCity(e.target.value)}
                      className="w-full px-4 py-3 rounded-2xl border border-[#D1CEBF] font-bold text-sm text-[#14201A] focus:outline-none focus:border-[#14634A] bg-white cursor-pointer"
                    >
                      {CITIES.map((c) => (
                        <option key={c} value={c}>
                          {c}
                        </option>
                      ))}
                    </select>
                  </div>

                  {role === 'recycler' && (
                    <div className="p-3.5 rounded-2xl bg-[#FAF8F5] border border-[#E3E0D5] space-y-3">
                      <div>
                        <label className="block text-[11px] font-bold text-[#14201A] mb-1">
                          {t('label_company')}
                        </label>
                        <input
                          type="text"
                          value={companyName}
                          onChange={(e) => setCompanyName(e.target.value)}
                          placeholder="e.g. Circular Metals Private Limited"
                          className="w-full px-3 py-2 rounded-xl border border-[#D1CEBF] text-xs font-bold bg-white"
                        />
                      </div>
                      <div>
                        <label className="block text-[11px] font-bold text-[#14201A] mb-1">
                          {t('label_cpcb_license')}
                        </label>
                        <input
                          type="text"
                          value={cpcbLicense}
                          onChange={(e) => setCpcbLicense(e.target.value)}
                          placeholder="e.g. CPCB-REG-DL-2024-042"
                          className="w-full px-3 py-2 rounded-xl border border-[#D1CEBF] text-xs font-bold bg-white"
                        />
                      </div>
                    </div>
                  )}

                  <button
                    type="submit"
                    disabled={loading || !name.trim() || (authMethod === 'phone' ? phone.length < 10 : !email.includes('@'))}
                    className="w-full py-3.5 rounded-2xl bg-[#0B3D2E] hover:bg-[#14634A] active:scale-98 disabled:opacity-50 text-white font-extrabold text-sm shadow-md flex items-center justify-center gap-2 cursor-pointer transition-all"
                  >
                    {loading ? (
                      <RefreshCw size={18} className="animate-spin" />
                    ) : (
                      <>
                        <span>{t('btn_send_otp')}</span>
                        <ArrowRight size={16} />
                      </>
                    )}
                  </button>

                  <div className="text-center pt-2">
                    <span className="text-xs text-[#5B6B62]">{t('prompt_existing_user')} </span>
                    <button
                      type="button"
                      onClick={() => handleTabChange('login')}
                      className="text-xs font-bold text-[#14634A] hover:underline cursor-pointer"
                    >
                      {t('tab_login')}
                    </button>
                  </div>
                </form>
              )}
            </div>
          )}

          {/* STEP 2: PROFESSIONAL OTP VERIFICATION */}
          {step === 'otp' && (
            <div className="animate-in fade-in slide-in-from-bottom-2 duration-200">
              {/* Back Navigation Bar */}
              <div className="flex items-center mb-5 pb-3 border-b border-[#E3E0D5]/70">
                <button
                  type="button"
                  onClick={() => {
                    setStep('form');
                    setError(null);
                  }}
                  className="inline-flex items-center gap-1.5 text-xs font-bold text-[#5B6B62] hover:text-[#0B3D2E] transition-colors cursor-pointer"
                >
                  <ArrowLeft size={16} />
                  <span>{i18n.language === 'mr' ? 'मागे' : i18n.language === 'hi' ? 'पीछे' : i18n.language === 'pa' ? 'ਪਿੱਛੇ' : 'Back'}</span>
                </button>
              </div>

              {/* Verification Header */}
              <div className="text-center mb-6">
                <div className="w-13 h-13 rounded-2xl bg-[#E4F4EA] text-[#14634A] flex items-center justify-center mx-auto mb-3 shadow-inner">
                  {authMethod === 'email' ? <Mail size={24} /> : <Smartphone size={24} />}
                </div>
                <h2 className="text-2xl font-black text-[#14201A] tracking-tight">
                  {t('otp_title')}
                </h2>
                <p className="mt-2 text-xs text-[#5B6B62] leading-relaxed">
                  {authMethod === 'email'
                    ? t('otp_subtitle_email', { email })
                    : t('otp_subtitle', { phone: formatPhone(phone) })}
                </p>
                <button
                  type="button"
                  onClick={() => {
                    setStep('form');
                    setError(null);
                  }}
                  className="mt-1.5 text-xs font-bold text-[#14634A] hover:underline inline-flex items-center gap-1 cursor-pointer"
                >
                  <Edit3 size={12} />
                  <span>{authMethod === 'email' ? t('btn_change_email') : t('btn_change_phone')}</span>
                </button>
              </div>

              {/* Error Banner */}
              {error && (
                <div className="mb-4 p-3 rounded-2xl bg-[#FFF0F0] border border-[#C93B2B]/30 text-[#C93B2B] text-xs font-bold flex items-center gap-2 animate-in fade-in">
                  <AlertCircle size={16} className="shrink-0" />
                  <span>{error}</span>
                </div>
              )}

              {/* Professional Sent Confirmation Badge */}
              <div className="mb-5 p-3 rounded-2xl bg-[#E4F4EA] border border-[#2E9E5B]/30 text-[#14634A] text-xs font-semibold flex items-center justify-between shadow-xs">
                <div className="flex items-center gap-2">
                  <CheckCircle2 size={16} className="text-[#2E9E5B] shrink-0" />
                  <span>
                    {authMethod === 'email'
                      ? `Verification code sent to ${email}`
                      : `SMS verification code sent to +91 ${formatPhone(phone)}`}
                  </span>
                </div>
                <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-white/90 border border-[#2E9E5B]/25 text-[#0B3D2E]">
                  Sent
                </span>
              </div>


              {/* Interactive 6-Digit PIN Pad */}
              <form onSubmit={handleVerifyOTP} className="space-y-6">
                <div>
                  <div
                    className="flex items-center justify-center gap-2 sm:gap-3"
                    onPaste={handlePaste}
                  >
                    {otpDigits.map((digit, index) => (
                      <input
                        key={index}
                        ref={(el) => {
                          otpInputsRef.current[index] = el;
                        }}
                        type="text"
                        inputMode="numeric"
                        maxLength={1}
                        value={digit}
                        onChange={(e) => handleDigitChange(index, e.target.value)}
                        onKeyDown={(e) => handleKeyDown(index, e)}
                        className={`w-11 h-14 sm:w-12 sm:h-15 text-center font-mono font-black text-2xl rounded-2xl border-2 transition-all outline-none ${
                          digit
                            ? 'border-[#14634A] bg-[#E4F4EA]/30 text-[#0B3D2E] shadow-xs'
                            : 'border-[#D1CEBF] bg-white text-[#14201A] focus:border-[#14634A] focus:ring-4 focus:ring-[#14634A]/10'
                        }`}
                      />
                    ))}
                  </div>
                </div>

                {/* Resend & Timer Controls */}
                <div className="flex items-center justify-between text-xs pt-1 px-1">
                  {resendSeconds > 0 ? (
                    <span className="text-[#5B6B62] font-semibold">
                      {t('btn_resend_otp')} in <strong className="text-[#0B3D2E] font-mono">0:{resendSeconds < 10 ? `0${resendSeconds}` : resendSeconds}</strong>
                    </span>
                  ) : (
                    <button
                      type="button"
                      onClick={() => (activeTab === 'login' ? handleSendLoginOTP() : handleSendSignupOTP())}
                      className="text-[#14634A] font-bold hover:underline cursor-pointer flex items-center gap-1"
                    >
                      <RefreshCw size={13} className={loading ? 'animate-spin' : ''} />
                      <span>{t('btn_resend_otp')}</span>
                    </button>
                  )}
                </div>

                {/* Verify Submit Button */}
                <button
                  type="submit"
                  disabled={loading || fullOtp.length < 6}
                  className="w-full py-3.5 rounded-2xl bg-[#0B3D2E] hover:bg-[#14634A] active:scale-98 disabled:opacity-40 text-white font-extrabold text-sm shadow-md hover:shadow-lg flex items-center justify-center gap-2 cursor-pointer transition-all"
                >
                  {loading ? (
                    <RefreshCw size={18} className="animate-spin" />
                  ) : (
                    <>
                      <KeyRound size={17} />
                      <span>{t('btn_verify_otp')}</span>
                    </>
                  )}
                </button>
              </form>
            </div>
          )}
        </div>
      </main>

      {/* Clean Professional Footer */}
      <footer className="p-4 text-center text-xs text-[#5B6B62] border-t border-[#E3E0D5] bg-white">
        Kabadiwala Connect • Smart India Hackathon 2026 • Ministry of Mines & JNARDDC
      </footer>
    </div>
  );
};
