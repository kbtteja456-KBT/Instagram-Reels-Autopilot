import React, { useState } from 'react';
import { Reel } from '../services/api';
import { TrashIcon, ExternalLinkIcon, CheckCircleIcon } from '../components/Icons';

interface VideosPageProps {
  reels: Reel[];
  onGenerateClick: () => void;
  onPublishReel: (reelId: string) => Promise<void>;
  onDeleteReel?: (reelId: string) => void;
}

export const VideosPage: React.FC<VideosPageProps> = ({
  reels,
  onGenerateClick,
  onPublishReel,
  onDeleteReel
}) => {
  const [selectedVideo, setSelectedVideo] = useState<Reel | null>(null);
  const [publishingId, setPublishingId] = useState<string | null>(null);
  const [feedbackMessage, setFeedbackMessage] = useState<string | null>(null);

  const handleOpenVideo = (video: Reel) => {
    setSelectedVideo(video);
  };

  const handlePublish = async (video: Reel) => {
    setPublishingId(video._id);
    setFeedbackMessage(null);
    try {
      await onPublishReel(video._id);
      setFeedbackMessage(`🎉 Published successfully to your connected Instagram account!`);
      if (selectedVideo?._id === video._id) {
        setSelectedVideo({
          ...selectedVideo,
          status: 'PUBLISHED',
          instagram_url: selectedVideo.instagram_url || `https://www.instagram.com/reel/C_Mock123/`
        });
      }
    } catch (err: any) {
      setFeedbackMessage(`Upload error: ${err.message || 'Failed to publish to Instagram'}`);
    } finally {
      setPublishingId(null);
    }
  };

  return (
    <div className="page-body">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px' }}>
        <div>
          <h2 style={{ fontFamily: 'var(--font-display)', fontSize: '22px', fontWeight: 700 }}>Rendered &amp; Published Reels</h2>
          <p style={{ color: 'var(--text-muted)', fontSize: '14px' }}>
            Manage rendered 1080x1920 MP4 vertical assets, QC audits (&gt;=90/100), and live Instagram Reels.
          </p>
        </div>
        <button className="btn btn-primary" onClick={onGenerateClick}>
          + Render New Reel
        </button>
      </div>

      {feedbackMessage && (
        <div
          style={{
            padding: '12px 18px',
            borderRadius: '10px',
            background: 'rgba(16, 185, 129, 0.15)',
            border: '1px solid rgba(16, 185, 129, 0.35)',
            color: '#34d399',
            fontSize: '13px',
            fontWeight: 600,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
          }}
        >
          <span>{feedbackMessage}</span>
          <button onClick={() => setFeedbackMessage(null)} style={{ background: 'none', border: 'none', color: '#34d399', cursor: 'pointer' }}>✕</button>
        </div>
      )}

      {/* Video Cards Grid */}
      <div className="video-grid">
        {reels.map((video) => {
          const isPublished = video.status === 'PUBLISHED';
          const filename = video.file_path.split('/').pop() || video.file_path.split('\\').pop();

          return (
            <div
              key={video._id}
              className="video-card"
              onClick={() => handleOpenVideo(video)}
              style={{ cursor: 'pointer' }}
            >
              <div className="video-thumbnail-wrapper">
                <div
                  style={{
                    width: '100%',
                    height: '100%',
                    background: 'linear-gradient(180deg, #111827 0%, #0b0f19 100%)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: '#f59e0b',
                    fontSize: '32px'
                  }}
                >
                  ▶
                </div>

                <div className="video-qc-badge">
                  QC {video.quality_score || 95}/100
                </div>

                <div className="video-duration-badge">
                  {video.duration_seconds || 45}s
                </div>
              </div>

              <div className="video-info">
                <h4 className="video-title">{video.title}</h4>
                <div className="video-meta" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span>{isPublished ? '● Published' : '○ Ready to Publish'}</span>
                  <span style={{ color: isPublished ? '#10b981' : '#f59e0b', fontWeight: 600 }}>
                    {video.status}
                  </span>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Video Detail & 9:16 Preview Modal */}
      {selectedVideo && (
        <div
          style={{
            position: 'fixed',
            inset: 0,
            zIndex: 100,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            background: 'rgba(0, 0, 0, 0.85)',
            backdropFilter: 'blur(12px)',
            padding: '20px'
          }}
          onClick={() => setSelectedVideo(null)}
        >
          <div
            className="card"
            style={{
              maxWidth: '840px',
              width: '100%',
              display: 'flex',
              gap: '24px',
              maxHeight: '90vh',
              overflowY: 'auto'
            }}
            onClick={(e) => e.stopPropagation()}
          >
            {/* Left: 9:16 Viewport */}
            <div style={{ flexShrink: 0 }}>
              <div className="smartphone-viewport">
                <div className="smartphone-notch" />
                <video
                  src={`/api/media/download/${selectedVideo.file_path.split('/').pop()?.split('\\').pop()}`}
                  controls
                  autoPlay
                  loop
                  playsInline
                  style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                />
              </div>
            </div>

            {/* Right: Metadata & Actions */}
            <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '14px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <h3 style={{ fontFamily: 'var(--font-display)', fontSize: '18px', fontWeight: 700 }}>
                  {selectedVideo.title}
                </h3>
                <button
                  onClick={() => setSelectedVideo(null)}
                  style={{ background: 'none', border: 'none', color: '#94a3b8', fontSize: '18px', cursor: 'pointer' }}
                >
                  ✕
                </button>
              </div>

              <div>
                <span style={{ fontSize: '11px', textTransform: 'uppercase', fontWeight: 700, color: 'var(--text-muted)' }}>
                  Quality Control Audit
                </span>
                <div style={{ marginTop: '4px', display: 'flex', gap: '8px' }}>
                  <span className="status-badge-published">Score {selectedVideo.quality_score}/100</span>
                  <span className="slot-pill-3d" style={{ padding: '2px 8px', fontSize: '11px' }}>1080x1920 (9:16)</span>
                  <span className="slot-pill-3d" style={{ padding: '2px 8px', fontSize: '11px' }}>30 FPS</span>
                </div>
              </div>

              <div>
                <span style={{ fontSize: '11px', textTransform: 'uppercase', fontWeight: 700, color: 'var(--text-muted)' }}>
                  Caption &amp; Hashtags
                </span>
                <p style={{
                  fontSize: '13px',
                  color: '#cbd5e1',
                  background: 'rgba(8, 12, 22, 0.7)',
                  padding: '12px',
                  borderRadius: '10px',
                  border: '1px solid rgba(255, 255, 255, 0.08)',
                  marginTop: '4px',
                  whiteSpace: 'pre-wrap',
                  lineHeight: '1.5'
                }}>
                  {selectedVideo.caption}
                </p>
              </div>

              <div style={{ marginTop: 'auto', paddingTop: '16px', display: 'flex', gap: '12px' }}>
                {selectedVideo.status === 'PUBLISHED' && selectedVideo.instagram_url ? (
                  <a
                    href={selectedVideo.instagram_url}
                    target="_blank"
                    rel="noreferrer"
                    className="btn btn-primary"
                    style={{ background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)', textDecoration: 'none' }}
                  >
                    <ExternalLinkIcon size={14} />
                    <span>Live on Instagram</span>
                  </a>
                ) : (
                  <button
                    className="btn btn-primary"
                    onClick={() => handlePublish(selectedVideo)}
                    disabled={publishingId === selectedVideo._id}
                    style={{ background: 'linear-gradient(135deg, #833ab4 0%, #fd1d1d 50%, #fcb045 100%)' }}
                  >
                    <span>{publishingId === selectedVideo._id ? '⏳ Processing with Meta...' : '🚀 Publish to Instagram'}</span>
                  </button>
                )}

                <button
                  className="btn btn-secondary"
                  onClick={() => setSelectedVideo(null)}
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
