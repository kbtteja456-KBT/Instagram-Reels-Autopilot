import React from 'react';

interface IconProps {
  className?: string;
  size?: number;
  color?: string;
  style?: React.CSSProperties;
}

export const PlayTileIcon: React.FC<{ size?: number }> = ({ size = 36 }) => (
  <svg width={size} height={size} viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
    <defs>
      <linearGradient id="igTileGrad" x1="0" y1="0" x2="40" y2="40" gradientUnits="userSpaceOnUse">
        <stop stopColor="#833ab4" />
        <stop offset="0.5" stopColor="#e1306c" />
        <stop offset="1" stopColor="#fcb045" />
      </linearGradient>
      <filter id="igTileShadow" x="-20%" y="-20%" width="140%" height="140%">
        <feDropShadow dx="0" dy="4" stdDeviation="4" floodColor="#e1306c" floodOpacity="0.45" />
      </filter>
    </defs>
    <rect x="2" y="2" width="36" height="36" rx="11" fill="url(#igTileGrad)" filter="url(#igTileShadow)" stroke="rgba(255,255,255,0.4)" strokeWidth="1" />
    <path d="M16.5 13.5L27 20L16.5 26.5V13.5Z" fill="white" />
  </svg>
);

export const InstagramTileIcon: React.FC<{ size?: number }> = ({ size = 44 }) => (
  <svg width={size} height={size} viewBox="0 0 44 44" fill="none" xmlns="http://www.w3.org/2000/svg">
    <defs>
      <linearGradient id="igBannerGrad" x1="0" y1="0" x2="44" y2="44" gradientUnits="userSpaceOnUse">
        <stop stopColor="#833ab4" />
        <stop offset="0.4" stopColor="#fd1d1d" />
        <stop offset="1" stopColor="#fcb045" />
      </linearGradient>
      <filter id="igBannerShadow" x="-20%" y="-20%" width="140%" height="140%">
        <feDropShadow dx="0" dy="5" stdDeviation="6" floodColor="#e1306c" floodOpacity="0.4" />
      </filter>
    </defs>
    <rect x="2" y="2" width="40" height="40" rx="12" fill="url(#igBannerGrad)" filter="url(#igBannerShadow)" stroke="rgba(255,255,255,0.3)" strokeWidth="1" />
    <rect x="11" y="11" width="22" height="22" rx="6" stroke="white" strokeWidth="2.2" fill="none" />
    <circle cx="22" cy="22" r="5" stroke="white" strokeWidth="2.2" fill="none" />
    <circle cx="28.5" cy="15.5" r="1.5" fill="white" />
  </svg>
);

export const YouTubeRedTileIcon = InstagramTileIcon;

export const CalendarAmberTileIcon: React.FC<{ size?: number }> = ({ size = 48 }) => (
  <svg width={size} height={size} viewBox="0 0 52 52" fill="none" xmlns="http://www.w3.org/2000/svg">
    <defs>
      <linearGradient id="calGrad" x1="0" y1="0" x2="52" y2="52" gradientUnits="userSpaceOnUse">
        <stop stopColor="#fbbf24" />
        <stop offset="0.6" stopColor="#f59e0b" />
        <stop offset="1" stopColor="#d97706" />
      </linearGradient>
      <filter id="calShadow" x="-20%" y="-20%" width="140%" height="140%">
        <feDropShadow dx="0" dy="6" stdDeviation="6" floodColor="#d97706" floodOpacity="0.4" />
      </filter>
    </defs>
    <rect x="3" y="3" width="46" height="46" rx="14" fill="url(#calGrad)" filter="url(#calShadow)" stroke="rgba(255,255,255,0.35)" strokeWidth="1.2" />
    <rect x="12" y="10" width="28" height="5" rx="2" fill="rgba(255,255,255,0.8)" />
    <circle cx="18" cy="9" r="2" fill="#78350f" />
    <circle cx="34" cy="9" r="2" fill="#78350f" />
    <path d="M22 23L33 29.5L22 36V23Z" fill="white" />
  </svg>
);

