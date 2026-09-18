import React, { useState } from 'react';

interface CreateVideoModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (params: { topic: string; niche: string; target_duration_sec: number; publish_immediately: boolean }) => void;
  hasConnectedAccount?: boolean;
}

interface Preset {
  label: string;
  emoji: string;
  niche: string;
  prompt: string;
}

const PRESETS: Preset[] = [
  {
    label: 'Tech & AI News',
    emoji: '⚡',
    niche: 'Technology & AI',
    prompt: 'Top 3 autonomous AI agent workflows that compile code and replace routine software engineering in 2026'
  },
  {
    label: 'Quantum Breakthrough',
    emoji: '🔬',
    niche: 'Science & Future',
    prompt: 'How microscopic quantum processors operating near absolute zero are breaking supercomputer records'
  },
  {
    label: 'Wealth & Mindset',
    emoji: '💰',
    niche: 'Wealth & Financial Freedom',
    prompt: 'The 1% Rule of Digital Assets: Why waiting for the right moment keeps people poor'
  },
  {
    label: 'Stoic High Performance',
    emoji: '🏛️',
    niche: 'Productivity & High Performance',
    prompt: 'Marcus Aurelius on cognitive focus: How to remain calm when external chaos is everywhere'
  },
  {
    label: 'Dark Psychology',
    emoji: '🧠',
    niche: 'Psychology & Human Behavior',
    prompt: '3 psychological tricks that instantly reveal if someone is lying to you'
  }
];

