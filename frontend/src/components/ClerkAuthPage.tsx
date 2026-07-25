/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 *
 * ClerkAuthPage — Fully custom auth UI using Clerk hooks.
 * No Clerk native components (SignIn / SignUp) are used.
 * All UI is hand-crafted to match the PRISM design system.
 */

import React, { useState, useRef, useEffect } from 'react';
import { useSignIn, useSignUp, useClerk } from '@clerk/clerk-react';
import { COLORS } from '../constants/colors';

// ─── Types ────────────────────────────────────────────────────────────────────
type AuthMode = 'signin' | 'signup';
type SignInStage = 'credentials' | 'verify_email';
type SignUpStage = 'credentials' | 'verify_email';

// ─── Google Icon SVG ──────────────────────────────────────────────────────────
function GoogleIcon() {
  return (
    <svg viewBox="0 0 24 24" width="18" height="18" xmlns="http://www.w3.org/2000/svg">
      <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4" />
      <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853" />
      <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l3.66-2.84z" fill="#FBBC05" />
      <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335" />
    </svg>
  );
}

// ─── Eye icon for password toggle ────────────────────────────────────────────
function EyeIcon({ open }: { open: boolean }) {
  return open ? (
    <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
      <circle cx="12" cy="12" r="3" />
    </svg>
  ) : (
    <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24" />
      <line x1="1" y1="1" x2="23" y2="23" />
    </svg>
  );
}

// ─── Animated map decoration ──────────────────────────────────────────────────
function MapDecoration() {
  return (
    <div className="absolute inset-0 flex items-center justify-center pointer-events-none overflow-hidden">
      <svg
        viewBox="0 0 800 900"
        xmlns="http://www.w3.org/2000/svg"
        className="w-full h-full opacity-[0.15]"
        style={{ maxWidth: '640px', maxHeight: '100vh' }}
      >
        <path
          d="M400,60 L460,110 L510,165 L555,260 L585,410 L558,560 L505,755 L455,905 L355,955 L255,905 L205,805 L155,655 L105,505 L122,355 L185,205 L258,108 Z"
          fill="none"
          stroke={COLORS.primary.main}
          strokeOpacity="0.5"
          strokeWidth="1.5"
        >
          <animate attributeName="stroke-opacity" dur="4s" repeatCount="indefinite" values="0.2;0.55;0.2" />
        </path>
        <path
          d="M200,300 L580,300 M230,450 L570,450 M250,600 L540,600 M280,750 L520,750"
          stroke={COLORS.primary.main} strokeOpacity="0.08" strokeWidth="0.5"
        />
        <path
          d="M300,100 L280,900 M420,80 L400,920 M520,150 L490,800"
          stroke={COLORS.primary.main} strokeOpacity="0.06" strokeWidth="0.5"
        />
        {/* Pulsing hotspots */}
        <circle cx="420" cy="350" fill={COLORS.status.error} r="5">
          <animate attributeName="r" dur="2s" repeatCount="indefinite" values="3;7;3" />
          <animate attributeName="opacity" dur="2s" repeatCount="indefinite" values="1;0.3;1" />
        </circle>
        <circle cx="420" cy="350" fill="none" r="14" stroke={COLORS.status.error} strokeWidth="1" opacity="0">
          <animate attributeName="r" dur="2s" repeatCount="indefinite" values="5;24" />
          <animate attributeName="opacity" dur="2s" repeatCount="indefinite" values="0.5;0" />
        </circle>
        <circle cx="315" cy="600" fill={COLORS.status.warning} r="4">
          <animate attributeName="r" dur="2.5s" repeatCount="indefinite" values="3;6;3" />
          <animate attributeName="opacity" dur="2.5s" repeatCount="indefinite" values="1;0.3;1" />
        </circle>
        <circle cx="315" cy="600" fill="none" r="12" stroke={COLORS.status.warning} strokeWidth="1" opacity="0">
          <animate attributeName="r" dur="2.5s" repeatCount="indefinite" values="4;20" />
          <animate attributeName="opacity" dur="2.5s" repeatCount="indefinite" values="0.5;0" />
        </circle>
        <circle cx="480" cy="220" fill={COLORS.status.error} opacity="0.6" r="3">
          <animate attributeName="opacity" dur="3s" repeatCount="indefinite" values="0.6;0.15;0.6" />
        </circle>
        <circle cx="350" cy="150" fill={COLORS.status.warning} opacity="0.6" r="3">
          <animate attributeName="opacity" dur="3.5s" repeatCount="indefinite" values="0.6;0.15;0.6" />
        </circle>
        <circle cx="510" cy="530" fill={COLORS.primary.main} opacity="0.5" r="3">
          <animate attributeName="opacity" dur="4s" repeatCount="indefinite" values="0.5;0.1;0.5" />
        </circle>
        {/* Connection lines */}
        <line x1="420" y1="350" x2="315" y2="600" stroke={COLORS.primary.main} strokeOpacity="0.08" strokeWidth="0.8">
          <animate attributeName="stroke-opacity" dur="3s" repeatCount="indefinite" values="0.04;0.15;0.04" />
        </line>
        <line x1="420" y1="350" x2="480" y2="220" stroke={COLORS.status.error} strokeOpacity="0.08" strokeWidth="0.8">
          <animate attributeName="stroke-opacity" dur="2.5s" repeatCount="indefinite" values="0.04;0.12;0.04" />
        </line>
      </svg>
    </div>
  );
}

