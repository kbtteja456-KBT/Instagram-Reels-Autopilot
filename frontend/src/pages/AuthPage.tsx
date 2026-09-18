import React, { useState } from 'react';
import { api, UserProfile, WorkspaceContext } from '../services/api';

interface AuthPageProps {
  onAuthenticated: (user: UserProfile, workspace: WorkspaceContext) => void;
  onBack?: () => void;
}

export const AuthPage: React.FC<AuthPageProps> = ({ onAuthenticated, onBack }) => {
  const [isRegister, setIsRegister] = useState<boolean>(false);
  const [email, setEmail] = useState<string>('');
  const [password, setPassword] = useState<string>('');
  const [fullName, setFullName] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      if (isRegister) {
        const res = await api.register(email, password, fullName || undefined);
        onAuthenticated(res.user, res.workspace);
      } else {
        const res = await api.login(email, password);
        onAuthenticated(res.user, res.workspace);
      }
    } catch (err: any) {
      setError(err.message || 'Authentication failed. Please check your credentials.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page-wrapper" style={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      position: 'relative',
      zIndex: 10,
      padding: '24px'
    }}>
      <div className="auth-card" style={{
        width: '100%',
        maxWidth: '460px',
        background: 'rgba(15, 20, 28, 0.85)',
        backdropFilter: 'blur(20px)',
        WebkitBackdropFilter: 'blur(20px)',
        borderRadius: '24px',
        border: '1px solid rgba(245, 158, 11, 0.25)',
        boxShadow: '0 24px 64px -12px rgba(0, 0, 0, 0.85), 0 0 32px -4px rgba(225, 48, 108, 0.2)',
        padding: '36px',
        position: 'relative',
        overflow: 'hidden'
      }}>
        {onBack && (
          <button
            onClick={onBack}
            style={{
              background: 'none',
              border: 'none',
              color: '#8b949e',
              cursor: 'pointer',
              fontSize: '13px',
              padding: '0 0 16px 0',
              display: 'flex',
              alignItems: 'center',
              gap: '6px'
            }}
          >
            ← Back to Home
          </button>
        )}

        {/* Subtle Ambient Light Gradient */}
        <div style={{
          position: 'absolute',
          top: '-120px',
          right: '-120px',
          width: '240px',
          height: '240px',
          background: 'radial-gradient(circle, rgba(225, 48, 108, 0.2) 0%, transparent 70%)',
          pointerEvents: 'none'
        }} />

        {/* Brand Header */}
        <div style={{ textAlign: 'center', marginBottom: '28px' }}>
          <div style={{
            width: '56px',
            height: '56px',
            margin: '0 auto 16px auto',
            borderRadius: '16px',
            background: 'linear-gradient(135deg, #833ab4 0%, #fd1d1d 50%, #fcb045 100%)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 0 20px rgba(225, 48, 108, 0.4)',
            border: '1px solid rgba(245, 158, 11, 0.3)'
          }}>
            <svg width="28" height="28" viewBox="0 0 24 24" fill="#ffffff">
              <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/>
            </svg>
          </div>
          <h2 style={{
            fontFamily: "'Outfit', sans-serif",
            fontSize: '24px',
            fontWeight: 800,
            letterSpacing: '-0.5px',
            color: '#ffffff',
            margin: '0 0 6px 0'
          }}>
            {isRegister ? 'Create Your Workspace' : 'Welcome to Autopilot'}
          </h2>
          <p style={{
            fontSize: '13px',
            color: '#94a3b8',
            margin: 0
          }}>
            {isRegister
              ? 'Set up autonomous 9:16 Reels publishing'
              : 'Sign in to access your autonomous publishing pipeline'}
          </p>
        </div>

        {/* Auth Mode Toggle Tabs */}
        <div style={{
          display: 'flex',
          background: 'rgba(10, 14, 26, 0.6)',
          borderRadius: '12px',
          padding: '4px',
          marginBottom: '24px',
          border: '1px solid rgba(255, 255, 255, 0.08)'
        }}>
          <button
            type="button"
            onClick={() => { setIsRegister(false); setError(null); }}
            style={{
              flex: 1,
              padding: '8px 0',
              borderRadius: '8px',
              border: 'none',
              background: !isRegister ? 'linear-gradient(135deg, rgba(245, 158, 11, 0.2), rgba(225, 48, 108, 0.2))' : 'transparent',
              color: !isRegister ? '#ffffff' : '#8b949e',
              fontWeight: 700,
              fontSize: '13px',
              cursor: 'pointer',
              transition: 'all 0.2s',
              borderBottom: !isRegister ? '2px solid #f59e0b' : 'none'
            }}
          >
            Sign In
          </button>
          <button
            type="button"
            onClick={() => { setIsRegister(true); setError(null); }}
            style={{
              flex: 1,
              padding: '8px 0',
              borderRadius: '8px',
              border: 'none',
              background: isRegister ? 'linear-gradient(135deg, rgba(245, 158, 11, 0.2), rgba(225, 48, 108, 0.2))' : 'transparent',
              color: isRegister ? '#ffffff' : '#8b949e',
              fontWeight: 700,
              fontSize: '13px',
              cursor: 'pointer',
              transition: 'all 0.2s',
              borderBottom: isRegister ? '2px solid #e1306c' : 'none'
            }}
          >
            Create Workspace
          </button>
        </div>

        {/* Error Alert */}
        {error && (
          <div style={{
            padding: '10px 14px',
            borderRadius: '10px',
            background: 'rgba(239, 68, 68, 0.12)',
            border: '1px solid rgba(239, 68, 68, 0.3)',
            color: '#f87171',
            fontSize: '13px',
            marginBottom: '18px'
          }}>
            ⚠️ {error}
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {isRegister && (
            <div>
              <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, color: '#cbd5e1', marginBottom: '6px' }}>
                Full Name or Studio Name
              </label>
              <input
                type="text"
                required
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                placeholder="e.g. Alex Creator"
                style={{
                  width: '100%',
                  boxSizing: 'border-box',
                  padding: '11px 14px',
                  borderRadius: '10px',
                  background: 'rgba(10, 14, 26, 0.8)',
                  border: '1px solid rgba(245, 158, 11, 0.2)',
                  color: '#ffffff',
                  fontSize: '14px',
                  outline: 'none'
                }}
              />
            </div>
          )}

          <div>
            <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, color: '#cbd5e1', marginBottom: '6px' }}>
              Email Address
            </label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@creator.com"
              style={{
                width: '100%',
                boxSizing: 'border-box',
                padding: '11px 14px',
                borderRadius: '10px',
                background: 'rgba(10, 14, 26, 0.8)',
                border: '1px solid rgba(245, 158, 11, 0.2)',
                color: '#ffffff',
                fontSize: '14px',
                outline: 'none'
              }}
            />
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, color: '#cbd5e1', marginBottom: '6px' }}>
              Password
            </label>
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••••••"
              style={{
                width: '100%',
                boxSizing: 'border-box',
                padding: '11px 14px',
                borderRadius: '10px',
                background: 'rgba(10, 14, 26, 0.8)',
                border: '1px solid rgba(245, 158, 11, 0.2)',
                color: '#ffffff',
                fontSize: '14px',
                outline: 'none'
              }}
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            style={{
              marginTop: '8px',
              padding: '13px',
              borderRadius: '12px',
              border: 'none',
              background: 'linear-gradient(135deg, #f59e0b 0%, #e1306c 50%, #833ab4 100%)',
              color: '#ffffff',
              fontWeight: 800,
              fontSize: '14px',
              cursor: loading ? 'not-allowed' : 'pointer',
              opacity: loading ? 0.7 : 1,
              boxShadow: '0 6px 20px rgba(225, 48, 108, 0.4)',
              transition: 'transform 0.15s, box-shadow 0.15s'
            }}
          >
            {loading ? 'Authenticating...' : isRegister ? 'Launch Studio & Generate' : 'Sign In to Workspace ⚡'}
          </button>
        </form>

        <div style={{ marginTop: '20px', textAlign: 'center', fontSize: '12px', color: '#64748b' }}>
          By continuing, you agree to our{' '}
          <a href="/terms" style={{ color: '#fbbf24', textDecoration: 'none' }}>Terms</a> and{' '}
          <a href="/privacy" style={{ color: '#fbbf24', textDecoration: 'none' }}>Privacy Policy</a>.
        </div>
      </div>
    </div>
  );
};
