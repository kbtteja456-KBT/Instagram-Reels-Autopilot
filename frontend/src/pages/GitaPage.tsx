import React, { useCallback, useState } from 'react';
import { GitaChat, GitaMessage } from '../components/gita/GitaChat';
import { GitaSidebar } from '../components/gita/GitaSidebar';
import './gita.css';

const configuredApiUrl = String((import.meta as any).env?.VITE_API_URL || '').trim();
const API_BASE = configuredApiUrl
  ? `${(configuredApiUrl.startsWith('http') ? configuredApiUrl : `https://${configuredApiUrl}`).replace(/\/$/, '')}${configuredApiUrl.replace(/\/$/, '').endsWith('/api') ? '' : '/api'}`
  : '/api';

export function GitaPage() {
  const [messages, setMessages] = useState<GitaMessage[]>([]);
  const [language, setLanguage] = useState('English');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastQuestion, setLastQuestion] = useState('');

  React.useEffect(() => {
    document.title = 'Gita — A companion for life';
    const description = document.querySelector('meta[name="description"]') || document.createElement('meta');
    description.setAttribute('name', 'description');
    description.setAttribute('content', 'Explore the Bhagavad Gita through thoughtful, multilingual answers, practical reflections and guided reading paths.');
    if (!description.parentNode) document.head.appendChild(description);
  }, []);

  const ask = useCallback(async (question: string, history = messages) => {
    setLastQuestion(question);
    setError(null);
    setIsLoading(true);
    setMessages((current) => [...current, { role: 'user', content: question }]);
    try {
      const response = await fetch(`${API_BASE}/gita/ask`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question,
          language,
          history: history.slice(-8).map(({ role, content }) => ({ role, content })),
        }),
      });
      const data = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(data.detail || 'The companion is having trouble responding. Please try again.');
      setMessages((current) => [...current, { role: 'assistant', content: data.answer }]);
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : 'Something went wrong. Please try again.');
    } finally {
      setIsLoading(false);
    }
  }, [language, messages]);

  const startNew = () => {
    setMessages([]);
    setError(null);
    setLastQuestion('');
  };

  return (
    <div className="gita-app">
      <GitaSidebar onNewConversation={startNew} onQuestion={(question) => ask(question, [])} isBusy={isLoading} />
      <GitaChat
        messages={messages}
        language={language}
        onLanguageChange={setLanguage}
        onSend={(question) => ask(question)}
        isLoading={isLoading}
        error={error}
        onRetry={() => lastQuestion && ask(lastQuestion, messages.slice(0, -1))}
      />
    </div>
  );
}
