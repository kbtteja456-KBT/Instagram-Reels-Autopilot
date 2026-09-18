import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { KeyIcon, CheckCircleIcon } from './Icons';

interface ApiKeyVaultModalProps {
  isOpen: boolean;
  onClose: () => void;
  onKeysUpdated?: () => void;
}

export const ApiKeyVaultModal: React.FC<ApiKeyVaultModalProps> = ({ isOpen, onClose, onKeysUpdated }) => {
  const [activeProvider, setActiveProvider] = useState<'meta' | 'openrouter' | 'pexels' | 'groq'>('meta');
  const [metaAppId, setMetaAppId] = useState('');
  const [metaAppSecret, setMetaAppSecret] = useState('');
  const [openRouterKey, setOpenRouterKey] = useState('');
  const [pexelsKey, setPexelsKey] = useState('');
  const [groqKey, setGroqKey] = useState('');
  const [isSaving, setIsSaving] = useState(false);
  const [statusMsg, setStatusMsg] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  useEffect(() => {
    if (isOpen) {
      api.vault.get().then((res) => {
        if (res && res.keys) {
          if (res.keys.meta_app_id) setMetaAppId(res.keys.meta_app_id);
          if (res.keys.openrouter_api_key) setOpenRouterKey(res.keys.openrouter_api_key);
          if (res.keys.pexels_api_key) setPexelsKey(res.keys.pexels_api_key);
          if (res.keys.groq_api_key) setGroqKey(res.keys.groq_api_key);
        }
      }).catch(console.error);
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSaving(true);
    setStatusMsg(null);

    try {
      await api.vault.save({
        meta_app_id: metaAppId.trim() || undefined,
        meta_app_secret: metaAppSecret.trim() || undefined,
        openrouter_api_key: openRouterKey.trim() || undefined,
        pexels_api_key: pexelsKey.trim() || undefined,
        groq_api_key: groqKey.trim() || undefined
      });
      setStatusMsg({ type: 'success', text: 'AES-256 Vault updated successfully!' });
      if (onKeysUpdated) onKeysUpdated();
    } catch (err: any) {
      setStatusMsg({ type: 'error', text: err.message || 'Failed to save keys to vault.' });
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      background: 'rgba(5, 7, 10, 0.85)',
      backdropFilter: 'blur(16px)',
      WebkitBackdropFilter: 'blur(16px)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 9999,
      padding: '20px'
    }}>
      <div style={{
        width: '100%',
        maxWidth: '620px',
        maxHeight: '90vh',
        overflowY: 'auto',
        background: 'rgba(15, 20, 28, 0.95)',
        border: '1px solid rgba(245, 158, 11, 0.3)',
        borderRadius: '24px',
        boxShadow: '0 24px 64px rgba(0, 0, 0, 0.85), 0 0 32px rgba(225, 48, 108, 0.15)',
        padding: '32px',
        position: 'relative'
      }}>
        {/* Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <div style={{
              width: '42px',
              height: '42px',
              borderRadius: '12px',
              background: 'linear-gradient(135deg, rgba(245, 158, 11, 0.2), rgba(225, 48, 108, 0.2))',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#f59e0b'
            }}>
              <KeyIcon size={22} />
            </div>
            <div>
              <h2 style={{ fontSize: '1.25rem', fontWeight: 700, margin: 0, color: '#f8fafc' }}>
                API Key &amp; Meta Credentials Vault (BYOK)
              </h2>
              <p style={{ fontSize: '0.8125rem', color: 'var(--text-secondary)', margin: 0 }}>
                Encrypted at rest with AES-256 Fernet. Used exclusively for autonomous rendering.
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            style={{
              background: 'transparent',
              border: 'none',
              color: 'var(--text-muted)',
              fontSize: '1.5rem',
              cursor: 'pointer',
              lineHeight: 1
            }}
          >
            &times;
          </button>
        </div>

        {/* Provider Tabs */}
        <div style={{ display: 'flex', gap: '8px', marginBottom: '20px', overflowX: 'auto' }}>
          {[
            { id: 'meta', label: 'Meta Graph API' },
            { id: 'openrouter', label: 'OpenRouter (LLM)' },
            { id: 'groq', label: 'Groq (Llama 3.3)' },
            { id: 'pexels', label: 'Pexels (B-Roll)' }
          ].map((tab) => {
            const isSelected = activeProvider === tab.id;
            return (
              <button
                key={tab.id}
                type="button"
                onClick={() => { setActiveProvider(tab.id as any); setStatusMsg(null); }}
                style={{
                  padding: '10px 16px',
                  borderRadius: '12px',
                  border: isSelected ? '1px solid rgba(245, 158, 11, 0.5)' : '1px solid rgba(255, 255, 255, 0.08)',
                  background: isSelected ? 'rgba(245, 158, 11, 0.15)' : 'rgba(24, 29, 40, 0.6)',
                  color: isSelected ? '#f59e0b' : 'var(--text-secondary)',
                  fontWeight: 600,
                  fontSize: '0.8125rem',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px'
                }}
              >
                {isSelected && <CheckCircleIcon size={14} color="#10b981" />}
                {tab.label}
              </button>
            );
          })}
        </div>

        {/* Status Message */}
        {statusMsg && (
          <div style={{
            padding: '10px 14px',
            borderRadius: '10px',
            background: statusMsg.type === 'success' ? 'rgba(16, 185, 129, 0.15)' : 'rgba(239, 68, 68, 0.15)',
            border: `1px solid ${statusMsg.type === 'success' ? 'rgba(16, 185, 129, 0.3)' : 'rgba(239, 68, 68, 0.3)'}`,
            color: statusMsg.type === 'success' ? 'var(--accent-mint)' : '#f87171',
            fontSize: '13px',
            marginBottom: '18px'
          }}>
            {statusMsg.text}
          </div>
        )}

        <form onSubmit={handleSave} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {activeProvider === 'meta' && (
            <>
              <div>
                <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, color: '#cbd5e1', marginBottom: '6px' }}>
                  Meta App ID (Client ID)
                </label>
                <input
                  type="text"
                  value={metaAppId}
                  onChange={(e) => setMetaAppId(e.target.value)}
                  placeholder="e.g. 1048123456789"
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
                  Meta App Secret
                </label>
                <input
                  type="password"
                  value={metaAppSecret}
                  onChange={(e) => setMetaAppSecret(e.target.value)}
                  placeholder="••••••••••••••••••••••••••••••••"
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
            </>
          )}

          {activeProvider === 'openrouter' && (
            <div>
              <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, color: '#cbd5e1', marginBottom: '6px' }}>
                OpenRouter API Key (Optional Override)
              </label>
              <input
                type="password"
                value={openRouterKey}
                onChange={(e) => setOpenRouterKey(e.target.value)}
                placeholder="sk-or-v1-..."
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
              <p style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '4px' }}>
                When Zero-Cost Mode is enabled, free OpenRouter models are utilized at ₹0 cost.
              </p>
            </div>
          )}

          {activeProvider === 'groq' && (
            <div>
              <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, color: '#cbd5e1', marginBottom: '6px' }}>
                Groq Cloud API Key
              </label>
              <input
                type="password"
                value={groqKey}
                onChange={(e) => setGroqKey(e.target.value)}
                placeholder="gsk_..."
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

          {activeProvider === 'pexels' && (
            <div>
              <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, color: '#cbd5e1', marginBottom: '6px' }}>
                Pexels API Key
              </label>
              <input
                type="password"
                value={pexelsKey}
                onChange={(e) => setPexelsKey(e.target.value)}
                placeholder="Optional stock video API key"
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

          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '12px', marginTop: '12px' }}>
            <button
              type="button"
              className="btn btn-secondary"
              onClick={onClose}
            >
              Close
            </button>
            <button
              type="submit"
              className="btn btn-primary"
              disabled={isSaving}
            >
              {isSaving ? 'Encrypting & Storing...' : 'Save to Encrypted Vault'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
