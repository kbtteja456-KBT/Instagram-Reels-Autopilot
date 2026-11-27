import React, { useEffect, useRef, useState } from 'react';

export interface GitaMessage {
  role: 'user' | 'assistant';
  content: string;
}

const languages = [
  'English', 'हिन्दी', 'తెలుగు', 'தமிழ்', 'বাংলা', 'ಕನ್ನಡ', 'മലയാളം', 'मराठी', 'ગુજરાતી', 'ਪੰਜਾਬੀ', 'ଓଡ଼ିଆ', 'ಕನ್ನಡ', 'नेपाली', 'සිංහල', 'Français', 'Español', 'Deutsch', '日本語', '中文', 'العربية', 'فارسی', 'Русский', 'Italiano', 'Português'
].filter((language, index, all) => all.indexOf(language) === index);

const suggestions = [
  { title: 'Find calm in uncertainty', question: 'What does the Bhagavad Gita teach about finding calm when life feels uncertain?' },
  { title: 'Act without attachment', question: 'Explain the Gita’s teaching on action without attachment, with an example from everyday life.' },
  { title: 'Understand the self', question: 'How does the Bhagavad Gita describe the self? Please explain simply and mention a verse if you can.' },
  { title: 'Bring wisdom to work', question: 'How can I apply the Gita’s ideas to stress and responsibility at work?' },
];

interface GitaChatProps {
  messages: GitaMessage[];
  language: string;
  onLanguageChange: (language: string) => void;
  onSend: (message: string) => void;
  isLoading: boolean;
  error: string | null;
  onRetry: () => void;
}

export function GitaChat({ messages, language, onLanguageChange, onSend, isLoading, error, onRetry }: GitaChatProps) {
  const [draft, setDraft] = useState('');
  const endRef = useRef<HTMLDivElement>(null);
  const isConversationStarted = messages.length > 0;

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth', block: 'end' });
  }, [messages, isLoading]);

  const submit = (question = draft) => {
    const cleaned = question.trim();
    if (!cleaned || isLoading) return;
    setDraft('');
    onSend(cleaned);
  };

  return (
    <main className="gita-main">
      <header className="gita-topbar">
        <div className="gita-breadcrumb"><span className="gita-breadcrumb-dot" /> <span>YOUR SPACE FOR WISDOM</span></div>
        <label className="gita-language-label" htmlFor="gita-language">Respond in
          <select id="gita-language" value={language} onChange={(event) => onLanguageChange(event.target.value)}>
            {languages.map((item) => <option key={item} value={item}>{item}</option>)}
          </select>
        </label>
      </header>

      <div className={`gita-conversation ${isConversationStarted ? 'has-messages' : ''}`}>
        {!isConversationStarted ? (
          <section className="gita-welcome" aria-labelledby="gita-title">
            <div className="gita-welcome-symbol" aria-hidden="true"><span>ॐ</span></div>
            <p className="gita-eyebrow">AN ANCIENT WISDOM. A VERY HUMAN JOURNEY.</p>
            <h1 id="gita-title">A little more clarity,<br /><em>one question at a time.</em></h1>
            <p className="gita-intro-copy">Explore the Bhagavad Gita with a thoughtful companion. Ask what is on your mind; discover its teachings, context and ways to carry them into everyday life.</p>

            <div className="gita-suggestion-grid" aria-label="Questions to get started">
              {suggestions.map((suggestion, index) => (
                <button className="gita-suggestion" key={suggestion.title} onClick={() => submit(suggestion.question)} type="button">
                  <span className="gita-suggestion-index">0{index + 1}</span>
                  <span>{suggestion.title}</span>
                  <span className="gita-suggestion-arrow" aria-hidden="true">↗</span>
                </button>
              ))}
            </div>
          </section>
        ) : (
          <section className="gita-message-list" aria-label="Conversation" aria-live="polite">
            <div className="gita-message-intro"><span className="gita-mini-om">ॐ</span><span>A conversation rooted in the Gita</span></div>
            {messages.map((message, index) => (
              <article className={`gita-message gita-message-${message.role}`} key={`${message.role}-${index}`}>
                {message.role === 'assistant' && <div className="gita-assistant-mark" aria-hidden="true">ॐ</div>}
                <div className="gita-message-content">
                  <span className="gita-message-label">{message.role === 'assistant' ? 'GITA COMPANION' : 'YOU'}</span>
                  <p>{message.content}</p>
                </div>
              </article>
            ))}
            {isLoading && <div className="gita-message gita-message-assistant" role="status"><div className="gita-assistant-mark" aria-hidden="true">ॐ</div><div className="gita-message-content"><span className="gita-message-label">GITA COMPANION</span><p className="gita-thinking">Reflecting<span>.</span><span>.</span><span>.</span></p></div></div>}
            {error && <div className="gita-error" role="alert"><span>{error}</span><button type="button" onClick={onRetry}>Try again</button></div>}
            <div ref={endRef} />
          </section>
        )}
      </div>

      {!isConversationStarted && <div className="gita-daily-note"><span aria-hidden="true">✳</span><span>Not sure where to begin? Start with whatever is on your heart.</span></div>}

      <div className="gita-composer-wrap">
        <form className="gita-composer" onSubmit={(event) => { event.preventDefault(); submit(); }}>
          <label className="sr-only" htmlFor="gita-question">Ask a question about the Bhagavad Gita</label>
          <textarea
            id="gita-question"
            rows={1}
            maxLength={1800}
            placeholder="Ask about the Gita, life, or what’s on your mind…"
            value={draft}
            onChange={(event) => setDraft(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === 'Enter' && !event.shiftKey) {
                if (event.nativeEvent.isComposing || event.keyCode === 229) return;
                event.preventDefault();
                submit();
              }
            }}
            disabled={isLoading}
          />
          <button className="gita-send-button" type="submit" disabled={!draft.trim() || isLoading} aria-label="Send question">
            <span>Ask</span><span className="gita-send-arrow" aria-hidden="true">↑</span>
          </button>
        </form>
        <p className="gita-disclaimer">A reflective guide, not a substitute for your own study or a teacher. Interpretations can vary across traditions.</p>
      </div>
    </main>
  );
}