// ─── Shared input field ───────────────────────────────────────────────────────
interface InputFieldProps {
  id: string;
  label: string;
  type: string;
  value: string;
  onChange: (v: string) => void;
  placeholder?: string;
  autoComplete?: string;
  disabled?: boolean;
  suffix?: React.ReactNode;
}

function InputField({ id, label, type, value, onChange, placeholder, autoComplete, disabled, suffix }: InputFieldProps) {
  const [focused, setFocused] = useState(false);

  return (
    <div className="flex flex-col gap-1.5">
      <label
        htmlFor={id}
        style={{
          fontFamily: "'JetBrains Mono', monospace",
          fontSize: '11px',
          fontWeight: 600,
          letterSpacing: '0.1em',
          color: focused ? COLORS.primary.main : COLORS.text.muted,
          textTransform: 'uppercase',
          transition: 'color 0.2s ease',
        }}
      >
        {label}
      </label>
      <div
        style={{
          position: 'relative',
          border: `1px solid ${focused ? COLORS.primary.main + '88' : '#3A3030'}`,
          borderRadius: '8px',
          background: '#1A1414',
          transition: 'border-color 0.2s ease, box-shadow 0.2s ease',
          boxShadow: focused ? `0 0 0 3px ${COLORS.primary.main}18` : 'none',
        }}
      >
        <input
          id={id}
          type={type}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onFocus={() => setFocused(true)}
          onBlur={() => setFocused(false)}
          placeholder={placeholder}
          autoComplete={autoComplete}
          disabled={disabled}
          style={{
            width: '100%',
            padding: suffix ? '10px 44px 10px 14px' : '10px 14px',
            background: 'transparent',
            border: 'none',
            outline: 'none',
            color: COLORS.text.primary,
            fontFamily: "'Inter', sans-serif",
            fontSize: '14px',
            borderRadius: '8px',
          }}
        />
        {suffix && (
          <div style={{ position: 'absolute', right: '12px', top: '50%', transform: 'translateY(-50%)' }}>
            {suffix}
          </div>
        )}
      </div>
    </div>
  );
}

// ─── OTP input ────────────────────────────────────────────────────────────────
function OTPInput({ length = 6, value, onChange }: { length?: number; value: string; onChange: (v: string) => void }) {
  const inputs = useRef<(HTMLInputElement | null)[]>([]);
  const digits = value.split('').concat(Array(length).fill('')).slice(0, length);

  const handleChange = (idx: number, val: string) => {
    const sanitized = val.replace(/\D/g, '').slice(-1);
    const next = [...digits];
    next[idx] = sanitized;
    onChange(next.join(''));
    if (sanitized && idx < length - 1) inputs.current[idx + 1]?.focus();
  };

  const handleKeyDown = (idx: number, e: React.KeyboardEvent) => {
    if (e.key === 'Backspace' && !digits[idx] && idx > 0) {
      inputs.current[idx - 1]?.focus();
    }
  };

  const handlePaste = (e: React.ClipboardEvent) => {
    const pasted = e.clipboardData.getData('text').replace(/\D/g, '').slice(0, length);
    onChange(pasted.padEnd(length, '').slice(0, length));
    inputs.current[Math.min(pasted.length, length - 1)]?.focus();
    e.preventDefault();
  };

  return (
    <div className="flex gap-2 justify-center">
      {digits.map((d, i) => (
        <input
          key={i}
          ref={(el) => { inputs.current[i] = el; }}
          type="text"
          inputMode="numeric"
          maxLength={1}
          value={d}
          onChange={(e) => handleChange(i, e.target.value)}
          onKeyDown={(e) => handleKeyDown(i, e)}
          onPaste={handlePaste}
          style={{
            width: '44px',
            height: '52px',
            textAlign: 'center',
            background: '#1A1414',
            border: `1px solid ${d ? COLORS.primary.main + '88' : '#3A3030'}`,
            borderRadius: '8px',
            color: COLORS.text.primary,
            fontFamily: "'JetBrains Mono', monospace",
            fontSize: '20px',
            fontWeight: 700,
            outline: 'none',
            caretColor: COLORS.status.orange,
            transition: 'border-color 0.2s ease',
          }}
          onFocus={(e) => (e.target.style.borderColor = COLORS.primary.main)}
          onBlur={(e) => (e.target.style.borderColor = d ? COLORS.primary.main + '88' : '#3A3030')}
        />
      ))}
    </div>
  );
}

