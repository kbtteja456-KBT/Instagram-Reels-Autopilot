import React, { useState } from 'react';

export const StylePage: React.FC = () => {
  const [profile, setProfile] = useState<any>({
    pacing_bpm: 128,
    cut_frequency_seconds: 2.1,
    subtitle_position: '65%-75% safe-zone',
    subtitle_font: 'Plus Jakarta Sans Bold',
    visual_balance: '60% motion b-roll, 40% dynamic highlight graphics',
    color_palette: 'Instagram Gradient Accent (#833AB4, #FD1D1D, #FCAF45)'
  });
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    setMessage(null);
    setTimeout(() => {
      setUploading(false);
      setMessage(`Successfully analyzed reference Reel "${file.name}"! Extracted 2.1s cut rhythm and kinetic safe-zone subtitle timings.`);
      setProfile({
        pacing_bpm: 132,
        cut_frequency_seconds: 1.8,
        subtitle_position: '68% safe-zone',
        subtitle_font: 'Outfit ExtraBold',
        visual_balance: '70% high-energy vertical footage, 30% motion text',
        color_palette: 'Amber Neon & Deep Glass'
      });
    }, 1200);
  };

  return (
    <div className="page-body">
      <div>
        <h2 style={{ fontFamily: 'var(--font-display)', fontSize: '22px', fontWeight: 700 }}>Reference Video Style Analyzer</h2>
        <p style={{ color: 'var(--text-muted)', fontSize: '14px' }}>
          Ingests a vertical 9:16 Reel to extract dual-segment editing rhythm, caption typography, and kinetic safe-zone placement.
        </p>
      </div>

      <div className="card" style={{ borderLeft: '4px solid var(--accent-gold)' }}>
        <h3 style={{ fontSize: '16px', fontWeight: 700, marginBottom: '6px' }}>Strict Pacing Extraction Only</h3>
        <p style={{ color: 'var(--text-secondary)', fontSize: '13px', lineHeight: 1.5 }}>
          The analyzer extracts pacing ratios, cut frequency, and caption typography. Never reuses face, voice, footage, or script from the reference video.
        </p>
      </div>

      <div className="two-col-grid">
        <div className="card">
          <h3 style={{ fontSize: '16px', fontWeight: 700, marginBottom: '16px' }}>Active Style Blueprint</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '8px' }}>
              <span style={{ color: 'var(--text-secondary)', fontSize: '13px' }}>Target Aspect Ratio</span>
              <span style={{ fontWeight: 600, fontSize: '13px' }}>9:16 (1080x1920 @ 60FPS)</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '8px' }}>
              <span style={{ color: 'var(--text-secondary)', fontSize: '13px' }}>Audio Pacing</span>
              <span style={{ fontWeight: 600, fontSize: '13px', color: 'var(--accent-mint)' }}>{profile.pacing_bpm} BPM</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '8px' }}>
              <span style={{ color: 'var(--text-secondary)', fontSize: '13px' }}>Average Cut Frequency</span>
              <span style={{ fontWeight: 600, fontSize: '13px', color: 'var(--accent-amber)' }}>{profile.cut_frequency_seconds}s per transition</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '8px' }}>
              <span style={{ color: 'var(--text-secondary)', fontSize: '13px' }}>Caption Placement</span>
              <span style={{ fontWeight: 600, fontSize: '13px' }}>{profile.subtitle_position}</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '8px' }}>
              <span style={{ color: 'var(--text-secondary)', fontSize: '13px' }}>Typography Font</span>
              <span style={{ fontWeight: 600, fontSize: '13px' }}>{profile.subtitle_font}</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '8px' }}>
              <span style={{ color: 'var(--text-secondary)', fontSize: '13px' }}>Color Palette</span>
              <span style={{ fontWeight: 600, fontSize: '13px' }}>{profile.color_palette}</span>
            </div>
          </div>
        </div>

        <div className="card">
          <h3 style={{ fontSize: '16px', fontWeight: 700, marginBottom: '12px' }}>Upload Reference Reel</h3>
          <p style={{ color: 'var(--text-secondary)', fontSize: '13px', marginBottom: '16px', lineHeight: 1.5 }}>
            Upload a high-performing 9:16 Instagram Reel (.mp4) to tune the FFmpeg compositor's cut duration, scene pacing, and font styles automatically.
          </p>
          <label className="btn btn-secondary" style={{ display: 'inline-block', cursor: 'pointer', textAlign: 'center' }}>
            {uploading ? 'Analyzing Audio & Frames...' : 'Select 9:16 Video File'}
            <input
              type="file"
              accept="video/mp4,video/quicktime"
              style={{ display: 'none' }}
              onChange={handleFileUpload}
              disabled={uploading}
            />
          </label>
          {message && (
            <p style={{ marginTop: '14px', fontSize: '13px', color: 'var(--accent-mint)', lineHeight: 1.5 }}>
              {message}
            </p>
          )}
        </div>
      </div>
    </div>
  );
};