export const CalendarBlueTileIcon = CalendarAmberTileIcon;

export const DashboardIcon: React.FC<IconProps> = ({ size = 18, color = 'currentColor' }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
    <polyline points="9 22 9 12 15 12 15 22" />
  </svg>
);

export const VideosIcon: React.FC<IconProps> = ({ size = 18, color = 'currentColor' }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <rect width="20" height="20" x="2" y="2" rx="4" />
    <path d="M2 8h20" />
    <path d="m6 2 3 6" />
    <path d="m15 2 3 6" />
    <path d="m11 12 5 3-5 3v-6Z" fill={color} />
  </svg>
);

export const HealthIcon: React.FC<IconProps> = ({ size = 18, color = 'currentColor' }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M22 12h-4l-3 9L9 3l-3 9H2" />
  </svg>
);

export const StyleIcon: React.FC<IconProps> = ({ size = 18, color = 'currentColor' }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M21.174 6.812a1 1 0 0 0-3.986-3.987L3.842 16.174a2 2 0 0 0-.5.83l-1.321 4.352a.5.5 0 0 0 .623.622l4.353-1.32a2 2 0 0 0 .83-.497z" />
    <path d="m15 5 4 4" />
  </svg>
);

export const SettingsIcon: React.FC<IconProps> = ({ size = 18, color = 'currentColor' }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="12" r="3" />
    <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z" />
  </svg>
);

export const CheckCircleIcon: React.FC<IconProps> = ({ size = 14, color = '#10b981' }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
    <polyline points="20 6 9 17 4 12" />
  </svg>
);

export const ClockIcon: React.FC<IconProps> = ({ size = 14, color = '#f59e0b' }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="12" r="10" />
    <polyline points="12 6 12 12 16 14" />
  </svg>
);

export const SyncIcon: React.FC<IconProps> = ({ size = 14, color = 'currentColor' }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
    <path d="M21.5 2v6h-6M21.34 15.57a10 10 0 1 1-.57-8.38l5.67-5.67" />
  </svg>
);

export const ChevronDownIcon: React.FC<IconProps> = ({ size = 14, color = 'currentColor' }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
    <path d="m6 9 6 6 6-6" />
  </svg>
);

export const PauseIcon: React.FC<IconProps> = ({ size = 16, color = 'currentColor' }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill={color}>
    <rect x="6" y="4" width="4" height="16" rx="1.5" />
    <rect x="14" y="4" width="4" height="16" rx="1.5" />
  </svg>
);

export const PlayIcon: React.FC<IconProps> = ({ size = 16, color = 'currentColor' }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill={color}>
    <polygon points="5 3 19 12 5 21 5 3" />
  </svg>
);

export const SparklineAmber: React.FC<{ width?: number; height?: number }> = ({ width = 110, height = 36 }) => (
  <svg width={width} height={height} viewBox="0 0 120 40" fill="none" xmlns="http://www.w3.org/2000/svg">
    <defs>
      <linearGradient id="amberSparkGrad" x1="0" y1="0" x2="0" y2="40" gradientUnits="userSpaceOnUse">
        <stop stopColor="#f59e0b" stopOpacity="0.4" />
        <stop offset="1" stopColor="#f59e0b" stopOpacity="0" />
      </linearGradient>
    </defs>
    <path
      d="M0 32 C 25 32, 35 30, 50 25 C 65 20, 75 14, 90 20 C 105 26, 110 8, 120 4"
      stroke="#f59e0b"
      strokeWidth="2.5"
      strokeLinecap="round"
    />
    <path
      d="M0 32 C 25 32, 35 30, 50 25 C 65 20, 75 14, 90 20 C 105 26, 110 8, 120 4 V 40 H 0 Z"
      fill="url(#amberSparkGrad)"
    />
  </svg>
);

export const SparklineBlue = SparklineAmber;

