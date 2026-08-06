import React, { useEffect, useRef } from 'react';

export default function ChatWindow({ messages, isLoading }) {
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  return (
    <div className="chat-area">
      {messages.map((msg, index) => (
      <div key={index} className={`message-bubble ${msg.role === 'user' ? 'user' : 'bot'}${msg.isError ? ' error-bubble' : ''}`}>
          {msg.content}
        </div>
      ))}

      {isLoading && (
        <div className="message-bubble bot">
          <div className="typing-indicator">
            <div className="typing-dot" />
            <div className="typing-dot" />
            <div className="typing-dot" />
          </div>
        </div>
      )}

      <div ref={bottomRef} />
    </div>
  );
}