// ─── Orange primary button ────────────────────────────────────────────────────
function PrimaryButton({
  children, onClick, disabled, loading, type = 'button',
}: {
  children: React.ReactNode;
  onClick?: () => void;
  disabled?: boolean;
  loading?: boolean;
  type?: 'button' | 'submit';
}) {
  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled || loading}
      style={{
        width: '100%',
        padding: '11px 20px',
        background: disabled || loading
          ? 'rgba(249,115,22,0.4)'
          : 'linear-gradient(135deg, #F97316 0%, #EA580C 100%)',
        border: 'none',
        borderRadius: '8px',
        color: '#ffffff',
        fontFamily: "'Inter', sans-serif",
        fontSize: '14px',
        fontWeight: 700,
        letterSpacing: '0.06em',
        textTransform: 'uppercase',
        cursor: disabled || loading ? 'not-allowed' : 'pointer',
        transition: 'all 0.2s ease',
        boxShadow: disabled || loading ? 'none' : '0 4px 18px rgba(249,115,22,0.35)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        gap: '8px',
      }}
      onMouseEnter={(e) => {
        if (!disabled && !loading) {
          (e.currentTarget as HTMLButtonElement).style.transform = 'translateY(-1px)';
          (e.currentTarget as HTMLButtonElement).style.boxShadow = '0 6px 24px rgba(249,115,22,0.45)';
        }
      }}
      onMouseLeave={(e) => {
        (e.currentTarget as HTMLButtonElement).style.transform = 'translateY(0)';
        (e.currentTarget as HTMLButtonElement).style.boxShadow = disabled || loading ? 'none' : '0 4px 18px rgba(249,115,22,0.35)';
      }}
    >
      {loading && (
        <svg className="animate-spin" width="16" height="16" viewBox="0 0 24 24" fill="none">
          <circle cx="12" cy="12" r="10" stroke="rgba(255,255,255,0.3)" strokeWidth="3" />
          <path d="M12 2a10 10 0 0 1 10 10" stroke="#fff" strokeWidth="3" strokeLinecap="round" />
        </svg>
      )}
      {children}
    </button>
  );
}

// ─── Google button ────────────────────────────────────────────────────────────
function GoogleButton({ onClick, disabled }: { onClick: () => void; disabled?: boolean }) {
  return (
    <button
      type="button"
      onClick={onClick}
      disabled={disabled}
      style={{
        width: '100%',
        padding: '10px 20px',
        background: 'rgba(255,255,255,0.04)',
        border: '1px solid #3A3030',
        borderRadius: '8px',
        color: COLORS.text.primary,
        fontFamily: "'Inter', sans-serif",
        fontSize: '14px',
        fontWeight: 500,
        cursor: disabled ? 'not-allowed' : 'pointer',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        gap: '10px',
        transition: 'all 0.2s ease',
        opacity: disabled ? 0.5 : 1,
      }}
      onMouseEnter={(e) => {
        if (!disabled) {
          (e.currentTarget as HTMLButtonElement).style.background = 'rgba(255,255,255,0.08)';
          (e.currentTarget as HTMLButtonElement).style.borderColor = '#555';
        }
      }}
      onMouseLeave={(e) => {
        (e.currentTarget as HTMLButtonElement).style.background = 'rgba(255,255,255,0.04)';
        (e.currentTarget as HTMLButtonElement).style.borderColor = '#3A3030';
      }}
    >
      <GoogleIcon />
      Continue with Google
    </button>
  );
}