export const SparklineGreen: React.FC<{ width?: number; height?: number }> = ({ width = 110, height = 36 }) => (
  <svg width={width} height={height} viewBox="0 0 120 40" fill="none" xmlns="http://www.w3.org/2000/svg">
    <defs>
      <linearGradient id="greenSparkGrad" x1="0" y1="0" x2="0" y2="40" gradientUnits="userSpaceOnUse">
        <stop stopColor="#10b981" stopOpacity="0.4" />
        <stop offset="1" stopColor="#10b981" stopOpacity="0" />
      </linearGradient>
    </defs>
    <path
      d="M0 34 C 20 34, 30 26, 45 28 C 60 30, 70 18, 85 22 C 100 26, 110 6, 120 2"
      stroke="#10b981"
      strokeWidth="2.5"
      strokeLinecap="round"
    />
    <path
      d="M0 34 C 20 34, 30 26, 45 28 C 60 30, 70 18, 85 22 C 100 26, 110 6, 120 2 V 40 H 0 Z"
      fill="url(#greenSparkGrad)"
    />
  </svg>
);

export const TrashIcon: React.FC<IconProps> = ({ size = 16, color = 'currentColor', style }) => (
  <svg
    width={size}
    height={size}
    viewBox="0 0 24 24"
    fill="none"
    stroke={color}
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
    style={style}
  >
    <path d="M3 6h18" />
    <path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6" />
    <path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2" />
    <line x1="10" x2="10" y1="11" y2="17" />
    <line x1="14" x2="14" y1="11" y2="17" />
  </svg>
);

export const KeyIcon: React.FC<IconProps> = ({ size = 18, color = 'currentColor' }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="7.5" cy="15.5" r="5.5" />
    <path d="m21 2-9.6 9.6" />
    <path d="m15.5 7.5 3 3L22 7l-3-3" />
  </svg>
);

export const ShieldIcon: React.FC<IconProps> = ({ size = 18, color = 'currentColor' }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
  </svg>
);

export const SparklesIcon: React.FC<IconProps> = ({ size = 18, color = 'currentColor' }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z" />
  </svg>
);

export const ExternalLinkIcon: React.FC<IconProps> = ({ size = 14, color = 'currentColor' }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" />
    <polyline points="15 3 21 3 21 9" />
    <line x1="10" y1="14" x2="21" y2="3" />
  </svg>
);

export const RefreshIcon: React.FC<IconProps> = ({ size = 16, color = 'currentColor' }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M21 12a9 9 0 0 0-9-9 9.75 9.75 0 0 0-6.74 2.74L3 8" />
    <path d="M3 3v5h5" />
    <path d="M3 12a9 9 0 0 0 9 9 9.75 9.75 0 0 0 6.74-2.74L21 16" />
    <path d="M16 21h5v-5" />
  </svg>
);

export const InstagramIcon: React.FC<IconProps> = ({ size = 20, color = 'currentColor', className }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill={color} className={className}>
    <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z" />
  </svg>
);

export const ReelsIcon: React.FC<IconProps> = ({ size = 20, color = 'currentColor', className }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
    <rect x="2" y="2" width="20" height="20" rx="5" ry="5" />
    <path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z" />
    <polygon points="10 8 16 12 10 16 10 8" fill={color} />
  </svg>
);

export const MetaIcon: React.FC<IconProps> = ({ size = 20, color = 'currentColor', className }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill={color} className={className}>
    <path d="M16.99 4c-1.89 0-3.56.91-4.99 2.37C10.57 4.91 8.9 4 7.01 4 3.14 4 0 7.14 0 11.01c0 4.7 4.54 8.79 10.87 11.23.72.28 1.54.28 2.26 0C19.46 19.8 24 15.71 24 11.01 24 7.14 20.86 4 16.99 4zm-4.99 15.42C6.73 17.29 2.5 13.9 2.5 11.01c0-2.48 2.02-4.51 4.51-4.51 1.65 0 3.19.89 4.02 2.32.42.73 1.52.73 1.94 0 .83-1.43 2.37-2.32 4.02-2.32 2.49 0 4.51 2.03 4.51 4.51 0 2.89-4.23 6.28-9.5 8.41z" />
  </svg>
);
