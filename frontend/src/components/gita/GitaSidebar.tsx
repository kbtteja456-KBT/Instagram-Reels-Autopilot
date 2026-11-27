import React from 'react';

const readingPaths = [
  { number: '01', title: 'The pause before action', chapter: 'Chapter 1 · Arjuna’s inner conflict' },
  { number: '02', title: 'A steadier mind', chapter: 'Chapter 2 · The wisdom of discernment' },
  { number: '03', title: 'Work with intention', chapter: 'Chapter 3 · Karma Yoga' },
];

interface GitaSidebarProps {
  onNewConversation: () => void;
  onQuestion: (question: string) => void;
  isBusy: boolean;
}

export function GitaSidebar({ onNewConversation, onQuestion, isBusy }: GitaSidebarProps) {
  return (
    <aside className="gita-sidebar" aria-label="Bhagavad Gita companion navigation">
      <a className="gita-brand" href="/gita" aria-label="Gita companion home">
        <span className="gita-brand-mark" aria-hidden="true">ॐ</span>
        <span className="gita-brand-copy"><strong>Gita</strong><small>A companion for life</small></span>
      </a>

      <button className="gita-new-chat" onClick={onNewConversation} type="button" disabled={isBusy}>
        <span aria-hidden="true">＋</span> Begin a reflection
      </button>

      <div className="gita-side-label">A PATH TO EXPLORE</div>
      <nav className="gita-reading-list" aria-label="Reading paths">
        {readingPaths.map((path) => (
          <button
            className="gita-reading-item"
            key={path.number}
            onClick={() => onQuestion(`Guide me through ${path.title.toLowerCase()} in ${path.chapter}. Include one practical reflection.`)}
            type="button"
          >
            <span className="gita-reading-number">{path.number}</span>
            <span><strong>{path.title}</strong><small>{path.chapter}</small></span>
          </button>
        ))}
      </nav>

      <div className="gita-sidebar-spacer" />

      <button
        className="gita-practice-card"
        onClick={() => onQuestion('Offer me a gentle, practical Bhagavad Gita-inspired reflection for today, with one small action I can try.')}
        type="button"
      >
        <span className="gita-practice-kicker"><span className="gita-sun-dot" /> A MOMENT FOR TODAY</span>
        <strong>Begin where you are.</strong>
        <span>Ask for a small practice to carry into your day.</span>
        <span className="gita-practice-link">Find a practice <span aria-hidden="true">↗</span></span>
      </button>

      <a className="gita-return-link" href="/autopilot" aria-label="Return to the Instagram Autopilot workspace">
        <span aria-hidden="true">←</span> Back to your workspace
      </a>
    </aside>
  );
}