export const CreateVideoModal: React.FC<CreateVideoModalProps> = ({
  isOpen,
  onClose,
  onSubmit,
  hasConnectedAccount = true
}) => {
  const [topic, setTopic] = useState<string>('');
  const [niche, setNiche] = useState<string>('Technology & AI');
  const [duration, setDuration] = useState<number>(45);
  const [publishImmediately, setPublishImmediately] = useState<boolean>(false);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);

  if (!isOpen) return null;

  const handleApplyPreset = (preset: Preset) => {
    setTopic(preset.prompt);
    setNiche(preset.niche);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!topic.trim()) return;
    setIsSubmitting(true);
    onSubmit({
      topic: topic.trim(),
      niche,
      target_duration_sec: duration,
      publish_immediately: publishImmediately
    });
    setIsSubmitting(false);
    onClose();
  };

  return (
    <div
      style={{
        position: 'fixed',
        inset: 0,
        background: 'rgba(3, 7, 18, 0.85)',
        backdropFilter: 'blur(10px)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 1100,
        padding: '16px',
        animation: 'fadeIn 0.2s ease-out'
      }}
      onClick={onClose}
    >
      <div
        style={{
          maxWidth: '640px',
          width: '100%',
          background: 'linear-gradient(180deg, #0f172a 0%, #090d16 100%)',
          border: '1px solid rgba(245, 158, 11, 0.3)',
          borderRadius: '20px',
          padding: '28px',
          boxShadow: '0 25px 60px -15px rgba(0, 0, 0, 0.9), 0 0 35px rgba(225, 48, 108, 0.15)',
          color: '#f8fafc',
          maxHeight: '90vh',
          overflowY: 'auto'
        }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '16px' }}>
          <div>
            <h2 style={{ fontFamily: 'var(--font-display)', fontSize: '20px', fontWeight: 700, margin: 0, color: '#ffffff' }}>
              Create &amp; Render New Reel
            </h2>
            <p style={{ margin: '4px 0 0 0', fontSize: '13px', color: '#94a3b8' }}>
              Autonomous 14-Agent pipeline: Fact check → Hook → Edge-TTS → Kinetic ASS safe zone subtitles → 1080x1920 FFmpeg rendering.
            </p>
          </div>
          <button
            onClick={onClose}
            style={{
              background: 'transparent',
              border: 'none',
              color: '#94a3b8',
              cursor: 'pointer',
              fontSize: '20px',
              padding: '4px 8px'
            }}
          >
            ✕
          </button>
        </div>

        {/* Quick Presets */}
        <div style={{ marginBottom: '16px' }}>
          <label style={{ display: 'block', fontSize: '11.5px', fontWeight: 700, color: '#cbd5e1', marginBottom: '8px', textTransform: 'uppercase' }}>
            ⚡ Instant Viral Presets
          </label>
          <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
            {PRESETS.map((p) => (
              <button
                key={p.label}
                type="button"
                onClick={() => handleApplyPreset(p)}
                style={{
                  background: 'rgba(255, 255, 255, 0.05)',
                  border: '1px solid rgba(255, 255, 255, 0.1)',
                  borderRadius: '10px',
                  padding: '6px 12px',
                  color: '#e2e8f0',
                  fontSize: '12px',
                  fontWeight: 500,
                  cursor: 'pointer',
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '6px',
                  transition: 'all 0.2s ease'
                }}
              >
                <span>{p.emoji}</span>
                <span>{p.label}</span>
              </button>
            ))}
          </div>
        </div>

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {/* Prompt */}
          <div>
            <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, color: '#e2e8f0', marginBottom: '6px' }}>
              Reel Topic / Hook Prompt <span style={{ color: '#e1306c' }}>*</span>
            </label>
            <textarea
              required
              rows={3}
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              placeholder="e.g., 3 AI Tools That Will Replace Programmers in 2026"
              style={{
                width: '100%',
                background: 'rgba(8, 12, 22, 0.8)',
                border: '1px solid rgba(255, 255, 255, 0.15)',
                borderRadius: '12px',
                padding: '12px',
                color: '#ffffff',
                fontSize: '13.5px',
                fontFamily: 'inherit',
                resize: 'none'
              }}
            />
          </div>

          {/* Niche */}
          <div>
            <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, color: '#e2e8f0', marginBottom: '6px' }}>
              Target Niche
            </label>
            <select
              value={niche}
              onChange={(e) => setNiche(e.target.value)}
              style={{
                width: '100%',
                background: 'rgba(8, 12, 22, 0.8)',
                border: '1px solid rgba(255, 255, 255, 0.15)',
                borderRadius: '12px',
                padding: '10px 14px',
                color: '#ffffff',
                fontSize: '13.5px'
              }}
            >
              <option value="Technology & AI">Technology &amp; AI</option>
              <option value="Wealth & Financial Freedom">Wealth &amp; Financial Freedom</option>
              <option value="Productivity & High Performance">Productivity &amp; High Performance</option>
              <option value="Science & Future">Science &amp; Future</option>
              <option value="Psychology & Human Behavior">Psychology &amp; Human Behavior</option>
            </select>
          </div>

          {/* Duration Slider */}
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', fontWeight: 600, color: '#e2e8f0', marginBottom: '6px' }}>
              <span>Target Duration</span>
              <span style={{ color: '#f59e0b' }}>{duration} seconds</span>
            </div>
            <input
              type="range"
              min="25"
              max="60"
              step="5"
              value={duration}
              onChange={(e) => setDuration(Number(e.target.value))}
              style={{ width: '100%', accentColor: '#e1306c' }}
            />
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '10.5px', color: '#64748b', marginTop: '4px' }}>
              <span>25s (Snappy)</span>
              <span>45s (Optimal)</span>
              <span>60s (Deep-dive)</span>
            </div>
          </div>

          {/* Auto Publish */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '10px',
            background: 'rgba(255, 255, 255, 0.03)',
            padding: '12px 14px',
            borderRadius: '12px',
            border: '1px solid rgba(255, 255, 255, 0.08)'
          }}>
            <input
              type="checkbox"
              id="autoPublish"
              checked={publishImmediately}
              onChange={(e) => setPublishImmediately(e.target.checked)}
              style={{ width: '16px', height: '16px', accentColor: '#e1306c' }}
            />
            <label htmlFor="autoPublish" style={{ fontSize: '12.5px', color: '#cbd5e1', cursor: 'pointer' }}>
              Publish immediately to Instagram after QC gate passes (&gt;= 90/100)
            </label>
          </div>

          {/* Buttons */}
          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '12px', marginTop: '8px' }}>
            <button
              type="button"
              onClick={onClose}
              className="btn btn-secondary"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="btn btn-primary"
            >
              <span>{isSubmitting ? 'Starting Agents...' : '🚀 Launch Pipeline & Render'}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
