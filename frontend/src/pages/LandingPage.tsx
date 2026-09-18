import React, { useState } from 'react';

interface LandingPageProps {
  onLoginClick: () => void;
  onPrivacyClick: () => void;
  onTermsClick: () => void;
}

export const LandingPage: React.FC<LandingPageProps> = ({
  onLoginClick,
  onPrivacyClick,
  onTermsClick,
}) => {
  const [openFaq, setOpenFaq] = useState<number | null>(null);

  const toggleFaq = (index: number) => {
    setOpenFaq(openFaq === index ? null : index);
  };

  const faqs = [
    {
      q: 'How does AI Instagram Reels Autopilot operate without breaking Meta policies?',
      a: 'We interface exclusively with the official Meta Graph API (v19.0+) and Instagram Content Publishing API. We strictly avoid web scrapers, simulated headless browsers, or private API endpoints. Your account credentials and OAuth tokens are protected via AES-256 Fernet encryption at rest.'
    },
    {
      q: 'Is the Zero-Cost Mode really ₹0 / $0 guaranteed?',
      a: 'Yes. In Zero-Cost Mode, the system uses Microsoft Edge-TTS for local neural voiceover synthesis, DuckDuckGo for trending topic research, Groq / Free OpenRouter LLMs for storyboard scripts, and local FFmpeg hardware compositing. No paid cloud rendering services are invoked.'
    },
    {
      q: 'How does the 2-step Instagram container publishing pipeline work?',
      a: 'Meta requires videos to be published via a two-step process: (1) POST /media to create an IG Container pointing to a valid 1080x1920 MP4 URL, (2) Poll container status until FINISHED, and (3) POST /media_publish to publish the Reel live to your feed with caption and hashtags.'
    },
    {
      q: 'What is the Quality Control (QC) Gate?',
      a: 'Every rendered Reel undergoes an automated 6-point audit before publication: verifying vertical 9:16 resolution, audio loudness (approx -14 LUFS), duration (30-60s), subtitle safe-zone margins (65%-75% height), audio/video synchronization, and community guideline safety. A score >= 90/100 is strictly enforced.'
    }
  ];

  return (
    <div style={{
      width: '100%',
      minHeight: '100vh',
      background: 'transparent',
      color: '#e6edf3',
      fontFamily: "'Plus Jakarta Sans', sans-serif",
      position: 'relative',
      zIndex: 10,
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      boxSizing: 'border-box',
      overflowX: 'hidden'
    }}>
      {/* 1. NAVBAR */}
      <header style={{
        width: '100%',
        display: 'flex',
        justifyContent: 'center',
        position: 'sticky',
        top: 0,
        zIndex: 50,
        padding: '16px 0',
        boxSizing: 'border-box'
      }}>
        <nav style={{
          width: 'min(100% - 32px, 1200px)',
          margin: '0 auto',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: '16px',
          padding: '12px 24px',
          borderRadius: '16px',
          border: '1px solid rgba(245, 158, 11, 0.22)',
          backdropFilter: 'blur(16px)',
          WebkitBackdropFilter: 'blur(16px)',
          backgroundColor: 'rgba(15, 20, 28, 0.48)',
          boxShadow: '0 8px 32px rgba(0, 0, 0, 0.45)',
          boxSizing: 'border-box'
        }}>
          {/* Brand Identity */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <div style={{
              width: '38px',
              height: '38px',
              borderRadius: '10px',
              background: 'linear-gradient(135deg, #833ab4 0%, #fd1d1d 50%, #fcb045 100%)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: '0 0 16px rgba(225, 48, 108, 0.4)',
              border: '1px solid rgba(245, 158, 11, 0.3)'
            }}>
              <svg width="22" height="22" viewBox="0 0 24 24" fill="#ffffff">
                <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/>
              </svg>
            </div>
            <div>
              <h1 style={{
                fontFamily: "'Outfit', sans-serif",
                fontSize: '18px',
                fontWeight: 800,
                letterSpacing: '-0.3px',
                margin: 0,
                background: 'linear-gradient(to right, #ffffff, #fbbf24)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                lineHeight: 1.2
              }}>
                Auto Instagram Reels Bot
              </h1>
              <span style={{ fontSize: '10px', color: '#34d399', textTransform: 'uppercase', letterSpacing: '0.8px', fontWeight: 600 }}>
                Meta Graph API v19+ Engine
              </span>
            </div>
          </div>

          {/* Nav Links */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '20px', flexWrap: 'wrap' }}>
            <a
              href="#purpose"
              style={{
                color: '#fbbf24',
                textDecoration: 'none',
                fontSize: '13px',
                fontWeight: 600,
                transition: 'color 0.2s'
              }}
            >
              App Purpose
            </a>
            <a
              href="#pipeline"
              style={{
                color: '#94a3b8',
                textDecoration: 'none',
                fontSize: '13px',
                fontWeight: 500,
                transition: 'color 0.2s'
              }}
            >
              Pipeline
            </a>
            <a
              href="#faq"
              style={{
                color: '#94a3b8',
                textDecoration: 'none',
                fontSize: '13px',
                fontWeight: 500,
                transition: 'color 0.2s'
              }}
            >
              FAQ
            </a>
            <button
              onClick={onPrivacyClick}
              style={{
                background: 'none',
                border: 'none',
                color: '#94a3b8',
                cursor: 'pointer',
                fontSize: '13px',
                fontWeight: 500
              }}
            >
              Privacy Policy
            </button>
            <button
              onClick={onTermsClick}
              style={{
                background: 'none',
                border: 'none',
                color: '#94a3b8',
                cursor: 'pointer',
                fontSize: '13px',
                fontWeight: 500
              }}
            >
              Terms
            </button>
            <button
              onClick={onLoginClick}
              style={{
                background: 'linear-gradient(135deg, #f59e0b 0%, #e1306c 50%, #833ab4 100%)',
                color: '#ffffff',
                border: 'none',
                borderRadius: '8px',
                padding: '9px 20px',
                fontWeight: 800,
                fontSize: '13px',
                cursor: 'pointer',
                boxShadow: '0 4px 16px rgba(225, 48, 108, 0.4)',
                transition: 'transform 0.15s, box-shadow 0.15s'
              }}
            >
              Sign In / Launch ⚡
            </button>
          </div>
        </nav>
      </header>

      {/* 2. HERO SECTION */}
      <section style={{
        width: '100%',
        display: 'flex',
        justifyContent: 'center',
        margin: '28px 0 40px 0',
        boxSizing: 'border-box'
      }}>
        <div style={{
          width: 'min(100% - 32px, 1200px)',
          margin: '0 auto',
          backgroundColor: 'rgba(15, 20, 28, 0.45)',
          backdropFilter: 'blur(16px)',
          WebkitBackdropFilter: 'blur(16px)',
          border: '1px solid rgba(245, 158, 11, 0.28)',
          borderRadius: '24px',
          padding: 'clamp(36px, 5vw, 56px) clamp(20px, 4vw, 48px)',
          textAlign: 'center',
          boxShadow: '0 24px 64px rgba(0, 0, 0, 0.55), 0 0 32px rgba(245, 158, 11, 0.08)',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          boxSizing: 'border-box'
        }}>
          {/* Compliance Badge */}
          <div style={{
            display: 'inline-flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '8px',
            backgroundColor: 'rgba(245, 158, 11, 0.12)',
            border: '1px solid rgba(245, 158, 11, 0.35)',
            borderRadius: '999px',
            padding: '6px 20px',
            fontSize: '13px',
            fontWeight: 600,
            color: '#fbbf24',
            marginBottom: '24px',
            maxWidth: '100%',
            textAlign: 'center'
          }}>
            <span>⚡</span>
            <span>Official Meta Graph API v19.0+ • 100% Zero-Scraping Developer Compliance</span>
          </div>

          {/* Heading */}
          <h2 style={{
            fontFamily: "'Outfit', sans-serif",
            fontSize: 'clamp(28px, 4.2vw, 46px)',
            lineHeight: 1.22,
            fontWeight: 800,
            letterSpacing: '-1px',
            background: 'linear-gradient(135deg, #ffffff 15%, #fde047 40%, #fbbf24 70%, #f59e0b 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            margin: '0 auto 20px auto',
            maxWidth: '880px',
            textAlign: 'center'
          }}>
            Autonomous Instagram Reels Creation &amp; Scheduled Publishing
          </h2>

          {/* Description */}
          <p style={{
            fontSize: '16px',
            color: '#cbd5e1',
            maxWidth: '740px',
            margin: '0 auto 36px auto',
            lineHeight: 1.7,
            textAlign: 'center'
          }}>
            <strong style={{ color: '#fbbf24' }}>Auto Instagram Reels Bot</strong> is a creator automation suite that connects securely to your authorized Instagram Professional (Creator or Business) account, synthesizes high-retention 1080x1920 vertical videos with neural audio &amp; safe-zone kinetic subtitles, and publishes automatically on your 24/7 schedule.
          </p>

          {/* Action Buttons */}
          <div style={{
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            gap: '16px',
            flexWrap: 'wrap'
          }}>
            <button
              onClick={onLoginClick}
              style={{
                background: 'linear-gradient(135deg, #f59e0b 0%, #e1306c 50%, #833ab4 100%)',
                color: '#ffffff',
                border: 'none',
                borderRadius: '12px',
                padding: '14px 34px',
                fontSize: '15px',
                fontWeight: 800,
                cursor: 'pointer',
                boxShadow: '0 6px 24px rgba(225, 48, 108, 0.45)',
                transition: 'transform 0.15s, box-shadow 0.15s'
              }}
            >
              Get Started Free 🚀
            </button>
            <a
              href="#purpose"
              style={{
                background: 'rgba(16, 185, 129, 0.12)',
                border: '1px solid rgba(16, 185, 129, 0.35)',
                color: '#34d399',
                borderRadius: '12px',
                padding: '14px 28px',
                fontSize: '15px',
                fontWeight: 600,
                textDecoration: 'none',
                display: 'inline-flex',
                alignItems: 'center'
              }}
            >
              Learn App Purpose
            </a>
          </div>
        </div>
      </section>

      {/* 3. ABOUT THIS APPLICATION SECTION */}
      <section id="purpose" style={{
        width: '100%',
        display: 'flex',
        justifyContent: 'center',
        marginBottom: '40px',
        boxSizing: 'border-box'
      }}>
        <div style={{
          width: 'min(100% - 32px, 1200px)',
          margin: '0 auto',
          backgroundColor: 'rgba(15, 20, 28, 0.48)',
          backdropFilter: 'blur(16px)',
          WebkitBackdropFilter: 'blur(16px)',
          border: '1px solid rgba(245, 158, 11, 0.25)',
          borderRadius: '24px',
          padding: 'clamp(28px, 4vw, 44px) clamp(20px, 4vw, 40px)',
          boxShadow: '0 16px 48px rgba(0, 0, 0, 0.5), 0 0 24px rgba(245, 158, 11, 0.08)',
          boxSizing: 'border-box'
        }}>
          <div style={{
            display: 'inline-block',
            backgroundColor: 'rgba(16, 185, 129, 0.15)',
            color: '#34d399',
            fontSize: '12px',
            fontWeight: 700,
            textTransform: 'uppercase',
            letterSpacing: '1px',
            padding: '4px 12px',
            borderRadius: '6px',
            marginBottom: '16px'
          }}>
            About This Application
          </div>
          <h2 style={{
            fontFamily: "'Outfit', sans-serif",
            fontSize: '30px',
            fontWeight: 800,
            color: '#ffffff',
            marginBottom: '16px'
          }}>
            Purpose of Auto Instagram Reels Bot
          </h2>
          <p style={{ fontSize: '15px', color: '#cbd5e1', lineHeight: 1.7, marginBottom: '20px' }}>
            <strong style={{ color: '#fbbf24' }}>Auto Instagram Reels Bot</strong> is designed for creators, educators, developers, and brands aiming to scale short-form engagement without the multi-hour burden of daily manual editing. Crafting viral Instagram Reels demands research, scripting, audio engineering, safe-zone subtitle syncing, and vertical rendering.
          </p>
          <p style={{ fontSize: '15px', color: '#cbd5e1', lineHeight: 1.7, marginBottom: '28px' }}>
            Our engine unifies these operations into a cohesive, local-first state-machine pipeline. Once rendered and audited past a strict Quality Control gate (&gt;=90/100), Reels are published directly through the official Meta Graph API Content Publishing container flow.
          </p>

          <h3 style={{ fontSize: '18px', fontWeight: 700, color: '#fbbf24', marginBottom: '16px' }}>
            Why Auto Instagram Reels Bot Requests Meta Graph API Access:
          </h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '16px', marginBottom: '24px' }}>
            <div style={{ backgroundColor: 'rgba(22, 27, 34, 0.5)', backdropFilter: 'blur(12px)', WebkitBackdropFilter: 'blur(12px)', padding: '20px', borderRadius: '12px', border: '1px solid rgba(245, 158, 11, 0.2)' }}>
              <h4 style={{ color: '#fbbf24', margin: '0 0 8px 0', fontSize: '15px' }}>1. 2-Step Container Publishing</h4>
              <p style={{ fontSize: '13px', color: '#94a3b8', margin: 0, lineHeight: 1.6 }}>
                Uses <code style={{ color: '#34d399' }}>instagram_content_publish</code> to initiate container creation and upload 1080x1920 MP4 vertical Reels directly to your Instagram Professional account without manual friction.
              </p>
            </div>
            <div style={{ backgroundColor: 'rgba(22, 27, 34, 0.5)', backdropFilter: 'blur(12px)', WebkitBackdropFilter: 'blur(12px)', padding: '20px', borderRadius: '12px', border: '1px solid rgba(16, 185, 129, 0.2)' }}>
              <h4 style={{ color: '#34d399', margin: '0 0 8px 0', fontSize: '15px' }}>2. Professional Account Insights</h4>
              <p style={{ fontSize: '13px', color: '#94a3b8', margin: 0, lineHeight: 1.6 }}>
                Uses <code style={{ color: '#fbbf24' }}>instagram_basic</code> and <code style={{ color: '#fbbf24' }}>instagram_manage_insights</code> to confirm your verified account identity, follower count, and Reel play statistics in your private dashboard.
              </p>
            </div>
          </div>

          <div style={{
            backgroundColor: 'rgba(245, 158, 11, 0.08)',
            border: '1px solid rgba(245, 158, 11, 0.25)',
            borderRadius: '12px',
            padding: '16px 20px',
            fontSize: '13px',
            color: '#e2e8f0',
            lineHeight: 1.6
          }}>
            <strong style={{ color: '#fbbf24' }}>Meta Platform Terms &amp; Developer Policy Compliance:</strong> Auto Instagram Reels Bot's use and storage of Meta user data complies strictly with the Meta Developer Policies. All access tokens are AES-256 encrypted at rest and permanently purged upon account disconnect.
          </div>
        </div>
      </section>

      {/* 4. FEATURE PILLARS */}
      <section id="features" style={{
        width: '100%',
        display: 'flex',
        justifyContent: 'center',
        marginBottom: '40px',
        boxSizing: 'border-box'
      }}>
        <div style={{
          width: 'min(100% - 32px, 1200px)',
          margin: '0 auto',
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
          gap: '20px',
          boxSizing: 'border-box'
        }}>
          <div style={{
            backgroundColor: 'rgba(15, 20, 28, 0.45)',
            backdropFilter: 'blur(16px)',
            WebkitBackdropFilter: 'blur(16px)',
            border: '1px solid rgba(245, 158, 11, 0.2)',
            borderRadius: '16px',
            padding: '28px'
          }}>
            <div style={{ fontSize: '28px', marginBottom: '14px' }}>🚀</div>
            <h3 style={{ fontSize: '18px', fontWeight: 700, color: '#fbbf24', marginBottom: '10px' }}>
              Direct Meta Graph API Uploads
            </h3>
            <p style={{ fontSize: '13px', color: '#94a3b8', margin: 0, lineHeight: 1.6 }}>
              Seamlessly publish 1080x1920 vertical Reels directly to your connected Instagram account using official container endpoints.
            </p>
          </div>

          <div style={{
            backgroundColor: 'rgba(15, 20, 28, 0.45)',
            backdropFilter: 'blur(16px)',
            WebkitBackdropFilter: 'blur(16px)',
            border: '1px solid rgba(16, 185, 129, 0.2)',
            borderRadius: '16px',
            padding: '28px'
          }}>
            <div style={{ fontSize: '28px', marginBottom: '14px' }}>📊</div>
            <h3 style={{ fontSize: '18px', fontWeight: 700, color: '#34d399', marginBottom: '10px' }}>
              Live Account &amp; Reel Plays
            </h3>
            <p style={{ fontSize: '13px', color: '#94a3b8', margin: 0, lineHeight: 1.6 }}>
              Live follower counts, Reel plays, and pipeline telemetry monitored in real-time from your personal glassmorphic workspace.
            </p>
          </div>

          <div style={{
            backgroundColor: 'rgba(15, 20, 28, 0.45)',
            backdropFilter: 'blur(16px)',
            WebkitBackdropFilter: 'blur(16px)',
            border: '1px solid rgba(245, 158, 11, 0.2)',
            borderRadius: '16px',
            padding: '28px'
          }}>
            <div style={{ fontSize: '28px', marginBottom: '14px' }}>🛡️</div>
            <h3 style={{ fontSize: '18px', fontWeight: 700, color: '#fbbf24', marginBottom: '10px' }}>
              AES-256 Cryptographic Vault
            </h3>
            <p style={{ fontSize: '13px', color: '#94a3b8', margin: 0, lineHeight: 1.6 }}>
              BYOK multi-tenant token encryption ensures your Meta tokens and API keys are stored with military-grade privacy.
            </p>
          </div>
        </div>
      </section>

      {/* 5. 14-STAGE PIPELINE SECTION */}
      <section id="pipeline" style={{
        width: '100%',
        display: 'flex',
        justifyContent: 'center',
        marginBottom: '40px',
        boxSizing: 'border-box'
      }}>
        <div style={{
          width: 'min(100% - 32px, 1200px)',
          margin: '0 auto',
          backgroundColor: 'rgba(15, 20, 28, 0.48)',
          backdropFilter: 'blur(16px)',
          WebkitBackdropFilter: 'blur(16px)',
          border: '1px solid rgba(245, 158, 11, 0.25)',
          borderRadius: '24px',
          padding: 'clamp(28px, 4vw, 44px) clamp(20px, 4vw, 40px)',
          boxShadow: '0 16px 48px rgba(0, 0, 0, 0.5)',
          boxSizing: 'border-box'
        }}>
          <div style={{
            display: 'inline-block',
            backgroundColor: 'rgba(245, 158, 11, 0.15)',
            color: '#fbbf24',
            fontSize: '12px',
            fontWeight: 700,
            textTransform: 'uppercase',
            letterSpacing: '1px',
            padding: '4px 12px',
            borderRadius: '6px',
            marginBottom: '16px'
          }}>
            End-To-End Architecture
          </div>
          <h2 style={{ fontFamily: "'Outfit', sans-serif", fontSize: '28px', fontWeight: 800, color: '#ffffff', marginBottom: '12px' }}>
            The 14-Stage Autonomous Pipeline
          </h2>
          <p style={{ color: '#94a3b8', fontSize: '14px', marginBottom: '28px', maxWidth: '720px' }}>
            Every autonomous publishing cycle executes a deterministic sequence from trend discovery to verified Meta container upload:
          </p>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '14px' }}>
            {[
              { num: '01', title: 'Trend Research', desc: 'DuckDuckGo searches viral audio and niche pain points.' },
              { num: '02', title: 'Viral Scriptwriter', desc: 'Generates 3-second hook, body, and CTA retaining viewers.' },
              { num: '03', title: 'Neural Voiceover', desc: 'Edge-TTS synthesizes human-grade voice at ₹0 cost.' },
              { num: '04', title: 'Kinetic Subtitles', desc: 'Word-level ASS timestamps pinned in 65%-75% safe-zone.' },
              { num: '05', title: 'FFmpeg Compositor', desc: 'Renders 1080x1920 60FPS MP4 with motion transitions.' },
              { num: '06', title: 'QC Gate Audit', desc: 'Strict scoring verifies >=90/100 across 6 quality checks.' },
              { num: '07', title: 'Container Publishing', desc: 'Meta Graph API v19+ creates container and publishes Reel.' },
              { num: '08', title: 'Analytics Loop', desc: 'Polls view metrics and reinforces successful video patterns.' },
            ].map((st) => (
              <div key={st.num} style={{
                background: 'rgba(22, 27, 34, 0.5)',
                border: '1px solid rgba(255, 255, 255, 0.08)',
                borderRadius: '12px',
                padding: '16px'
              }}>
                <div style={{ color: '#fbbf24', fontSize: '12px', fontWeight: 800, marginBottom: '6px' }}>
                  STAGE {st.num}
                </div>
                <div style={{ fontWeight: 700, fontSize: '14px', color: '#ffffff', marginBottom: '6px' }}>
                  {st.title}
                </div>
                <div style={{ fontSize: '12px', color: '#94a3b8', lineHeight: 1.5 }}>
                  {st.desc}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* 6. FAQ SECTION */}
      <section id="faq" style={{
        width: '100%',
        display: 'flex',
        justifyContent: 'center',
        marginBottom: '60px',
        boxSizing: 'border-box'
      }}>
        <div style={{
          width: 'min(100% - 32px, 1200px)',
          margin: '0 auto',
          backgroundColor: 'rgba(15, 20, 28, 0.48)',
          backdropFilter: 'blur(16px)',
          WebkitBackdropFilter: 'blur(16px)',
          border: '1px solid rgba(245, 158, 11, 0.25)',
          borderRadius: '24px',
          padding: 'clamp(28px, 4vw, 44px) clamp(20px, 4vw, 40px)',
          boxShadow: '0 16px 48px rgba(0, 0, 0, 0.5)',
          boxSizing: 'border-box'
        }}>
          <h2 style={{ fontFamily: "'Outfit', sans-serif", fontSize: '28px', fontWeight: 800, color: '#ffffff', marginBottom: '20px' }}>
            Frequently Asked Questions
          </h2>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {faqs.map((faq, idx) => (
              <div
                key={idx}
                onClick={() => toggleFaq(idx)}
                style={{
                  background: 'rgba(22, 27, 34, 0.6)',
                  border: '1px solid rgba(245, 158, 11, 0.15)',
                  borderRadius: '12px',
                  padding: '16px 20px',
                  cursor: 'pointer',
                  transition: 'border-color 0.2s'
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ fontWeight: 700, fontSize: '14px', color: '#f8fafc' }}>{faq.q}</span>
                  <span style={{ color: '#fbbf24', fontSize: '18px', fontWeight: 700 }}>
                    {openFaq === idx ? '−' : '+'}
                  </span>
                </div>
                {openFaq === idx && (
                  <p style={{ fontSize: '13px', color: '#94a3b8', lineHeight: 1.6, marginTop: '12px', margin: '12px 0 0 0' }}>
                    {faq.a}
                  </p>
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* 7. FOOTER */}
      <footer style={{
        width: '100%',
        borderTop: '1px solid rgba(245, 158, 11, 0.15)',
        padding: '36px 0',
        backgroundColor: 'rgba(9, 12, 16, 0.55)',
        backdropFilter: 'blur(16px)',
        WebkitBackdropFilter: 'blur(16px)',
        display: 'flex',
        justifyContent: 'center',
        boxSizing: 'border-box'
      }}>
        <div style={{
          width: 'min(100% - 32px, 1200px)',
          margin: '0 auto',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: '16px',
          boxSizing: 'border-box'
        }}>
          <div>
            <div style={{ fontWeight: 700, color: '#f8fafc', fontSize: '14px' }}>
              Auto Instagram Reels Bot
            </div>
            <div style={{ color: '#64748b', fontSize: '12px', marginTop: '2px' }}>
              Meta Graph API Content Publishing Engine • Local-First Autonomous System
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
            <button
              onClick={onPrivacyClick}
              style={{ background: 'none', border: 'none', color: '#94a3b8', cursor: 'pointer', fontSize: '12px' }}
            >
              Privacy Policy
            </button>
            <button
              onClick={onTermsClick}
              style={{ background: 'none', border: 'none', color: '#94a3b8', cursor: 'pointer', fontSize: '12px' }}
            >
              Terms of Service
            </button>
            <button
              onClick={onLoginClick}
              style={{ background: 'none', border: 'none', color: '#fbbf24', cursor: 'pointer', fontSize: '12px', fontWeight: 600 }}
            >
              Sign In →
            </button>
          </div>
        </div>
      </footer>
    </div>
  );
};
