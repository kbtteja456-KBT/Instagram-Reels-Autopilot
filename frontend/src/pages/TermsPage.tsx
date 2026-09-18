import React from 'react';

interface TermsPageProps {
  onBack?: () => void;
}

export const TermsPage: React.FC<TermsPageProps> = ({ onBack }) => {
  return (
    <div style={{
      minHeight: '100vh',
      background: 'transparent',
      color: '#e2e8f0',
      fontFamily: "'Plus Jakarta Sans', sans-serif",
      padding: '40px 20px',
      lineHeight: 1.7,
      position: 'relative',
      zIndex: 10,
      overflowY: 'auto'
    }}>
      <div style={{
        maxWidth: '860px',
        margin: '0 auto',
        backgroundColor: 'rgba(15, 20, 28, 0.88)',
        backdropFilter: 'blur(20px)',
        WebkitBackdropFilter: 'blur(20px)',
        border: '1px solid rgba(245, 158, 11, 0.25)',
        borderRadius: '20px',
        padding: '40px',
        boxShadow: '0 24px 64px rgba(0, 0, 0, 0.8), 0 0 32px rgba(225, 48, 108, 0.1)'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '24px' }}>
          {onBack && (
            <button
              onClick={onBack}
              style={{
                background: 'rgba(245, 158, 11, 0.1)',
                border: '1px solid rgba(245, 158, 11, 0.3)',
                color: '#fbbf24',
                padding: '8px 18px',
                borderRadius: '8px',
                cursor: 'pointer',
                fontWeight: 600,
                fontSize: '14px'
              }}
            >
              ← Back to Auto Instagram Reels Bot
            </button>
          )}

          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <span style={{ fontSize: '12px', color: '#fbbf24', background: 'rgba(245, 158, 11, 0.15)', padding: '4px 10px', borderRadius: '6px', fontWeight: 600 }}>
              Meta Developer Terms of Service
            </span>
          </div>
        </div>

        <h1 style={{
          fontSize: '32px',
          fontWeight: 800,
          marginBottom: '8px',
          background: 'linear-gradient(to right, #ffffff, #fbbf24)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent'
        }}>
          Terms of Service
        </h1>
        <p style={{ color: '#94a3b8', fontSize: '13px', marginBottom: '32px' }}>
          Effective Date: January 1, 2026 • Last Updated: September 11, 2026
        </p>

        <section style={{ marginBottom: '28px' }}>
          <h2 style={{ fontSize: '18px', fontWeight: 700, color: '#fbbf24', marginBottom: '10px' }}>
            1. Agreement to Terms
          </h2>
          <p style={{ fontSize: '14px', color: '#cbd5e1' }}>
            By using <strong>Auto Instagram Reels Bot</strong>, you agree to comply with and be bound by these Terms of Service, along with Meta&apos;s Platform Terms and Developer Policies. If you do not agree to these terms, do not install or use the platform.
          </p>
        </section>

        <section style={{ marginBottom: '28px' }}>
          <h2 style={{ fontSize: '18px', fontWeight: 700, color: '#fbbf24', marginBottom: '10px' }}>
            2. Content Guidelines &amp; Quality Control Gate
          </h2>
          <p style={{ fontSize: '14px', color: '#cbd5e1' }}>
            Users are solely responsible for the content generated and published through their accounts. You agree not to configure the system to generate or distribute hate speech, harassment, sexually explicit content, deceptive financial schemes, or copyright-infringing materials. Our built-in QC Gate audits scripts and assets to prevent violations before publication.
          </p>
        </section>

        <section style={{ marginBottom: '28px' }}>
          <h2 style={{ fontSize: '18px', fontWeight: 700, color: '#fbbf24', marginBottom: '10px' }}>
            3. Meta Platform API Rate Limits
          </h2>
          <p style={{ fontSize: '14px', color: '#cbd5e1' }}>
            Publishing calls are governed by Meta&apos;s Instagram Content Publishing API rate limits (maximum 25 publishing API calls per 24 hours per professional account). Auto Instagram Reels Bot schedules posts (default 2 Reels/day) safely within platform boundaries to guarantee zero quota exhaustion or throttling.
          </p>
        </section>

        <section style={{ marginBottom: '28px' }}>
          <h2 style={{ fontSize: '18px', fontWeight: 700, color: '#fbbf24', marginBottom: '10px' }}>
            4. Limitation of Liability
          </h2>
          <p style={{ fontSize: '14px', color: '#cbd5e1' }}>
            Auto Instagram Reels Bot is provided &quot;as is&quot; without warranties of any kind. In no event shall the authors or copyright holders be liable for any claim, damages, account suspension, or other liability arising from your use of the software.
          </p>
        </section>
      </div>
    </div>
  );
};
