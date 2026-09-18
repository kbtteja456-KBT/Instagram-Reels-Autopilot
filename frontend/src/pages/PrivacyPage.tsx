import React from 'react';

interface PrivacyPageProps {
  onBack?: () => void;
}

export const PrivacyPage: React.FC<PrivacyPageProps> = ({ onBack }) => {
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
            <span style={{ fontSize: '12px', color: '#10b981', background: 'rgba(16, 185, 129, 0.15)', padding: '4px 10px', borderRadius: '6px', fontWeight: 600 }}>
              Meta Graph API v19+ Compliant
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
          Privacy Policy
        </h1>
        <p style={{ color: '#94a3b8', fontSize: '13px', marginBottom: '32px' }}>
          Effective Date: January 1, 2026 • Last Updated: September 11, 2026
        </p>

        <section style={{ marginBottom: '28px' }}>
          <h2 style={{ fontSize: '18px', fontWeight: 700, color: '#fbbf24', marginBottom: '10px' }}>
            1. Introduction &amp; Local-First Architecture
          </h2>
          <p style={{ fontSize: '14px', color: '#cbd5e1' }}>
            <strong>Auto Instagram Reels Bot</strong> operates primarily as a local-first software system. Your video assets, audio renders, transcripts, and operational configurations reside directly on your local system or private cloud container. We do not transmit your media assets or account credentials to external advertising networks or data brokers.
          </p>
        </section>

        <section style={{ marginBottom: '28px' }}>
          <h2 style={{ fontSize: '18px', fontWeight: 700, color: '#fbbf24', marginBottom: '10px' }}>
            2. Meta User Data &amp; Graph API Access
          </h2>
          <p style={{ fontSize: '14px', color: '#cbd5e1', marginBottom: '10px' }}>
            When you connect your Instagram Professional (Creator or Business) Account via Meta OAuth 2.0, Auto Instagram Reels Bot accesses specific platform scopes:
          </p>
          <ul style={{ paddingLeft: '20px', fontSize: '14px', color: '#cbd5e1' }}>
            <li style={{ marginBottom: '8px' }}>
              <code style={{ color: '#34d399' }}>instagram_content_publish</code>: Used strictly to create 2-step media containers and publish user-approved vertical Reels directly to your verified Instagram account.
            </li>
            <li style={{ marginBottom: '8px' }}>
              <code style={{ color: '#fbbf24' }}>instagram_basic</code>: Used solely to verify account identity, account username, and profile picture in your workspace.
            </li>
            <li style={{ marginBottom: '8px' }}>
              <code style={{ color: '#fbbf24' }}>instagram_manage_insights</code>: Used solely to display aggregated follower counts and Reel play analytics within your workspace dashboard.
            </li>
          </ul>
        </section>

        <section style={{ marginBottom: '28px' }}>
          <h2 style={{ fontSize: '18px', fontWeight: 700, color: '#fbbf24', marginBottom: '10px' }}>
            3. Cryptographic Token Storage (AES-256 Fernet)
          </h2>
          <p style={{ fontSize: '14px', color: '#cbd5e1' }}>
            All OAuth tokens (Short-Lived User Tokens, 60-day Long-Lived User Tokens, and Page Access Tokens) are encrypted at rest using AES-256 (Fernet) symmetric cryptography prior to database insertion. Unencrypted tokens exist only transiently in process memory during active publishing calls.
          </p>
        </section>

        <section style={{ marginBottom: '28px' }}>
          <h2 style={{ fontSize: '18px', fontWeight: 700, color: '#fbbf24', marginBottom: '10px' }}>
            4. Data Retention &amp; Instant Account Disconnect
          </h2>
          <p style={{ fontSize: '14px', color: '#cbd5e1' }}>
            You maintain 100% control over your credentials. Clicking &quot;Disconnect Instagram Account&quot; in the Settings panel immediately and permanently deletes all encrypted token documents and channel references from the MongoDB database.
          </p>
        </section>

        <section style={{ marginBottom: '28px' }}>
          <h2 style={{ fontSize: '18px', fontWeight: 700, color: '#fbbf24', marginBottom: '10px' }}>
            5. Zero-Scraping Guarantee
          </h2>
          <p style={{ fontSize: '14px', color: '#cbd5e1' }}>
            Auto Instagram Reels Bot interfaces exclusively with official Meta Graph API (v19.0+) endpoints. We never simulate browser logins, hijack sessions, or scrape private data from Instagram servers.
          </p>
        </section>
      </div>
    </div>
  );
};
