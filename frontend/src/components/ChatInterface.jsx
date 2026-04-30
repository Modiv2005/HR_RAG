"use client";

import { useState, useRef, useEffect } from 'react';

export default function ChatInterface() {
  const [query, setQuery] = useState('');
  const [messages, setMessages] = useState([
    { role: 'assistant', content: 'Hello! I am your AI HR Assistant. I can answer questions based strictly on our company policy documents. How can I help you today?', sources: null }
  ]);
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleQuery = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    const userMessage = { role: 'user', content: query };
    setMessages((prev) => [...prev, userMessage]);
    setQuery('');
    setLoading(true);

    try {
      const response = await fetch('http://localhost:8000/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: userMessage.content }),
      });

      if (!response.ok) {
        throw new Error('Failed to get answer');
      }

      const data = await response.json();
      
      setMessages((prev) => [...prev, { 
        role: 'assistant', 
        content: data.answer,
        sources: data.sources && data.sources.length > 0 ? data.sources : null
      }]);
    } catch (error) {
      setMessages((prev) => [...prev, { 
        role: 'assistant', 
        content: `Error: ${error.message}` 
      }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="glass-panel chat-container">
      <h2>Employee Query Chat</h2>
      
      <div className="chat-history">
        {messages.map((msg, idx) => (
          <div key={idx} className={`message ${msg.role}`}>
            <div>{msg.content}</div>
            
            {/* Show sources if assistant used retrieved context */}
            {msg.role === 'assistant' && msg.sources && (
              <div className="source-box">
                <strong>Sources:</strong>
                <ul style={{ marginLeft: '1.5rem', marginTop: '0.5rem' }}>
                  {msg.sources.map((src, i) => (
                    <li key={i}>
                      {src.source} <span style={{opacity: 0.7}}>(relevance score: {src.score.toFixed(2)})</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        ))}
        {loading && (
          <div className="message assistant" style={{ opacity: 0.7 }}>
            Searching policy documents...
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <form className="input-area" onSubmit={handleQuery}>
        <input 
          type="text" 
          value={query} 
          onChange={(e) => setQuery(e.target.value)} 
          placeholder="e.g. How many casual leaves are allowed?"
          disabled={loading}
        />
        <button type="submit" disabled={loading || !query.trim()}>
          Ask
        </button>
      </form>
    </div>
  );
}
