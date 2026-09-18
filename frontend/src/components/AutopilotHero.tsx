import React from 'react';
import { CalendarAmberTileIcon, CheckCircleIcon, ClockIcon, PauseIcon, PlayIcon } from './Icons';
import { AutopilotStatus } from '../services/api';

interface AutopilotHeroProps {
  status?: AutopilotStatus;
  onToggle: () => void;
}

export const AutopilotHero: React.FC<AutopilotHeroProps> = ({ status, onToggle }) => {
  const isEnabled = status?.is_active ?? true;

  const renderSlotBadge = (timeStr: string) => {
    return (
      <span className="status-badge-scheduled">
        <ClockIcon size={12} color="#f59e0b" />
        {timeStr}
      </span>
    );
  };

  return (
    <div className="card autopilot-hero-3d">
      <div className="hero-left-section">
        <div style={{ flexShrink: 0 }}>
          <CalendarAmberTileIcon size={48} />
        </div>
        <div className="hero-content-col">
          <h2>Autonomous Daily Reels Publishing</h2>
          <p>
            Target: 2 original 1080x1920 Instagram Reels daily at {status?.slot1_time || '07:00'} &amp; {status?.slot2_time || '18:00'} ({status?.timezone || 'Asia/Kolkata'}).<br />
            Pre-generation windows run autonomously with strict Quality Control (&gt;= 90/100).
          </p>
          <div className="hero-slots-row">
            <div className="slot-pill-3d">
              <span>☀️ Morning Slot ({status?.slot1_time || '07:00'})</span>
              {renderSlotBadge('Scheduled')}
            </div>
            <div className="slot-pill-3d">
              <span>🌙 Evening Slot ({status?.slot2_time || '18:00'})</span>
              {renderSlotBadge('Scheduled')}
            </div>
          </div>
        </div>
      </div>

      <div className="hero-right-section">
        <div className="robot-column">
          <div className="robot-mascot-wrapper">
            <div className="robot-speech-bubble">
              Creating Viral Reels Everyday!
            </div>
            <img
              src="/mascot.jpg"
              alt="Reels Autopilot Mascot"
              className="robot-mascot-img"
            />
          </div>

          <button
            className={`btn hero-pause-btn ${isEnabled ? 'btn-danger' : 'btn-primary'}`}
            onClick={onToggle}
          >
            {isEnabled ? (
              <>
                <PauseIcon size={15} />
                <span>Pause Autopilot</span>
              </>
            ) : (
              <>
                <PlayIcon size={15} />
                <span>Resume Autopilot</span>
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};