// ─── Error message ────────────────────────────────────────────────────────────
function ErrorMessage({ msg }: { msg: string }) {
  if (!msg) return null;
  return (
    <div
      style={{
        padding: '10px 14px',
        background: 'rgba(255,107,107,0.1)',
        border: '1px solid rgba(255,107,107,0.3)',
        borderRadius: '8px',
        color: '#FF8080',
        fontFamily: "'Inter', sans-serif",
        fontSize: '13px',
        display: 'flex',
        alignItems: 'center',
        gap: '8px',
      }}
    >
      <span style={{ fontSize: '15px' }}>⚠</span>
      {msg}
    </div>
  );
}

// ─── Divider ──────────────────────────────────────────────────────────────────
function Divider() {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
      <div style={{ flex: 1, height: '1px', background: '#2A2020' }} />
      <span style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: '10px', color: COLORS.text.muted, letterSpacing: '0.12em' }}>
        OR
      </span>
      <div style={{ flex: 1, height: '1px', background: '#2A2020' }} />
    </div>
  );
}

// ─── Sign In Form ─────────────────────────────────────────────────────────────
function SignInForm({ onSwitchToSignUp }: { onSwitchToSignUp: () => void }) {
  const { signIn, isLoaded, setActive } = useSignIn();
  const { signUp } = useSignUp();
  const [stage, setStage] = useState<SignInStage>('credentials');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPass, setShowPass] = useState(false);
  const [otp, setOtp] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleGoogleSignIn = async () => {
    if (!isLoaded || !signIn) return;
    setError('');
    try {
      await signIn.authenticateWithRedirect({
        strategy: 'oauth_google',
        redirectUrl: '/sso-callback',
        redirectUrlComplete: '/',
      });
    } catch (err: any) {
      setError(err?.errors?.[0]?.longMessage || 'Google sign-in failed. Please try again.');
    }
  };

  const handleEmailSignIn = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!isLoaded || !email || !password) return;
    setError('');
    setLoading(true);
    try {
      const result = await signIn.create({ identifier: email, password });
      if (result.status === 'complete') {
        await setActive({ session: result.createdSessionId });
        window.location.href = '/';
      } else if (result.status === 'needs_first_factor') {
        // Could need email code
        setStage('verify_email');
      } else {
        setError('Unexpected sign-in state. Please try again.');
      }
    } catch (err: any) {
      setError(err?.errors?.[0]?.longMessage || 'Invalid credentials. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleOtpVerify = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!isLoaded || otp.length < 6) return;
    setError('');
    setLoading(true);
    try {
      const result = await signIn.attemptFirstFactor({ strategy: 'email_code', code: otp });
      if (result.status === 'complete') {
        await setActive({ session: result.createdSessionId });
        window.location.href = '/';
      } else {
        setError('Verification incomplete. Please try again.');
      }
    } catch (err: any) {
      setError(err?.errors?.[0]?.longMessage || 'Invalid code. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (stage === 'verify_email') {
    return (
      <div className="flex flex-col gap-5">
        <div className="text-center">
          <div style={{ fontSize: '32px', marginBottom: '8px' }}>📧</div>
          <h2 style={{ fontFamily: "'Inter', sans-serif", fontSize: '18px', fontWeight: 700, color: COLORS.text.primary, margin: 0 }}>
            Check your email
          </h2>
          <p style={{ fontFamily: "'Inter', sans-serif", fontSize: '13px', color: COLORS.text.muted, marginTop: '6px' }}>
            We sent a 6-digit code to <strong style={{ color: COLORS.text.primary }}>{email}</strong>
          </p>
        </div>
        <ErrorMessage msg={error} />
        <OTPInput value={otp} onChange={setOtp} />
        <PrimaryButton onClick={handleOtpVerify as any} loading={loading} disabled={otp.length < 6}>
          Verify Code
        </PrimaryButton>
        <button
          type="button"
          onClick={() => { setStage('credentials'); setOtp(''); setError(''); }}
          style={{ background: 'none', border: 'none', color: COLORS.text.muted, fontFamily: "'Inter', sans-serif", fontSize: '13px', cursor: 'pointer' }}
        >
          ← Back to sign in
        </button>
      </div>
    );
  }

  return (
    <form onSubmit={handleEmailSignIn} className="flex flex-col gap-4">
      <ErrorMessage msg={error} />

      <GoogleButton onClick={handleGoogleSignIn} disabled={!isLoaded || loading} />

      <Divider />

      <InputField
        id="signin-email"
        label="Email Address"
        type="email"
        value={email}
        onChange={setEmail}
        placeholder="officer@ksp.gov.in"
        autoComplete="email"
        disabled={loading}
      />

      <InputField
        id="signin-password"
        label="Password"
        type={showPass ? 'text' : 'password'}
        value={password}
        onChange={setPassword}
        placeholder="••••••••"
        autoComplete="current-password"
        disabled={loading}
        suffix={
          <button
            type="button"
            onClick={() => setShowPass(!showPass)}
            style={{ background: 'none', border: 'none', cursor: 'pointer', color: COLORS.text.muted, display: 'flex', alignItems: 'center', padding: 0 }}
          >
            <EyeIcon open={showPass} />
          </button>
        }
      />

      <PrimaryButton type="submit" loading={loading} disabled={!isLoaded || !email || !password}>
        Sign In
      </PrimaryButton>

      <p style={{ textAlign: 'center', fontFamily: "'Inter', sans-serif", fontSize: '13px', color: COLORS.text.muted, margin: 0 }}>
        No account?{' '}
        <button
          type="button"
          onClick={onSwitchToSignUp}
          style={{ background: 'none', border: 'none', color: '#F97316', fontWeight: 600, cursor: 'pointer', fontSize: '13px', padding: 0 }}
        >
          Sign Up
        </button>
      </p>
    </form>
  );
}

// ─── Sign Up Form ─────────────────────────────────────────────────────────────
function SignUpForm({ onSwitchToSignIn }: { onSwitchToSignIn: () => void }) {
  const { signUp, isLoaded, setActive } = useSignUp();
  const { signIn } = useSignIn();
  const [stage, setStage] = useState<SignUpStage>('credentials');
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPass, setShowPass] = useState(false);
  const [otp, setOtp] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleGoogleSignUp = async () => {
    if (!isLoaded || !signUp) return;
    setError('');
    try {
      await signUp.authenticateWithRedirect({
        strategy: 'oauth_google',
        redirectUrl: '/sso-callback',
        redirectUrlComplete: '/',
      });
    } catch (err: any) {
      setError(err?.errors?.[0]?.longMessage || 'Google sign-up failed. Please try again.');
    }
  };

  const handleSignUp = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!isLoaded || !email || !password) return;
    setError('');
    setLoading(true);
    try {
      await signUp.create({ firstName, lastName, emailAddress: email, password });
      await signUp.prepareEmailAddressVerification({ strategy: 'email_code' });
      setStage('verify_email');
    } catch (err: any) {
      setError(err?.errors?.[0]?.longMessage || 'Registration failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleOtpVerify = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!isLoaded || otp.length < 6) return;
    setError('');
    setLoading(true);
    try {
      const result = await signUp.attemptEmailAddressVerification({ code: otp });
      if (result.status === 'complete') {
        await setActive({ session: result.createdSessionId });
        window.location.href = '/';
      } else {
        setError('Verification incomplete. Please try again.');
      }
    } catch (err: any) {
      setError(err?.errors?.[0]?.longMessage || 'Invalid code. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (stage === 'verify_email') {
    return (
      <div className="flex flex-col gap-5">
        <div className="text-center">
          <div style={{ fontSize: '32px', marginBottom: '8px' }}>📧</div>
          <h2 style={{ fontFamily: "'Inter', sans-serif", fontSize: '18px', fontWeight: 700, color: COLORS.text.primary, margin: 0 }}>
            Verify your email
          </h2>
          <p style={{ fontFamily: "'Inter', sans-serif", fontSize: '13px', color: COLORS.text.muted, marginTop: '6px' }}>
            We sent a 6-digit code to <strong style={{ color: COLORS.text.primary }}>{email}</strong>
          </p>
        </div>
        <ErrorMessage msg={error} />
        <OTPInput value={otp} onChange={setOtp} />
        <PrimaryButton onClick={handleOtpVerify as any} loading={loading} disabled={otp.length < 6}>
          Verify &amp; Create Account
        </PrimaryButton>
        <button
          type="button"
          onClick={() => { setStage('credentials'); setOtp(''); setError(''); }}
          style={{ background: 'none', border: 'none', color: COLORS.text.muted, fontFamily: "'Inter', sans-serif", fontSize: '13px', cursor: 'pointer' }}
        >
          ← Back
        </button>
      </div>
    );
  }

  return (
    <form onSubmit={handleSignUp} className="flex flex-col gap-4">
      <ErrorMessage msg={error} />

      <GoogleButton onClick={handleGoogleSignUp} disabled={!isLoaded || loading} />

      <Divider />

      <div className="flex gap-3">
        <InputField
          id="signup-first"
          label="First Name"
          type="text"
          value={firstName}
          onChange={setFirstName}
          placeholder="Arjun"
          autoComplete="given-name"
          disabled={loading}
        />
        <InputField
          id="signup-last"
          label="Last Name"
          type="text"
          value={lastName}
          onChange={setLastName}
          placeholder="Kumar"
          autoComplete="family-name"
          disabled={loading}
        />
      </div>

      <InputField
        id="signup-email"
        label="Email Address"
        type="email"
        value={email}
        onChange={setEmail}
        placeholder="officer@ksp.gov.in"
        autoComplete="email"
        disabled={loading}
      />

      <InputField
        id="signup-password"
        label="Password"
        type={showPass ? 'text' : 'password'}
        value={password}
        onChange={setPassword}
        placeholder="Min. 8 characters"
        autoComplete="new-password"
        disabled={loading}
        suffix={
          <button
            type="button"
            onClick={() => setShowPass(!showPass)}
            style={{ background: 'none', border: 'none', cursor: 'pointer', color: COLORS.text.muted, display: 'flex', alignItems: 'center', padding: 0 }}
          >
            <EyeIcon open={showPass} />
          </button>
        }
      />

      {/* Password strength bar */}
      {password.length > 0 && (
        <div style={{ display: 'flex', gap: '4px', alignItems: 'center' }}>
          {[1, 2, 3, 4].map((level) => {
            const strength = Math.min(
              Math.floor(password.length / 3) +
              (/[A-Z]/.test(password) ? 1 : 0) +
              (/[0-9]/.test(password) ? 1 : 0) +
              (/[^A-Za-z0-9]/.test(password) ? 1 : 0),
              4
            );
            const color = strength >= 4 ? '#22C55E' : strength >= 3 ? '#F97316' : strength >= 2 ? '#FBBF24' : '#EF4444';
            return (
              <div
                key={level}
                style={{
                  flex: 1, height: '3px', borderRadius: '2px',
                  background: level <= strength ? color : '#2A2020',
                  transition: 'background 0.3s ease',
                }}
              />
            );
          })}
          <span style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: '10px', color: COLORS.text.muted, marginLeft: '4px', minWidth: '40px' }}>
            {['', 'Weak', 'Fair', 'Good', 'Strong'][Math.min(
              Math.floor(password.length / 3) +
              (/[A-Z]/.test(password) ? 1 : 0) +
              (/[0-9]/.test(password) ? 1 : 0) +
              (/[^A-Za-z0-9]/.test(password) ? 1 : 0),
              4
            )]}
          </span>
        </div>
      )}

      <PrimaryButton type="submit" loading={loading} disabled={!isLoaded || !email || !password}>
        Create Account
      </PrimaryButton>

      <p style={{ textAlign: 'center', fontFamily: "'Inter', sans-serif", fontSize: '13px', color: COLORS.text.muted, margin: 0 }}>
        Already have access?{' '}
        <button
          type="button"
          onClick={onSwitchToSignIn}
          style={{ background: 'none', border: 'none', color: '#F97316', fontWeight: 600, cursor: 'pointer', fontSize: '13px', padding: 0 }}
        >
          Sign In
        </button>
      </p>
    </form>
  );
}

// ─── Main ClerkAuthPage ───────────────────────────────────────────────────────
export default function ClerkAuthPage() {
  const clerk = useClerk();
  const [mode, setMode] = useState<AuthMode>('signin');

  // Animate card in on mount
  const [mounted, setMounted] = useState(false);
  useEffect(() => { const t = setTimeout(() => setMounted(true), 60); return () => clearTimeout(t); }, []);

  // Grid hover glow — smooth trailing effect via rAF lerp
  const [glowPos, setGlowPos] = useState({ x: -999, y: -999 });
  const containerRef = useRef<HTMLDivElement>(null);
  const targetPos  = useRef({ x: -999, y: -999 });   // raw cursor target (no re-render)
  const currentPos = useRef({ x: -999, y: -999 });   // animated position
  const rafId      = useRef<number>(0);
  const isActive   = useRef(false);

  // lerp helper
  const lerp = (a: number, b: number, t: number) => a + (b - a) * t;

  // rAF loop — runs only while mouse is inside
  const startLoop = () => {
    const tick = () => {
      if (!isActive.current) return;

      const dx = targetPos.current.x - currentPos.current.x;
      const dy = targetPos.current.y - currentPos.current.y;

      // Only update state if moved more than half a pixel (avoid jitter)
      if (Math.abs(dx) > 0.5 || Math.abs(dy) > 0.5) {
        currentPos.current.x = lerp(currentPos.current.x, targetPos.current.x, 0.1);
        currentPos.current.y = lerp(currentPos.current.y, targetPos.current.y, 0.1);
        setGlowPos({ x: currentPos.current.x, y: currentPos.current.y });
      }

      rafId.current = requestAnimationFrame(tick);
    };
    rafId.current = requestAnimationFrame(tick);
  };

  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    const rect = containerRef.current?.getBoundingClientRect();
    if (!rect) return;
    targetPos.current = { x: e.clientX - rect.left, y: e.clientY - rect.top };

    // Kick off the loop on first move
    if (!isActive.current) {
      isActive.current = true;
      // Teleport current to target on first entry so trail starts from cursor
      currentPos.current = { ...targetPos.current };
      startLoop();
    }
  };

  const handleMouseLeave = () => {
    isActive.current = false;
    cancelAnimationFrame(rafId.current);
    // Fade out by moving target far off-screen
    targetPos.current  = { x: -999, y: -999 };
    currentPos.current = { x: -999, y: -999 };
    setGlowPos({ x: -999, y: -999 });
  };

  // Cleanup rAF on unmount
  useEffect(() => () => cancelAnimationFrame(rafId.current), []);

  return (
    <div
      ref={containerRef}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      style={{
        position: 'relative',
        display: 'flex',
        height: '100vh',
        width: '100%',
        alignItems: 'center',
        justifyContent: 'center',
        overflow: 'hidden',
        backgroundColor: '#0B0909',
        backgroundImage: `
          linear-gradient(rgba(180, 225, 235, 0.06) 1px, transparent 1px),
          linear-gradient(90deg, rgba(180, 225, 235, 0.06) 1px, transparent 1px)
        `,
        backgroundSize: '32px 32px',
      }}
    >
      {/* Grid cursor glow */}
      <div
        style={{
          position: 'absolute', inset: 0, pointerEvents: 'none', zIndex: 1,
          backgroundImage: `
            linear-gradient(rgba(180, 225, 235, 0.55) 1px, transparent 1px),
            linear-gradient(90deg, rgba(180, 225, 235, 0.55) 1px, transparent 1px)
          `,
          backgroundSize: '32px 32px',
          WebkitMaskImage: `radial-gradient(circle 120px at ${glowPos.x}px ${glowPos.y}px, black 0%, transparent 100%)`,
          maskImage: `radial-gradient(circle 120px at ${glowPos.x}px ${glowPos.y}px, black 0%, transparent 100%)`,
          transition: 'opacity 0.15s ease',
        }}
      />
      {/* Map background */}
      <MapDecoration />

      {/* Radial vignette */}
      <div
        style={{
          position: 'absolute', inset: 0, pointerEvents: 'none',
          background: 'radial-gradient(ellipse 75% 75% at 50% 50%, transparent 25%, rgba(11,9,9,0.8) 100%)',
        }}
      />

      {/* Scan-line texture */}
      <div
        style={{
          position: 'absolute', inset: 0, pointerEvents: 'none',
          backgroundImage: 'repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(180,225,235,0.012) 2px, rgba(180,225,235,0.012) 4px)',
        }}
      />

      {/* Status indicator — top left */}
      <div
        style={{
          position: 'absolute', top: '24px', left: '32px', zIndex: 20,
          display: 'flex', alignItems: 'center', gap: '8px',
          fontFamily: "'JetBrains Mono', monospace", fontSize: '10px',
          color: COLORS.text.muted, letterSpacing: '0.15em',
        }}
      >
        <span
          style={{
            display: 'inline-block', width: '6px', height: '6px', borderRadius: '50%',
            backgroundColor: COLORS.primary.main,
            boxShadow: `0 0 8px ${COLORS.primary.main}`,
            animation: 'pulse 2s ease-in-out infinite',
          }}
        />
        SYS.AUTH.ACTIVE
      </div>

      {/* Version — top right */}
      <div
        style={{
          position: 'absolute', top: '24px', right: '32px', zIndex: 20,
          fontFamily: "'JetBrains Mono', monospace", fontSize: '10px',
          color: COLORS.text.muted, opacity: 0.4, letterSpacing: '0.12em',
        }}
      >
        PRISM v2.0
      </div>

      {/* Coordinates — bottom left */}
      <div
        style={{
          position: 'absolute', bottom: '24px', left: '32px', zIndex: 20,
          display: 'flex', flexDirection: 'column', gap: '4px', opacity: 0.35,
          fontFamily: "'JetBrains Mono', monospace", fontSize: '10px', color: COLORS.text.muted,
        }}
      >
        <span>SEC-A // GRID: 12.9716°N, 77.5946°E</span>
        <span>DATA FEED: ENCRYPTED // TIER-1</span>
      </div>

      {/* ── Main Card ── */}
      <div
        style={{
          position: 'relative', zIndex: 20,
          width: '100%', maxWidth: '440px', margin: '0 16px',
          background: 'rgba(18, 14, 14, 0.88)',
          backdropFilter: 'blur(28px)', WebkitBackdropFilter: 'blur(28px)',
          border: `1px solid rgba(180, 225, 235, 0.15)`,
          borderRadius: '18px',
          boxShadow: `
            0 0 0 1px rgba(180,225,235,0.04),
            0 40px 80px rgba(0,0,0,0.75),
            0 0 100px rgba(180,225,235,0.03) inset
          `,
          opacity: mounted ? 1 : 0,
          transform: mounted ? 'translateY(0)' : 'translateY(16px)',
          transition: 'opacity 0.4s ease, transform 0.4s ease',
          maxHeight: '92vh',
          overflowY: 'auto',
        }}
      >
        {/* Top accent line */}
        <div
          style={{
            height: '2px',
            background: `linear-gradient(90deg, transparent, ${COLORS.primary.main}99, transparent)`,
            borderRadius: '18px 18px 0 0',
          }}
        />

        <div style={{ padding: '28px 32px 32px' }}>
          {/* ── Branding ── */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '24px' }}>
            <img src="/logo.svg" alt="PRISM Logo" style={{ height: '36px', width: '36px', objectFit: 'contain' }} />
            <div>
              <div style={{
                fontFamily: "'JetBrains Mono', monospace", fontSize: '21px', fontWeight: 700,
                color: COLORS.text.primary, letterSpacing: '0.06em', lineHeight: 1,
              }}>
                PRISM
              </div>
              <div style={{
                fontFamily: "'JetBrains Mono', monospace", fontSize: '10px',
                color: COLORS.text.muted, letterSpacing: '0.1em', marginTop: '3px',
              }}>
                Crime Intelligence & Analytics Platform
              </div>
            </div>
          </div>

          {/* ── Tab toggle ── */}
          <div
            style={{
              display: 'flex', marginBottom: '24px',
              background: 'rgba(255,255,255,0.03)',
              border: '1px solid #241C1C',
              borderRadius: '10px', padding: '4px', gap: '4px',
            }}
          >
            {(['signin', 'signup'] as AuthMode[]).map((m) => (
              <button
                key={m}
                type="button"
                onClick={() => setMode(m)}
                style={{
                  flex: 1, padding: '8px 16px', borderRadius: '7px',
                  fontFamily: "'Inter', sans-serif", fontSize: '13px', fontWeight: 600,
                  letterSpacing: '0.04em', border: 'none', cursor: 'pointer',
                  transition: 'all 0.22s ease',
                  ...(mode === m
                    ? {
                        background: 'linear-gradient(135deg, #F97316 0%, #EA580C 100%)',
                        color: '#ffffff',
                        boxShadow: '0 2px 14px rgba(249,115,22,0.4)',
                      }
                    : {
                        background: 'transparent',
                        color: COLORS.text.muted,
                      }),
                }}
              >
                {m === 'signin' ? 'Sign In' : 'Sign Up'}
              </button>
            ))}
          </div>

          {/* ── Form area ── */}
          <div
            style={{
              opacity: 1,
              transition: 'opacity 0.2s ease',
            }}
          >
            {mode === 'signin' ? (
              <SignInForm onSwitchToSignUp={() => setMode('signup')} />
            ) : (
              <SignUpForm onSwitchToSignIn={() => setMode('signin')} />
            )}
          </div>

          {/* ── Footer ── */}
          <div
            style={{
              marginTop: '24px', paddingTop: '18px',
              borderTop: '1px solid rgba(255,255,255,0.05)',
              textAlign: 'center',
            }}
          >
            <p style={{
              fontFamily: "'JetBrains Mono', monospace", fontSize: '10px',
              color: COLORS.text.muted, letterSpacing: '0.08em', opacity: 0.6, margin: 0,
            }}>
              Karnataka State Police — Authorized Personnel Only
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
