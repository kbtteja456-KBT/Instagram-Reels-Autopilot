import React, { useState, useEffect } from 'react';
import { api } from '../services/api';

interface SettingsPageProps {
  onDisconnectInstagram?: () => void;
}

export const SettingsPage: React.FC<SettingsPageProps> = ({ onDisconnectInstagram }) => {
  const [settings, setSettings] = useState<any>(null);
  const [saving, setSaving] = useState(false);
  const [statusMsg, setStatusMsg] = useState<string | null>(null);

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      const data = await api.settings.get();
      setSettings(data || {
        zero_cost_mode: true,
        timezone: 'Asia/Kolkata',
        slot1_time: '07:00',
        slot2_time: '18:00',
        daily_reel_limit: 2,
        public_media_base_url: 'http://localhost:8000',
        niche: 'AI, Tech & Modern Engineering',
        custom_content_prompt: '',
        default_duration_sec: 45,
        preferred_format: 'auto',
        target_audience: 'Creators, Tech Enthusiasts & Students'
      });
    } catch (e) {
      console.error(e);
      setSettings({
        zero_cost_mode: true,
        timezone: 'Asia/Kolkata',
        slot1_time: '07:00',
        slot2_time: '18:00',
        daily_reel_limit: 2,
        public_media_base_url: 'http://localhost:8000',
        niche: 'AI, Tech & Modern Engineering',
        custom_content_prompt: '',
        default_duration_sec: 45,
        preferred_format: 'auto',
        target_audience: 'Creators, Tech Enthusiasts & Students'
      });
    }
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setStatusMsg(null);
    try {
      await api.settings.update(settings);
      setStatusMsg('Settings successfully updated!');
    } catch (err: any) {
      setStatusMsg(`Error: ${err.message || 'Failed to save'}`);
    } finally {
      setSaving(false);
    }
  };

  if (!settings) {
    return (
      <div className="page-body">
        <p>Loading settings...</p>
      </div>
    );
  }

  return (
    <div className="page-body">
      <div>
        <h2 style={{ fontFamily: 'var(--font-display)', fontSize: '22px', fontWeight: 700 }}>System &amp; Instagram Settings</h2>
        <p style={{ color: 'var(--text-muted)', fontSize: '14px' }}>
          Configure autonomous publishing rules, Zero-Cost Mode, Meta Media Ingestion URL, and AI models.
        </p>
      </div>

      <form onSubmit={handleSave} style={{ display: 'flex', flexDirection: 'column', gap: '20px', maxWidth: '760px' }}>
        {/* Zero-Cost Mode */}
        <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <h3 style={{ fontSize: '16px', fontWeight: 700 }}>Zero-Cost Hard Mode</h3>
          <p style={{ color: 'var(--text-secondary)', fontSize: '13px' }}>
            When enabled, all paid API calls (paid LLM models, paid TTS, paid stock footage) are blocked outright. Video generation operates 100% free via Edge-TTS, DuckDuckGo research, and Free OpenRouter/Groq.
          </p>
          <label style={{ display: 'flex', alignItems: 'center', gap: '10px', cursor: 'pointer' }}>
            <input
              type="checkbox"
              checked={Boolean(settings.zero_cost_mode)}
              onChange={(e) => setSettings({ ...settings, zero_cost_mode: e.target.checked })}
              style={{ width: '18px', height: '18px', accentColor: 'var(--accent-amber)' }}
            />
            <span style={{ fontWeight: 600, color: settings.zero_cost_mode ? 'var(--accent-mint)' : 'var(--text-secondary)' }}>
              Enable Zero-Cost Mode (₹0 Guarantee)
            </span>
          </label>
        </div>

        {/* Schedule & Timezone */}
        <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <h3 style={{ fontSize: '16px', fontWeight: 700 }}>Publishing Schedule &amp; Timezone</h3>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px' }}>
            <div>
              <label style={{ fontSize: '12px', color: 'var(--text-muted)', display: 'block', marginBottom: '6px' }}>
                Slot 1 (Morning)
              </label>
              <input
                type="text"
                value={settings.slot1_time || '07:00'}
                onChange={(e) =>
                  setSettings({
                    ...settings,
                    slot1_time: e.target.value
                  })
                }
                style={{ width: '100%', padding: '10px 12px', background: 'rgba(0,0,0,0.3)', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-sm)', color: '#fff', fontSize: '14px' }}
              />
            </div>
            <div>
              <label style={{ fontSize: '12px', color: 'var(--text-muted)', display: 'block', marginBottom: '6px' }}>
                Slot 2 (Evening)
              </label>
              <input
                type="text"
                value={settings.slot2_time || '18:00'}
                onChange={(e) =>
                  setSettings({
                    ...settings,
                    slot2_time: e.target.value
                  })
                }
                style={{ width: '100%', padding: '10px 12px', background: 'rgba(0,0,0,0.3)', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-sm)', color: '#fff', fontSize: '14px' }}
              />
            </div>
          </div>
          <div>
            <label style={{ fontSize: '12px', color: 'var(--text-muted)', display: 'block', marginBottom: '6px' }}>
              Timezone
            </label>
            <input
              type="text"
              value={settings.timezone || 'Asia/Kolkata'}
              onChange={(e) =>
                setSettings({
                  ...settings,
                  timezone: e.target.value
                })
              }
              style={{ width: '100%', padding: '10px 12px', background: 'rgba(0,0,0,0.3)', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-sm)', color: '#fff', fontSize: '14px' }}
            />
          </div>
        </div>

        {/* Meta Media Ingestion URL */}
        <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
          <div>
            <h3 style={{ fontSize: '16px', fontWeight: 700, marginBottom: '4px' }}>Meta Media Ingestion URL</h3>
            <p style={{ color: 'var(--text-secondary)', fontSize: '13px', margin: 0 }}>
              Meta's servers require a publicly accessible URL to download rendered Reels for container creation via the Content Publishing API. When testing locally, provide an ngrok or Cloudflare tunnel URL.
            </p>
          </div>
          <input
            type="text"
            value={settings.public_media_base_url || 'http://localhost:8000'}
            placeholder="e.g. https://your-tunnel.ngrok-free.app"
            onChange={(e) => setSettings({ ...settings, public_media_base_url: e.target.value })}
            style={{ width: '100%', padding: '10px 12px', background: 'rgba(0,0,0,0.3)', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-sm)', color: '#fff', fontSize: '14px' }}
          />
        </div>

        {/* Content & Concept Guidelines */}
        <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: '18px' }}>
          <div>
            <h3 style={{ fontSize: '16px', fontWeight: 700, marginBottom: '4px' }}>Content, Concept &amp; Duration Configuration</h3>
            <p style={{ color: 'var(--text-secondary)', fontSize: '13px', margin: 0 }}>
              Specify your niche, custom topic guidelines, video duration, and preferred visual format for automated Reel synthesis.
            </p>
          </div>

          <div>
            <label style={{ fontSize: '13px', fontWeight: 600, color: '#f8fafc', display: 'block', marginBottom: '6px' }}>
              Primary Instagram Niche
            </label>
            <input
              type="text"
              value={settings.niche || ''}
              placeholder="e.g. AI & Tech News, Python Coding, Entrepreneurship, Stoic Philosophy"
              onChange={(e) => setSettings({ ...settings, niche: e.target.value })}
              style={{ width: '100%', padding: '10px 12px', background: 'rgba(0,0,0,0.3)', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-sm)', color: '#fff', fontSize: '14px' }}
            />
          </div>

          <div>
            <label style={{ fontSize: '13px', fontWeight: 600, color: '#f8fafc', display: 'block', marginBottom: '6px' }}>
              Custom Topic &amp; Script Guidelines
            </label>
            <p style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '8px' }}>
              Enter prompt notes, article summary, or instructions. The agent pipeline will synthesize script, kinetic captions, and visuals aligned with this.
            </p>
            <textarea
              rows={4}
              value={settings.custom_content_prompt || ''}
              placeholder="e.g. Focus on high-retention technical tips for software engineers, explain architecture concepts clearly with safe-zone captions..."
              onChange={(e) => setSettings({ ...settings, custom_content_prompt: e.target.value })}
              style={{
                width: '100%',
                boxSizing: 'border-box',
                padding: '12px',
                background: 'rgba(0,0,0,0.3)',
                border: '1px solid var(--border-subtle)',
                borderRadius: 'var(--radius-sm)',
                color: '#fff',
                fontSize: '13.5px',
                lineHeight: 1.5,
                resize: 'vertical',
                fontFamily: 'inherit'
              }}
            />
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
            <div>
              <label style={{ fontSize: '13px', fontWeight: 600, color: '#f8fafc', display: 'block', marginBottom: '6px' }}>
                Reel Duration
              </label>
              <div style={{ display: 'flex', gap: '8px' }}>
                {[30, 45, 60].map((sec) => (
                  <button
                    type="button"
                    key={sec}
                    onClick={() => setSettings({ ...settings, default_duration_sec: sec })}
                    style={{
                      flex: 1,
                      padding: '8px 0',
                      borderRadius: '8px',
                      background: (settings.default_duration_sec || 45) === sec ? '#e1306c' : 'rgba(0,0,0,0.3)',
                      border: `1px solid ${(settings.default_duration_sec || 45) === sec ? '#fd1d1d' : 'var(--border-subtle)'}`,
                      color: '#ffffff',
                      fontSize: '13px',
                      fontWeight: 600,
                      cursor: 'pointer'
                    }}
                  >
                    {sec}s
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label style={{ fontSize: '13px', fontWeight: 600, color: '#f8fafc', display: 'block', marginBottom: '6px' }}>
                Preferred Visual Format
              </label>
              <select
                value={settings.preferred_format || 'auto'}
                onChange={(e) => setSettings({ ...settings, preferred_format: e.target.value })}
                style={{
                  width: '100%',
                  padding: '9px 12px',
                  background: '#1e293b',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: 'var(--radius-sm)',
                  color: '#fff',
                  fontSize: '13px',
                  cursor: 'pointer',
                  outline: 'none'
                }}
              >
                <option value="auto">✨ Auto-Detect from Topic</option>
                <option value="documentary">📹 Motion B-Roll &amp; Kinetic Safe-Zone Subtitles</option>
                <option value="quiz_card">💻 Interactive Code Quiz Card</option>
                <option value="quote_card">🏛️ High-Impact Quote Card</option>
                <option value="trivia_quiz">🧠 Trivia &amp; Brain Teaser</option>
              </select>
            </div>
          </div>

          <div>
            <label style={{ fontSize: '13px', fontWeight: 600, color: '#f8fafc', display: 'block', marginBottom: '6px' }}>
              Target Audience Persona
            </label>
            <input
              type="text"
              value={settings.target_audience || ''}
              placeholder="e.g. Software Developers, Content Creators, Students"
              onChange={(e) => setSettings({ ...settings, target_audience: e.target.value })}
              style={{ width: '100%', padding: '10px 12px', background: 'rgba(0,0,0,0.3)', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-sm)', color: '#fff', fontSize: '14px' }}
            />
          </div>
        </div>

        {onDisconnectInstagram && (
          <div className="card" style={{ borderLeft: '4px solid var(--accent-rose)' }}>
            <h3 style={{ fontSize: '16px', fontWeight: 700, color: '#f87171', marginBottom: '6px' }}>Disconnect Instagram Account</h3>
            <p style={{ color: 'var(--text-secondary)', fontSize: '13px', marginBottom: '14px' }}>
              Disconnecting your account revokes and immediately purges all encrypted Meta access tokens from the database.
            </p>
            <button
              type="button"
              className="btn btn-secondary"
              onClick={onDisconnectInstagram}
              style={{ borderColor: 'rgba(239, 68, 68, 0.4)', color: '#f87171' }}
            >
              Disconnect Instagram Account
            </button>
          </div>
        )}

        <div>
          <button type="submit" className="btn btn-primary" disabled={saving}>
            {saving ? 'Saving...' : 'Save Configuration'}
          </button>
          {statusMsg && (
            <span style={{ marginLeft: '14px', fontSize: '13px', color: statusMsg.startsWith('Error') ? 'var(--accent-rose)' : 'var(--accent-mint)' }}>
              {statusMsg}
            </span>
          )}
        </div>
      </form>
    </div>
  );
};
