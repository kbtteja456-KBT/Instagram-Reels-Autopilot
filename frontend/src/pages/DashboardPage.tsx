import React, { useState } from 'react';
import { AutopilotHero } from '../components/AutopilotHero';
import { StatsRow } from '../components/StatsRow';
import { ActivityFeed } from '../components/ActivityFeed';
import {
  InstagramAccount,
  Reel,
  AutopilotStatus,
  api
} from '../services/api';
import { InstagramTileIcon, CheckCircleIcon, SyncIcon, ChevronDownIcon, PlayIcon, MetaIcon } from '../components/Icons';

interface DashboardPageProps {
  account?: InstagramAccount;
  reels: Reel[];
  autopilotStatus?: AutopilotStatus;
  onToggleAutopilot: () => void;
  onGenerateClick: () => void;
  onRefreshData?: () => void;
}

export const DashboardPage: React.FC<DashboardPageProps> = ({
  account,
  reels,
  autopilotStatus,
  onToggleAutopilot,
  onGenerateClick,
  onRefreshData
}) => {
  const [isSyncing, setIsSyncing] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const [syncNotice, setSyncNotice] = useState<string | null>(null);

  const isConnected = Boolean(account?.is_connected);
  const username = account?.username || 'autopilot_reels';
  const igUserId = account?.instagram_user_id || '17841400000000001';

  const handleConnect = async () => {
    setIsConnecting(true);
    setSyncNotice(null);
    try {
      const res = await api.instagram.connect();
      if (res.auth_url) {
        window.location.href = res.auth_url;
      }
    } catch (err: any) {
      setSyncNotice(`Connection note: ${err.message || 'Connecting to Meta'}`);
      setIsConnecting(false);
    }
  };

  const handleSync = async () => {
    setIsSyncing(true);
    setSyncNotice(null);
    try {
      const res = await api.instagram.sync();
      setSyncNotice('Stats synced successfully from Meta Graph API!');
      if (onRefreshData) onRefreshData();
    } catch (err: any) {
      setSyncNotice(`Sync note: ${err.message}`);
    } finally {
      setIsSyncing(false);
    }
  };

  return (
    <div className="page-body">
      {/* 1. Instagram Connection Banner Card */}
      {!isConnected ? (
        <div
          className="card yt-connected-card"
          style={{
            border: '1px solid rgba(225, 48, 108, 0.3)',
            background: 'linear-gradient(135deg, rgba(225, 48, 108, 0.08), rgba(15, 23, 42, 0.7))'
          }}
        >
          <div className="yt-card-left">
            <InstagramTileIcon size={44} />
            <div>
              <div className="yt-card-title-row">
                <span className="yt-channel-name" style={{ color: '#f87171' }}>No Instagram Account Connected</span>
              </div>
              <div className="yt-channel-id" style={{ marginTop: '4px', color: '#94a3b8' }}>
                Connect your Instagram Professional (Creator or Business) account to enable 1-click publishing, scheduled Reels, and live analytics.
              </div>
            </div>
          </div>

          <div className="yt-card-right">
            <button
              className="btn btn-primary"
              onClick={handleConnect}
              disabled={isConnecting}
              style={{
                background: 'linear-gradient(135deg, #833ab4 0%, #fd1d1d 50%, #fcb045 100%)',
                borderColor: '#e1306c',
                color: '#ffffff',
                fontWeight: 600,
                padding: '8px 18px',
                display: 'inline-flex',
                alignItems: 'center',
                gap: '8px',
                cursor: 'pointer'
              }}
            >
              <MetaIcon size={18} />
              <span>{isConnecting ? 'Connecting...' : 'Connect Instagram'}</span>
            </button>
          </div>
        </div>
      ) : (
        <div className="card yt-connected-card">
          <div className="yt-card-left">
            <InstagramTileIcon size={44} />
            <div>
              <div className="yt-card-title-row">
                <span className="yt-channel-name">@{username}</span>
                <span className="yt-channel-handle">{account?.name || 'Instagram Creator'}</span>
              </div>
              <div className="yt-channel-id">
                IG User ID: <code>{igUserId}</code> • Meta Graph API v19.0
              </div>
            </div>
          </div>

          <div className="yt-card-right">
            <span className="yt-connected-badge">
              <CheckCircleIcon size={13} color="#10b981" />
              Instagram Connected
            </span>

            <button
              className="btn btn-secondary yt-sync-btn"
              onClick={handleSync}
              disabled={isSyncing}
            >
              <SyncIcon size={13} />
              <span>{isSyncing ? 'Syncing...' : 'Sync Stats'}</span>
              <ChevronDownIcon size={11} color="#94a3b8" />
            </button>
          </div>
        </div>
      )}

      {syncNotice && (
        <div style={{
          fontSize: '12.5px',
          padding: '8px 14px',
          borderRadius: '10px',
          background: 'rgba(16, 185, 129, 0.15)',
          border: '1px solid rgba(16, 185, 129, 0.3)',
          color: 'var(--accent-mint)'
        }}>
          ℹ️ {syncNotice}
        </div>
      )}

      {/* 2. Autonomous Daily Publishing Hero Card */}
      <AutopilotHero status={autopilotStatus} onToggle={onToggleAutopilot} />

      {/* 3. Metric Cards Row */}
      <StatsRow
        videosCount={reels.length}
        account={account}
        avgQcScore={95.4}
      />

      {/* 4. Live Pipeline Activity & Quick Action Row */}
      <div className="bottom-dashboard-grid">
        <ActivityFeed />

        <div className="card quick-action-card">
          <div>
            <div className="quick-action-header">
              <div className="quick-action-tile">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="#ffffff">
                  <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" />
                </svg>
              </div>
              <h3 className="quick-action-title">Quick Action</h3>
            </div>
            <p className="quick-action-desc" style={{ marginTop: '12px' }}>
              Manually trigger the full autopilot pipeline now. Researches, scripts, synthesizes voice via Edge-TTS, extracts kinetic ASS subtitles in safe zone, renders 1080x1920 MP4 via FFmpeg, and verifies QC gate (&gt;=90/100).
            </p>
          </div>

          <button
            className="btn btn-primary quick-action-btn"
            onClick={onGenerateClick}
          >
            <PlayIcon size={16} />
            <span>+ Create &amp; Render Reel Now</span>
          </button>
        </div>
      </div>
    </div>
  );
};
